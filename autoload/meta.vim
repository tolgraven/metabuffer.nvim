if has('nvim')
  function! meta#start(default) abort
    return _meta_start(a:default)
  endfunction
  function! meta#resume(default) abort
    return _meta_resume(a:default)
  endfunction
	function! meta#callback_update(default) abort
		return _meta_callback_signs(a:default)
	endfunction
else
  function! meta#start(default) abort
    return meta#rplugin#start(a:default)
  endfunction
  function! meta#resume(default) abort
    return meta#rplugin#resume(a:default)
  endfunction
endif

if !exists('g:meta#custom_mappings')
  let g:meta#custom_mappings = []
endif
if !exists('g:meta#highlight_groups')
	let g:meta#highlight_groups = {'meta': 'Title', 'buffer': 'MetaSearchHitBuffer'}
endif
if !exists('g:meta#syntax_on_init')
	let g:meta#syntax_on_init = 'buffer'
endif

"need these globally so dont need meta syntax to use them...
highlight default link MetaStatuslineModeInsert  	Tag
highlight default link MetaStatuslineModeReplace 	Todo

highlight default link MetaStatuslineQuery  			Normal

highlight default link MetaStatuslineFile        	Comment
highlight default link MetaStatuslineMiddle      	None

highlight default link MetaStatuslineMatcherAll   Statement
highlight default link MetaStatuslineMatcherFuzzy  Number

highlight default link MetaStatuslineCaseSmart     String
highlight default link MetaStatuslineCaseIgnore    Special
highlight default link MetaStaatuslineCaseNormal   Normal

highlight default link MetaStatuslineSyntaxBuffer Normal
highlight default link MetaStatuslineSyntaxMeta 	Number

highlight default link MetaStatuslineIndicator   	Tag
highlight default link MetaStatuslineKey   				Comment

highlight default link MetaSignAqua							  GruvboxAquaSign 
highlight default link MetaSignBlue							  GruvboxBlueSign  
highlight default link MetaSignPurple						  GruvboxPurpleSign
highlight default link MetaSignGreen  						GruvboxGreenSign 
highlight default link MetaSignYellow						  GruvboxYellowSign
highlight default link MetaSignOrange						  GruvboxOrangeSign
highlight default link MetaSignRed								GruvboxRedSign

" highlight MetaSearchHitBuffer 		cterm=reverse,bold 	guibg=#799ca1 guifg=#282828
highlight MetaSearchHitBuffer 		cterm=bold gui=italic	guibg=#181818 guifg=#99b9e5
highlight default link MetaSearchHitFuzzy					MetaStatuslineMatcherFuzzy
" gui=bold,underline

" noremap # 								:Meta<CR>
" noremap ## 							  :MetaResume<CR>
" noremap ** 							  :MetaCursorWord<CR>
" " vnoremap ** 				 <C-o>:MetaCursorWord<CR>|		"no work.	also, ought to have a "MetaWithSelection"
" noremap *** 							:MetaResumeCursorWord<CR>
" noremap <Leader>** 			  :sp<CR>:MetaResumeCursorWord<CR>

