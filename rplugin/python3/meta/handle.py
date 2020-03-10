"""Handle module."""
from abc import ABCMeta, abstractmethod
import re


class MetaHandle(metaclass=ABCMeta):
  """Goverkill"""
  name = 'abstract'

  opts_to_stash = []  # ex ['foldcolumn', 'number', 'relativenumber', 'wrap', 'conceallevel']
  saved_opts = {}
  default_opts = {}

  ANSI_ESCAPE = re.compile(r'\x1b\[[0-9a-zA-Z;]*?m')

  def __init__(self, nvim, target, model = None, opts = {}):
    """Constructor.
    Args:
        nvim.(neovim.Nvim): neovim
    """
    self.nvim = nvim
    self.target = target
    self.model = model

    if self.opts_to_stash and model:
      self.store_opts(self.opts_to_stash, model) # wrongthink. works when taking over a window etc but not buf

    for kind in [self.default_opts, self.saved_opts, opts]:
      self.apply_opts(kind)

    self.vim_id = target.number #why grab all these fn vars? ah right to ensure we are who we think later..
    self.on_init()


  def __del__(self):
    """Destructor. Nuke any extra yada. Restore orig target properties. But fancy stuff in on_term"""
    self.restore_opts() # or eh dunno double, only for window?. taking over buffer seems mean
    self.on_term()


  def push_opt(self, opt, val):
    if self.target.options.get(opt):
      self.saved_opts[opt] = self.target.options[opt]
    self.target.options[opt] = val

  def pop_opt(self, opt):
    if self.saved_opts.get(opt):
      self.target.options[opt] = self.saved_opts[opt]


  def store_opts(self, opts, origin=None):
    origin = origin or self.target
    for opt in opts:
      if origin.options.get(opt):
        self.saved_opts[opt] = origin.options[opt]

  # getting "invalid option: number" on restore. so window leaking into buffer?
  # but need exception handling anyways so. just, investigate.
  # also "invalid option: modifiable" - so guess buf also applying to window then
  def apply_opts(self, opts):
    for opt,val in opts.items():
      try:    self.target.options[opt] = val
      except: pass

  def restore_opts(self):
    self.apply_opts(self.saved_opts)



  @abstractmethod
  def on_init(self):
    """Specific initialization
    Args:
    Returns:
    """
    raise NotImplementedError

  @abstractmethod
  def on_term(self):
    """
    Args:
    Returns:
    """
    raise NotImplementedError


