import tkinter as tk
from Widgets.Custom.regexframe import StatusBar, RegexpFrame

def main():
    top = tk.Tk()
    message = tk.StringVar()
    status_list = [('Message:', message)]
    sb = StatusBar(top, status_list)
    sb.pack(side=tk.BOTTOM, fill=tk.X, expand=0)
    rgf = RegexpFrame(top, message)
    rgf.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    w, h = top.winfo_screenwidth(), top.winfo_screenheight()
    top.geometry("%dx%d+0+0" % (w, h))
    top.mainloop()

if __name__ == '__main__':
    main()