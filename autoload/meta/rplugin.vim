" guessing whatever the case might be better vim/nvim crossover stuff by now?
" keep it here for now...

let s:rep = expand('<sfile>:p:h:h:h')


function! meta#rplugin#start(default) abort
  if !meta#rplugin#init()
    return
  endif
  python3 << EOC
def _temporary_scope():
    import vim
    import rplugin
    from meta import start
    nvim = rplugin.Neovim(vim)
    start(nvim, [nvim.eval('a:default')], False)
_temporary_scope()
del _temporary_scope
EOC
endfunction

function! meta#rplugin#resume(default) abort
  if !meta#rplugin#init()
    return
  endif
  python3 << EOC
def _temporary_scope():
    import vim
    import rplugin
    from meta import start
    nvim = rplugin.Neovim(vim)
    start(nvim, [nvim.eval('a:default')], True)
_temporary_scope()
del _temporary_scope
EOC
endfunction

function! meta#rplugin#init() abort
  if exists('s:supported')
    return s:supported
  endif
  try
    let result = rplugin#init(s:rep, {
          \ 'python': 0,
          \ 'python3': has('python3'),
          \})
    let s:supported = result.python3
    if !s:supported
      echoerr 'Metabuffer requires a Neovim or Vim with Python3 support (+python3)'
    endif
  catch /^Vim\%((\a\+)\)\=:E117/
    echoerr 'Metabuffer cant be bothered supporting vim8.'
    let s:supported = 0
  endtry
  return s:supported
endfunction
