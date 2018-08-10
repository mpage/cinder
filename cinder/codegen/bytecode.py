from cinder import ir
from cinder.bytecode import (
    INSTRUCTION_SIZE_B,
    Instruction,
    Opcode
)
from typing import Dict


class InstructionEncoder:
    """Lowers ir instructions into bytecode instructions"""

    def __init__(self, offsets: Dict[ir.Label, int]) -> None:
        """
        Args:
            offsets - Maps symbolic names into bytecode offsets. This is used to name
                the jump targets for instructions that branch.
        """
        self.offsets = offsets

    def encode(self, instr: ir.Instruction, offset: int) -> Instruction:
        if isinstance(instr, ir.ReturnValue):
            return self.encode_return(instr)
        elif isinstance(instr, ir.ConditionalBranch):
            return self.encode_cond_branch(instr)
        elif isinstance(instr, ir.Load):
            return self.encode_load(instr)
        elif isinstance(instr, ir.LoadAttr):
            return Instruction(Opcode.LOAD_ATTR, instr.index)
        elif isinstance(instr, ir.UnaryOperation) and instr.kind == ir.UnaryOperationKind.NOT:
            return Instruction(Opcode.UNARY_NOT, 0)
        elif isinstance(instr, ir.Store):
            return Instruction(Opcode.STORE_FAST, instr.index)
        elif isinstance(instr, ir.Branch):
            dest_offset = self.offsets[instr.target]
            delta = dest_offset - (offset + INSTRUCTION_SIZE_B)
            if delta >= 0 and delta < 256:
                return Instruction(Opcode.JUMP_FORWARD, delta)
            return Instruction(Opcode.JUMP_ABSOLUTE, self.offsets[instr.target])
        elif isinstance(instr, ir.PopTop):
            return Instruction(Opcode.POP_TOP, 0)
        elif isinstance(instr, ir.StoreAttr):
            return Instruction(Opcode.STORE_ATTR, instr.index)
        elif isinstance(instr, ir.LoadGlobal):
            return Instruction(Opcode.LOAD_GLOBAL, instr.index)
        elif isinstance(instr, ir.Call):
            return Instruction(Opcode.CALL_FUNCTION, instr.num_args)
        elif isinstance(instr, ir.Compare):
            return Instruction(Opcode.COMPARE_OP, instr.predicate.value)
        raise ValueError(f'Cannot encode ir instruction {instr}')

    def encode_return(self, instr: ir.ReturnValue) -> Instruction:
        return Instruction(Opcode.RETURN_VALUE, 0)

    POOL_OPCODES = {
        ir.VarPool.LOCALS: Opcode.LOAD_FAST,
        ir.VarPool.CONSTANTS: Opcode.LOAD_CONST,
    }

    def encode_load(self, instr: ir.Load) -> Instruction:
        return Instruction(self.POOL_OPCODES[instr.pool], instr.index)

    # This is a truth table mapping (pop_before_eval, jump_branch) to the
    # corresponding opcode.
    COND_BRANCH_OPCODES = {
        (True, True): Opcode.POP_JUMP_IF_TRUE,
        (True, False): Opcode.POP_JUMP_IF_FALSE,
        (False, True): Opcode.JUMP_IF_TRUE_OR_POP,
        (False, False): Opcode.JUMP_IF_FALSE_OR_POP,
    }

    def encode_cond_branch(self, instr: ir.ConditionalBranch) -> Instruction:
        op_key = (instr.pop_before_eval, instr.jump_when_true)
        opcode = self.COND_BRANCH_OPCODES[op_key]
        if instr.jump_when_true:
            offset = self.offsets[instr.true_branch]
        else:
            offset = self.offsets[instr.false_branch]
        return Instruction(opcode, offset)


def assemble(cfg: ir.ControlFlowGraph) -> bytes:
    """Converts a CFG into the corresponding Python bytecode"""
    # Arrange basic blocks in order they should appear in the bytecode
    # Compute block offsets
    offsets: Dict[ir.Label, int] = {}
    offset = 0
    for block in cfg:
        offsets[block.label] = offset
        num_instrs = len(block.instructions)
        if block.is_loop_header or block.is_loop_footer:
            # We need to insert SETUP_LOOP in the case of loop headers and
            # POP_BLOCK in the case of loop footers.
            num_instrs += 1
        offset += num_instrs * INSTRUCTION_SIZE_B
    # Adjust block offsets so that loop headers don't include SETUP_LOOP
    for block in cfg:
        if block.is_loop_header:
            offsets[block.label] += INSTRUCTION_SIZE_B
    # Relocate jumps and generate code
    code = bytearray(offset)
    offset = 0
    encoder = InstructionEncoder(offsets)
    for block in cfg:
        if block.is_loop_header:
            footer = None
            for succ in cfg.get_successors(block):
                if not isinstance(succ, ir.BasicBlock):
                    continue
                if succ.is_loop_footer:
                    footer = succ.label
                    break
            assert footer is not None
            code[offset] = Opcode.SETUP_LOOP
            code[offset + 1] = offsets[footer] - offset
            offset += 2
        elif block.is_loop_footer:
            code[offset] = Opcode.POP_BLOCK
            code[offset + 1] = 0
            offset += 2
        for ir_instr in block.instructions:
            instr = encoder.encode(ir_instr, offset)
            code[offset] = instr.opcode
            code[offset + 1] = instr.argument
            offset += 2
    return bytes(code)
