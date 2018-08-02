import ctypes

from ctypes import pythonapi
from peachpy import *
from peachpy.x86_64 import *
from peachpy.x86_64.registers import rsp

dllib = ctypes.CDLL(None)
dllib.dlsym.restype = ctypes.c_void_p

# Caller saved registers: r10, r11, parameter passing regs (rdi, rsi, rdx, rcx, r8, r9)
# Callee saved registers: rbx, rbp, rsp (implicitly), r12 - r15,


def pysym(name):
    return dllib.dlsym(pythonapi._handle, name)


def incref(pyobj, temp, amount=1):
    """Increment the reference count of the PyObject* stored in pyobj.

    Args:
        pyobj: A register storing the PyObject* being incremented
        temp: A temporary register
        amount: How much to increment the reference count by
    """
    MOV(temp, [pyobj])
    LEA(temp, [temp + amount])
    MOV([pyobj], temp)


def decref(pyobj, temp, amount=1):
    """Decrement the reference count of the PyObject* stored in pyobj.

    Args:
        pyobj: A register storing the PyObject* being incremented
        temp: A temporary register
        amount: How much to decrement the reference count by
    """
    MOV(temp, [pyobj])
    LEA(temp, [temp - amount])
    MOV([pyobj], temp)


def load_attr(name):
    POP(rdi)
    MOV(rsi, id(name))
    MOV(rdx, pysym(b'PyObject_GetAttr'))
    PUSH(rdi)
    CALL(rdx)
    POP(rdi)
    decref(rdi, rsi)
    PUSH(rax)


def return_value():
    # Top of stack contains PyObject*
    POP(rax)
    decref(rax, rdx)
    RETURN(rax)


def make_adder():
    left = Argument(ptr())
    right = Argument(ptr())
    with Function("test_add", (left, right), uint64_t) as func:
        LOAD.ARGUMENT(rdi, left)
        LOAD.ARGUMENT(rsi, right)
        # Yuck - how do we handle rip relative addressing?
        MOV(rdx, pysym(b'PyNumber_Add'))
        CALL(rdx)
        RETURN(rax)
    encoded_function = func.finalize(abi.detect()).encode()
    return encoded_function.load()


class JitFunc:
    def __init__(self, func, sig):
        self.loaded = func.finalize(abi.detect()).encode().load()
        typ = ctypes.CFUNCTYPE(*sig)
        self.entry = typ(self.loaded.loader.code_address)
        self.address = self.loaded.loader.code_address


def make_identity_func():
    obj = Argument(ptr())
    with Function("identity", (obj,), uint64_t) as func:
        LOAD.ARGUMENT(rdi, obj)
        MOV(rax, rdi)
        RETURN(rax)
    return JitFunc(func, (ctypes.py_object, ctypes.py_object))


def make_getattr_func(name):
    obj = Argument(ptr())
    with Function("getattr", (obj,), uint64_t) as func:
        LOAD.ARGUMENT(rdi, obj)
        incref(rdi, rax)
        PUSH(rdi)
        load_attr(name)
        return_value()
    abi_func = func.finalize(abi.detect())
    encoded_function = abi_func.encode()
    loaded_function = encoded_function.load()
    typ = ctypes.CFUNCTYPE(ctypes.py_object, ctypes.py_object)
    return loaded_function, typ(loaded_function.loader.code_address)


def make_get_refcount():
    obj = Argument(ptr())
    with Function("get_refcount", (obj,), uint64_t) as func:
        LOAD.ARGUMENT(rdi, obj)
        MOV(rax, [rdi])
        LEA(rdx, [rax + 1])
        MOV([rdi], rdx)
        RETURN(rdx)
    abi_func = func.finalize(abi.detect())
    encoded_function = abi_func.encode()
    loaded_function = encoded_function.load()
    typ = ctypes.CFUNCTYPE(ctypes.c_ssize_t, ctypes.py_object)
    return loaded_function, typ(loaded_function.loader.code_address)
