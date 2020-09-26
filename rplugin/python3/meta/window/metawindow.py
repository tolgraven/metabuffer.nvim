from .base import AbstractWindow


class Window(AbstractWindow):
  """A container window potentially consisting of several linked windows acting in tandem"""
  name = 'metawindow'
  #               'colorcolumn': '',
  #               'cursorline': True, 'cursorcolumn': False, }
  default_opts = {'nospell': '', 'nofoldenable': '',  #'spell': False, 'foldenable': False,
                  'nocursorcolumn': '', }
  opts_to_stash = ['foldcolumn',
                   'number', 'relativenumber',
                   'wrap', 'conceallevel']
  # buf also "clone everything ya dummy option"

  # statusfmt = ['mode', 'prefix', 'query', 'query', 'file', '']
  statusline = ''.join([
        '%%#MetaStatuslineMode%s#%s%%#MetaStatuslineQuery#%s',
        '%%#MetaStatuslineFile# %s',
        '%%#MetaStatuslineIndicator# %d/%d',
        '%%#Normal# %d',
        '%s',
        '%%#MetaStatuslineMiddle#%%=',
        '%%#MetaStatuslineMatcher%s# %s %%#MetaStatuslineKey#%s',
        '%%#MetaStatuslineCase%s# %s %%#MetaStatuslineKey#%s',
        '%%#MetaStatuslineSyntax%s# %s %%#MetaStatuslineKey#%s ',])

  # move most stuff. def of meta* gotta be having multiple backing objects
  # (buf repr bufs, window container of eg window + floating sidebar)
  # windows = []

  def __init__(self, nvim, window = None, opts = {}):
    """IDEAS:
    -Link window configuration to buffers in relational way (if cpp here then h there...)
    -Slice up to loads of thin side-by-side windows when doing replace op w many candidates
    (basically zoom in to right around hits -> show 100+ tot instead of 20-30-whatev)
    -Post-line comments broken off into own window -> auto aligned and out of way,
    can shift focus and let code clip and show more comment...
    """
    super().__init__(nvim, window or nvim.current.window,
                     self.opts_to_stash,
                     self.default_opts)



  def set_statusline(self, mode, prefix, query, name, num_hits, num_lines,
                     line_nr,
                     debug_out,
                     matcher, case, hl_prefix, syntax):
      hotkey = {'matcher': 'C^',
                'case': 'C_',
                'pause': 'Cc',
                'syntax': 'Cs'}  # until figure out how to fetch the keymap back properly

      text = self.statusline % (
          mode.capitalize(), prefix, query, name,
          num_hits, num_lines,
          line_nr,
          debug_out,
          matcher.capitalize(), matcher, hotkey['matcher'],
          case.capitalize(),    case,    hotkey['case'],
          hl_prefix,            syntax,  hotkey['syntax']) #remember:
        # this will later go in promptwindow, input being its reg buf
        # with timeoutlen set v short
        # which also solves throttling etc

      super().set_statusline(text)

