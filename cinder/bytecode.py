import dis
import enum

from typing import (
    Dict,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Type,
)

from cinder import ir


class Opcode(enum.IntEnum):
    POP_TOP                      = 1
    ROT_TWO                      = 2
    ROT_THREE                    = 3
    DUP_TOP                      = 4
    DUP_TOP_TWO                  = 5
    NOP                          = 9
    UNARY_POSITIVE               = 10
    UNARY_NEGATIVE               = 11
    UNARY_NOT                    = 12
    UNARY_INVERT                 = 15
    BINARY_MATRIX_MULTIPLY       = 16
    INPLACE_MATRIX_MULTIPLY      = 17
    BINARY_POWER                 = 19
    BINARY_MULTIPLY              = 20
    BINARY_MODULO                = 22
    BINARY_ADD                   = 23
    BINARY_SUBTRACT              = 24
    BINARY_SUBSCR                = 25
    BINARY_FLOOR_DIVIDE          = 26
    BINARY_TRUE_DIVIDE           = 27
    INPLACE_FLOOR_DIVIDE         = 28
    INPLACE_TRUE_DIVIDE          = 29
    GET_AITER                    = 50
    GET_ANEXT                    = 51
    BEFORE_ASYNC_WITH            = 52
    INPLACE_ADD                  = 55
    INPLACE_SUBTRACT             = 56
    INPLACE_MULTIPLY             = 57
    INPLACE_MODULO               = 59
    STORE_SUBSCR                 = 60
    DELETE_SUBSCR                = 61
    BINARY_LSHIFT                = 62
    BINARY_RSHIFT                = 63
    BINARY_AND                   = 64
    BINARY_XOR                   = 65
    BINARY_OR                    = 66
    INPLACE_POWER                = 67
    GET_ITER                     = 68
    GET_YIELD_FROM_ITER          = 69
    PRINT_EXPR                   = 70
    LOAD_BUILD_CLASS             = 71
    YIELD_FROM                   = 72
    GET_AWAITABLE                = 73
    INPLACE_LSHIFT               = 75
    INPLACE_RSHIFT               = 76
    INPLACE_AND                  = 77
    INPLACE_XOR                  = 78
    INPLACE_OR                   = 79
    BREAK_LOOP                   = 80
    WITH_CLEANUP_START           = 81
    WITH_CLEANUP_FINISH          = 82
    RETURN_VALUE                 = 83
    IMPORT_STAR                  = 84
    SETUP_ANNOTATIONS            = 85
    YIELD_VALUE                  = 86
    POP_BLOCK                    = 87
    END_FINALLY                  = 88
    POP_EXCEPT                   = 89
    STORE_NAME                   = 90      # Index in name list
    HAVE_ARGUMENT                = 90      # Pseudo-opcode. Opcodes > than this have an arg.
    DELETE_NAME                  = 91      # ""
    UNPACK_SEQUENCE              = 92      # Number of tuple items
    FOR_ITER                     = 93
    UNPACK_EX                    = 94
    STORE_ATTR                   = 95      # Index in name list
    DELETE_ATTR                  = 96      # ""
    STORE_GLOBAL                 = 97      # ""
    DELETE_GLOBAL                = 98      # ""
    LOAD_CONST                   = 100     # Index in const list
    LOAD_NAME                    = 101     # Index in name list
    BUILD_TUPLE                  = 102     # Number of tuple items
    BUILD_LIST                   = 103     # Number of list items
    BUILD_SET                    = 104     # Number of set items
    BUILD_MAP                    = 105     # Number of dict entries (upto 255
    LOAD_ATTR                    = 106     # Index in name list
    COMPARE_OP                   = 107     # Comparison operator
    IMPORT_NAME                  = 108     # Index in name list
    IMPORT_FROM                  = 109     # Index in name list
    JUMP_FORWARD                 = 110     # Number of bytes to skip
    JUMP_IF_FALSE_OR_POP         = 111     # Target byte offset from beginning of code
    JUMP_IF_TRUE_OR_POP          = 112     # ""
    JUMP_ABSOLUTE                = 113     # ""
    POP_JUMP_IF_FALSE            = 114     # ""
    POP_JUMP_IF_TRUE             = 115     # ""
    LOAD_GLOBAL                  = 116     # Index in name list
    CONTINUE_LOOP                = 119     # Target address
    SETUP_LOOP                   = 120     # Distance to target address
    SETUP_EXCEPT                 = 121     # ""
    SETUP_FINALLY                = 122     # ""
    LOAD_FAST                    = 124     # Local variable number
    STORE_FAST                   = 125     # Local variable number
    DELETE_FAST                  = 126     # Local variable number
    STORE_ANNOTATION             = 127     # Index in name list
    RAISE_VARARGS                = 130     # Number of raise arguments (1, 2, or 3
    CALL_FUNCTION                = 131     # #args
    MAKE_FUNCTION                = 132     # Flags
    BUILD_SLICE                  = 133     # Number of items
    LOAD_CLOSURE                 = 135
    LOAD_DEREF                   = 136
    STORE_DEREF                  = 137
    DELETE_DEREF                 = 138
    CALL_FUNCTION_KW             = 141     # #args + #kwargs
    CALL_FUNCTION_EX             = 142     # Flags
    SETUP_WITH                   = 143
    LIST_APPEND                  = 145
    SET_ADD                      = 146
    MAP_ADD                      = 147
    LOAD_CLASSDEREF              = 148
    EXTENDED_ARG                 = 144
    BUILD_LIST_UNPACK            = 149
    BUILD_MAP_UNPACK             = 150
    BUILD_MAP_UNPACK_WITH_CALL   = 151
    BUILD_TUPLE_UNPACK           = 152
    BUILD_SET_UNPACK             = 153
    SETUP_ASYNC_WITH             = 154
    FORMAT_VALUE                 = 155
    BUILD_CONST_KEY_MAP          = 156
    BUILD_STRING                 = 157
    BUILD_TUPLE_UNPACK_WITH_CALL = 158


# TODO(mpage): Flesh this out
DIRECT_BRANCH_OPCODES = {
    Opcode.JUMP_ABSOLUTE,
    Opcode.JUMP_FORWARD,
    Opcode.RETURN_VALUE,
}

# TODO(mpage): Flesh this out
CONDITIONAL_BRANCH_OPCODES = {
    Opcode.FOR_ITER,
    Opcode.JUMP_IF_TRUE_OR_POP,
    Opcode.JUMP_IF_FALSE_OR_POP,
    Opcode.POP_JUMP_IF_FALSE,
    Opcode.POP_JUMP_IF_TRUE,
}


BRANCH_OPCODES = DIRECT_BRANCH_OPCODES | CONDITIONAL_BRANCH_OPCODES


# TODO(mpage): Flesh this out
RELATIVE_BRANCH_OPCODES = {
    Opcode.FOR_ITER,
    Opcode.JUMP_FORWARD,
}


# TODO(mpage): Flesh this out
ABSOLUTE_BRANCH_OPCODES = {
    Opcode.CONTINUE_LOOP,
    Opcode.JUMP_ABSOLUTE,
    Opcode.JUMP_IF_FALSE_OR_POP,
    Opcode.JUMP_IF_TRUE_OR_POP,
    Opcode.POP_JUMP_IF_FALSE,
    Opcode.POP_JUMP_IF_TRUE,
}


INSTRUCTION_SIZE_B = 2


class Instruction(NamedTuple):
    opcode: Opcode
    argument: int


Offset = int


class BytecodeIterator:
    def __init__(self, code: bytes, start: Optional[int] = None, end: Optional[int] = None) -> None:
        self.code = code
        if start is None:
            self.offset = 0
        else:
            self.offset = start
        if end is None:
            self.end = len(code)
        else:
            self.end = end
        self.extended_arg = 0

    def __iter__(self) -> 'BytecodeIterator':
        return self

    def __next__(self) -> Tuple[Offset, Instruction]:
        if self.offset >= self.end:
            raise StopIteration
        opcode = self.code[self.offset]
        arg = -1
        if opcode >= Opcode.HAVE_ARGUMENT:
            arg = self.code[self.offset + 1] | self.extended_arg
            if opcode == Opcode.EXTENDED_ARG:
                self.extended_arg = arg << 8
            else:
                self.extended_arg = 0
        instr = Instruction(Opcode(opcode), arg)
        offset = self.offset
        self.offset += INSTRUCTION_SIZE_B
        return offset, instr


def compute_block_boundaries(code: bytes) -> List[Tuple[int, int]]:
    """Compute the offsets of basic blocks.

    An offset starts a new basic block if:
      - It is the target of a branch
      - It follows a conditional branch

    Returns:
        A list of half open intervals, where each interval contains a
        basic block.
    """
    if len(code) == 0:
        return []
    block_starts = {0}
    last_offset = len(code)
    for offset, instr in BytecodeIterator(code):
        opcode = instr.opcode
        next_instr_offset = offset + INSTRUCTION_SIZE_B
        if opcode in BRANCH_OPCODES and next_instr_offset < last_offset:
            block_starts.add(next_instr_offset)
        if opcode in RELATIVE_BRANCH_OPCODES:
            block_starts.add(next_instr_offset + instr.argument)
        elif opcode in ABSOLUTE_BRANCH_OPCODES:
            block_starts.add(instr.argument)
    sorted_block_starts = sorted(block_starts)
    sorted_block_starts.append(len(code))
    boundaries: List[Tuple[int, int]] = []
    for i in range(0, len(sorted_block_starts) - 1):
        boundaries.append((sorted_block_starts[i], sorted_block_starts[i + 1]))
    return boundaries


_UNIMPLEMENTED = 'UNIMPLEMENTED'


class InstructionDecoder:
    """Lifts bytecode instructions into ir instructions"""

    def __init__(self, labels: Dict[int, ir.Label]) -> None:
        """
        Args:
            labels - Maps bytecode offsets to symbol names. This is used to name
                the jump targets for instructions that branch.
        """
        self.labels = labels

    def decode(self, offset: Offset, instr: Instruction) -> ir.Instruction:
        decoder = self.decoders.get(instr.opcode, None)
        if decoder is None:
            raise ValueError(f'Cannot decode opcode {dis.opname[instr.opcode]}')
        return decoder(self, offset, instr)

    def decode_return(self, offset: Offset, instr: Instruction) -> ir.Instruction:
        return ir.ReturnValue()

    LOAD_POOLS = {
        Opcode.LOAD_CONST: ir.VarPool.CONSTANTS,
        Opcode.LOAD_FAST: ir.VarPool.LOCALS,
    }

    def decode_load(self, offset: Offset, instr: Instruction) -> ir.Instruction:
        return ir.Load(instr.argument, self.LOAD_POOLS[instr.opcode])

    def decode_cond_branch(self, offset: Offset, instr: Instruction) -> ir.Instruction:
        jump_br = self.labels[instr.argument]
        pass_br = self.labels[offset + INSTRUCTION_SIZE_B]
        if instr.opcode == Opcode.JUMP_IF_FALSE_OR_POP:
            return ir.ConditionalBranch(pass_br, jump_br, False, False)
        elif instr.opcode == Opcode.JUMP_IF_TRUE_OR_POP:
            return ir.ConditionalBranch(jump_br, pass_br, False, True)
        elif instr.opcode == Opcode.POP_JUMP_IF_FALSE:
            return ir.ConditionalBranch(pass_br, jump_br, True, False)
        else:
            raise ValueError(f'Cannot decode {dis.opname[instr.opcode]}')

    def decode_load_attr(self, offset: Offset, instr: Instruction) -> ir.Instruction:
        return ir.LoadAttr(instr.argument)

    def decode_unary_operation(self, offset: Offset, instr: Instruction) -> ir.Instruction:
        return ir.UnaryOperation(ir.UnaryOperationKind.NOT)

    def decode_store(self, offset: Offset, instr: Instruction) -> ir.Instruction:
        return ir.Store(instr.argument)

    def decode_branch(self, offset: Offset, instr: Instruction) -> ir.Instruction:
        return ir.Branch(self.labels[instr.argument])

    def decode_jump_forward(self, offset: Offset, instr: Instruction) -> ir.Instruction:
        return ir.Branch(self.labels[offset + INSTRUCTION_SIZE_B + instr.argument])

    def decode_pop_top(self, offset: Offset, instr: Instruction) -> ir.Instruction:
        return ir.PopTop()

    def decode_store_attr(self, offset: Offset, instr: Instruction) -> ir.Instruction:
        return ir.StoreAttr(instr.argument)

    def decode_load_global(self, offset: Offset, instr: Instruction) -> ir.Instruction:
        return ir.LoadGlobal(instr.argument)

    def decode_call(self, offset: Offset, instr: Instruction) -> ir.Instruction:
        return ir.Call(instr.argument)

    COMPARE_PREDICATES = {p.value: p for p in (
        ir.ComparePredicate.IS,
        ir.ComparePredicate.IS_NOT,)
    }

    def decode_compare(self, offset: Offset, instr: Instruction) -> ir.Instruction:
        predicate = self.COMPARE_PREDICATES.get(instr.argument, None)
        if predicate is None:
            name = dis.cmp_op[instr.argument]
            raise ValueError(f"Cannot decode compare predicate {name}")
        return ir.Compare(predicate)

    BINARY_OPERATORS = {
        Opcode.BINARY_AND: ir.BinaryOperator.AND,
    }

    def decode_binary_op(self, offset: Offset, instr: Instruction) -> ir.Instruction:
        operator = self.BINARY_OPERATORS.get(instr.opcode, None)
        if operator is None:
            raise ValueError(f'Cannot decode {dis.opname[instr.opcode]}')
        return ir.BinaryOperation(operator)

    decoders = {
        Opcode.CALL_FUNCTION: decode_call,
        Opcode.BINARY_AND: decode_binary_op,
        Opcode.COMPARE_OP: decode_compare,
        Opcode.JUMP_ABSOLUTE: decode_branch,
        Opcode.JUMP_FORWARD: decode_jump_forward,
        Opcode.JUMP_IF_TRUE_OR_POP: decode_cond_branch,
        Opcode.JUMP_IF_FALSE_OR_POP: decode_cond_branch,
        Opcode.LOAD_ATTR: decode_load_attr,
        Opcode.LOAD_CONST: decode_load,
        Opcode.LOAD_FAST: decode_load,
        Opcode.LOAD_GLOBAL: decode_load_global,
        Opcode.POP_JUMP_IF_FALSE: decode_cond_branch,
        Opcode.POP_TOP: decode_pop_top,
        Opcode.RETURN_VALUE: decode_return,
        Opcode.STORE_ATTR: decode_store_attr,
        Opcode.STORE_FAST: decode_store,
        Opcode.UNARY_NOT: decode_unary_operation,
    }


def is_block_setup(code: bytes, start: int, end: int) -> bool:
    return ((start + INSTRUCTION_SIZE_B == end) and
            (code[start] == Opcode.SETUP_LOOP))


def disassemble(code: bytes) -> ir.ControlFlowGraph:
    """Build a CFG from the bytecode in the supplied code object

    Raises:
        ValueError: If the bytecode contains opcodes that we do not
            yet understand.
    """
    # Label blocks
    block_boundaries = compute_block_boundaries(code)
    labels = {}
    for i, interval in enumerate(block_boundaries):
        labels[interval[0]] = f'bb{i}'
    # Construct blocks
    blocks = []
    decoder = InstructionDecoder(labels)
    for start, end in block_boundaries:
        if is_block_setup(code, start, end):
            # Skip basic blocks that only set up the block stack
            continue
        is_loop_header = False
        is_loop_footer = False
        ir_instrs = []
        for offset, instr in BytecodeIterator(code, start, end):
            if instr.opcode == Opcode.POP_BLOCK:
                is_loop_footer = True
            elif instr.opcode == Opcode.SETUP_LOOP:
                pass
            else:
                if start >= 2 and code[start - 2] == Opcode.SETUP_LOOP:
                    is_loop_header = True
                ir_instrs.append(decoder.decode(offset, instr))
        blocks.append(ir.BasicBlock(
            labels[start], ir_instrs, is_loop_header, is_loop_footer))
    return ir.build_initial_cfg(blocks)
