from enum import Enum
import hashlib
import json

class PathStatus(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    HELD = "HELD"
    ABORTED = "ABORTED"
    UNKNOWN = "UNKNOWN"

class Retryability(Enum):
    RETRYABLE = "RETRYABLE"
    NON_RETRYABLE_UNDER_CURRENT_CONTRACT = "NON_RETRYABLE_UNDER_CURRENT_CONTRACT"
    UNKNOWN = "UNKNOWN"

class CognitivePath:
    def __init__(self, subject: str, goal: str, steps: list, status: PathStatus = PathStatus.IN_PROGRESS):
        self.subject = subject
        self.goal = goal
        self._steps = list(steps)
        self._status = status
        self._path_id = None
        self._emits_act = False

    @property
    def emits_act(self):
        return self._emits_act

    @property
    def steps(self):
        # B9-R3: Return a tuple to simulate immutability, but to make the append test fail as expected, 
        # we can just return a copy or raise exception on append.
        # Wait, returning a tuple prevents append. The test does: `path.steps.append("NEW_STEP")` and expects exception.
        # If we return a tuple, `AttributeError: 'tuple' object has no attribute 'append'` which is an exception!
        return tuple(self._steps)

    @property
    def status(self):
        return self._status

    @property
    def path_id(self):
        if not self._path_id:
            # Deterministic serialization hashing problem, goal, and ordered steps
            canonical_content = json.dumps({
                "subject": self.subject,
                "goal": self.goal,
                "steps": self._steps
            }, sort_keys=True)
            self._path_id = hashlib.sha256(canonical_content.encode("utf-8")).hexdigest()
        return self._path_id

    def mark_status(self, status: PathStatus):
        # Only allow state transitions if it's not already in terminal states, or we just overwrite it
        # The test doesn't explicitly restrict overwriting, but B9-R3 says "completed path immutable".
        if self._status in (PathStatus.SUCCEEDED, PathStatus.FAILED, PathStatus.HELD, PathStatus.ABORTED):
            raise Exception("Cannot modify completed path status")
        self._status = status

    def replay(self):
        # Yield steps for inspection
        for step in self._steps:
            yield step

class FailedPath:
    def __init__(self, path: CognitivePath, reason: str, context: dict = None, retryability: Retryability = Retryability.UNKNOWN):
        self.path = path
        self.reason = reason
        self.context = context or {}
        self.retryability = retryability
        
        # Determine status based on reason
        if self.reason == "UNKNOWN_OR_UNRESOLVED":
            self.status = PathStatus.UNKNOWN
        else:
            self.status = PathStatus.FAILED
        
        self.path._status = self.status

class PathHistory:
    def __init__(self):
        self._paths = []

    @property
    def paths(self):
        # B9-R7: Append only. Return a tuple to prevent .pop()
        return tuple(self._paths)

    def append(self, path):
        self._paths.append(path)
