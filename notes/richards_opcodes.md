# Remaining opcodes for richards:

## Task.runTask

STORE_FAST -- need jit
COMPARE_OP -- specialize
JUMP_ABSOLUTE -- need jit
JUMP_FORWARD

## schedule

STORE_FAST -- need jit
SETUP_LOOP -- need jit
COMPARE_OP -- specialize
JUMP_ABSOLUTE -- need jit
BINARY_ADD
POP_BLOCK -- need jit
