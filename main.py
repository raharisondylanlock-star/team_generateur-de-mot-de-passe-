import tkinter as tk

from ui.login import LoginApp


def main():
    root = tk.Tk()
    LoginApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
