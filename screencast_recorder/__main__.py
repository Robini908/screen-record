import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "gui":
        sys.argv.pop(1)
        from .gui import gui_main
        gui_main()
    else:
        from .cli import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()
