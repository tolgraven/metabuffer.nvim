"""Window module."""
from meta.handle import MetaHandle


class AbstractWindow(MetaHandle):
    """An abstract window class.

    Attributes:
        nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
        nvim.window (neovim.Nvim.window): A ``neovim.Nvim.window`` instance.
    """

    name = 'abstract'
    # statusline =  ''

    # self._save_window_options = {}
    # window_options = {
    #     'colorcolumn', 'concealcursor', 'conceallevel',
    #     'cursorcolumn', 'cursorline', 'foldcolumn',
    #     'foldenable', 'list',
    #     'number', 'relativenumber', 'signcolumn',
    #     'spell', 'winfixheight', 'wrap',
    # }
    # for k in window_options:
    #     self._save_window_options[k] = self._vim.current.window.options[k]
    # self._options = self._vim.current.buffer.options

    #per denite:
    # Note: Have to use setlocal instead of "current.window.options"
    # "current.window.options" changes global value instead of local in neovim.
    def __init__(self, nvim, window, opts_to_stash = [], opts = {}):
        super().__init__(nvim, window, window, opts_to_stash, opts)
        self.window = window

    def apply_opts(self, opts, target = None):
      for opt,val in opts.items():
        try:
          self.nvim.command('setlocal %s%s%s' % (opt, "=" if val else '', val))
        # or some need prepend "no" instead ugh...
        except: pass

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


    # @property
    # def buffer(self): return self.buffer
    # @buffer.setter
    # def buffer(self, buf):
    def set_buf(self, buf):
      if isinstance(buf, int):
        self.nvim.command('noautocmd keepjumps buffer %d' % buf)
      # if isinstance(buf, int): #buf.number:  # reg nvim buf
      elif buf.number: #buf.number:  # reg nvim buf
        self.set_buf(buf.number)
      elif buf.buffer: #isinstance metabuf
        self.set_buf(buf.buffer)



