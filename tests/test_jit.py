from cinder import jit


def identity(x):
    return x


def test_jit():
    _, foo = jit.compile(identity)
    assert foo(100) == 100
