from cinder import install_interpreter, uninstall_interpreter
from cinder.runtime import patch_scheduler
from test.libregrtest import main


if __name__ == '__main__':
    patch_scheduler()
    install_interpreter()
    try:
        main()
    finally:
        uninstall_interpreter()
