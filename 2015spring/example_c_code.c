typedef struct foobar {
    int f;
    int b;
    struct foobar * fb;
} foobar;
int q[100];
foobar w[100];
int z;
int foo(int a, int b) {
    int x;
    int y;
    return (x+y);
};
int bar(int c, int d) {
    int y;
    int z;
};
test() {};
typedef int strange_unit;
strange_unit bob;
char a;
unsigned char b;
signed char c;
short d;
unsigned short e;
signed short f;
long g;
unsigned long h;
signed long i;
typedef struct zoo {
char a;
unsigned char b;
signed char c;
short d;
unsigned short e;
signed short f;
long g;
unsigned long h;
signed long i;
} zoo;

class Test {
	void foo(int);
	void foo2();
	int i;
};

void Test::foo() {
return;
};

void Testing() {
    class Test * t;
    t = new Test;
    t->foo2();
    t->foo(5);
};

class Test2:Test {
	void foo2();
	void bar();
	int j;
};

