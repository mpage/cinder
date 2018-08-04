from cinder import jit


def identity(x):
    return x


class Foo:
    def __init__(self, bar):
        self.bar = bar


def get_bar(x):
    return x.bar


def invert(x):
    return not x


def cond_branch(x, y, z):
    if x:
        return y
    return z


def test_load_fast_and_return_value():
    foo = jit.compile(identity)
    assert foo(100) == 100


def test_load_attr():
    x = jit.compile(get_bar)
    foo = Foo('testing 123')
    assert x(foo) == 'testing 123'


def test_invert():
    jit_invert = jit.compile(invert)
    assert jit_invert(False) == True
    assert jit_invert(True) == False
    assert jit_invert(1) == False


def test_cond_branch():
    test = jit.compile(cond_branch)
    assert test(True, 1, 2) == 1
    assert test(False, 1, 2) == 2
    assert test(1, 'foo', 'bar') == 'foo'
    assert test(0, 'foo', 'bar') == 'bar'
