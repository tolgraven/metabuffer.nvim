
from .dummy import DummyBuffer


class PointerBuffer(DummyBuffer):
  """A buffer with text representing not itself but some other resource, probably a file. Edits to the buffer should then propogate into ie. changing file names, or loading new files"""
  name = 'genericpointer'


    def __init__(self, buffer):
        """Constructor.

        Args:
            nvim.buffer (neovim.Nvim): A ``neovim.Nvim.buffer`` instance.
        """
        self.vimbuffer = buffer   # the nvim.buffer object holding our results
        self.sources = []         # a list of Buffer objects, together
        # representing the total  text content of this dummy buffer
        # self.matcher/s
        self.attributes = {[]}    # the relevant optialso reachable from the buffer object itself..ons we need, also
        self.ranker = ranker # steal something from denite since we need to be able to
        # sort, not the text within each source but the sources themselves
        # self.syntax = if created from one source/all sources same syntax then
        # use it automatically. 
        self.presentation = True        #like for dummy buffers, stuff to change
        # presentation (whitespace, columns etc...) and other minor stuff,
        # without touching original for those operations

