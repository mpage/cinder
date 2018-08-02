import ctypes

import cinder

from cinder import jit


# def test_adder():
#     func = jit.make_adder()
#     typ = ctypes.CFUNCTYPE(ctypes.py_object, ctypes.py_object, ctypes.py_object)
#     adder = typ(func.loader.code_address)
#     result = adder(50, 50)
#     assert result == 100


# def test_jit():
#     identity = jit.make_identity_func()
#     assert identity.entry(123) is 123


# class Foo:
#     def __init__(self, x):
#         self.x = x


# def test_loadattr():
#     foo = Foo('hi matt')
#     f, my_getattr = jit.make_getattr_func('x')
#     assert my_getattr(foo), 'hi matt'

# def test_get_refcount():
#     func, get_refcount = jit.make_get_refcount()
#     value = 123456789
#     value_address = id(value)
#     print("==> Initial")
#     ob_refcnt = ctypes.c_long.from_address(value_address)
#     print(ob_refcnt)
#     v2 = value
#     print("==> After new reference is created")
#     ob_refcnt = ctypes.c_long.from_address(value_address)
#     print(ob_refcnt)
#     print("==> After call to get_refcount")
#     print(get_refcount(value))
#     ob_refcnt = ctypes.c_long.from_address(value_address)
#     print(ob_refcnt)


def test_jit():
    foo = cinder.JitFunction(100)
