import collections
import dis
import enum

from types import CodeType
from typing import (
    Any,
    Deque,
    Dict,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Set,
)


Label = str


class Instruction:
    pass


class ReturnValue(Instruction):
    def __str__(self) -> str:
        return 'RETURN_VALUE'


class LoadFast(Instruction):
    def __init__(self, index: int) -> None:
        self.index = index

    def __str__(self) -> str:
        return f'LOAD_FAST {self.index}'


class LoadConst(Instruction):
    def __init__(self, index: int) -> None:
        self.index = index

    def __str__(self) -> str:
        return f'LOAD_CONST {self.index}'


class ConditionalBranch(Instruction):
    def __init__(
        self,
        true_branch: Label,
        false_branch: Label,
        pop_before_eval: bool,
        jump_when_true: bool
    ) -> None:
        self.true_branch = true_branch
        self.false_branch = false_branch
        self.pop_before_eval = pop_before_eval
        self.jump_when_true = jump_when_true

    def __str__(self) -> str:
        return f'COND_BRANCH true={self.true_branch} false={self.false_branch}'


class Node:
    pass


class EntryNode(Node):
    pass


class ExitNode(Node):
    pass


class BasicBlock(Node):
    def __init__(
        self,
        label: Label,
        instructions: List[Instruction]
    ) -> None:
        if len(instructions) == 0:
            raise ValueError('Basic blocks cannot be empty')
        self.label = label
        self.instructions = instructions
        self.terminator = instructions[-1]

    def __str__(self) -> str:
        lines = [
            f'{self.label}:',
        ]
        for instr in self.instructions:
            lines.append(f'  {instr}')
        return "\n".join(lines)


class CFGIterator:
    """Iterates through the basic blocks in a control flow graph in reverse
    post order (tsort).
    """

    def __init__(self, cfg: 'ControlFlowGraph') -> None:
        self.cfg = cfg
        self.queue: Deque[Node] = collections.deque([cfg.entry_node])
        self.visited: Set[Node] = set()

    def __iter__(self) -> 'CFGIterator':
        return self

    def __next__(self) -> BasicBlock:
        while self.queue:
            node = self.queue.popleft()
            if node in self.visited:
                continue
            for succ in self.cfg.get_successors(node):
                self.queue.append(succ)
            self.visited.add(node)
            if not isinstance(node, BasicBlock):
                continue
            return node
        raise StopIteration


class ControlFlowGraph:
    def __init__(self) -> None:
        self.entry_node = EntryNode()
        self.exit_node = ExitNode()
        # src -> dst
        self.edges: Dict[Node, Set[Node]] = {
            self.entry_node: set(),
            self.exit_node: set(),
        }

    def add_block(self, block: BasicBlock) -> None:
        self.edges[block] = set()

    def add_edge(self, src: Node, dst: Node) -> None:
        self.edges[src].add(dst)

    def get_successors(self, node: Node) -> Iterable[Node]:
        return self.edges.get(node, set())

    def __iter__(self) -> Iterator[BasicBlock]:
        return CFGIterator(self)

    def __str__(self) -> str:
        output = ['entry:']
        blocks = [node for node in self if isinstance(node, BasicBlock)]
        blocks = sorted(blocks, key=lambda b: b.label)
        for block in blocks:
            output.append(str(block))
        return "\n".join(output)


def build_initial_cfg(blocks: List[BasicBlock]) -> ControlFlowGraph:
    """Build a CFG from a list of basic blocks.

    Assumes that the blocks are in order, with the first block as the entry
    block.
    """
    cfg = ControlFlowGraph()
    if not blocks:
        return cfg
    cfg.add_edge(cfg.entry_node, blocks[0])
    block_index = {block.label: block for block in blocks}
    for i, block in enumerate(blocks):
        cfg.add_block(block)
        # Outgoing edges are as follows if the terminator is a:
        #   - Direct branch      => block of branch target
        #   - Conditional branch => block of branch target and next block
        #   - Return             => exit node
        #   - Otherwise          => next block
        terminator = block.terminator
        if isinstance(terminator, ReturnValue):
            cfg.add_edge(block, cfg.exit_node)
        elif isinstance(terminator, ConditionalBranch):
            cfg.add_edge(block, block_index[terminator.true_branch])
            cfg.add_edge(block, block_index[terminator.false_branch])
        else:
            cfg.add_edge(block, blocks[i + 1])
    return cfg
