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

  def __init__(self, nvim, target, opts = {}):
    """Constructor.
    Args:
        nvim.(neovim.Nvim): neovim
    """
    self.nvim = nvim
    self.target = target

    self.store_opts(self.opts_to_stash)
    for kind in [self.default_opts, self.saved_opts, opts]:
      self.apply_opts(kind)

    self.vim_id = target.number #why grab all these fn vars? ah right to ensure we are who we think later..
    self.on_init()


  def push_opt(self, opt, val):
    try:    self.saved_opts[opt] = self.target.options[opt]
    except: pass
    self.target.options[opt] = val

  def pop_opt(self, opt):
    if self.saved_opts[opt]:
      self.target.options[opt] = self.saved_opts[opt]
  #this is good but for start() try use case a problem maybe so dont use target for now
      # self.nvim.current.buffer.options[opt] = self.saved_opts[opt]


  def __del__(self):
    """Destructor. Nuke any extra yada. Restore orig target properties. But fancy stuff in on_term"""
    self.restore_opts() # or eh dunno double, only for window?. taking over buffer seems mean
    self.on_term()

  def store_opts(self, opts):
    for opt in opts:
        if self.target.options[opt]:
            self.saved_opts[opt] = self.target.options[opt]

  # getting "invalid option: number" on restore. so window leaking into buffer?
  # but need exception handling anyways so. just, investigate.
  def apply_opts(self, opts):
    for opt,val in opts.items():
      try:    self.target.options[opt] = val
      except: pass

  def restore_opts(self):
    for opt,val in self.saved_opts.items():
        # self.nvim.current.target.options[opt] = val # imagine if wrong windowz
        self.target.options[opt] = val



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


