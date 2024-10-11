import sqlite3
import tkinter as tk
from datetime import date, datetime
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
    scrollbar.grid(row=1, column=2, pady=(0, 0), sticky="ns")

    return tree


# function to destroy existing toplevels to prevent them from accumulating.
def remove_toplevels(self):
    for widget in self.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()


# function to insert data from database into the treeview,
# use id as tag to color rows
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
            else:
                self.tree.tag_configure(item[0], background="white")


# function to select date from a calendar
def get_date(date_last_entry, top):
    # destroy calendar if it already exists
    # (prevents multiple overlying calendars on repeatedly clicking the entry)
    for child in top.winfo_children():
        if isinstance(child, tk.Toplevel):
            child.destroy()

    # update date_last_entry after date is selected with OK button
    def cal_done():
        date_last_entry.delete(0, tk.END)
        date_last_entry.insert(0, cal.selection_get())
        top2.destroy()

    def cal_cancel():
        top2.destroy()

    # create a toplevel for the calendar
    top2 = tk.Toplevel(top)
    top2.title("Calendar")
    top2.configure(background="#cacaca")
    top2.geometry("+163+175")
    # keep calendar in front of it' parent window
    top2.wm_transient(top)

    cal = Calendar(
        top2,
        font="Arial 14",
        selectmode="day",
        cursor="arrow",
        locale="en_US",
        date_pattern="yyyy/mm/dd",
        showweeknumbers="False",
        foreground="black",
        background="#cacaca",
        headersbackground="#dbdbdb",
        weekendbackground="white",
        othermonthwebackground="#ececec",
        selectforeground="red",
        selectbackground="#dbdbdb",
    )
    cal.selection_set(date_last_entry.get())
    cal.grid(row=0, column=0)
    ttk.Button(top2, text="ok", width=2, command=cal_done).grid(
        row=1, column=0, padx=(80, 0), pady=3, sticky="w"
    )
    ttk.Button(top2, text="cancel", width=5, command=cal_cancel).grid(
        row=1, column=0, padx=(0, 80), sticky="e"
    )


# function to update treeview after change to database
def refresh(self):
    # connect to database and create cursor
    self.con = sqlite3.connect("home_reminders.db")
    self.cur = self.con.cursor()
    # select data depending on the current view (all vs pending)
    if self.view_current:
        data = self.cur.execute("""
            SELECT * FROM reminders
            WHERE date_next >= DATE('now') OR date_next IS NULL
            ORDER BY date_next ASC
        """)
    else:
        data = self.cur.execute("""
            SELECT * FROM reminders
            ORDER BY date_next ASC
        """)

    for item in self.tree.get_children():
        self.tree.delete(item)

    insert_data(self, data)

    self.focus()
    self.refreshed = True
