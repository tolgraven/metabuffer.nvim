"""Window module."""
from meta.handle import MetaHandle


class AbstractWindow(MetaHandle):
    """An abstract window class.

    Attributes:
        nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
        nvim.window (neovim.Nvim.window): A ``neovim.Nvim.window`` instance.
    """

    name = 'abstract'
    statusline =  ''

    def __init__(self, nvim, window, opts = {}):
        """Constructor.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
            nvim.window (neovim.Nvim): A ``neovim.Nvim.window`` instance.
        """
        super().__init__(nvim, window, None, opts)
        self.window = window


    def set_statusline(self, text):
      self.window.options['statusline'] = text

    def set_cursor(self, row = 1, col = None):
      col = col or self.window.cursor[1]
      self.nvim.call('cursor', [row, col])

    def set_row(self, row, addjump=False):
      """Not really called row tho is it. But set line sounds ambiguous"""
      if addjump:
        self.nvim.command(':' + str(row))     # Jump to selected line
      else:
        self.set_cursor(row)

    def set_col(self, col):
      row = self.nvim.current.window.cursor[0]
      self.set_cursor(row, col)

