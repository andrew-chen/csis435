(defun fib (x) (cond
	(< x 3) 1
	else (+ (fib (- x 1)) (fib (- x 2)))
))
(fib 1)
(fib 2)
(fib 3)
(fib 4)
(fib 5)
(defun fact (x) (cond
	(< x 1) 1
	else (* x (fact (- x 1)))
))
(fact 1)
(fact 2)
(fact 3)
(fact 4)
(fact 5)
