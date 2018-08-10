from cinder.codegen import x64


def identity(x):
    return x


class Foo:
    def __init__(self, bar):
        self.bar = bar


def get_bar(x):
    return x.bar


def set_bar(x, v):
    x.bar = v
    return x


def invert(x):
    return not x


def pop_jump(x, y, z):
    if x:
        return y
    return z


def jump_if_true(x, y):
    return x or y


def jump_if_false(x, y):
    return x and y


def load_const():
    return 100


my_global = 'testing 123'


def load_global():
    return my_global


def call0(f):
    return f()


def call1(f, arg):
    return f(arg)


def call3(f, arg, arg1, arg2):
    return f(arg, arg1, arg2)


def get_third(x, y, z):
    return z


def store_local(x):
    y = x
    z = x
    return y


def while_loop(x, y):
    while x:
        x = y
    return y


def jump_forward(x, y, z):
    if x:
        if y:
            return 1
    else:
        return 2


def cmp_is(x, y):
    return x is y


def test_load_fast_and_return_value():
    foo = x64.compile(identity)
    assert foo(100) == 100


def test_load_attr():
    x = x64.compile(get_bar)
    foo = Foo('testing 123')
    assert x(foo) == 'testing 123'


def test_invert():
    x64_invert = x64.compile(invert)
    assert x64_invert(False) == True
    assert x64_invert(True) == False
    assert x64_invert(1) == False


def test_pop_jump():
    test = x64.compile(pop_jump)
    assert test(True, 1, 2) == 1
    assert test(False, 1, 2) == 2
    assert test(1, 'foo', 'bar') == 'foo'
    assert test(0, 'foo', 'bar') == 'bar'


def test_jump_if_true():
    test = x64.compile(jump_if_true)
    assert test(True, False) == True
    assert test(False, 1) == 1
    assert test(0, 'foo') == 'foo'
    assert test(1, 'bar') == 1


def test_jump_if_false():
    test = x64.compile(jump_if_false)
    assert test(False, 1) == False
    assert test(True, 1) == 1
    assert test(0, 'foo') == 0
    assert test(1, 'bar') == 'bar'


def test_load_const():
    test = x64.compile(load_const)
    assert test() == 100


def test_store_attr():
    test = x64.compile(set_bar)
    foo = Foo(None)
    test(foo, 'testing 123')
    assert foo.bar == 'testing 123'


def test_load_global():
    test = x64.compile(load_global)
    assert test() == 'testing 123'


def test_call():
    test_call0 = x64.compile(call0)
    assert test_call0(load_const) == 100

    test_call1 = x64.compile(call1)
    assert test_call1(identity, 'testing') == 'testing'

    test_call3 = x64.compile(call3)
    assert test_call3(get_third, 1, 2, 3) == 3


def test_store():
    test = x64.compile(store_local)
    assert test(10) == 10


def test_while_loop():
    test = x64.compile(while_loop)
    assert test(True, 0) == 0


def test_jump_forward():
    test = x64.compile(jump_forward)
    assert test(True, True) == 1
    assert test(True, False) == None
    assert test(False, False) == 2


def test_is():
    test = x64.compile(cmp_is)
    assert test(1, 1) == True
    assert test(1, 2) == False


def test_is_not():
    def f(x, y):
        return x is not y

    test = x64.compile(f)
    assert test(1, 1) == False
    assert test(1, 2) == True
