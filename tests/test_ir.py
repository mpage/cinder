import dis
import ir


def single_block():
    return 123


def cond_jump(x):
    if x:
        return 1
    return 2


def test_single_block():
    cfg = ir.build_cfg(single_block.__code__)
    expected = ir.ControlFlowGraph()
    block = ir.BasicBlock(
        instructions=list(dis.get_instructions(single_block.__code__))
    )
    expected.entry.edges.append(ir.Edge(expected.entry, block))
    block.edges.append(ir.Edge(block, expected.exit))
    assert cfg == expected


def test_cond_jump():
    cfg = ir.build_cfg(cond_jump.__code__)
    for node in cfg:
        print(node)
    raise Exception
