FUNCTION main() AS INT
    LET a AS INT = 1
    IF a == 1 THEN
        PRINT "a is 1"
    ELIF a == 2 THEN
        PRINT "a is 2"
    ELSE
        PRINT "a is neither 1 nor 2"
    ENDIF

    LET b AS INT = 2
    IF b == 1 THEN
        PRINT "b is 1"
    ELIF b == 2 THEN
        PRINT "b is 2"
    ELSE
        PRINT "b is neither 1 nor 2"
    ENDIF

    LET c AS INT = 3
    IF c == 1 THEN
        PRINT "c is 1"
    ELIF c == 2 THEN
        PRINT "c is 2"
    ELSE
        PRINT "c is neither 1 nor 2"
    ENDIF
ENDFUNCTION