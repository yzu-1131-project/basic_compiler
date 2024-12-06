FUNCTION func1(num AS INT) AS VOID
	IF num <= 0 THEN
        RETURN
	ELSE
        PRINT num
        return func1(num - 1)
    ENDIF
ENDFUNCTION

FUNCTION main() AS INT
    func1(10)
ENDFUNCTION
