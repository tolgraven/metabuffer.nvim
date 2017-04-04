if has('nvim')
  function! lista#start(default) abort
    return _lista_start(a:default)
  endfunction
  function! lista#resume(default) abort
    return _lista_resume(a:default)
  endfunction
	function! lista#callback_update(default) abort
		return _lista_callback_signs(a:default)
	endfunction
else
  function! lista#start(default) abort
    return lista#rplugin#start(a:default)
  endfunction
  function! lista#resume(default) abort
    return lista#rplugin#resume(a:default)
  endfunction
endif

if !exists('g:lista#custom_mappings')
  let g:lista#custom_mappings = []
endif
if !exists('g:lista#highlight_group')
	let g:lista#highlight_group = 'Title'
endif

"need these globally so dont need lista syntax to use them...
highlight default link ListaStatuslineModeInsert  	Tag
highlight default link ListaStatuslineModeReplace 	Todo

highlight default link ListaStatuslineQuery  				Normal

highlight default link ListaStatuslineFile        	Comment
highlight default link ListaStatuslineMiddle      	None

highlight default link ListaStatuslineMatcherAll   	Tag
highlight default link ListaStatuslineMatcherFuzzy  Number

highlight default link ListaStatuslineCaseSmart     String
highlight default link ListaStatuslineCaseIgnore    Special
highlight default link ListaStatuslineCaseNormal    Normal

highlight default link ListaStatuslineSyntaxBuffer 	Normal
highlight default link ListaStatuslineSyntaxLista 	Number

highlight default link ListaStatuslineIndicator   	Statement
highlight default link ListaStatuslineKey   				Comment

