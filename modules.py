import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk  # noqa: F401


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
    scrollbar.grid(row=1, column=2, pady=(0, 0), sticky="ns")

    return tree


# function to destroy existing toplevels to prevent them from accumulating.
def remove_toplevels(self):
    for widget in self.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()


# insert data from database into the treeview, use id as tag,
# color rows where date_next is None or before today (expired)
def insert_data(self, data):
    for item in data:
        self.tree.insert("", tk.END, values=item, tags=item[0])
        if item[5] is None:
            self.tree.tag_configure(item[0], background="yellow")
        else:
            dat_nxt = datetime.strptime(item[5], "%Y-%m-%d").date()
            if dat_nxt < date.today():
                self.tree.tag_configure(item[0], background="yellow")
            elif dat_nxt == date.today():
                self.tree.tag_configure(item[0], background="cyan")
