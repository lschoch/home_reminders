import sqlite3
import tkinter as tk
from datetime import date, datetime, timedelta  # noqa: F401
from tkinter import ttk

from dateutil.relativedelta import relativedelta
from tkcalendar import Calendar

from modules2 import AutocompleteCombobox


# create toplevel
class TopLvl(tk.Toplevel):
    def __init__(self, master, title):
        super().__init__(master)
        self.title(title)
        self.config(padx=20, pady=20)
        x = master.winfo_x()
        y = master.winfo_y()
        self.geometry("+%d+%d" % (x + 110, y + 335))

        # create list of values for period_combobox that will be be accessed
        # outside the combobox configuration
        self.period_list = ["", "days", "weeks", "months", "years"]

        # create entry labels and widgets for the top level
        ttk.Label(self, text="description", background="#ececec").grid(
            row=0, column=0, padx=(0, 5), pady=(0, 15), sticky="e"
        )
        self.description_entry = ttk.Entry(self)
        self.description_entry.grid(
            row=0, column=1, padx=(0, 15), pady=(0, 15)
        )

        ttk.Label(self, text="frequency", background="#ececec").grid(
            row=0, column=2, padx=5, pady=(0, 15), sticky="e"
        )
        self.frequency_entry = ttk.Entry(self)
        self.frequency_entry.grid(row=0, column=3, padx=(0, 15), pady=(0, 15))

        ttk.Label(self, text="period", background="#ececec").grid(
            row=0, column=4, padx=5, pady=(0, 15), sticky="e"
        )
        self.period_combobox = AutocompleteCombobox(self)
        self.period_combobox.set_list(self.period_list)
        self.period_combobox.grid(row=0, column=5, pady=(0, 15))
        self.period_combobox.grid(row=0, column=5, pady=(0, 15))

        ttk.Label(self, text="date_last", background="#ececec").grid(
            row=1, column=0, padx=(0, 5), pady=(0, 15), sticky="e"
        )
        self.date_last_entry = ttk.Entry(self)
        self.date_last_entry.grid(row=1, column=1, padx=(0, 15), pady=(0, 15))

        ttk.Label(self, text="source", background="#ececec").grid(
            row=1, column=2, padx=(0, 5), pady=(0, 15), sticky="e"
        )
        self.source_entry = ttk.Entry(self)
        self.source_entry.grid(row=1, column=3, padx=(0, 15), pady=(0, 15))


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
        # restore overrideredirect to False
        top2.wm_overrideredirect(False)
        top2.destroy()

    def cal_cancel():
        # restore overrideredirect to False
        top2.wm_overrideredirect(False)
        top2.destroy()

    # function to set date_last_entry from calendar click
    def on_cal_selection_changed(event):
        date_last_entry.delete(0, tk.END)
        date_last_entry.insert(0, cal.selection_get())
        top2.destroy()

    # create a toplevel for the calendar
    top2 = tk.Toplevel(top)

    # remove title bar
    top2.wm_overrideredirect(True)

    top2.configure(background="#cacaca")
    x = top.winfo_x()
    y = top.winfo_y()
    top2.geometry("+%d+%d" % (x + 48, y + 120))

    # keep calendar in front of it's parent window
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
    # if date_last_entry is not empty, set calendar to date_last_entry
    if top.date_last_entry.get():
        cal.selection_set(top.date_last_entry.get())

    cal.grid(row=0, column=0)
    ttk.Button(top2, text="ok", width=2, command=cal_done).grid(
        row=1, column=0, padx=(80, 0), pady=3, sticky="w"
    )
    ttk.Button(top2, text="cancel", width=5, command=cal_cancel).grid(
        row=1, column=0, padx=(0, 80), sticky="e"
    )

    # bind CalendarSelected event to function that sets date_last_entry
    cal.bind("<<CalendarSelected>>", on_cal_selection_changed)


# function to update treeview after change to database
def refresh(self):
    # connect to database and create cursor
    self.con = sqlite3.connect("home_reminders.db")
    self.cur = self.con.cursor()
    # select data depending on the current view (all vs future)
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
    self.refreshed = True


# function to calculate date_next given period
def date_next_calc(date_last, frequency, period):
    match period:
        case "":
            date_next = ""
        case "days":
            date_next = datetime.strptime(
                date_last, "%Y-%m-%d"
            ).date() + timedelta(days=frequency)
            date_next = date_next.strftime("%Y-%m-%d")
        case "weeks":
            date_next = datetime.strptime(
                date_last, "%Y-%m-%d"
            ).date() + timedelta(weeks=frequency)
            date_next = date_next.strftime("%Y-%m-%d")
        case "months":
            date_next = datetime.strptime(
                date_last, "%Y-%m-%d"
            ).date() + relativedelta(months=frequency)
            date_next = date_next.strftime("%Y-%m-%d")
        case "years":
            date_next = datetime.strptime(
                date_last, "%Y-%m-%d"
            ).date() + relativedelta(years=frequency)
            date_next = date_next.strftime("%Y-%m-%d")
    return date_next


# create a validation function
def valid_frequency(input_data):
    if input_data:
        try:
            float(input_data)
            return True
        except ValueError:
            return False
    else:
        return False
