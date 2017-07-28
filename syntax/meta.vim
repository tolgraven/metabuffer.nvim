if exists('b:current_syntax')
  finish
endif
let b:current_syntax = 'meta'

highlight default link MetaStatuslineModeInsert  Define
highlight default link MetaStatuslineModeReplace Todo
highlight default link MetaStatuslineFile        Comment
highlight default link MetaStatuslineMiddle      None
highlight default link MetaStatuslineMatcher     Statement
highlight default link MetaStatuslineIndicator   Tag

syntax match Comment /.*/ contains=Title
