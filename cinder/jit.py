import ctypes
import types as pytypes

from cinder import (
    bytecode,
    ir,
    JitFunction,
)
from ctypes import pythonapi
from ctypes.util import find_library
from peachpy import *
from peachpy.x86_64 import *
from peachpy.x86_64.registers import rsp
from typing import Tuple

_cinder_name = find_library('_cinder')
_cinder = ctypes.CDLL(_cinder_name)
_cinder.get_call_function_address.restype = ctypes.c_void_p


dllib = ctypes.CDLL(None)
dllib.dlsym.restype = ctypes.c_void_p


def pysym(name):
    """Look up a symbol exposed by CPython"""
    return dllib.dlsym(pythonapi._handle, name)


class Runtime:
    PY_SYMBOLS = (
        '_PyDict_LoadGlobal',
        'PyObject_GetAttr',
        'PyObject_IsTrue',
        'PyObject_SetAttr',
    )

# Initialize pointers from libpython
for name in Runtime.PY_SYMBOLS:
    symbol = pysym(name.encode())
    setattr(Runtime, name, symbol)

# Initialize pointers from cinder
Runtime.call_function = _cinder.get_call_function_address()

# Calling convention and stack-frame layout for jit-compiled functions
#
# Jit functions take a single argument, a PyObject**, that points to the beginning of
# the argument list. This matches CPythons fast calling convention.
#
# The following registers are initialized in the function prologue and must remain fixed
# for the lifetime of the function:
#
#   r12 - Holds a pointer to the function's arguments
#   rbp - Holds a pointer to the beginning of the local variable storage
#
# Immediate after the function prologue completes, the stack looks like
#
# +------------------------------------+ Frame (fixed size)
# | Saved r12                          |
# | Saved rbp                          |
# |+----------------+ Local variables  | <--- rbp
# ||Local 0         |                  |
# ||...             |                  |
# ||Local N         |                  |
# |+----------------+                  |
# +------------------------------------+
# .                                    .
# .  Value stack      | Growth         .
# .  (the stack)      v                .
# .                                    .
# +....................................+

# Caller saved registers: r10, r11, parameter passing regs (rdi, rsi, rdx, rcx, r8, r9)
# Callee saved registers: rbx, rbp, rsp (implicitly), r12 - r15,

def prologue(args, num_locals):
    LOAD.ARGUMENT(r12, args)
    MOV(rbp, rsp)
    SUB(rsp, num_locals * 8)


def epilogue():
    MOV(rsp, rbp)


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


def duplicate_and_reverse(num_items):
    """Duplicate the top <num_items> items on the stack, but in reverse order"""
    reverse_args = Label()
    reverse_done = Label()
    MOV(rdi, rsp)
    LEA(rsi, [rdi + num_items * 8])
    LABEL(reverse_args)
    CMP(rdi, rsi)
    JE(reverse_done)
    MOV(rdx, [rdi])
    PUSH(rdx)
    LEA(rdi, [rdi + 8])
    JMP(reverse_args)
    LABEL(reverse_done)


def call_function(num_args):
    """Perform the equivalent of CALL_FUNCTION"""
    # This is heinous. CPython's stack grows in the opposite direction of the
    # machine's stack so we are forced to reverse the order of the arguments
    # and function on the stack before calling into the runtime. Obviously we
    # need to fix this.
    num_items = num_args + 1
    duplicate_and_reverse(num_items)
    # call_function takes a PyObject*** to the TOS
    LEA(rdi, [rsp + num_items * 8])
    PUSH(rdi)
    # Call call_function
    MOV(rdi, rsp)
    MOV(rsi, num_args)
    MOV(rdx, 0)
    MOV(rcx, Runtime.call_function)
    CALL(rcx)
    # call_function takes care of decrementing refcounts on the arguments and
    # function.
    #
    # pop the temporary stack pointer, the arguments, and the function (and their duplicates)
    # from the stack
    num_items = 1 + num_items * 2
    LEA(rsp, [rsp + num_items * 8])
    PUSH(rax)


def load_const(code, index):
    """Load a reference to const onto the stack.

    NB: This embeds a pointer to the constant into the jitted code. This is potentially invalid
    if the code object for the function is re-assigned.

    Args:
        code: The code object
        index: An index into the constants tuple of the code object
    """
    MOV(rdi, id(code.co_consts[index]))
    incref(rdi, rsi)
    PUSH(rdi)


def load_arg(index):
    # TODO(mpage): Error handling
    MOV(rdi, [r12 + index * 8])
    incref(rdi, rsi)
    PUSH(rdi)


def store_arg(index):
    POP(rdi)
    MOV([r12 + index * 8], rdi)


def load_local(index):
    # TODO(mpage): Error handling
    MOV(rdi, [rbp - (index + 1) * 8])
    incref(rdi, rsi)
    PUSH(rdi)


def store_local(index):
    POP(rdi)
    MOV([rbp - (index + 1) * 8], rdi)


def pop_top():
    """Discard the top-most element on the stack"""
    POP(rdi)
    decref(rdi, rsi)


def load_attr(name):
    """Call PyObject_GetAttr(<tos>, name) and push the result.

    NB: This embeds a pointer to the constant into the jitted code. This is potentially invalid
    if the code object for the function is re-assigned.

    Args:
        name: The name being looked up. This should be a PyObject* retrieved from the
            co_names tuple of the code object that is being jit compiled.
    """
    POP(rdi)
    MOV(rsi, id(name))
    MOV(rdx, Runtime.PyObject_GetAttr)
    PUSH(rdi)
    CALL(rdx)
    # TODO(mpage): Error handling
    POP(rdi)
    decref(rdi, rsi)
    PUSH(rax)


def store_attr(name):
    """Call PyObject_SetAttr(<tos>, <name>, <tos + 1>)

    NB: This embeds a pointer to the constant into the jitted code. This is potentially invalid
    if the code object for the function is re-assigned.

    Args:
        name: The name of the attribute being set. This should be a PyObject* retrieved from
            the co_names tuple of the code object being compiled.
    """
    MOV(rdi, [rsp])
    MOV(rdx, [rsp + 8])
    MOV(rsi, id(name))
    MOV(rcx, Runtime.PyObject_SetAttr)
    CALL(rcx)
    # TODO(mpage): Error handling
    # Dispose of owner and value
    POP(rdi)
    decref(rdi, rsi)
    POP(rdi)
    decref(rdi, rsi)


def load_global(globals, builtins, name):
    """Implement global lookup for functions whose globals and builtins are dictionaries.

    NB: This directly embeds pointers to globals and builtins, so the jitted code will need
    to be invalidated if either change

    Args:
        name: The name of the global being looked up
        globals: The globals dictionary
        builtins: The builtins dictionary
    """
    MOV(rdi, id(globals))
    MOV(rsi, id(builtins))
    MOV(rdx, id(name))
    MOV(rcx, Runtime._PyDict_LoadGlobal)
    CALL(rcx)
    # TODO(mpage): Error handling
    incref(rax, rdi)
    PUSH(rax)


def unary_not():
    # TODO(mpage): Error handling around call to PyObject_IsTrue
    false_label = Label()
    done_label = Label()
    POP(r13)
    MOV(rdi, r13)
    MOV(rdx, Runtime.PyObject_IsTrue)
    CALL(rdx)
    decref(r13, r14)
    CMP(rax, 0)
    JNZ(false_label)
    MOV(r13, id(True))
    incref(r13, r14)
    PUSH(r13)
    JMP(done_label)
    LABEL(false_label)
    MOV(r13, id(False))
    incref(r13, r14)
    PUSH(r13)
    LABEL(done_label)


def conditional_branch(instr, labels):
    # TODO(mpage): Error handling
    MOV(r14, id(True))
    MOV(r15, id(False))
    true, false = r14, r15
    fall_through = Label()
    do_branch = Label()
    if instr.pop_before_eval:
        POP(r13)
        if instr.jump_when_true:
            # TOS == Py_False?
            CMP(r13, false)
            JE(fall_through)
            # TOS == Py_True?
            CMP(r13, true)
            JE(do_branch)
            # Call PyObject_IsTrue(TOS)
            MOV(rdi, r13)
            MOV(rsi, Runtime.PyObject_IsTrue)
            CALL(rsi)
            CMP(rax, 0)
            JE(fall_through)
            # TOS is truthy, do the branch
            LABEL(do_branch)
            decref(r13, r14)
            JMP(labels[instr.true_branch])
            # TOS is falsey, fall through
            LABEL(fall_through)
            decref(r13, r14)
        else:
            # TOS == Py_True?
            CMP(r13, true)
            JE(fall_through)
            # TOS == Py_False?
            CMP(r13, false)
            JE(do_branch)
            # Call PyObject_IsTrue(TOS)
            MOV(rdi, r13)
            MOV(rsi, Runtime.PyObject_IsTrue)
            CALL(rsi)
            CMP(rax, 0)
            JG(fall_through)
            # TOS is truthy, do the branch
            LABEL(do_branch)
            decref(r13, r14)
            JMP(labels[instr.false_branch])
            # TOS is falsey, fall through
            LABEL(fall_through)
            decref(r13, r14)
    else:
        MOV(r13, [rsp])
        if instr.jump_when_true:
            # TOS == Py_False?
            CMP(r13, false)
            JE(fall_through)
            CMP(r13, true)
            JE(labels[instr.true_branch])
            # Call PyObject_IsTrue(TOS)
            MOV(rdi, r13)
            MOV(rsi, Runtime.PyObject_IsTrue)
            CALL(rsi)
            # TOS is truthy, jump
            CMP(rax, 0)
            JG(labels[instr.true_branch])
            # TOS is falsey, pop and fall through
            LABEL(fall_through)
            decref(r13, r14)
            ADD(rsp, 8)
        else:
            # TOS == Py_True?
            CMP(r13, true)
            JE(fall_through)
            CMP(r13, false)
            # TOS is false, jump
            JE(labels[instr.false_branch])
            # Call PyObject_IsTrue(TOS)
            MOV(rdi, r13)
            MOV(rsi, Runtime.PyObject_IsTrue)
            CALL(rsi)
            # TOS is falsey, jump
            CMP(rax, 0)
            JE(labels[instr.false_branch])
            # TOS is truthy, pop and fall through
            LABEL(fall_through)
            decref(r13, r14)
            ADD(rsp, 8)


def return_value():
    # Top of stack contains PyObject*
    # TODO(mpage): Decref any remaining items on the stack
    POP(rax)
    epilogue()
    RETURN(rax)


_SUPPORTED_INSTRUCTIONS = {
    ir.Call,
    ir.ConditionalBranch,
    ir.LoadAttr,
    ir.LoadGlobal,
    ir.Load,
    ir.ReturnValue,
    ir.Store,
    ir.StoreAttr,
    ir.UnaryOperation,
}


def compile(func):
    code = func.__code__
    cfg = bytecode.disassemble(code.co_code)
    blocks = list(cfg)
    for block in blocks:
        for instr in block.instructions:
            if instr.__class__ not in _SUPPORTED_INSTRUCTIONS:
                raise ValueError(f'Cannot compile {instr}')
    args = Argument(ptr())
    with Function(func.__name__, (args,), uint64_t) as ppfunc:
        num_locals = code.co_nlocals - code.co_argcount
        prologue(args, num_locals)
        labels = {block.label: Label() for block in blocks}
        for block in blocks:
            LABEL(labels[block.label])
            for instr in block.instructions:
                if isinstance(instr, ir.Load):
                    if instr.pool == ir.VarPool.LOCALS:
                        index = instr.index
                        if index < code.co_argcount:
                            load_arg(index)
                        else:
                            load_local(index - code.co_argcount)
                    elif instr.pool == ir.VarPool.CONSTANTS:
                        load_const(code, instr.index)
                    else:
                        raise ValueError('Can only load arguments or constants')
                elif isinstance(instr, ir.Store):
                    if instr.index < code.co_argcount:
                        store_arg(instr.index)
                    else:
                        print("Store local")
                        store_local(instr.index - code.co_argcount)
                elif isinstance(instr, ir.LoadAttr):
                    load_attr(code.co_names[instr.index])
                elif isinstance(instr, ir.ReturnValue):
                    return_value()
                elif isinstance(instr, ir.UnaryOperation):
                    if instr.kind != ir.UnaryOperationKind.NOT:
                        raise ValueError('Can only encode unary not')
                    unary_not()
                elif isinstance(instr, ir.ConditionalBranch):
                    conditional_branch(instr, labels)
                elif isinstance(instr, ir.StoreAttr):
                    store_attr(code.co_names[instr.index])
                elif isinstance(instr, ir.LoadGlobal):
                    globals = getattr(func, '__globals__', None)
                    if globals.__class__ is not dict:
                        raise ValueError('Cannot compile functions whose globals are not a dictionary')
                    builtins = globals.get('__builtins__', None)
                    if isinstance(builtins, dict):
                        pass
                    elif isinstance(builtins, pytypes.ModuleType):
                        builtins = maybe_builtins.__dict__
                    else:
                        raise ValueError(f'Cannot compile functions whose builtins are not a module or dictionary')
                    load_global(globals, builtins, code.co_names[instr.index])
                elif isinstance(instr, ir.Call):
                    call_function(instr.num_args)
    encoded = ppfunc.finalize(abi.detect()).encode()
    print(encoded.format_code())
    loaded = encoded.load()
    return JitFunction(loaded, loaded.loader.code_address)
