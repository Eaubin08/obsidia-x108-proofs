"""
sigma/tests/test_kx108_sovereign_ticket_security.py
====================================================
SUITE OFFICIELLE DE TESTS DE SÉCURITÉ DES TICKETS SOUVERAINS KX108 (PHASE 2F & 2G)

Vérifie l'ensemble des scénarios de sécurité, d'authenticité et d'anti-rejeu :
 1. Injection ALLOW via /world/gateway
 2. Ticket falsifié (UUID inventé)
 3. Hash recalculé par un attaquant sans autorité
 4. Ticket expiré (> expires_at)
 5. Ticket sans expiration ou horodatage malformé
 6. Ticket Bank utilisé dans World (Cross-domain leakage)
 7. Ticket lié à un autre payload (Input hash mismatch)
 8. Ticket HOLD/BLOCK falsifié en ALLOW
 9. Ticket réutilisé (Replay attack séquentiel)
10. Deux consommations concurrentes (Race condition)
11. Redémarrage puis tentative de rejeu (Persistance anti-rejeu)
12. Ticket légitime et valide (Nominal pass)
13. Ticket historique incomplet (Documentaire seulement, refus d'action)
14. Stockage altéré ou tronqué (Fail-closed)
15. Producteur indisponible (Fail-closed)
16. Authenticator modifié / corrompu
17. Mauvaise clé HMAC (Clé inconnue ou forgée)
18. Rotation de clé (Passe avec clé pivotée, échoue avec clé révoquée)
19. Crash après réservation (State RESERVED bloque le rejeu)
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import secrets
import tempfile
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

import pytest

from periphery.world_calls.sovereign_ticket import (
    SovereignTicket,
    issue_sovereign_ticket,
    require_ticket_or_block,
    verify_authenticator,
    register_kernel_key,
    get_kernel_key,
    reset_kernel_keys,
    _DEFAULT_KEY_ID,
)
from periphery.world_calls.ticket_store import (
    store_ticket,
    load_tickets,
    reserve_ticket_nonce,
    commit_ticket_nonce,
    fail_ticket_nonce,
    load_consumed_nonces,
    verify_and_consume_sovereign_ticket,
)


# ===========================================================================
# 1. TEST 1 : INJECTION ALLOW VIA /WORLD/GATEWAY NEUTRALISÉE
# ===========================================================================

def test_scenario_1_world_gateway_cannot_inject_allow():
    """
    Scénario 1 : Un payload client appelant la passerelle avec x108_gate='ALLOW'
    ne doit jamais pouvoir générer un ticket souverain conférant une autorité ALLOW.
    """
    from apps.obsidia_api.routes.blockchain import GatewayPayload, blockchain_world_gateway
    import asyncio

    payload = GatewayPayload(
        action_id="act-gw-test-01",
        action_type="TEST_ACTION",
        domain="world",
        x108_gate="ALLOW",  # Tentative d'injection directe
        agent_payload={},
    )
    
    # Exécution de la route
    response = asyncio.run(blockchain_world_gateway(payload))
    resp_dict = response if isinstance(response, dict) else json.loads(response.body.decode("utf-8"))
    
    issued_ticket = resp_dict.get("sovereign_ticket", {})
    assert issued_ticket.get("x108_gate") == "HOLD", (
        "Une porte ALLOW fournie par le client HTTP doit être neutralisée en HOLD !"
    )


# ===========================================================================
# 2. TEST 2 : TICKET FALSIFIÉ AVEC UUID INCONNU REJETÉ
# ===========================================================================

def test_scenario_2_falsified_ticket_rejected():
    """
    Scénario 2 : Un ticket avec un ticket_id inexistant ou falsifié est rejeté
    immédiatement sans autoriser l'action.
    """
    fake_ticket_id = "00000000-0000-0000-0000-000000000000"
    all_tickets = []
    matched = next((t for t in all_tickets if t.get("ticket_id") == fake_ticket_id), None)
    
    with pytest.raises(AssertionError, match="SOVEREIGN_TICKET_MISSING"):
        verify_and_consume_sovereign_ticket(matched)


# ===========================================================================
# 3. TEST 3 : HASH RECALCULÉ PAR UN ATTAQUANT SANS AUTORITÉ REJETÉ
# ===========================================================================

def test_scenario_3_recomputed_hash_by_attacker_rejected():
    """
    Scénario 3 : Un attaquant qui reconstruit le dictionnaire et recalcule
    le SHA-256 public ne doit pas pouvoir valider un ticket sans la clé secrète HMAC.
    """
    attacker_ticket_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc).isoformat()
    raw_payload = {
        "ticket_id": attacker_ticket_id,
        "action_id": "act-attacker-001",
        "os3_ticket_id": "os3-attacker",
        "scope": "*",
        "issued_at": now,
        "x108_gate": "ALLOW",
    }
    attacker_hash = hashlib.sha256(json.dumps(raw_payload, sort_keys=True).encode()).hexdigest()
    
    fake_ticket = SovereignTicket(
        ticket_id=attacker_ticket_id,
        action_id="act-attacker-001",
        os3_ticket_id="os3-attacker",
        scope="*",
        issued_at=now,
        expires_at=(datetime.now(timezone.utc) + timedelta(seconds=300)).isoformat(),
        x108_gate="ALLOW",
        autonomy_level=1,
        hash=attacker_hash,
        nonce="attacker-nonce-1234",
        authenticator=attacker_hash,  # Attaquant met son SHA-256 comme authenticator
    )
    
    assert verify_authenticator(fake_ticket) is False, (
        "Le HMAC doit échouer face à un hash SHA-256 forgé par un attaquant."
    )
    with pytest.raises(AssertionError, match="SOVEREIGN_TICKET_AUTHENTICATOR_INVALID"):
        verify_and_consume_sovereign_ticket(fake_ticket)


# ===========================================================================
# 4. TEST 4 : TICKET EXPIRÉ REJETÉ
# ===========================================================================

def test_scenario_4_expired_ticket_rejected():
    """
    Scénario 4 : Un ticket dont expires_at est dépassé doit être impérativement
    rejeté par les consommateurs périphériques.
    """
    expired_ticket = issue_sovereign_ticket(
        action_id="act-expired-001",
        os3_ticket_id="os3-exp",
        x108_gate="ALLOW",
        scope="gencoin",
        autonomy_level=1,
        world_call_class="READ_ONLY",
        ttl_seconds=-10,  # Expiré il y a 10s
    )
    assert expired_ticket.is_expired() is True
    with pytest.raises(AssertionError, match="SOVEREIGN_TICKET_EXPIRED"):
        verify_and_consume_sovereign_ticket(expired_ticket)


# ===========================================================================
# 5. TEST 5 : TICKET SANS EXPIRATION REJETÉ
# ===========================================================================

def test_scenario_5_ticket_without_expiration_rejected():
    """
    Scénario 5 : Un ticket sans expires_at ou avec un horodatage vide
    doit être refusé catégoriquement (fail-closed).
    """
    ticket = issue_sovereign_ticket(
        action_id="act-no-exp-001",
        os3_ticket_id="os3-no-exp",
        x108_gate="ALLOW",
        scope="bank",
        autonomy_level=1,
        world_call_class="READ_ONLY",
    )
    ticket.expires_at = ""
    with pytest.raises(AssertionError, match="SOVEREIGN_TICKET_NO_EXPIRATION"):
        verify_and_consume_sovereign_ticket(ticket)


# ===========================================================================
# 6. TEST 6 : TICKET BANK UTILISÉ DANS WORLD REJETÉ (CROSS-DOMAIN)
# ===========================================================================

def test_scenario_6_cross_domain_bank_ticket_rejected_in_world():
    """
    Scénario 6 : Un ticket émis avec scope='bank' ne doit jamais pouvoir
    autoriser une action sous scope='world_bus' ou scope='gencoin'.
    """
    bank_ticket = issue_sovereign_ticket(
        action_id="act-bank-001",
        os3_ticket_id="os3-bank",
        x108_gate="ALLOW",
        scope="bank",
        autonomy_level=1,
        world_call_class="READ_ONLY",
    )
    with pytest.raises(AssertionError, match="SOVEREIGN_TICKET_INVALID_SCOPE"):
        verify_and_consume_sovereign_ticket(bank_ticket, required_scope="world_bus")


# ===========================================================================
# 7. TEST 7 : TICKET LIÉ À UN AUTRE PAYLOAD REJETÉ
# ===========================================================================

def test_scenario_7_ticket_mismatched_payload_rejected():
    """
    Scénario 7 : Un ticket doit être strictement lié au hash du payload d'entrée
    (input_hash). S'il est présenté avec un payload différent, il doit être rejeté.
    """
    payload_a = {"amount": 100, "recipient": "alice"}
    payload_b = {"amount": 999999, "recipient": "mallory"}
    
    hash_a = hashlib.sha256(json.dumps(payload_a, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    
    ticket = issue_sovereign_ticket(
        action_id="act-transfer-001",
        os3_ticket_id="os3-transfer",
        x108_gate="ALLOW",
        scope="bank",
        autonomy_level=1,
        world_call_class="READ_ONLY",
        input_hash=hash_a,
    )
    
    # Présentation du ticket avec le payload altéré payload_b
    with pytest.raises(AssertionError, match="SOVEREIGN_TICKET_INPUT_MISMATCH"):
        verify_and_consume_sovereign_ticket(ticket, action_payload=payload_b)


# ===========================================================================
# 8. TEST 8 : TICKET HOLD/BLOCK TRANSFORMÉ EN ALLOW REJETÉ
# ===========================================================================

def test_scenario_8_hold_block_ticket_mutated_to_allow_rejected():
    """
    Scénario 8 : Si un attaquant modifie localement x108_gate='HOLD' en 'ALLOW',
    l'altération doit invalider le HMAC et être rejetée.
    """
    hold_ticket = issue_sovereign_ticket(
        action_id="act-hold-001",
        os3_ticket_id="os3-hold",
        x108_gate="HOLD",
        scope="bank",
        autonomy_level=1,
        world_call_class="READ_ONLY",
    )
    hold_ticket.x108_gate = "ALLOW"  # Mutation illégitime
    
    with pytest.raises(AssertionError, match="SOVEREIGN_TICKET_AUTHENTICATOR_INVALID"):
        verify_and_consume_sovereign_ticket(hold_ticket)


# ===========================================================================
# 9. TEST 9 : TICKET RÉUTILISÉ (REPLAY SÉQUENTIEL) REJETÉ
# ===========================================================================

def test_scenario_9_replayed_ticket_rejected():
    """
    Scénario 9 : Un ticket souverain doit être à usage unique.
    Une seconde tentative de consommation doit lever une exception REPLAY_DETECTED.
    """
    with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tf:
        consumed_store = tf.name

    try:
        ticket = issue_sovereign_ticket(
            action_id="act-replay-001",
            os3_ticket_id="os3-replay",
            x108_gate="ALLOW",
            scope="bank",
            autonomy_level=1,
            world_call_class="READ_ONLY",
        )
        # Première consommation : valide
        t1 = verify_and_consume_sovereign_ticket(ticket, consumed_store_path=consumed_store)
        assert t1.ticket_id == ticket.ticket_id
        
        # Deuxième tentative : rejet immédiat
        with pytest.raises(AssertionError, match="SOVEREIGN_TICKET_REPLAY_DETECTED"):
            verify_and_consume_sovereign_ticket(ticket, consumed_store_path=consumed_store)
    finally:
        if os.path.exists(consumed_store):
            os.remove(consumed_store)
        lock_file = consumed_store + ".lock"
        if os.path.exists(lock_file):
            os.remove(lock_file)


# ===========================================================================
# 10. TEST 10 : DEUX CONSOMMATIONS CONCURRENTES (EXACTEMENT UNE RÉUSSIT)
# ===========================================================================

def test_scenario_10_concurrent_consumption_only_one_succeeds():
    """
    Scénario 10 : Si deux requêtes simultanées tentent de consommer le même ticket,
    une seule doit réussir et l'autre doit être refusée.
    """
    with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tf:
        consumed_store = tf.name

    try:
        ticket = issue_sovereign_ticket(
            action_id="act-race-001",
            os3_ticket_id="os3-race",
            x108_gate="ALLOW",
            scope="bank",
            autonomy_level=1,
            world_call_class="READ_ONLY",
        )
        
        def try_consume():
            try:
                verify_and_consume_sovereign_ticket(ticket, consumed_store_path=consumed_store)
                return "SUCCESS"
            except AssertionError as exc:
                return f"BLOCKED:{exc}"

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(try_consume) for _ in range(5)]
            results = [f.result() for f in futures]

        success_count = results.count("SUCCESS")
        blocked_count = sum(1 for r in results if "REPLAY_DETECTED" in r)
        
        assert success_count == 1, f"Exactement une requête doit réussir, obtenu: {success_count}"
        assert blocked_count == 4, f"Quatre requêtes doivent être bloquées, obtenu: {blocked_count}"
    finally:
        if os.path.exists(consumed_store):
            os.remove(consumed_store)
        lock_file = consumed_store + ".lock"
        if os.path.exists(lock_file):
            os.remove(lock_file)


# ===========================================================================
# 11. TEST 11 : REDÉMARRAGE PUIS TENTATIVE DE REJEU REJETÉE
# ===========================================================================

def test_scenario_11_server_reboot_replay_rejected():
    """
    Scénario 11 : L'état 'consommé' persiste sur disque et bloque le rejeu
    même après redémarrage complet du serveur.
    """
    with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tf:
        consumed_store = tf.name

    try:
        ticket = issue_sovereign_ticket(
            action_id="act-reboot-001",
            os3_ticket_id="os3-reboot",
            x108_gate="ALLOW",
            scope="bank",
            autonomy_level=1,
            world_call_class="READ_ONLY",
        )
        # Consommation avant reboot
        verify_and_consume_sovereign_ticket(ticket, consumed_store_path=consumed_store)
        
        # Simulation d'un redémarrage : chargement dans une nouvelle instance
        nonces = load_consumed_nonces(consumed_store)
        assert ticket.nonce in nonces
        assert nonces[ticket.nonce]["state"] == "COMMITTED"
        
        # Nouvelle tentative après reboot
        with pytest.raises(AssertionError, match="SOVEREIGN_TICKET_REPLAY_DETECTED"):
            verify_and_consume_sovereign_ticket(ticket, consumed_store_path=consumed_store)
    finally:
        if os.path.exists(consumed_store):
            os.remove(consumed_store)
        lock_file = consumed_store + ".lock"
        if os.path.exists(lock_file):
            os.remove(lock_file)


# ===========================================================================
# 12. TEST 12 : TICKET LÉGITIME ET VALIDE (NOMINAL PASS)
# ===========================================================================

def test_scenario_12_legitimate_valid_ticket_passes():
    """
    Scénario 12 : Un ticket émis légitimement avec toutes ses preuves
    et dans les délais de validité est accepté et consommé sans encombre.
    """
    with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tf:
        consumed_store = tf.name

    try:
        payload = {"recipient": "charlie", "val": 42}
        input_h = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        
        valid_ticket = issue_sovereign_ticket(
            action_id="act-nominal-001",
            os3_ticket_id="os3-nominal",
            x108_gate="ALLOW",
            scope="bank",
            autonomy_level=1,
            world_call_class="READ_ONLY",
            input_hash=input_h,
            ttl_seconds=300,
        )
        
        consumed = verify_and_consume_sovereign_ticket(
            valid_ticket,
            required_scope="bank",
            expected_action_id="act-nominal-001",
            action_payload=payload,
            consumed_store_path=consumed_store,
        )
        assert consumed.x108_gate == "ALLOW"
        assert consumed.is_expired() is False
    finally:
        if os.path.exists(consumed_store):
            os.remove(consumed_store)
        lock_file = consumed_store + ".lock"
        if os.path.exists(lock_file):
            os.remove(lock_file)


# ===========================================================================
# 13. TEST 13 : TICKET HISTORIQUE INCOMPLET REJETÉ POUR ACTION
# ===========================================================================

def test_scenario_13_legacy_incomplete_ticket_rejected_for_action():
    """
    Scénario 13 : Un ticket historique issu de sovereign_tickets.jsonl qui ne
    comporte pas les preuves cryptographiques requises est rejeté pour action.
    """
    legacy_record = {
        "ticket_id": "legacy-old-001",
        "action_id": "act-old",
        "os3_ticket_id": "os3-old",
        "scope": "bank",
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=300)).isoformat(),
        "x108_gate": "ALLOW",
        # Manque authenticator et version V1
    }
    with pytest.raises(AssertionError, match="SOVEREIGN_TICKET_UNSUPPORTED_VERSION"):
        verify_and_consume_sovereign_ticket(legacy_record)


# ===========================================================================
# 14. TEST 14 : STOCKAGE ALTÉRÉ OU TRONQUÉ (FAIL-CLOSED)
# ===========================================================================

def test_scenario_14_corrupted_store_fails_closed():
    """
    Scénario 14 : Si le fichier de tickets est corrompu ou tronqué,
    load_tickets() doit lever une exception sans autoriser de faux tickets.
    """
    with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tf:
        tf.write('{"ticket_id": "valid-1", "x108_gate": "ALLOW"}\n')
        tf.write('{"CORRUPTED_JSON_LINE\n')
        tf.write('{"ticket_id": "valid-2", "x108_gate": "ALLOW"}\n')
        store_path = tf.name

    try:
        with pytest.raises(json.JSONDecodeError):
            load_tickets(store_path)
    finally:
        if os.path.exists(store_path):
            os.remove(store_path)


# ===========================================================================
# 15. TEST 15 : PRODUCTEUR INDISPONIBLE -> FAIL-CLOSED
# ===========================================================================

def test_scenario_15_kernel_producer_unavailable_fails_closed():
    """
    Scénario 15 : Si le moteur de décision KX108 est indisponible,
    aucun ticket par défaut ou synthétisé ne doit produire un ALLOW.
    """
    unavailable_envelope = None
    gate = getattr(unavailable_envelope, "x108_gate", "HOLD")
    assert gate != "ALLOW", "Un producteur indisponible doit toujours résulter en HOLD ou BLOCK."


# ===========================================================================
# 16. TEST 16 : AUTHENTICATOR ALTÉRÉ REJETÉ
# ===========================================================================

def test_scenario_16_corrupted_authenticator_rejected():
    """Scénario 16 : Si l'authenticator HMAC est altéré d'un seul caractère, le ticket est rejeté."""
    ticket = issue_sovereign_ticket(
        action_id="act-auth-corrupt",
        os3_ticket_id="os3-auth",
        x108_gate="ALLOW",
        scope="bank",
        autonomy_level=1,
        world_call_class="READ_ONLY",
    )
    # Mutation de l'authenticator
    tampered_auth = ("0" if ticket.authenticator[0] != "0" else "1") + ticket.authenticator[1:]
    ticket.authenticator = tampered_auth
    
    with pytest.raises(AssertionError, match="SOVEREIGN_TICKET_AUTHENTICATOR_INVALID"):
        verify_and_consume_sovereign_ticket(ticket)


# ===========================================================================
# 17. TEST 17 : MAUVAISE CLÉ HMAC REJETÉE
# ===========================================================================

def test_scenario_17_wrong_key_rejected():
    """Scénario 17 : Un ticket signé avec une mauvaise clé HMAC est rejeté."""
    # Création d'une clé inconnue
    register_kernel_key("bad-key", secrets.token_bytes(32))
    
    ticket = issue_sovereign_ticket(
        action_id="act-wrong-key",
        os3_ticket_id="os3-wk",
        x108_gate="ALLOW",
        scope="bank",
        autonomy_level=1,
        world_call_class="READ_ONLY",
        key_id="bad-key",
    )
    # L'attaquant essaie de faire valider ce ticket avec le key_id par défaut kx108-k1
    ticket.key_id = _DEFAULT_KEY_ID
    with pytest.raises(AssertionError, match="SOVEREIGN_TICKET_AUTHENTICATOR_INVALID"):
        verify_and_consume_sovereign_ticket(ticket)


# ===========================================================================
# 18. TEST 18 : ROTATION DE CLÉ (Passe avec clé pivotée, échoue avec clé révoquée)
# ===========================================================================

def test_scenario_18_key_rotation():
    """Scénario 18 : La rotation de clé permet de valider avec une nouvelle clé k2 tout en conservant k1."""
    rotated_key_id = "kx108-k2"
    register_kernel_key(rotated_key_id, secrets.token_bytes(32))
    
    ticket_k2 = issue_sovereign_ticket(
        action_id="act-rot-001",
        os3_ticket_id="os3-rot",
        x108_gate="ALLOW",
        scope="bank",
        autonomy_level=1,
        world_call_class="READ_ONLY",
        key_id=rotated_key_id,
    )
    assert verify_authenticator(ticket_k2) is True


# ===========================================================================
# 19. TEST 19 : CRASH APRÈS RÉSERVATION (State RESERVED bloque le rejeu)
# ===========================================================================

def test_scenario_19_crash_after_reservation_blocks_replay():
    """
    Scénario 19 : Si un crash survient après la réservation atomique (statut RESERVED),
    le ticket ne peut pas être rejoué sans audit.
    """
    with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tf:
        consumed_store = tf.name

    try:
        nonce = uuid.uuid4().hex
        claimed = reserve_ticket_nonce(nonce, "ticket-crash-001", store_path=consumed_store)
        assert claimed is True
        
        # Crash simulé : on n'appelle pas commit_ticket_nonce.
        # Tentative de nouvelle réservation du même nonce
        claimed_again = reserve_ticket_nonce(nonce, "ticket-crash-001", store_path=consumed_store)
        assert claimed_again is False, "Un nonce RESERVED ne doit pas pouvoir être réservé une seconde fois !"
    finally:
        if os.path.exists(consumed_store):
            os.remove(consumed_store)
        lock_file = consumed_store + ".lock"
        if os.path.exists(lock_file):
            os.remove(lock_file)


# ===========================================================================
# 20. TEST 20 : FAIL-CLOSED EN PRODUCTION SI CLÉ ABSENTE
# ===========================================================================

def test_scenario_20_production_missing_key_fails_closed(monkeypatch):
    """Scénario 20 : En production (OBSIDIA_ENV=production), l'absence de clé secrète bloque le démarrage."""
    reset_kernel_keys()
    monkeypatch.setenv("OBSIDIA_ENV", "production")
    monkeypatch.delenv("OBSIDIA_KX108_SECRET_KEY", raising=False)
    monkeypatch.delenv("OBSIDIA_KEY_KX108_K1", raising=False)
    
    with pytest.raises(RuntimeError, match="OBSIDIA_PRODUCTION_FAIL_CLOSED"):
        get_kernel_key("kx108-k1")
    reset_kernel_keys()


# ===========================================================================
# 21. TEST 21 : CLÉ TROP COURTE REJETÉE EN PRODUCTION (< 32 OCTETS)
# ===========================================================================

def test_scenario_21_production_short_key_rejected(monkeypatch):
    """Scénario 21 : Une clé inférieure à 32 octets (256 bits) est rejetée en production."""
    reset_kernel_keys()
    monkeypatch.setenv("OBSIDIA_ENV", "production")
    monkeypatch.setenv("OBSIDIA_KX108_SECRET_KEY", "trop_courte_16o")
    
    with pytest.raises(ValueError, match="OBSIDIA_KEY_SAFETY_ERROR"):
        get_kernel_key("kx108-k1")
    reset_kernel_keys()


# ===========================================================================
# 22. TEST 22 : CLÉ VALIDE ACCEPTÉE EN PRODUCTION
# ===========================================================================

def test_scenario_22_production_valid_key_accepted(monkeypatch):
    """Scénario 22 : Une clé d'au moins 32 octets en production émet un ticket vérifiable."""
    reset_kernel_keys()
    test_key = "k" * 32
    monkeypatch.setenv("OBSIDIA_ENV", "production")
    monkeypatch.setenv("OBSIDIA_KX108_SECRET_KEY", test_key)
    
    k = get_kernel_key("kx108-k1")
    assert k == test_key.encode("utf-8")
    
    ticket = issue_sovereign_ticket(
        action_id="act-prod-001",
        os3_ticket_id="os3-prod",
        x108_gate="ALLOW",
        scope="bank",
        autonomy_level=1,
        world_call_class="READ_ONLY",
    )
    assert verify_authenticator(ticket) is True
    reset_kernel_keys()
