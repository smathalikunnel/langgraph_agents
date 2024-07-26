class A:
    def do_something(self):
        print("Method Defined In: A")


class B(A):
    def do_something(self):
        print("Method Defined In: B")


class C(A):
    def do_something(self):
        print("Method Defined In: C")


class D(B, C):
    pass


d = D()
d.do_something()  # Output: Method Defined In: B