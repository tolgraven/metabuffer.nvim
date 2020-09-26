
class ModeIndexer:
    """Indexer for switchable mode (matcher type, ignorecase, syntax...)"""
    def __init__(self, candidates, index=0, on_leave=None, on_active=None):
        """Constructor.
        Args:
            candidates (Sequence): The things being selected.
            index (Integer): Index on creation
            on_leave: Function or str reference to method to call on a candidate
                      before changing from it - cleanup.
            on_active: Function or str reference to method to call on a candidate
                      after changing to it - setup"""
        self.candidates = candidates
        self._index = index
        self._on_leave = on_leave
        self._on_active = on_active

    @property
    def index(self): return self._index
    @index.setter
    def index(self, value):
        if value is self.index: return
        self.on_leave()
        value = value % len(self.candidates)
        self._index = value
        self.on_active()

    @property
    def current(self): return self.candidates[self.index]

    def on_leave(self):  self._call(self._on_leave)
    def on_active(self): self._call(self._on_active)

    def _call(self, function):
        if isinstance(function, str):           # lookup method
            getattr(self.current, function)()
        elif function:                          # call lambda
            function(self)

    def next(self, offset=1):
        self.index += offset
        return self.current

    def previous(self, offset=1):
        self.index -= offset
        return self.current

