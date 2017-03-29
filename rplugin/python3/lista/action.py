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


DEFAULT_ACTION_RULES = [
    ('lista:select_next_candidate', _select_next_candidate),
    ('lista:select_previous_candidate', _select_previous_candidate),
    ('lista:switch_matcher', _switch_matcher),
    ('lista:switch_case', _switch_case),
    ('lista:switch_highlight', _switch_highlight),
]


DEFAULT_ACTION_KEYMAP = [
    ('<PageUp>', '<lista:select_previous_candidate>', 'noremap'),
    ('<PageDown>', '<lista:select_next_candidate>', 'noremap'),
    ('<C-T>', '<lista:select_previous_candidate>', 'noremap'),
    ('<C-G>', '<lista:select_next_candidate>', 'noremap'),
    ('<C-N>', '<lista:select_previous_candidate>', 'noremap'),
    ('<C-P>', '<lista:select_next_candidate>', 'noremap'),
    ('<C-K>', '<lista:select_previous_candidate>', 'noremap'),
    ('<C-J>', '<lista:select_next_candidate>', 'noremap'),
    ('<Left>', '<lista:select_previous_candidate>', 'noremap'),
    ('<Right>', '<lista:select_next_candidate>', 'noremap'),
    ('<S-Tab>', '<lista:select_previous_candidate>', 'noremap'),
    ('<Tab>', '<lista:select_next_candidate>', 'noremap'),
    ('<C-^>', '<lista:switch_matcher>', 'noremap'),
    ('<C-6>', '<lista:switch_matcher>', 'noremap'),
    ('<C-_>', '<lista:switch_case>', 'noremap'),
    ('<C-->', '<lista:switch_case>', 'noremap'),
    ('<C-S>', '<lista:switch_highlight>', 'noremap'),
]
