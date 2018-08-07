# Must have

- README
- Loop support in the jit
-- Need to setup/teardown the block stack in the prologue / epilogue
-- Code for pushing / popping block stack entries
-- Code generation for labels
-- Long term solution is an analysis pass to split loads/stores into {LOAD,STORE}_{ARG,LOCAL}
-- Short term we can do the split in the code generator based on the index of the argument
- Make JitFunction a non-data descriptor
- Error handling

# Nice to have

- Analysis pass to split {LOAD,STORE}_FAST into {LOAD,STORE}_ARG and {LOAD,STORE}_FAST
- Use caller saved regs where possible
- Type annotations for jit.py
0