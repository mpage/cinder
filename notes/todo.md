# Must have

- Make JitFunction a non-data descriptor
- Error handling
- Refactor code generation into a class
- Directory layout
- Make temporary register have a default value for incref/decref

# Nice to have

- Analysis pass to split {LOAD,STORE}_FAST into {LOAD,STORE}_ARG and {LOAD,STORE}_FAST
- Use caller saved regs where possible
- Type annotations for jit.py
- Fully compile away the block stack