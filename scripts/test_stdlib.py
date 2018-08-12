from cinder import install_interpreter, uninstall_interpreter
from test.libregrtest import main


if __name__ == '__main__':
    install_interpreter()
    try:
        main()
    finally:
        uninstall_interpreter()
