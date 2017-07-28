def _select_next_candidate(meta, params):
    line, col = meta.nvim.current.window.cursor
    meta.nvim.call('cursor', [line + 1, col])


def _select_previous_candidate(meta, params):
    line, col = meta.nvim.current.window.cursor
    meta.nvim.call('cursor', [line - 1, col])


def _switch_matcher(meta, params):
    meta.switch_matcher()


def _switch_case(meta, params):
    meta.switch_case()


def _switch_highlight(meta, params):
    meta.switch_highlight()

def _pause_prompt(meta, params):
    meta._pause_prompt()


DEFAULT_ACTION_RULES = [
    ('meta:select_next_candidate', _select_next_candidate),
    ('meta:select_previous_candidate', _select_previous_candidate),
    ('meta:switch_matcher', _switch_matcher),
    ('meta:switch_case', _switch_case),
    ('meta:switch_highlight', _switch_highlight),
    ('meta:pause_prompt', _pause_prompt),
]


DEFAULT_ACTION_KEYMAP = [
    ('<PageUp>', '<meta:select_previous_candidate>', 'noremap'),
    ('<PageDown>', '<meta:select_next_candidate>', 'noremap'),
    ('<C-A>', '<meta:move_caret_to_head>', 'noremap'),
    ('<C-T>', '<meta:select_previous_candidate>', 'noremap'),
    ('<C-G>', '<meta:select_next_candidate>', 'noremap'),
    ('<C-P>', '<meta:select_previous_candidate>', 'noremap'),
    ('<C-N>', '<meta:select_next_candidate>', 'noremap'),
    ('<C-K>', '<meta:select_previous_candidate>', 'noremap'),
    ('<C-J>', '<meta:select_next_candidate>', 'noremap'),
    ('<Left>', '<meta:move_caret_to_left>', 'noremap'),
    ('<Right>', '<meta:move_caret_to_right>', 'noremap'),
    ('<C-I>', '<meta:toggle_insert_mode>', 'noremap'),
    # ('<S-Right>', '<meta:move_caret_to_one_word_right>', 'noremap'),
    # ('<C-Right>', '<meta:move_caret_to_one_word_right>', 'noremap'),
    # ('<S-Left>', '<meta:move_caret_to_one_word_left>', 'noremap'),
    # ('<C-Left>', '<meta:move_caret_to_one_word_left>', 'noremap'),
    ('<S-Tab>', '<meta:select_previous_candidate>', 'noremap'),
    ('<Tab>', '<meta:select_next_candidate>', 'noremap'),
    ('<C-^>', '<meta:switch_matcher>', 'noremap'),
    ('<C-6>', '<meta:switch_matcher>', 'noremap'),
    ('<C-_>', '<meta:switch_case>', 'noremap'),
    ('<C-->', '<meta:switch_case>', 'noremap'),
    ('<C-S>', '<meta:switch_highlight>', 'noremap'),
    ('<M-H>', '<meta:switch_highlight>', 'noremap'),
    ('<C-z>', '<meta:_pause_prompt>', 'noremap'),
    ]
# yank_to_default_register
# yank_to_register
    # paste_from_default_register

