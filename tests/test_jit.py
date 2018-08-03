import cinder
import cinder.jit


def test_jit():
    identity = cinder.jit.make_identity_func()
    foo = cinder.JitFunction(identity.address)
    assert foo(100) == 100
