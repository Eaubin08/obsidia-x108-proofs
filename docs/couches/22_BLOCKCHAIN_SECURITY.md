# 22 · Blockchain et sécurité de chaîne

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Transactions, signatures, fraîcheur des oracles et simulation, toujours bornées par les frontières.

## Où elle intervient dans le trajet d'une demande

- **Étape 4 · Organes spécialisés** : Brody comprend et formule, la mémoire rappelle, les domaines vérifient leur terrain, Obsidure prépare un candidat, Sigma et le Peripheral Mesh mesurent la cohérence, Tree34 et Thermo apportent leurs lectures. Ils proposent, ils ne décident pas.

Voir le trajet complet : [guide général](../README.md).

## Où est son code aujourd'hui

**Points d'entrée connus :**

- [periphery/blockchain/](../../periphery/blockchain) · blockchain

D'après le registre de fonctionnalités V3, **20 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `periphery/blockchain/` | 12 |
| `periphery/schemas/` | 3 |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 2 |
| `demos/local_flows/` | 1 |
| `periphery/pepites_search_algo/` | 1 |
| `scripts/` | 1 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (13)

### Documents de référence — à lire en premier

- [Gencoin — Not a Token Policy V1](../blockchain/GENCOIN_NOT_A_TOKEN_POLICY_V1.md) · `docs/blockchain/GENCOIN_NOT_A_TOKEN_POLICY_V1.md`
  <br>Role: Declares and enforces that Gencoin is a ledger-only system, never a blockchain token.
- [No Private Key Policy V1](../blockchain/NO_PRIVATE_KEY_POLICY_V1.md) · `docs/blockchain/NO_PRIVATE_KEY_POLICY_V1.md`
  <br>Role: Absolute prohibition on storing, reading, requesting, or accessing any private key, seed phrase, or mnemonic.
- [Blockchain Security Layer](../blockchain/README.md) · `docs/blockchain/README.md`
  <br>Tests: tests/periphery/testblockchain.py + tests/nonsovereignty/testblockchain.py
- [Smart Contract Risk Gate V1](../blockchain/SMART_CONTRACT_RISK_GATE_V1.md) · `docs/blockchain/SMART_CONTRACT_RISK_GATE_V1.md`
  <br>Role: Blocks unaudited smart contract deployment and evaluates contract interaction risk.
- [Token Policy V1](../blockchain/TOKEN_POLICY_V1.md) · `docs/blockchain/TOKEN_POLICY_V1.md`
  <br>Role: Blocks all token minting, deployment, and creation. Gencoin is explicitly NOT a token.
- [Blockchain Security Layer V1](../blockchain/BLOCKCHAIN_SECURITY_LAYER_V1.md) · `docs/blockchain/BLOCKCHAIN_SECURITY_LAYER_V1.md` *(référence probable)*
  <br>The Blockchain Security Layer classifies every action that touches a blockchain domain and routes it through appropriate security gates. No blockchain action executes without…
- [Bridge Risk Gate V1](../blockchain/BRIDGE_RISK_GATE_V1.md) · `docs/blockchain/BRIDGE_RISK_GATE_V1.md` *(référence probable)*
  <br>The Bridge Risk Gate evaluates the risk of cross-chain bridge operations. All mainnet bridge transfers are absolutely blocked. Unaudited bridges and unverified liquidity…
- [DeFi Risk Gate V1](../blockchain/DEFI_RISK_GATE_V1.md) · `docs/blockchain/DEFI_RISK_GATE_V1.md` *(référence probable)*
  <br>The DeFi Risk Gate evaluates the risk profile of any proposed DeFi interaction — lending, borrowing, staking, liquidity provision, yield farming. All DeFi actions are held for…
- [Oracle Freshness Gate V1](../blockchain/ORACLE_FRESHNESS_GATE_V1.md) · `docs/blockchain/ORACLE_FRESHNESS_GATE_V1.md` *(référence probable)*
  <br>The Oracle Freshness Gate ensures that any action depending on oracle data uses fresh data (< 5 minutes old by default). Stale oracle data triggers a HOLD, preventing actions…
- [Signature Boundary — No Signing V1](../blockchain/SIGNATURE_BOUNDARY_NO_SIGNING_V1.md) · `docs/blockchain/SIGNATURE_BOUNDARY_NO_SIGNING_V1.md` *(référence probable)*
  <br>The Signature Boundary blocks any request involving cryptographic signing — SIGNMESSAGE, ETHSIGN, PERSONALSIGN, SIGNTYPEDDATA, EIP712SIGN, or any operation containing "SIGN" in…
- [Transaction Simulator — Dry-Run Only V1](../blockchain/TRANSACTION_SIMULATOR_DRYRUN_V1.md) · `docs/blockchain/TRANSACTION_SIMULATOR_DRYRUN_V1.md` *(référence probable)*
  <br>The Transaction Simulator evaluates what WOULD happen if a transaction were sent — gas estimates, risk scores, cost projections — but NEVER broadcasts to any chain. It is a…
- [Wallet Security Boundary V1](../blockchain/WALLET_SECURITY_BOUNDARY_V1.md) · `docs/blockchain/WALLET_SECURITY_BOUNDARY_V1.md` *(référence probable)*
  <br>The Wallet Security Gate is the first and most critical blockchain security module. It blocks any request involving private keys, seed phrases, mnemonics, or wallet connections…

<details><summary><b>Rapports, audits et preuves d'exécution</b> (1)</summary>

**`docs/blockchain/`** · *dossier lu par du code : ne pas déplacer*

- [ONCHAIN_AUDIT_PACKET_V1.md](../blockchain/ONCHAIN_AUDIT_PACKET_V1.md) — On-Chain Audit Packet V1

</details>

## Fichiers liés au code

13 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
