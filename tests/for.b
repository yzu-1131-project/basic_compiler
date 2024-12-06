FUNCTION main() AS INT
    PRINT "FOR loop"
    FOR i = 1 TO 3
        PRINT i
    ENDFOR

    PRINT "WHILE loop"
    LET j AS INT = 3
    WHILE j <= 5
        PRINT j
        j = j + 1
    ENDWHILE

    PRINT "DO WHILE loop"
    LET k AS INT = 6
    DO
        PRINT k
        k = k + 1
    ENDDO WHILE k < 10
ENDFUNCTION
