"""Buffer module."""
from copy import (copy, deepcopy)
from collections import namedtuple
from meta.handle import MetaHandle

View = namedtuple('BufferView', [
   'source', 'indexes',
])

class AbstractBuffer(MetaHandle):
  """An abstract buffer class.

  Attributes:
    nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
    nvim.buffer (neovim.Nvim.buffer): A ``neovim.Nvim.buffer`` instance.
    opts (dict): A dictionary containing options to apply on creation
  """

  name = 'abstract'
  # transforms = []             # small stuff to run on update before presenting
  # views = []  # a metabuffer should be able to present the same material with multiple views

  def __init__(self, nvim, buffer = None, model = None, name = None, opts = {}): # sending a (nvim, not meta) buffer to model. cause seems silly just taking over stuff that's how you break shit
    """Basically all of this should go up AbstractBuffer"""

    model = model or nvim.current.buffer             #or can we set inn arg
    if not name: # XXX beware different behavior here right now tho
      # name = Buffer.get_name(self.nvim, model)
      curr = nvim.current.buffer
      AbstractBuffer.switch_buf(nvim, model)
      # self._name = nvim.eval('simplify(expand("%:~:."))')      #need override super which fetches from target.name?
      name = nvim.eval('simplify(expand("%:~:."))')      #need override super which fetches from target.name?
      AbstractBuffer.switch_buf(nvim, curr)
    # else:
      # self._name = name

    # self.nvim.command("silent keepalt file! %s-%s" % (self.name_buf, self.name))
    super().__init__(nvim, buffer or AbstractBuffer.new(nvim), model, opts)   # create new buf, pass it up
    self.set_name("%s-%s" % (name, self.name)) # will ensure activates self.buffer properly

    # self.activate()
    # self.nvim.command("silent keepalt file! %s-%s" % (self.name_buf, self.name))
    self.buffer = self.target


  # @name_buf.setter
  # def name_buf(self, name):
  @property
  def name_buf(self): return self._name

  @property
  def name_short(self): return self._name.split('/')[-1]
  # @name_obj.setter
  # def name_obj(self, val):  self._name = val
  @property
  def content(self):    return self._content
  @property
  def line_count(self): return len(self.content)
  # def line_count(self): return self.buffer.api.line_count() # good in theory but remember minimize calls across..
  @property
  def indices(self):    return self.filtered_indexes
  @property
  def all_indices(self): return self._indices


  def add_transform(self, f):
    self.transforms.append(f)


  def source_line_nr(self, index):
    """Skip error checking right now so can se where goes wrong"""
    if len(self.indices):
      # try:
        return self.indices[index] + 1
      # except IndexError:
        # return None
    else:
      return None

  def closest_index(self, line_nr, attempt_true_index=True):
    """For current (filtered) indexes, get matching index if available, else
    the one nearest given line_nr.
    Which should actually also be an index because we're looking up indexes dumbo."""
    index = None
    if attempt_true_index:
      try:  index = self.indices.index(line_nr)
      except ValueError: pass # line filtered out, find closest. prepare for awful algo!
    return index if index != None else self._closest_index(line_nr)


  def _closest_index(self, line_nr):
    for idx in range(len(self.indices)):
      if self.indices[idx] > line_nr:
        idxs = max(idx-1, 0), idx
        dist = [abs(line_nr - line) for line in [self.indices[i] for i in idxs]]
        return idxs[0] if dist[0] < dist[1] else idxs[1]
    return -1       # max idx


  def run_filter(self, matcher, query, ignorecase, run_clean = False):
    if run_clean: self.reset_filter() # new, restarted or backtracking

    matcher.filter(query,
                   self.filtered_indexes,   # .filtered_indexes bc fn is side-effecting, .indices is getter...
                   self.content[:],
                   ignorecase) # ^  weird thing with regex matcher (which unlike others can end up with more chars AND more hits) if go eg 'function|return' only adds the return lines once hit backspace...
    # ^ the horror!! fix this uncouth unpure monstrosity. don't change content in place, return new...
    # also remember if need to look through .indices many times, make a set copy and do it on that for constant time.
    if len(self.indices) < 1000:
      matcher.highlight(query, ignorecase)        # highlights instances with the appropriate highlighting group
    else:
      matcher.remove_highlight()                  #too much, man. better if it resigns to just hl currently visible tho...


  def reset_filter(self):
    """Reset filtered indexes to original (which might later be pre-filtered, tho...)"""
    self.filtered_indexes = deepcopy(self._indices)

  @property
  def syntax(self):
    """Return model/target buffer syntax"""
    return self.model.options['syntax']

  def update(self):
    """update shown content off any filter. but need further sep, have two
    Buffers for available vs. displayed content, then keep taking that concept further"""

    viewinfo = self.nvim.call('winsaveview')  # save where view centered etcetc. Not always ideal when filtering takes us off-center
    self.push_opt('modifiable', True)
    self.buffer[:] = [self.content[i] for i in self.indices] # does it run loop and then call w final result or update incr? def need former for performance.
    self.pop_opt('modifiable')
    self.nvim.call('winrestview', viewinfo)



  def push_line(self, idx, txt):
    self.nvim.api.buf_set_lines(self.model.handle, idx+1, idx+1, False, txt)

  def activate(self, target = None):
    target = target or self.target
    self.nvim.command('noautocmd keepjumps %dbuffer' % target.handle)

  # def push_view()...

  def set_name(self, buf_name, target = None):
    target = target or self.target
    curr = self.nvim.current.buffer #assuming we are active win in first place... ugh
    if curr.handle != target.handle: self.activate(target)
    # self.nvim.command("silent keepalt file! %s-%s" % (self.name_buf, self.name))
    self.nvim.command("silent keepalt file! %s" % buf_name)
    if curr.handle != target.handle: self.activate(curr)
    self._name = buf_name


  # @staticmethod
  # def activate_and_run(nvim, buffer, f):


  @staticmethod
  def switch_buf(nvim, vimbuffer):
    """Makes little sense here, but does make sense to wrap since got noautocmd
    keepjumps possibly keepalt? yada. Static better. But then no nvim instance
    hah."""
    # nvim.command('noautocmd keepjumps buffer %d' % vimbuffer.number)
    if isinstance(vimbuffer, AbstractBuffer):
      vimbuffer = vimbuffer.buffer
    nvim.command('noautocmd keepjumps %dbuffer' % vimbuffer.number) #ensures always works w number
    # return copy(nvim.current.buffer)
    return nvim.current.buffer

  @staticmethod
  def new(nvim):
    """Create and return a new (nvim) buffer"""
    # handle = nvim.api.create_buf(False, True) # buflisted=unlisted, scratch so buftype=nofile, bufhidden=hide
    handle = nvim.api.create_buf(False, False) # buflisted=unlisted, #2 True = scratch so buftype=nofile, bufhidden=hide
    return handle #so, now doesnt switch
    # current = nvim.current.buffer
    # nvim.command('noautocmd keepjumps enew')
    # return nvim.current.buffer
    # return [nvim.current.buffer, current]


# Types of buffers:
# - Regular: vim buffer, as normal. A potential source
# - Meta: a vim dummy buffer containing multiple other buffers as its inputs,
# and through then, back-propgating changes to their original location
# - UI: helper buffer containing UI elements, basically to get around vim's
# limitations here (only 2 char sign column, etc). Should be linked with other
# buffers through a metawindow container...

# better to minimize types so that sources is a list by default I guess, whether contains one or several
# but guess point is a metabuffer will contain refs to a bunch of instances of its relatives... who filter themselves and handle their own shit yeah?

  def __del__(self):
    """nuke self"""
    # self.buffer.options['bufhidden'] = 'wipe'
    # self.nvim.command('sign unplace * buffer=%d' % self.vim_id)
    # self.nvim.command('bwipe %d' % self.vim_id)  #something like that


  # @syntax_type.setter
  # def syntax_type(self, new_type):
  #   self.syntax_type = new_type


  # "exceptions" - some lines/buffers need to be frozen/unaffected by edits. How best handle?
  # because not just about not propogating back to source, but also (I guess?) instantly reverting edits so they keep showing up the same...


  def sign_add(self, signstuff):
    # first like check to see the sign we're adding is actually defined, if not, do it
    # self.nvim.command('sign place ')
    pass

  def sign_delete(self, signstuff):
    # self.nvim.command('sign unplace ')
    pass

