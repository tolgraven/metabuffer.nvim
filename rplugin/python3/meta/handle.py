"""Handle module."""
from abc import ABCMeta, abstractmethod
import re
import pynvim

class MetaHandle(metaclass=ABCMeta):
  """Goverkill"""
  name = 'abstract'
  instances = []
  # instances: List[MetaHandle] = []

  # opts_to_stash = []  # ex ['foldcolumn', 'number', 'relativenumber', 'wrap', 'conceallevel']
  # saved_opts = {}
  # default_opts = {}
   # If you have, for example, a list as a class attribute and you do changes to this list, it affects all instances of that class.
   # ^ welp there ya go. dumb-dumb. already discovered that the hard way last time around too and forgot hah

  def __init__(self, nvim, target, model = None, opts_from_model = [], opts = {}):
    """Constructor.
    Args:
        nvim.(neovim.Nvim): neovim
    """
    self.nvim = nvim
    self.target = target
    self.model = model or target
    self.all_orig_opts = self.model.options
    self.saved_opts = {}

    if opts_from_model:
      self.store_opts(opts_from_model, self.model) # wrongthink. works when taking over a window etc but not buf

    for kind in [self.saved_opts, opts]:
      self.apply_opts(kind, self.target) # apply cloned and passed opts

    self.vim_id = target.number #remove tho
    self.on_init()
    self.instances.append(self)


  def __del__(self):
    """Destructors can't be relied on. Use a .destroy or something instead..."""
    # if not self.terminated: self.destroy()
    self.destroy()

  def destroy(self):
    """Ersatz destructor."""
    if self.terminated: return
    self.restore_opts()  # or eh dunno double, only for window?. taking over buffer seems mean
    self.on_term()
    self.terminated = True


  def push_opt(self, opt, val):
    if self.target.options.get(opt):
      self.saved_opts[opt] = self.target.options[opt]
    self.target.options[opt] = val

  def pop_opt(self, opt):
    if self.saved_opts.get(opt):
      self.target.options[opt] = self.saved_opts[opt]


  def store_opts(self, opts, origin):
    # origin = origin or self.target
    for opt in opts:
      if origin.options.get(opt):
        self.saved_opts[opt] = origin.options[opt]

  def apply_opts(self, opts, target):
    for opt,val in opts.items():
      # self.target.options[opt] = val
      target.options[opt] = val
      # try:    self.target.options[opt] = val
      # except: pass

  def restore_opts(self):
    """Not working right yet - only applies when model == target, ie taking over
    existing object. Then must restore"""
    self.apply_opts(self.saved_opts, self.model) # well.

  # eh fuck abstract bs. for this anyways
  # @abstractmethod
  def on_init(self):
    """Specific initialization"""
    pass
    # raise NotImplementedError

  # @abstractmethod
  def on_term(self):
    pass
    # raise NotImplementedError


