def __change_line(nvim, offset):
    line, col = nvim.current.window.cursor
    nvim.call('cursor', [line + offset, col])

def _select_next_candidate(meta, params):
    __change_line(meta.nvim, 1)
    # line, col = meta.nvim.current.window.cursor
    # meta.nvim.call('cursor', [line + 1, col])

def _select_previous_candidate(meta, params):
    __change_line(meta.nvim, -1)
    # line, col = meta.nvim.current.window.cursor
    # meta.nvim.call('cursor', [line - 1, col])


def _switch_matcher(meta, params):
    meta.switch_mode('matcher')

def _switch_case(meta, params):
    meta.switch_mode('case')

def _switch_highlight(meta, params):
    meta.switch_mode('syntax')

def _pause_prompt(meta, params):
    meta.pause_prompt()
def _accept_and_stay(meta, params):
    from .prompt.prompt import STATUS_PAUSE
    return STATUS_PAUSE

DEFAULT_ACTION_RULES = [
    ('meta:select_next_candidate', _select_next_candidate),
    ('meta:select_previous_candidate', _select_previous_candidate),
    ('meta:switch_matcher', _switch_matcher),
    ('meta:switch_case', _switch_case),
    ('meta:switch_highlight', _switch_highlight),
    ('meta:pause_prompt', _accept_and_stay),
]


DEFAULT_ACTION_KEYMAP = [
    ('<PageUp>', '<meta:select_previous_candidate>', 'noremap'),
    ('<PageDown>', '<meta:select_next_candidate>', 'noremap'),
    ('<C-A>', '<meta:move_caret_to_head>', 'noremap'),
    ('<C-E>', '<meta:move_caret_to_tail>', 'noremap'),
    ('<C-P>', '<meta:select_previous_candidate>', 'noremap'),
    ('<C-N>', '<meta:select_next_candidate>', 'noremap'),
    ('<C-K>', '<meta:select_previous_candidate>', 'noremap'),
    ('<C-J>', '<meta:select_next_candidate>', 'noremap'),
    ('<Left>', '<meta:move_caret_to_left>', 'noremap'),
    ('<Right>', '<meta:move_caret_to_right>', 'noremap'),
    ('<C-I>', '<meta:toggle_insert_mode>', 'noremap'),
    # ('<M-b>', '<meta:move_caret_to_one_word_right>', 'noremap'),
    # ('<C-Right>', '<meta:move_caret_to_one_word_right>', 'noremap'),
    # ('<M-f>', '<meta:move_caret_to_one_word_left>', 'noremap'),
    # ('<C-Left>', '<meta:move_caret_to_one_word_left>', 'noremap'),
    ('<S-Tab>', '<meta:select_previous_candidate>', 'noremap'),
    ('<Tab>', '<meta:select_next_candidate>', 'noremap'),
    ('<C-^>', '<meta:switch_matcher>', 'noremap'),
    ('<C-6>', '<meta:switch_matcher>', 'noremap'),
    ('<C-_>', '<meta:switch_case>', 'noremap'),
    ('<C-O>', '<meta:switch_case>', 'noremap'),
    ('<C-S>', '<meta:switch_highlight>', 'noremap'),
    ('<M-H>', '<meta:switch_highlight>', 'noremap'),
    ('<C-z>', '<meta:pause_prompt>', 'noremap'),      # not even reaching
    ('<M-CR>', '<meta:pause_prompt>', 'noremap'),      # not even reaching
    ]
# yank_to_default_register
# yank_to_register
    # paste_from_default_register

