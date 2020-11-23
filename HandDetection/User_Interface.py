from tkinter import *
import tkinter.messagebox as tm

_user_name = ''
_surname = ''
_add_new_user = False
_user_also_exist = False
_clear_database = False
_delete_current_user = False

global _include_ratio
global _flip_camera
_include_ratio = True
_flip_camera = True


class LoginFrame(Frame):
    def __init__(self, master):
        super().__init__(master)

        self.label_0 = Label(self, text="\nnew user", font=("Helvetica", 16), fg="blue")
        self.label_1 = Label(self, text="Name: ")
        self.label_2 = Label(self, text="Surname: ")

        self.entry_0 = Entry(self)
        self.entry_1 = Entry(self)
        self.entry_2 = Entry(self)

        self.label_0.grid(row=0, column=1)
        self.label_1.grid(row=1, sticky=E)
        self.label_2.grid(row=2, sticky=E)
        self.entry_1.grid(row=1, column=1)
        self.entry_2.grid(row=2, column=1)

        global _checked_1
        self._checked_1 = IntVar(value=1)
        self.checkbox = Checkbutton(self, text="Include ratio", variable=self._checked_1, command=self._include_ratio)
        self.checkbox.grid(row=4, columnspan=1)

        global _checked_2
        self._checked_2 = IntVar(value=1)
        self.checkbox = Checkbutton(self, text="Camera flip", variable=self._checked_2, command=self._include_flip)
        self.checkbox.grid(row=3, columnspan=1)

        self.logbtn_1 = Button(self, text="Add new user", height=0, width=18, command=self._login_btn_clickked)
        self.logbtn_2 = Button(self, text="User already exists", height=0, width=18, command=self._user_also_exist)
        self.logbtn_3 = Button(self, text="Delete current user", height=0, width=18, command=self._delete_current_user)
        self.logbtn_4 = Button(self, text="clear database", height=0, width=10, command=self._clear_data_base)
        self.logbtn_1.grid(row=3, column=1)
        self.logbtn_2.grid(row=5, column=1)
        self.logbtn_3.grid(row=4, column=1)
        self.logbtn_4.grid(row=5, column=0)

        self.pack()


    def _login_btn_clickked(self):
        if len(self.entry_1.get()) <= 3 or len(self.entry_2.get()) <= 3:
            tm.showerror("Login error", "Incorrect username")
        else:
            text = "Welcome %s, %s" % (self.entry_1.get(), self.entry_2.get())
            tm.showinfo("Login info", text)
            global _user_name, _surname, _add_new_user
            _user_name = self.entry_1.get()
            _surname = self.entry_2.get()
            _add_new_user = True
            root.destroy()


    def _user_also_exist(self):
        var = tm.askokcancel("Proceed: ")

        if var == True:
            global _user_also_exist
            _user_also_exist = var
            root.destroy()


    def _clear_data_base(self):
        var = tm.askretrycancel("Are you sure?")

        if var == True:
            global _clear_database
            _clear_database = var
            root.destroy()


    def _include_ratio(self):
        global _include_ratio

        if self._checked_1.get() == 0:
            _include_ratio = False
        else:
            _include_ratio = True


    def _include_flip(self):
        global _flip_camera

        if self._checked_2.get() == 0:
            _flip_camera = False
        else:
            _flip_camera = True


    def _delete_current_user(self):
        if len(self.entry_1.get()) <= 3 or len(self.entry_2.get()) <= 3:
            tm.showerror("Login error", "Incorrect username")
        else:
            text = "If person named %s %s, %s" % (self.entry_1.get(), self.entry_2.get(), "exists in the database, then it will be removed!")
            tm.showinfo("User info", text)
            global _user_name, _surname, _delete_current_user
            _user_name = self.entry_1.get()
            _surname = self.entry_2.get()
            _delete_current_user = True
            root.destroy()





root = Tk()

w = 400  # width for the Tk root
h = 200  # height for the Tk root

ws = root.winfo_screenwidth() - 150   # width of the screen
hs = root.winfo_screenheight() - 300  # height of the screen

x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

lf = LoginFrame(root.geometry('%dx%d+%d+%d' % (w, h, x, y)))

def doSomething():
    root.destroy()
    exit()

root.protocol('WM_DELETE_WINDOW', doSomething)
root.mainloop()