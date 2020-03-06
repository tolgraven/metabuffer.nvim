from .base import AbstractWindow


class Window(AbstractWindow):
  """A container window potentially consisting of several linked windows acting in tandem"""
  name = 'metawindow'
  default_opts = {'spell': False, 'foldenable': False,
                'colorcolumn': '',
                'cursorline': True, 'cursorcolumn': False, }
  opts_to_stash = ['foldcolumn', 'number', 'relativenumber', 'wrap', 'conceallevel']
  # buf also "save everything ya dummy option"

  statusline = ''.join([
        '%%#MetaStatuslineMode%s#%s%%#MetaStatuslineQuery#%s',
        '%%#MetaStatuslineFile# %s',
        '%%#MetaStatuslineIndicator# %d/%d',
        '%%#Normal# %d',
        '%%#MetaStatuslineMiddle#%%=',
        '%%#MetaStatuslineMatcher%s# %s %%#MetaStatuslineKey#%s',
        '%%#MetaStatuslineCase%s# %s %%#MetaStatuslineKey#%s',
        '%%#MetaStatuslineSyntax%s# %s %%#MetaStatuslineKey#%s ',])


  # def __init__(self, nvim, window = None, metabuffer, opts = {}):
  def __init__(self, nvim, window = None, opts = {}):
    """Constructor.

    Args:
        nvim.window (neovim.Nvim): A ``neovim.Nvim.window`` instance - the master window
    """

    window = window or nvim.current.window
    # self.metabuffer = metabuffer
    super().__init__(nvim, window, opts)


  def on_init(self):
    pass

  def on_term(self):
    pass

  def set_statusline(self, mode, prefix, query, name, num_hits, num_lines,
                     line_nr, matcher, case, hl_prefix, syntax):
      hotkey = {'matcher': 'C^', 'case': 'C_', 'pause': 'Cc', 'syntax': 'Cs'}  # until figure out how to fetch the keymap back properly

      text = self.statusline % (
          mode.capitalize(), prefix, query, name,
          num_hits, num_lines, line_nr,
          matcher.capitalize(), matcher, hotkey['matcher'],
          case.capitalize(),    case,    hotkey['case'],
          hl_prefix,            syntax,   hotkey['syntax']) #remember:
        # this will later go in promptwindow, input being its reg buf
        # with timeoutlen set v short
        # which also solves throttling etc

      self.push_opt('statusline', text)
      # self.set_statusline(text)
      # self.nvim.current.window.options['statusline'] =



