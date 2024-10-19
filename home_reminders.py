import sqlite3
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from classes import TopLvl
from functions import (
    create_tree_widget,
    date_next_calc,
    get_date,
    insert_data,
    refresh,
    remove_toplevels,
    valid_frequency,
)

# connect to database and create cursor
con = sqlite3.connect("home_reminders.db")
cur = con.cursor()

# create table if it doesn't exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS reminders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT,
        frequency TEXT,
        period TEXT,
        date_last TEXT,
        date_next TEXT,
        source TEXT)
""")

# select data for display, bring NULLs forward so they don't get lost
data = cur.execute("""
    SELECT * FROM reminders
    WHERE date_next >= DATE('now')
    ORDER BY date_next ASC, description ASC
""")


# create the main window
class App(tk.Tk):
    def __init__(self, **kw):
        super().__init__(**kw)

        self.title("Home Reminders")
        self.geometry("1000x300")
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # create variable to prevent calling
        # treeview_on_selection_changed after refresh
        self.refreshed = False

        # flag to track whether coming from view_all or view_current
        self.view_current = True

        self.lbl_msg = tk.StringVar()
        self.lbl_msg.set("Future items - select a row to update or delete")

        # create main screen
        self.btn = ttk.Button(self, text="Future", command=self.future).grid(
            row=1, column=0, padx=20, pady=(20, 0), sticky="n"
        )
        self.btn = ttk.Button(
            self, text="Expired", command=self.view_all
        ).grid(row=1, column=0, padx=20, pady=(72, 0), sticky="n")
        self.btn = ttk.Button(self, text="New", command=self.create_new).grid(
            row=1, column=0, padx=20, pady=(0, 72), sticky="s"
        )
        self.btn = ttk.Button(
            self, text="Quit", command=self.quit_program
        ).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="s")
        self.view_lbl = ttk.Label(
            self,
            textvariable=self.lbl_msg,
            background="#ececec",
            font=("Arial", 18),
        ).grid(row=0, column=1, padx=(5, 0), pady=(20, 4), sticky="w")

        # create treeview to display data
        self.tree = create_tree_widget(self)

        # add data to treeview
        insert_data(self, data)

        # query database for expired reminders
        expired = cur.execute("""
            SELECT * FROM reminders
            WHERE date_next < DATE('now')
            ORDER BY date_next ASC, description ASC
        """).fetchall()

        self.tree.focus_set()

        # message user if there are expired reminders
        if expired:
            """ messagebox.showinfo(
                "", f"There are {len(expired)} expired reminders."
            ) """
            self.lbl_msg.set(f"There are {len(expired)} expired reminders.")

    # create top level window for entry of data for new item
    def create_new(self):
        # remove any existing toplevels
        remove_toplevels(self)

        # create new toplevel
        top = TopLvl(self, "New Item")
        top.date_last_entry.insert(0, date.today())

        # get_date_cmd calls get date (calendar pop-up)
        def get_date_cmd(event):
            get_date(top.date_last_entry, top)

        # bind click in date_last_entry to get_date_cmd
        top.date_last_entry.bind("<1>", get_date_cmd)

        # function to save new item to database
        def save_item():
            # validate inputs
            if not valid_frequency(top.frequency_entry.get()):
                messagebox.showinfo(
                    "Invalid Input", "Frequency requires a numeric input."
                )
                return

            if not top.date_last_entry.get() or not top.period_combobox.get():
                messagebox.showinfo(
                    "Invalid Input", "Please select a period and a date_last."
                )
                return

            # check for duplicate description
            result = cur.execute("""SELECT * FROM reminders""")
            for item in result.fetchall():
                if item[1] == top.description_entry.get():
                    messagebox.showinfo(
                        "Invalid Input",
                        """There is already an item with that description.\n
                        Try again.""",
                    )
                    return

            # calculate date_next
            date_last = top.date_last_entry.get()
            frequency = int(top.frequency_entry.get())
            period = top.period_combobox.get()
            date_next = date_next_calc(date_last, frequency, period)

            data_get = (
                top.description_entry.get(),
                frequency,
                top.period_combobox.get(),
                date_last,
                date_next,
                top.source_entry.get(),
            )
            cur.execute(
                """
                INSERT INTO reminders (
                    description,
                    frequency,
                    period,
                    date_last,
                    date_next,
                    source)
                VALUES (?, ?, ?, ?, ?, ?)""",
                data_get,
            )
            con.commit()
            refresh(self)
            top.destroy()
            self.tree.focus()

        def cancel():
            # remove_toplevels(self)
            top.destroy()
            self.tree.focus()

        ttk.Button(top, text="Save", command=save_item).grid(
            row=2, column=1, padx=(33, 0), pady=(15, 0), sticky="w"
        )

        ttk.Button(top, text="Cancel", command=cancel).grid(
            row=2, column=3, padx=(0, 48), pady=(15, 0), sticky="e"
        )

    def future(self):
        self.view_current = True
        self.lbl_msg.set("Future items - select a row to update or delete")
        refresh(self)

    def view_all(self):
        self.lbl_msg.set("All items - select a row to update or delete")
        data = cur.execute("""
            SELECT * FROM reminders
            ORDER BY date_next ASC, description ASC
        """)
        for item in self.tree.get_children():
            self.tree.delete(item)
        insert_data(self, data)
        self.refreshed = True
        self.view_current = False
        self.tree.focus_set()

    def quit_program(self):
        self.destroy()

    # create toplevel to manage row selection
    def on_treeview_selection_changed(self, event):
        # abort if the selection change was after a refresh
        if self.refreshed:
            self.refreshed = False
            return

        selected_item = self.tree.focus()
        remove_toplevels(self)

        # create toplevel
        top = TopLvl(self, "Selection")

        # capture id and description fields of the selected item
        id = self.tree.item(selected_item)["values"][0]
        original_description = self.tree.item(selected_item)["values"][1]

        # populate entries with data from the selection
        top.description_entry.insert(
            0, self.tree.item(selected_item)["values"][1]
        )
        top.frequency_entry.insert(
            0, self.tree.item(selected_item)["values"][2]
        )

        # use index function to determine index of the period_combobox value
        indx = top.period_list.index(
            self.tree.item(selected_item)["values"][3]
        )
        # set the combobox value using current function
        top.period_combobox.current(indx)
        top.date_last_entry.insert(
            0, self.tree.item(selected_item)["values"][4]
        )
        top.source_entry.insert(0, self.tree.item(selected_item)["values"][6])

        # get_date_cmd calls get date (calendar pop-up)
        def get_date_cmd(self):
            get_date(top.date_last_entry, top)

        # bind click in date_last_entry to get_date_cmd
        top.date_last_entry.bind("<1>", get_date_cmd)

        # update database
        def update_item():
            # validate inputs
            if not valid_frequency(top.frequency_entry.get()):
                messagebox.showinfo(
                    "Invalid Input", "Frequency requires a numeric input."
                )
                return

            if not top.date_last_entry.get() or not top.period_combobox.get():
                messagebox.showinfo(
                    "Invalid Input", "Please select a period and a date_last."
                )
                return

            # check for duplicate description
            result = cur.execute("""SELECT * FROM reminders""")
            for item in result.fetchall():
                if (
                    # item[1] is the selected description
                    item[1] == top.description_entry.get()
                    # duplicate OK if just changing other parameters
                    # item[0] is the selected id
                    and not item[0] == id
                ):
                    # reset original description
                    top.description_entry.delete(0, tk.END)
                    top.description_entry.insert(0, original_description)
                    messagebox.showinfo(
                        "Invalid Input",
                        """There is already an item with that description.\n
                        Try again.""",
                    )
                    return

            # calculate date_next
            date_last = top.date_last_entry.get()
            frequency = int(top.frequency_entry.get())
            period = top.period_combobox.get()
            date_next = date_next_calc(date_last, frequency, period)

            cur.execute(
                """
                UPDATE reminders
                SET (
                description, frequency, period, date_last, date_next, source) =
                    (?, ?, ?, ?, ?, ?)
                WHERE id = ? """,
                (
                    top.description_entry.get(),
                    top.frequency_entry.get(),
                    top.period_combobox.get(),
                    top.date_last_entry.get(),
                    date_next,
                    top.source_entry.get(),
                    self.tree.item(selected_item)["values"][0],
                ),
            )
            con.commit()
            remove_toplevels(self)
            refresh(self)

        # delete item from database
        def delete_item():
            id = self.tree.item(selected_item)["values"][0]
            cur.execute(
                """
                DELETE FROM reminders
                WHERE id = ?""",
                (id,),
            )
            con.commit()
            refresh(self)
            remove_toplevels(self)

        def cancel():
            remove_toplevels(self)

        ttk.Button(top, text="Update", command=update_item).grid(
            row=2, column=1, pady=(15, 0), sticky="w"
        )

        ttk.Button(top, text="Delete", command=delete_item).grid(
            row=2, column=3, pady=(15, 0), sticky="w"
        )

        ttk.Button(top, text="Cancel", command=cancel).grid(
            row=2, column=5, pady=(15, 0), sticky="w"
        )


if __name__ == "__main__":
    app = App()
    app.mainloop()
