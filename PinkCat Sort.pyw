import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
from app import FileSorterGUI


def main():
    ctk.set_appearance_mode("dark")
    root = TkinterDnD.Tk()
    FileSorterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
