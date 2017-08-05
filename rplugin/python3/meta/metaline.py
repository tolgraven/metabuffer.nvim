class MetaLine():
  """A line of text, to keep inside a metabuffer, with associated metadata"""


  def __init__(self, nvim, text = '\n'):
    """Constructor.

    Args:
        nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
    """
    self.nvim = nvim
    self.text = text  #lines will have to include '\n' at end I guess so setting to '' kills automatically...
    # likely properties:
    self.origin = buffer  #associated origin buffer, if any...
    # self.index = 
    self.static = False
    self.type = 'text'  # dir, variable, various command output types etc...
    #then depending on above would set like default callback to handle parsing 
    # changes to line, and execute operations off of them
    if not self.static:
      if self.type is 'text': self.callback = 'replace'  #nuke old, in new

