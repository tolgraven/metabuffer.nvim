from .window import AbstractWindow
from meta.buffer.prompt import Buffer as PromptBuffer


class PromptWindow(AbstractWindow):
  """A window acting as a sleepy prompt"""
  name = 'promptwindow'


  def __init__(self, nvim, parent, height = 5):
    # XXX question: this just a small thing that we'll put in new prompt class
    # when redesigning it to use a reg buffer/window instead of vim's prompt?
    self.nvim.command('botright new')
    self.window = self.nvim.current.window

