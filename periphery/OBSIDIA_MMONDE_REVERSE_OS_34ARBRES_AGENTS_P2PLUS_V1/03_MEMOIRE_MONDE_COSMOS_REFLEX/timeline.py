
class Timeline:
    def __init__(self, events=None):
        self.events = events or []

    def add_event(self, event):
        self.events.append(event)

