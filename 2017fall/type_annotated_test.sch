(defun (single) fib (((single) x)) (cond
	(< x 3) 1
	else (+ (fib (- x 1)) (fib (- x 2)))
))
(fib 1)
(fib 2)
(fib 3)
(fib 4)
(fib 5)
(defun (single) fact (((single) x)) (cond
	(< x 1) 1
	else (* x (fact (- x 1)))
))
(fact 1)
(fact 2)
(fact 3)
(fact 4)
(fact 5)
(defun (single) sumfromto (((single) x) ((single) y)) (cond
        (< x y) (+ x (sumfromto (+ x 1) y))
        else x
))
(sumfromto 1 1)
(sumfromto 1 2)
(sumfromto 2 4)
(sumfromto 4 8)
(sumfromto 1 10)
