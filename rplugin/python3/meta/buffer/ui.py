
from .base import AbstractBuffer


class Buffer(AbstractBuffer):
  """A buffer acting as a UI element, providing additional data for a linked
  proper buffer. Ie line numbers, comments and other data that cant be shown in
  the original buffer due to UI or syntax highlighting restrictions. Instead
  open another window to left or right and link it..."""
  name = 'ui' # or view, or whatever...


  def __init__(self, nvim, extending_buffer, role, opts = {}):
    self.parent = extending_buffer

    super().__init__(nvim, None,
                      model=extending_buffer.buffer,
                      # name=role,
                      name=None,
                      opts=opts)
    AbstractBuffer.switch_buf(nvim, extending_buffer) #switch back to parent


  def update(self):
    src = self.parent.indices
    self.buffer[:] = ['%d \t%s' % (src[i],
                                   self.parent.name_buf)
                        for i in range(len(src))]
    # self.nvim.api.buf_set_lines(self.buffer, 0, -1, False, txt)
    # actually might be ok this amount of code for a dedicated index/linenr
    # view...

  def set_source(self):
    pass
  # def update(self, status):
  #     """Update state to match lines outputted by master buffer"""
  #     # so like get line numbers from lista or wherever the matcher resides...
  #     # or alt is skip having special type for ui buffer, just put it as a
  #     # regular (dummy)buffer and just let lista deal with the filtering via indices and its own on_update
