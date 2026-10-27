
import uuid
from periphery.event_bus import get_bus, EventEnvelope

class BrodyBridge:
    def __init__(self):
        self.bridge_id = str(uuid.uuid4())
        self.is_attached = False
        self._received = 0
        self._stats = {'processed': 0}

    def stats(self):
        return self._stats

    def handle_trad_context(self, env: EventEnvelope):
        self._received += 1
        self._stats['processed'] += 1
        print(f'[BRODY_DEBUG] REÇU: {env.topic} | Payload: {env.payload}')

    def attach_to_bus(self, bus=None):
        bus = bus or get_bus()
        bus.subscribe(self.handle_trad_context)
        self.is_attached = True
        print('Brody est maintenant attaché au bus.')

def get_bridge():
    global _bridge
    if '_bridge' not in globals() or _bridge is None:
        _bridge = BrodyBridge()
        _bridge.attach_to_bus()
    return _bridge
