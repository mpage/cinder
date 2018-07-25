import collections
import dis

from enum import Enum
from types import CodeType
from typing import (
    Dict,
    List,
    NamedTuple,
    Optional,
    Set,
)


class Edge(NamedTuple):
    src: 'Node'
    dst: 'Node'


class TrueEdge(Edge):
    """Corresponds to the true branch of a conditional branch"""
    pass


class FalseEdge(Edge):
    """Corresponds to the false branch of a conditional branch"""
    pass


class Node:
    def __init__(self) -> None:
        self.edges = []

    def add_edge(self, edge: 'Edge') -> None:
        self.edges.append(edge)


class EntryNode(Node):
    """Sentinel node that is the entry to a CFG"""
    pass


class ExitNode(Node):
    """Sentinel node that is the exit of a CFG"""
    pass


class BasicBlock(Node):
    def __init__(self, instructions: Optional[List[dis.Instruction]] = None) -> None:
        super(BasicBlock, self).__init__()
        self.instructions = instructions or []

    def __str__(self) -> str:
        lines = [
            f'BasicBlock({id(self)}',
            '  Instructions:',
        ]
        for instr in self.instructions:
            lines.append(f'    {instr}')
        lines.append('  Edges:')
        connected_node_ids = [id(edge.dst) for edge in self.edges]
        edge_str = ', '.join(map(str, sorted(connected_node_ids)))
        lines.append(f'    {edge_str}')
        return '\n'.join(lines)


# TODO(mpage): Consider converting this to a generator function
class CFGIterator:
    """Iterates through the basic blocks in a control flow graph in reverse
    post order (tsort).
    """

    def __init__(self, cfg: 'ControlFlowGraph'):
        self.queue = collections.deque([cfg.entry])
        self.visited: Set[int] = set()

    def __iter__(self):
        return self

    def __next__(self):
        while self.queue:
            node = self.queue.popleft()
            if id(node) in self.visited:
                continue
            for edge in node.edges:
                self.queue.append(edge.dst)
            self.visited.add(id(node))
            return node
        raise StopIteration


def _pluck_klass(x):
    return x.__class__


class ControlFlowGraph:
    def __init__(self):
        self.entry = EntryNode()
        self.exit = ExitNode()

    def __iter__(self):
        return CFGIterator(self)

    def __eq__(self, other):
        # NB: This should only be used for tests.
        # Two CFGs are considered equal iff they have identical rpo traversals.
        if self.__class__ != other.__class__:
            return False
        selfq = collections.deque()
        if self.entry.edges:
            assert len(self.entry.edges) == 1
            selfq.append(self.entry.edges[0].dst)
        self_visited = set()
        otherq = collections.deque()
        if other.entry.edges:
            assert len(other.entry.edges) == 1
            otherq.append(other.entry.edges[0].dst)
        other_visited = set()
        while selfq and otherq:
            self_node = selfq.popleft()
            other_node = otherq.popleft()
            if isinstance(self_node, ExitNode) and isinstance(other_node, ExitNode):
                continue
            if self_node.instructions != other_node.instructions:
                return False
            self_edges = []
            if id(self_node) not in self_visited:
                self_visited.add(id(self_node))
                self_edges = sorted(self_node.edges, key=_pluck_klass)
            if id(other_node) not in other_visited:
                other_visited.add(id(other_node))
                other_edges = sorted(other_node.edges, key=_pluck_klass)
            if len(self_edges) != len(other_edges):
                return False
            for self_edge, other_edge in zip(self_edges, other_edges):
                if self_edge.__class__ != other_edge.__class__:
                    return False
                selfq.append(self_edge.dst)
                otherq.append(other_edge.dst)
        return not selfq and not otherq


# TODO(mpage): flesh these out
_IS_BRANCH_NAMES = (
    'POP_JUMP_IF_FALSE', 'POP_JUMP_IF_TRUE',
    'JUMP_IF_TRUE_OR_POP', 'JUMP_IF_FALSE_OR_POP',
    'RETURN_VALUE',
    'JUMP_FORWARD', 'JUMP_ABSOLUTE',
    'FOR_ITER',
)
IS_BRANCH = {dis.opmap[name] for name in _IS_BRANCH_NAMES}

_IS_COND_BRANCH_NAMES = (
    'POP_JUMP_IF_FALSE',
    'POP_JUMP_IF_TRUE',
    'JUMP_IF_TRUE_OR_POP',
    'JUMP_IF_FALSE_OR_POP',
    'FOR_ITER',
)
IS_COND_BRANCH = {dis.opmap[name] for name in _IS_COND_BRANCH_NAMES}

RETURN_VALUE_OPCODE = dis.opmap['RETURN_VALUE']


# TODO(mpage): get_instructions is inefficient. Rewrite if necessary, when
# time permits.
#
# Offset is a label iff:
#   - It is the target of a branch
#   - It follows a conditional branch
#
# Outgoing edges from a block:
#   - If last insn is direct branch, block beginning with branch target
#   - If last insn is an indirect branch, block w/ target and block beginning
#     at next insns
#   - If last insn is a return, exit node
#   - If last insn is not a branch, block beginning at next insn. This
#     shouldn't happen, but is theoretically possible if the next instruction
#     is a jump target.
def get_labels(code: CodeType) -> Set[int]:
    labels = {0}
    last_offset = len(code.co_code)
    for instr in dis.get_instructions(code):
        opcode = instr.opcode
        next_instr_offset = instr.offset + 2
        if opcode in IS_BRANCH and next_instr_offset < last_offset:
            labels.add(next_instr_offset)
        # TODO(mpage): These checks are O(N)
        if opcode in dis.hasjrel:
            labels.add(instr.argval)
        elif opcode in dis.hasjabs:
            labels.add(instr.argval)
    return labels


def build_cfg(code: CodeType) -> ControlFlowGraph:
    """Build a CFG from the bytecode in the supplied code object"""
    cfg = ControlFlowGraph()
    labels = get_labels(code)
    # Fill in basic blocks
    blocks = {offset: BasicBlock() for offset in labels}
    block = BasicBlock()
    for instr in dis.get_instructions(code):
        if instr.offset in labels:
            block = blocks[instr.offset]
        block.instructions.append(instr)
    # Connect blocks together
    for block in blocks.values():
        instr = block.instructions[-1]
        opcode = instr.opcode
        if opcode in dis.hasjrel:
            dst = blocks[instr.argval]
            block.add_edge(Edge(block, dst))
        elif opcode in dis.hasjabs:
            dst = blocks[instr.argval]
            block.add_edge(Edge(block, dst))
        elif opcode == dis.opmap['RETURN_VALUE']:
            block.add_edge(Edge(block, cfg.exit))
        if opcode in IS_COND_BRANCH or opcode not in IS_BRANCH:
            block.add_edge(Edge(block, blocks[instr.offset + 2]))
    cfg.entry.add_edge(Edge(cfg.entry, blocks[0]))
    return cfg
