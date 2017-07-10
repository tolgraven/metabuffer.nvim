
from .buffer import AbstractBuffer


class DummyBuffer(AbstractBuffer):
  """A vim buffer not meant for end consumption, but as a malleable and
  temporary mirror"""
  name = 'dummy'


    def __init__(self, buffer):
        """Constructor.

        Args:
            nvim.buffer (neovim.Nvim): A ``neovim.Nvim.buffer`` instance.
        """
        self.vimbuffer = buffer      # the nvim buffer object
        self.sources = []         # a list of Buffer objects, together
        # representing the total text content of this dummy buffer
        # self.matcher/s
        self.attributes = {[]}    # the relevant optialso reachable from the buffer object itself..ons we need, also
        self.ranker # steal something from denite since we need to be able to
        # sort, not the text within each source but the sources themselves
        # self.syntax = if created from one source/all sources same syntax then
        # use it automatically. 



    def add(self, buffer)
    """Add/connect a Buffer source to the dummy buffer"""

    def text(self, text)
    """Get the full text representing all the sources"""

    def filter(self,  )   # look closer at lista's filters and how fzr/denite etc do it.
    """Apply a semi-permanent filter limiting the contents in turn presented to
    matchers and available for modification"""


