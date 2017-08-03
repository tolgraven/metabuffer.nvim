
from .buffer import AbstractBuffer


class Buffer(AbstractBuffer):
  """A regular vim buffer object"""
  name = 'buffer'

    def __init__(self, buffer):
        """Constructor.

        Args:
            nvim.buffer (neovim.Nvim): A ``neovim.Nvim.buffer`` instance.
        """
        self.buffer = buffer
        self.attributes = {[]}    # the relevant options we need, also


        # buf_opts = {'buftype': 'nofile', 'bufhidden': 'wipe', 'buflisted': False,}
        # ^ hell no
        for opt,val in buf_opts.items():
            self.nvim.current.buffer.options[opt] = val

