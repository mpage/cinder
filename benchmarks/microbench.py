import argparse
import time

from cinder import (
    install_interpreter,
    jit,
    uninstall_interpreter,
)


def identity(x):
    return x


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-iters', default=100000000, type=int)
    args = parser.parse_args()
    jit_identity = jit.compile(identity)
    print("==> Starting bytecode iterations")
    start = time.time()
    for _ in range(args.num_iters):
        identity(1)
    elapsed = time.time() - start
    print("==> Took %0.5fs" % (elapsed,))

    print("==> Starting jit iterations")
    start = time.time()
    install_interpreter()
    for _ in range(args.num_iters):
        jit_identity(1)
    uninstall_interpreter()
    elapsed = time.time() - start
    print("==> Took %0.5fs" % (elapsed,))
