"""
obsidia_mission_authority_freshness_lock_v0.py
=============================================
STAGE 4F REPAIR — verrou de LINÉARISATION inter-processus pour l'autorité
de mission bornée. NON_SOUVERAIN.

Ce module N'EST PAS une autorité, N'EST PAS une décision, N'AUTORISE RIEN.
Il fournit UNIQUEMENT une sérialisation de concurrence entre :

  * `obsidia_mission_authority_v0.record_mission_authority_revocation(...)`
    (publication canonique d'une révocation HMA)

  * la section critique de mutation gouvernée Stage 4 dans
    `obsidia_governed_apply_v0.run_governed_content_apply(...)`
    (re-vérification finale de fraîcheur + `atomic_replace_with_bytes`)

Les DEUX participants acquièrent le MÊME verrou, indexé par `mission_id`.
Conséquence (modèle V0) : une révocation HMA canoniquement committée et
une mutation gouvernée Stage 4 possèdent un ORDRE TOTAL SÉRIALISÉ. Il
devient impossible d'obtenir « révocation committée AVANT la mutation »
ET « la mutation réussit quand même sous cette HMA révoquée ».

CLAIM BOUNDARY : ce module ne prétend PAS qu'une demande humaine de
révocation arrivant PENDANT la section critique annule une action déjà
linéarisée. La propriété V0 est : ordre de commit sérialisé.

Verrou réel du SE (jamais un simple fichier-témoin) :
  * Windows : `msvcrt.locking` (verrou de plage d'octets, propriété du
    processus — libéré par le SE à la fermeture du descripteur OU à la
    mort du processus).
  * POSIX   : `fcntl.flock(LOCK_EX)` (mêmes garanties de propriété).

  PROCESS_CRASH_RELEASES_LOCK            = TRUE  (propriété SE)
  LOCK_FILE_PRESENCE_ALONE_MEANS_LOCKED  = FALSE (on tente toujours le verrou SE)
  LOCK_ACQUISITION_TIMEOUT               = BORNÉ  (défaut 30 s, paramétrable)
  LOCK_TIMEOUT_BEHAVIOR                  = FAIL_CLOSED (exception, jamais d'attente infinie)
"""
from __future__ import annotations

import hashlib
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path

LOCK_DOMAIN_TAG = "OBSIDIA_STAGE4F_MISSION_AUTHORITY_FRESHNESS_LOCK_V0"
SOVEREIGNTY = "NON_SOVEREIGN"
IS_AUTHORIZATION = False
IS_DECISION = False

DEFAULT_TIMEOUT_S = 30.0
_POLL_S = 0.05

_IS_WINDOWS = (os.name == "nt")
if _IS_WINDOWS:
    import msvcrt
else:
    import fcntl


class MissionAuthorityLockTimeout(RuntimeError):
    """Acquisition du verrou impossible dans le délai borné — FAIL_CLOSED."""


def authority_lock_root_for(mission_id: str, mission_store_dir: "str | Path") -> str:
    """Racine de verrou CANONIQUE, dérivée de façon identique par le writer
    de révocation et par C2. Un seul chemin par mission."""
    _scripts = Path(__file__).resolve().parent
    if str(_scripts) not in sys.path:
        sys.path.insert(0, str(_scripts))
    import obsidia_bounded_mission_v0 as _M
    return str(_M._mission_dir(str(mission_id), Path(mission_store_dir)) / ".authority_locks")


def lock_path_for(mission_id: str, lock_root: "str | Path") -> Path:
    d = Path(lock_root)
    d.mkdir(parents=True, exist_ok=True)
    tag = hashlib.sha256(("mission:" + str(mission_id)).encode("utf-8")).hexdigest()[:32]
    return d / f"mission-authority-{tag}.lock"


def _try_acquire(fd: int) -> bool:
    try:
        if _IS_WINDOWS:
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False


def _release(fd: int) -> None:
    try:
        if _IS_WINDOWS:
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(fd, fcntl.LOCK_UN)
    except OSError:
        pass


@contextmanager
def mission_authority_lock(mission_id: str, *, lock_root: "str | Path",
                           timeout_s: float = DEFAULT_TIMEOUT_S):
    """Section critique inter-processus indexée par `mission_id`.

    Libération GARANTIE en sortie (succès, exception, `return` anticipé du
    bloc appelant) ET à la mort du processus (propriété SE du verrou)."""
    if not (isinstance(mission_id, str) and mission_id.strip()):
        raise ValueError("MISSION_ID_REQUIRED_FOR_AUTHORITY_LOCK")
    p = lock_path_for(mission_id, lock_root)
    fd = os.open(str(p), os.O_RDWR | os.O_CREAT, 0o600)
    try:
        # Windows verrouille une plage de >=1 octet depuis la position courante.
        if os.fstat(fd).st_size < 1:
            try:
                os.write(fd, b"\0")
            except OSError:
                pass
        deadline = time.monotonic() + max(0.0, float(timeout_s))
        acquired = False
        while True:
            if _try_acquire(fd):
                acquired = True
                break
            if time.monotonic() >= deadline:
                break
            time.sleep(_POLL_S)
        if not acquired:
            raise MissionAuthorityLockTimeout(
                f"MISSION_AUTHORITY_LOCK_TIMEOUT:{timeout_s}s:{mission_id}")
        try:
            yield p
        finally:
            _release(fd)
    finally:
        os.close(fd)
