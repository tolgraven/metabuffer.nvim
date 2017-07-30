
from .dummy import DummyBuffer


class UiBuffer(DummyBuffer):
  """A buffer acting as a UI element, providing additional data for a linked
  proper buffer. Ie line numbers, comments and other data that cant be shown in
  the original buffer due to UI or syntax highlighting restrictions. Instead
  open another window to left or right and link it..."""
  name = 'ui'


    def __init__(self, buffer, extends):
        """Constructor.

        Attributes:
            nvim.buffer (neovim.Nvim): A ``neovim.Nvim.buffer`` instance.
        """
        self.vimbuffer = buffer   # the nvim.buffer object holding our results
        self.extends = extends    # master metabuffer object that we're extending
        # self.syntax = 

    def on_update(self, status):
        """Update state to match lines outputted by master buffer"""
        # so like get line numbers from lista or wherever the matcher resides...
        # or alt is skip having special type for ui buffer, just put it as a
        # regular (dummy)buffer and just let lista deal with the filtering via indices and its own on_update

