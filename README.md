# cinder

Cinder is a toolkit for optimizing Python programs.

## Overview

This is a proof-of-concept toolkit for optimizing Python programs. It's primary
aim is to implement enough functionality to compile the hot functions in the
Richard's benchmark into machine code.

It is composed of the following modules:

- `cinder.bytecode` - Helper functions for working with Python bytecode.
- `cinder.ir` - A simple, stack-based IR that abstracts away some of the
  redundancy found in Python bytecode.
- `cinder.codegen.bytecode` - Generate Python bytecode from IR.
- `cinder.codegen.x64` - Simple, template-style x86-64 code generation for
  Python opcodes and helpers to generate the equivalent machine code for a
  Python function.

The pipeline for compiling a Python function into machine-code is fairly
straight-foward:

```
bytecode -> IR -> machine code
```

At a future point we may want to run optimization passes on the IR, but for
now, we generate machine code from it immediately.

## Examples

Compile and execute a simple function:

```
from cinder.codegen import x64

def is_truthy(x):
  if x:
     return True
  return False

compiled = x64.compile(is_truthy)

print(compiled(1))
```

Additionally, `cinder` provides an alternate interpreter loop with a fast
calling convention for compiled functions. You can use it like so:

```
from cinder import install_interpreter, uninstall_interpreter

install_interpreter()

# Execute code

uninstall_interpreter()
```

See `benchmarks/bm_richards.py` for a more complete example.

## Caveats

This is a proof-of-concept, and, as such, much functionality is
missing. Notably,

- No error handling is performed after runtime calls. We know that Richards raises no errors,
  so that is not needed yet.
- Keyword and ex calling of jit functions is unsupported. The VM will likely crash.
- Argument defaulting is unsupported.
- Constant references are embedded directly into the generated code.

## Development

To set up your local development environment, you will need pipenv. You can
install it with `pip install --user pipenv`. After this, you should be able to
run `pipenv --help` and get help output. If `pipenv` isn't found, you will need
to add `$HOME/.local/bin` to your shell `PATH`.

Once you have pipenv, run `pipenv update -d` to create a virtual environment
and install all packages needed for cinder development into it.

Then you can run `pipenv run python setup.py test` to run the tests and pipenv
run mypy cinder to typecheck.  These must pass cleanly before your changes can
be merged.

Alternatively, you can activate a pipenv shell with `pipenv shell`. This allows
you to run `python setup.py test` and `mypy` directly.
