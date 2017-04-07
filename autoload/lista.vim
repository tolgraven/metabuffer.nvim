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
if !exists('g:lista#highlight_groups')
	let g:lista#highlight_groups = {'lista': 'Title', 'buffer': 'ListaSearchHitBuffer'}
endif
if !exists('g:lista#syntax_init')
	let g:lista#syntax_init = 'buffer'
endif

"need these globally so dont need lista syntax to use them...
highlight default link ListaStatuslineModeInsert  	Tag
highlight default link ListaStatuslineModeReplace 	Todo

highlight default link ListaStatuslineQuery  				Normal

highlight default link ListaStatuslineFile        	Comment
highlight default link ListaStatuslineMiddle      	None

highlight default link ListaStatuslineMatcherAll   	Statement
highlight default link ListaStatuslineMatcherFuzzy  Number

highlight default link ListaStatuslineCaseSmart     String
highlight default link ListaStatuslineCaseIgnore    Special
highlight default link ListaStatuslineCaseNormal    Normal

highlight default link ListaStatuslineSyntaxBuffer 	Normal
highlight default link ListaStatuslineSyntaxLista 	Number

highlight default link ListaStatuslineIndicator   	Tag
highlight default link ListaStatuslineKey   				Comment

highlight default link ListaSignAqua							  GruvboxAquaSign 
highlight default link ListaSignBlue							  GruvboxBlueSign  
highlight default link ListaSignPurple						  GruvboxPurpleSign
highlight default link ListaSignGreen  						  GruvboxGreenSign 
highlight default link ListaSignYellow						  GruvboxYellowSign
highlight default link ListaSignOrange						  GruvboxOrangeSign
highlight default link ListaSignRed								  GruvboxRedSign

" highlight ListaSearchHitBuffer 		cterm=reverse,bold 	guibg=#799ca1 guifg=#282828
highlight ListaSearchHitBuffer 		cterm=bold gui=italic	guibg=#181818 guifg=#99b9e5
highlight default link ListaSearchHitFuzzy					ListaStatuslineMatcherFuzzy
" gui=bold,underline
