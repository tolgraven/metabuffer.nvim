from .base import AbstractBuffer


class Buffer(AbstractBuffer):
  """A regular vim buffer object"""
  name = 'buffer'

  def on_init(self):
    self.nvim.command('')
