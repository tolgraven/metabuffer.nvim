

class ModeIndexer:
    """Indexer for switchable mode (matcher type, ignorecase, syntax...)"""
    def __init__(self, candidates, index=0, on_leave=None, on_active=None):
        """Constructor.
        Args:
            candidates (Sequence): A candidates.
        """
        self.candidates = candidates
        self._index = index
        self._on_leave = on_leave
        self._on_active = on_active

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self.on_leave
        value = value % len(self.candidates)
        self._index = value
        self.on_active

    @property
    def current(self):
      return self.candidates[self.index]


    def on_leave(self): self._safe_call(self._on_leave)

    def on_active(self): self._safe_call(self._on_active)

    def _safe_call(self, method):
        if isinstance(method, str): #lookup method
            getattr(self.current, method)()
        elif method:
            method(self) #call lambda


    def next(self, offset=1):
        self.index += offset
        return self.current

    def previous(self, offset=1):
        self.index -= offset
        return self.current


