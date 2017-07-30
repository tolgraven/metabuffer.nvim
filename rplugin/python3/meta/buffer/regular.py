
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


        self._line_count = len(self._content)
        self._indices = list(range(self._line_count))
        self._buffer_name = self.nvim.eval('simplify(expand("%:~:."))')
        buf_opts = {'buftype': 'nofile', 'bufhidden': 'wipe', 'buflisted': False,}
        for opt,val in buf_opts.items():
            self.nvim.current.buffer.options[opt] = val




