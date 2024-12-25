# CS321B Introduction to Compiler

```markdown
program -> { stmt }

stmt ->
    class_stmt
    | func_stmt
    | struct_stmt
    | normal_stmt
    | declaration_stmt

class_stmt ->
    "CLASS" ident nl
    { ( "PUBLIC" | "PRIVATE" ) nl
      func_stmt | declaration_stmt }
    "ENDCLASS" nl

func_stmt ->
    "FUNCTION" ident "(" [ param_list ] ")" [ "AS" type ] nl
    { normal_stmt | declaration_stmt }
    "ENDFUNCTION" nl

param_list ->
    ident "AS" type { "," ident "AS" type }

struct_stmt ->
    "STRUCT" ident nl
    { ident "AS" type nl }
    "ENDSTRUCT" nl

normal_stmt ->
    decision_stmt
    | loop_stmt
    | io_stmt
    | jump_stmt

declaration_stmt ->
    "LET" ident "AS" type "=" expr nl
    | "DIM" ident "AS" type [ "(" expr ")" ] nl
    | "CONST" ( "LET" | "DIM" ) ident "AS" type [ "(" expr ")" ] "=" expr nl

decision_stmt ->
    if_stmt
    | switch_stmt

if_stmt ->
    "IF" expr "THEN" nl
    { normal_stmt }
    { "ELIF" expr "THEN" nl { normal_stmt } }
    [ "ELSE" nl { normal_stmt } ]
    "ENDIF" nl

switch_stmt ->
    "SWITCH" expr nl
    { "CASE" expr nl { normal_stmt } }
    [ "DEFAULT" nl { normal_stmt } ]
    "ENDSWITCH" nl

loop_stmt ->
    "WHILE" expr nl
    { normal_stmt }
    "ENDWHILE" nl
    | "DO" nl
    { normal_stmt }
    "ENDDO" [ "WHILE" expr ] nl
    | "FOR" ident "AS" type "=" expr "TO" expr [ "STEP" expr ] nl
    { normal_stmt }
    "ENDFOR" nl

io_stmt ->
    "INPUT" ident nl
    | "PRINT" [ color ] ( expr | string ) nl
    | "OPEN" string "FOR" ( "INPUT" | "OUTPUT" ) "AS" ident nl
    | "CLOSE" ident nl

jump_stmt ->
    "LABEL" ident nl
    | "GOTO" ident nl
    | "BREAK" nl
    | "CONTINUE" nl
    | "RETURN" [ expr ] nl

expr -> logical_expr

logical_expr -> logical_term { "OR" logical_term }

logical_term -> logical_factor { "AND" logical_factor }

logical_factor -> [ "NOT" ] comparison

comparison -> arith_expr [ ( "==" | "!=" | "<" | ">" | "<=" | ">=" ) arith_expr ]

arith_expr -> arith_term { ( "+" | "-" ) arith_term }

arith_term -> arith_factor { ( "*" | "/" ) arith_factor }

arith_factor -> [ "+" | "-" ] arith_base

arith_base ->
    "(" expr ")"
    | bool
    | int
    | float
    | string
    | ident
    | function_call

function_call -> ident "(" [ expr { "," expr } ] ")"

type -> "BOOL" | "INT" | "FLOAT" | "STRING" | ident

color ->
    "BLACK"
    | "WHITE"
    | "RED"
    | "ORANGE"
    | "YELLOW"
    | "GREEN"
    | "BLUE"
    | "INDIGO"
    | "VIOLET"

bool -> "TRUE" | "FALSE"

int -> [0-9]+

float -> [0-9]+ "." [0-9]+

string -> "\"" .*? "\""

ident -> [a-zA-Z_][a-zA-Z0-9_]*

nl -> ( "\n" | "\r\n" )+
```

### Reference
https://github.com/AZHenley/teenytinycompiler
