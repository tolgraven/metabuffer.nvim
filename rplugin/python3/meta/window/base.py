"""Window module."""
from meta.handle import MetaHandle


class AbstractWindow(MetaHandle):
    """An abstract window class.

    Attributes:
        nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
        nvim.window (neovim.Nvim.window): A ``neovim.Nvim.window`` instance.
    """

    name = 'abstract'

    def __init__(self, nvim, window, opts = {}):
        """Constructor.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
            nvim.window (neovim.Nvim): A ``neovim.Nvim.window`` instance.
        """
        super().__init__(nvim, window, opts)
        self.window = window


    def set_statusline(self, text):
      self.window.options['statusline'] = text


    statusfmt = ['mode', 'prefix', 'query', 'query', 'file', '']
    statusline =  ''

