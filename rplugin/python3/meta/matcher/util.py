def assign_content(nvim, content):
    """Assign content to the current buffer.

    Args:
        nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
        content (str): A str content.
    """
    viewinfo = nvim.call('winsaveview')
    nvim.current.buffer.options['modifiable'] = True
    nvim.current.buffer[:] = content
    nvim.current.buffer.options['modifiable'] = False
    nvim.call('winrestview', viewinfo)

# from denite util lib
import re
import os
import sys
import glob

from os.path import normpath, join


def convert2list(expr):
    return (expr if isinstance(expr, list) else [expr])

def split_input(text):
    return [x for x in re.split(r'\s+', text) if x != '']


def globruntime(runtimepath, path):
    ret = []
    for rtp in re.split(',', runtimepath):
        ret += glob.glob(rtp + '/' + path)
    return ret

def clear_cmdline(vim):
    vim.command('redraw | echo')

def path2dir(path):
    return path if os.path.isdir(path) else os.path.dirname(path)


def regex_convert_str_vim(string):
    return re.sub(r'([\^$.*\\/~\[\]])', r'\\\1', string)

def regex_convert_py_vim(expr):
    return r'\v' + re.sub(r'(?!\\)([/~])', r'\\\1', expr)

def convert2fuzzy_pattern(text):
    return '\|'.join([escape_fuzzy(x, True) for x in split_input(text)])

def convert2regex_pattern(text):
    return '\|'.join(split_input(text))


def escape(expr):
    return expr.replace("'", "''")

def escape_fuzzy(string, camelcase):
    # Escape string for python regexp.
    p = re.sub(r'([a-zA-Z0-9_-])(?!$)', r'\1[^\1]*', string)
    if camelcase and re.search(r'[A-Z](?!$)', string):
        p = re.sub(r'([a-z])(?!$)',
                   (lambda pat: '['+pat.group(1)+pat.group(1).upper()+']'), p)
    p = re.sub(r'/(?!$)', r'/[^/]*', p)
    return p


def parse_jump_line(path_head, line):
    m = re.search(r'^(.*):(\d+)(?::(\d+))?:(.*)$', line)
    if not m or not m.group(1) or not m.group(4):
        return []

    if re.search(r':\d+$', m.group(1)):
        # Use column pattern
        m = re.search(r'^(.*):(\d+):(\d+):(.*)$', line)

    [path, linenr, col, text] = m.groups()

    if not linenr:
        linenr = '1'
    if not col:
        col = '0'
    if not os.path.isabs(path):
        path = join(path_head, path)

    return [path, linenr, col, text]


def expand(path):
    return os.path.expandvars(os.path.expanduser(path))

def abspath(vim, path):
    return normpath(join(vim.call('getcwd'), expand(path)))


def parse_command(array, **kwargs):
    def parse_arg(arg):
        if arg.startswith(':') and arg[1:] in kwargs:
            return kwargs[arg[1:]]
        return arg

    return [parse_arg(i) for i in array]


def parse_tagline(line):
    elem = [e for e in line.split("\t") if e != '']
    return {
        'name': elem[0],
        'file': elem[1],
        'pattern': re.sub(r'^/|/;"$', '', elem[2]),
        'type': elem[3],
        'ref': ' '.join(elem[4:])
    }


# def load_external_module(file, module):
#     current = os.path.dirname(os.path.abspath(file))
#     module_dir = join(os.path.dirname(current), module)
#     sys.path.insert(0, module_dir)

