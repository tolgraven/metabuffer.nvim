function! meta#start(default) abort
	return _meta_start(a:default)
endfunction
function! meta#resume(default) abort
	return _meta_resume(a:default)
endfunction
function! meta#sync(default) abort
	return _meta_sync(a:default)
endfunction
function! meta#finish(default) abort
	return _meta_finish(a:default)
endfunction
function! meta#callback_signs(default) abort
	return _meta_callback_signs(a:default)
endfunction
" from denite, keep in mind: " Add current position to the jumplist.
" execute line('.')

let g:meta#custom_mappings  = get(g:, 'meta#custom_mappings',	[])
" let g:meta#highlight_groups = get(g:, 'meta#highlight_groups', {'faded': 'Title', 'buffer': 'MetaSearchHit'})
let g:meta#highlight_groups = get(g:, 'meta#highlight_groups', {'All': 'Title', 'Fuzzy': 'Number', 'Regex': 'Special'})
let g:meta#syntax_on_init   = get(g:, 'meta#syntax_on_init',	'buffer')
let g:meta#prefix           = get(g:, 'meta#prefix',		'#')

"need these globally so dont need meta syntax to use them...
highlight default link MetaStatuslineModeInsert			Tag
highlight default link MetaStatuslineModeReplace		Todo

highlight default link MetaStatuslineQuery  				Normal

highlight default link MetaStatuslineFile        		Comment
highlight default link MetaStatuslineMiddle      		None

" highlight default link MetaStatuslineMatcherAll   	Statement
highlight MetaStatuslineMatcherAll   	cterm=bold gui=italic	guibg=#181818 guifg=#99b9e5
" highlight default link MetaStatuslineMatcherFuzzy		Number
highlight MetaStatuslineMatcherFuzzy	cterm=bold gui=italic	guibg=#181818 guifg=#af8589
" highlight default link MetaStatuslineMatcherRegex		Special
highlight MetaStatuslineMatcherRegex	cterm=bold gui=italic	guibg=#181818 guifg=#ca782b

highlight default link MetaStatuslineCaseSmart			String
highlight default link MetaStatuslineCaseIgnore			Special
highlight default link MetaStatuslineCaseNormal			Normal

highlight default link MetaStatuslineSyntaxBuffer		Normal
highlight default link MetaStatuslineSyntaxFaded		Number

highlight default link MetaStatuslineIndicator			Tag
highlight default link MetaStatuslineKey						Comment

highlight default link MetaSignAqua									BruvboxAquaSign 
highlight default link MetaSignBlue									BruvboxBlueSign  
highlight default link MetaSignPurple								BruvboxPurpleSign
highlight default link MetaSignGreen								BruvboxGreenSign 
highlight default link MetaSignYellow								BruvboxYellowSign
highlight default link MetaSignOrange								BruvboxOrangeSign
highlight default link MetaSignRed									BruvboxRedSign

highlight default link MetaSearchHitAll							MetaStatuslineMatcherAll 	"fallback
highlight default link MetaSearchHitBuffer					MetaStatuslineMatcherAll
highlight default link MetaSearchHitFuzzy						MetaStatuslineMatcherFuzzy
highlight default link MetaSearchHitFuzzyBetween		BruvboxPurpleFadedBg
highlight default link MetaSearchHitRegex						MetaStatuslineMatcherRegex

" noremap # 								:Meta<CR>
" noremap ## 							  :MetaResume<CR>
" noremap ** 							  :MetaCursorWord<CR>
" " vnoremap ** 				 <C-o>:MetaCursorWord<CR>|		"no work.	also, ought to have a "MetaWithSelection"
" noremap *** 							:MetaResumeCursorWord<CR>
" noremap <Leader>** 			  :sp<CR>:MetaResumeCursorWord<CR>
