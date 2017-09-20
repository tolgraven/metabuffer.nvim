""""MetaPrompt module."""
import copy
import re
import weakref
from collections import namedtuple
from datetime import timedelta
from .prompt.action import ACTION_PATTERN
from .prompt.util import build_echon_expr
from .prompt import *

from .window.prompt import PromptWindow
from .window.metawindow import MetaWindow

ACTION_KEYSTROKE_PATTERN = re.compile(r'<(?P<action>%s)>' % ACTION_PATTERN.pattern)


STATUS_PROGRESS, STATUS_ACCEPT, STATUS_CANCEL, STATUS_INTERRUPT = 0, 1, 2, 3
INSERT_MODE_INSERT, INSERT_MODE_REPLACE = 1, 2


Condition = namedtuple('Condition', ['text', 'caret_locus'])


class MetaPrompt:
    """MetaPrompt class.

    Attributes:
        name: Prompt instance name
    """

    name = 'master'

    def __init__(self, nvim, parent_window, text=''):
        """Constructor.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
        """
        # from .keymap import DEFAULT_KEYMAP_RULES, Keymap
        # from .action import DEFAULT_ACTION
        # self.action = copy.copy(DEFAULT_ACTION)
        # self.keymap = Keymap.from_rules(nvim, DEFAULT_KEYMAP_RULES)
        self.nvim = nvim
        self.text = text
        self.window = MetaWindow(self.nvim, parent_window)
        self.promptwindow = PromptWindow()
        self.window.add(self.promptwindow)


    def insert_text(self, text):
        """Prob go straight to PromptWindow / buffer for these"""
        pass

    def redraw_prompt(self):
        """Redraw prompt."""
        pass

    def start(self):
        """Initialize the prompt. Set up autocmd hooks so on_update gets called when text is changed
        Or do the upcoming nvim hook thing, fetch info on that and try it out..."""
        if self.nvim.options['timeout']:
            timeoutlen = timedelta( milliseconds=int(self.nvim.options['timeoutlen']))
        else: timeoutlen = None
        # i guess depending on settings / timeoutlen etc might defer updates,
        # using own timer or by hooking cursorhold instead? meh, later q...
        self.nvim.command('augroup MetabufferUpdate | autocmd!')
        self.nvim.command('autocmd TextChanged,TextChangedI call meta#sync()')
        self.nvim.command('autocmd BufLeave call meta#finish()')  #osv
        self.nvim.command('augroup END')
        # if self.text: self.nvim.call('histadd', 'input', self.text)
        # return self.on_term(status)


    def on_update(self):
        """Main loop type thing. How do we steer here? Since we won't have any
        continous main loop at all"""
        self.last_text = self.text
        

    def on_redraw(self):
        """Redraw the prompt.

        Update matchadds and stuff I guess, when contents (or syntax etc) changes
        """
        pass

    def on_keypress(self, keystroke):
        """Not needed"""
        pass

    def on_term(self, status):
        """Finalize the prompt.

        Args:
            status (int): A prompt status.

        Returns:
            int: A status which is used as a result value of the prompt.
        """
        return status

    def store(self):
        """Save current prompt condition into a Condition instance."""
        return Condition(
            text=self.text,
            caret_locus=self.caret.locus,
        )

    def restore(self, condition):
        """Load current prompt condition from a Condition instance."""
        self.text = condition.text
        self.caret.locus = condition.caret_locus
