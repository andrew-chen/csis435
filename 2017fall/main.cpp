extern "C" {
	double fib(double);
	double fact(double);
};
#include <iostream>
int main() {
	std::cout << fib(5.0) << std::endl;
	std::cout << fact(5.0) << std::endl;
	return 0;
};
