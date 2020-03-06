
DEFAULT_META_SIGN_START = 666
DUMMY_SIGN_INDEX = 0

class Signs():
  """vim signs"""
  buffers = []
  signs = []

  colors = ['MetaSign' + color for color in \
            ['Aqua', 'Blue', 'Purple', 'Green', 'Yellow', 'Orange', 'Red']]
  sign_id_start, signs_defined = 90101, []


  def __init__(self, nvim, parent_buffer = None, starting_id = DEFAULT_META_SIGN_START, force = False):
    """Constructor.

    Args:
    """
    self.nvim = nvim
    self.signs.append(MetaSign(nvim, 'MetaDummy', 666)) #to force blabla cant remember
    self.buffers.append(parent_buffer)

    if force or (parent_buffer and parent_buffer.has_signs):  # also place dummy if there were signs placed/signcolumn visible, so layout stays the same
      self.signs[DUMMY_SIGN_INDEX].place(1, parent_buffer)


  def thing_in_meta_on_update(self): #comment: 'remove all signs since they get fucked when we replace text of buffer anyways. Replace dummy'
    self.nvim.command('sign unplace * buffer=%d' % self.nvim.current.buffer.number)  # no point not clearing since all end up at line 1... but guess theoretically we might want to be able to move along existing signs from other fuckers, sounds far off though so this works for now
    self.nvim.command('sign place 666 line=1 name=MetaDummy buffer=%d' %
                      self.nvim.current.buffer.number)


  def __del__(self):
    for buf in self.buffers:  # no point not clearing since all end up at line 1... but guess theoretically we might want to be able to move along existing signs from other fuckers, sounds far off though so this works for now
      self.nvim.command('sign unplace * buffer=%d' % buf.vim_id)


  def update(self, hit_count=None, jump_to_next=1): #fixup so works here...
      pass
      if not self.signs_enabled:  return
      hit_count = hit_count or len(self._indices)
      win_height = self.nvim.current.window.height
      buf_nr = self.nvim.current.buffer.number

      for hit_line_index in range(min(hit_count, win_height)):
          source_line_nr = self._indices[hit_line_index] + 1

          if source_line_nr not in self.signs_defined:
              highlight = next((colors[x] for x in range(len(colors))
                                if x * 100 + 99 >= source_line_nr), 'Normal')
              index_text = str(source_line_nr)[-2:]

              sign_to_define = 'sign define MetaLine%d text=%s texthl=%s' % (
                                source_line_nr, index_text, highlight)
              self.nvim.command(sign_to_define)
              self.signs_defined.append(source_line_nr)

          # remember, all placed signs get reset to line 1 when content is replaced.
          sign_to_place = 'sign place %d line=%d name=MetaLine%d buffer=%d' \
              % (self.sign_id_start + hit_line_index, hit_line_index + 1,
                  source_line_nr, buf_nr)

          self.nvim.command(sign_to_place)


class MetaSign():
  """Represending a sign, so can keep and reuse whether defined in vim or not"""

  # def __init__(self, nvim, name, sign_id = STARTING_ID++, parent_buffer = None):
  def __init__(self, nvim, name, sign_id = None, parent_buffer = None):
    """Constructor.

    Args:
    """
    self.nvim = nvim
    self.name = name
    self.sign_id = sign_id or 666 #new_sign_uid() #yeah lookup best way
    self.nvim.command('sign define ' + name)


  def place(self, line, buffer = None):
    self.nvim.command('sign place %d line=%d name=%s buffer=%d'%
                          self.sign_id, line, self.name, buffer.vim_id)

  def unplace(self, line, buffer = None):
    self.nvim.command('sign unplace ' + line)
