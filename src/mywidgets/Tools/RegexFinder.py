import tkinter as tk
from src.Widgets.Custom.regexframe import StatusBar, RegexpFrame

def main():
    top = tk.Tk()
    top.attributes('-zoomed', True)
    message = tk.StringVar()
    status_list = [('Message:', message)]
    sb = StatusBar(top, status_list)
    sb.pack(side=tk.BOTTOM, fill=tk.X, expand=0)
    rgf = RegexpFrame(top, message)
    rgf.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    top.mainloop()

if __name__ == '__main__':
    main()