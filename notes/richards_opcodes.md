# Remaining opcodes for richards:

## Task.runTask

LOAD_GLOBAL
CALL_FUNCTION
STORE_FAST -- need jit
COMPARE_OP -- specialize
JUMP_ABSOLUTE -- need jit
JUMP_FORWARD

## schedule

LOAD_GLOBAL
STORE_FAST -- need jit
SETUP_LOOP -- need jit
COMPARE_OP -- specialize
CALL_FUNCTION
JUMP_ABSOLUTE -- need jit
BINARY_ADD
POP_BLOCK
