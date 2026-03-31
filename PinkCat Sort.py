from tkinterdnd2 import TkinterDnD
from app import FileSorterGUI


def main():
    root = TkinterDnD.Tk()
    FileSorterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
