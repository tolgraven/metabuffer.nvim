from .base import AbstractWindow
from meta.buffer.base import AbstractBuffer


class Window(AbstractWindow):
  """A floating vim window"""
  name = 'floatingwindow'

  def __init__(self, nvim, buffer = None,
               opts = {}):
    # call nvim_win_set_option(win, 'winhl', 'Normal:MyHighlight') # " optional: change highlight, otherwise Pmenu is used
    # nvim.current.window.options['winhl', 'Normal:Somegroup']

    if not buffer:
        buffer = AbstractBuffer.new(nvim)

    parent = 'editor' # win or editor for anchored. Cursor for float-float
    if parent == 'editor':
      parent_width = nvim.options['columns']
      parent_height = nvim.options['lines'] - 2 # tabline, cmdline
    elif parent == 'window':
      parent_width = nvim.current.window.options['columns']
      parent_height = nvim.current.window.options['lines'] # - 1 #statusline?
    # fix decent presets for docked lrtb, whether to win or editor.
    # (afa look up correct w/h etc)
    width = 20 #parent_width - yada
    # height = parent_height - 3 # cmdline, statusline, tabbar...

    # opts = {'relative': 'win',   # cursor, editor, win
    config = {'relative': 'editor',   # cursor, editor, win
            # 'win': id,        #when win, if not curr
            'width': width,
            'height': parent_height, #nvim.current.window.height,
            # 'bufpos': [100, 10],  # buf-relative scrol
            'col': 100,
            'row': 1,       # works when uh I guess height < size etc yada. so set by window
            'anchor': 'NE',
            'style': 'minimal'}
    # window = nvim.api.open_win(buffer.handle, enter=False, config=config)
    window_handle = nvim.api.open_win(buffer.handle, False, config)
    # window_handle = nvim.api.open_win(buffer.handle, True, config)
    # nvim.command('wincmd p')

    window = window_handle
    # window = nvim.windows[window_handle]
    window.options['winblend'] = 25

    super().__init__(nvim, window, opts)
    # interesting it's showing number given open_win supposed to disable it...
    # window.options['number'] = False
    # window.options['nonumber'] = True

  def show(self, visible=True):
    pass
