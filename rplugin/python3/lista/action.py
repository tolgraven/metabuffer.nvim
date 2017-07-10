def _select_next_candidate(lista, params):
    line, col = lista.nvim.current.window.cursor
    lista.nvim.call('cursor', [line + 1, col])


def _select_previous_candidate(lista, params):
    line, col = lista.nvim.current.window.cursor
    lista.nvim.call('cursor', [line - 1, col])


def _switch_matcher(lista, params):
    lista.switch_matcher()


def _switch_case(lista, params):
    lista.switch_case()


def _switch_highlight(lista, params):
    lista.switch_highlight()

def _pause_prompt(lista, params):
    lista._pause_prompt()


DEFAULT_ACTION_RULES = [
    ('lista:select_next_candidate', _select_next_candidate),
    ('lista:select_previous_candidate', _select_previous_candidate),
    ('lista:switch_matcher', _switch_matcher),
    ('lista:switch_case', _switch_case),
    ('lista:switch_highlight', _switch_highlight),
    ('lista:pause_prompt', _pause_prompt),
]


pause_prompt = [
    ('<PageUp>', '<lista:select_previous_candidate>', 'noremap'),
    ('<PageDown>', '<lista:select_next_candidate>', 'noremap'),
    ('<C-A>', '<lista:move_caret_to_head>', 'noremap'),
    ('<C-T>', '<lista:select_previous_candidate>', 'noremap'),
    ('<C-G>', '<lista:select_next_candidate>', 'noremap'),
    ('<C-P>', '<lista:select_previous_candidate>', 'noremap'),
    ('<C-N>', '<lista:select_next_candidate>', 'noremap'),
    ('<C-K>', '<lista:select_previous_candidate>', 'noremap'),
    ('<C-J>', '<lista:select_next_candidate>', 'noremap'),
    ('<Left>', '<lista:move_caret_to_left>', 'noremap'),
    ('<Right>', '<lista:move_caret_to_right>', 'noremap'),
    ('<C-I>', '<lista:toggle_insert_mode>', 'noremap'),
    # ('<S-Right>', '<lista:move_caret_to_one_word_right>', 'noremap'),
    # ('<C-Right>', '<lista:move_caret_to_one_word_right>', 'noremap'),
    # ('<S-Left>', '<lista:move_caret_to_one_word_left>', 'noremap'),
    # ('<C-Left>', '<lista:move_caret_to_one_word_left>', 'noremap'),
    ('<S-Tab>', '<lista:select_previous_candidate>', 'noremap'),
    ('<Tab>', '<lista:select_next_candidate>', 'noremap'),
    ('<C-^>', '<lista:switch_matcher>', 'noremap'),
    ('<C-6>', '<lista:switch_matcher>', 'noremap'),
    ('<C-_>', '<lista:switch_case>', 'noremap'),
    ('<C-->', '<lista:switch_case>', 'noremap'),
    ('<C-S>', '<lista:switch_highlight>', 'noremap'),
    ('<M-H>', '<lista:switch_highlight>', 'noremap'),
    ('<C-z>', '<lista:pause>', 'noremap'),
    ]
# yank_to_default_register
# yank_to_register
    # paste_from_default_register

