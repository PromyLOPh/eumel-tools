" Vim syntax file
" Copy to ~/.vim/syntax/ and enable with :set filetype=elan
" Language: ELAN
" Maintainer: Lars-Dominik Braun <lars+eumel@6xq.net>
" Latest Revision: 2019-02-07

if exists("b:current_syntax")
  finish
endif

syn keyword elanStatement PROC ENDPROC OP PACKET ENDPACKET LEAVE WITH END LET DEFINES
syn keyword elanConditional IF ELSE FI THEN SELECT OF ELIF
syn keyword elanRepeat FOR FROM UPTO REP PER WHILE UNTIL
syn keyword elanBoolean TRUE FALSE
syn keyword elanType DATASPACE INT TEXT BOOL THESAURUS FILE REAL
syn match   elanOperator      ":="
syn match   elanOperator      "::"
syn match   elanOperator      "\*"
syn match   elanOperator      "<>"
syn keyword elanOperator AND OR CAND COR NOT XOR
syn keyword elanOperator DIV MUL ISUB INCR DECR MOD SUB LENGTH CAT LIKE CONTAINS
syn keyword elanStorageClass VAR CONST BOUND ROW
syn keyword elanStructure STRUCT TYPE
syn keyword elanLabel CASE OTHERWISE
syn match   elanNumber		"-\=\<\d\+\>"
syn match	elanFloat		"\d\+\.\d\+"

syn region elanComment	start=+(\*+  end=+\*)+
" XXX: tried to fix strings containing numbers that are not escapes, like "2",
syn region elanString start=+"+rs=s+1 end=+"+re=e-1 contains=elanStringEscape
"syn match  elanStringEscape	contained +"[0-9]\+"+


hi def link elanBoolean		Boolean
hi def link elanConditional	Conditional
hi def link elanRepeat		Repeat
hi def link elanType		Type
hi def link elanComment		Comment
hi def link elanOperator	Operator
hi def link elanString		String
hi def link elanStringEscape	Special
hi def link elanStorageClass	StorageClass
hi def link elanStructure		Structure
hi def link elanLabel		Label
hi def link elanStatement Statement
hi def link elanNumber Number
hi def link elanFloat Float

let b:current_syntax = "elan"


