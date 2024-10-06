import tkinter as tk
from tkinter import messagebox, ttk  # noqa: F401

from tkcalendar import Calendar


# create treeview to display data from database
def create_tree_widget(self):
    columns = (
        "id",
        "description",
        "frequency",
        "period",
        "date_last",
        "date_next",
        "source",
    )
    tree = ttk.Treeview(self, columns=columns, show="headings")

    # define headings and columns
    tree.heading("id", text="Id")
    tree.heading("description", text="Item", anchor="w")
    tree.heading("frequency", text="Frequency")
    tree.heading("period", text="Period")
    tree.heading("date_last", text="Last")
    tree.heading("date_next", text="Next")
    tree.heading("source", text="Source", anchor="w")
    tree.column("id", width=50, anchor="center")
    tree.column("description", anchor="w")
    tree.column("frequency", width=65, anchor="center")
    tree.column("period", width=75, anchor="center")
    tree.column("date_last", width=100, anchor="center")
    tree.column("date_next", width=100, anchor="center")
    tree.column("source", width=200, anchor="w")
    tree.focus()

    tree.bind("<<TreeviewSelect>>", self.on_treeview_selection_changed)
    tree.grid(row=1, column=1)

    # add a scrollbar
    scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=1, column=2, pady=20, sticky="ns")

    return tree


# function to destroy existing toplevels to prevent them from accumulating.
def remove_toplevels(self):
    for widget in self.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()


def get_date(self, date_last_entry):
    def cal_done():
        top.withdraw()
        root.quit()

    root = tk.Tk()
    root.withdraw()  # keep the root window from appearing

    top = tk.Toplevel(root)

    cal = Calendar(
        top,
        font="Arial 14",
        selectmode="day",
        cursor="arrow",
        locale="en_US",
        date_pattern="yyyy/mm/dd",
    )
    cal.pack(fill="both", expand=True)
    ttk.Button(top, text="ok", command=cal_done).pack()

    # selected_date = None
    root.mainloop()
    self.date_last_entry.insert(0, cal.selection_get())
