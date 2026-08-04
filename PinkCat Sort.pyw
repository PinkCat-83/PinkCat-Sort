from tkinterdnd2 import TkinterDnD
from app import FileSorterGUI


def main():
    # Appearance mode (dark/light) is set by ui/styles.py based on the
    # active theme — do not override it here.
    root = TkinterDnD.Tk()
    FileSorterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
