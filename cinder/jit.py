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
    """Increment the reference count of a PyObject.

    Args:
        pyobj: A register storing a pointer to the PyObject whose refcount is being incremented
        temp: A temporary register
        amount: How much to increment the reference count by
    """
    MOV(temp, [pyobj])
    LEA(temp, [temp + amount])
    MOV([pyobj], temp)


def decref(pyobj, temp, amount=1):
    """Decrement the reference count of a PyObject.

    Args:
        pyobj: A register storing a pointer to the PyObject whose refcount is being deceremented.
        temp: A temporary register
        amount: How much to decrement the reference count by
    """
    MOV(temp, [pyobj])
    LEA(temp, [temp - amount])
    MOV([pyobj], temp)


def load_fast(args, index):
    MOV(r12, [args + index * 8])
    incref(r12, rsi)
    PUSH(r12)


def load_attr(name):
    """Call PyObject_GetAttr(<tos>, name) and push the result.

    Args:
        name: The name being looked up. This should be an ordinary Python object retrieved from the
            co_names tuple of the code object that is being jit compiled.
    """
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
    RETURN(rax)


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
        load_fast(rdi, 0)
        return_value()
    return JitFunc(func, (ctypes.py_object, ctypes.py_object))
