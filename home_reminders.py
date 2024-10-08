import sqlite3
import tkinter as tk
from datetime import date, datetime  # noqa: F401
from tkinter import messagebox, ttk  # noqa: F401

from tkcalendar import Calendar

from modules import create_tree_widget, insert_data, remove_toplevels

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
        date_next TEXT AS (DATE(date_last, '+' || frequency || ' ' ||
            period)) STORED,
        source TEXT)
""")

# select data for display, bring NULLs forward so they don't get lost
data = cur.execute("""
    SELECT * FROM reminders
    WHERE date_next >= DATE('now') OR date_next IS NULL
    ORDER BY date_next ASC
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

        # create main screen
        self.btn = ttk.Button(self, text="Pending", command=self.pending).grid(
            row=1, column=0, padx=20, pady=(20, 0), sticky="n"
        )
        self.btn = ttk.Button(self, text="All", command=self.view_all).grid(
            row=1, column=0, padx=20, pady=(72, 0), sticky="n"
        )
        self.btn = ttk.Button(self, text="New", command=self.create_new).grid(
            row=1, column=0, padx=20, pady=(0, 72), sticky="s"
        )
        self.btn = ttk.Button(
            self, text="Quit", command=self.quit_program
        ).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="s")
        self.lbl = ttk.Label(
            self,
            text="Select row to update or delete.",
            background="#ececec",
            font=("Arial", 18),
            anchor="center",
        ).grid(
            row=0,
            column=1,
            pady=(20, 4),
        )

        # create treeview to display data
        self.tree = create_tree_widget(self)

        # add data to treeview
        insert_data(self, data)

    # create top level window for entry of data for new item
    def create_new(self):
        # remove any existing toplevels
        remove_toplevels(self)

        # create new toplevel
        top = tk.Toplevel(self, padx=20, pady=20)
        top.title("New Item")
        x = self.winfo_x()
        y = self.winfo_y()
        top.geometry("+%d+%d" % (x + 110, y + 335))

        # create entry labels and widgets
        ttk.Label(top, text="description", background="#ececec").grid(
            row=0, column=0, padx=(0, 5), pady=(0, 15), sticky="e"
        )
        description_entry = ttk.Entry(top)

        description_entry.grid(row=0, column=1, padx=(0, 15), pady=(0, 15))
        ttk.Label(top, text="frequency", background="#ececec").grid(
            row=0, column=2, padx=5, pady=(0, 15), sticky="e"
        )
        frequency_entry = ttk.Entry(top)
        frequency_entry.grid(row=0, column=3, padx=(0, 15), pady=(0, 15))

        ttk.Label(top, text="period", background="#ececec").grid(
            row=0, column=4, padx=5, pady=(0, 15), sticky="e"
        )
        period_entry = ttk.Combobox(
            top,
            state="readonly",
            values=["days", "weeks", "months", "years"],
        )
        period_entry.grid(row=0, column=5, pady=(0, 15))

        ttk.Label(top, text="date_last", background="#ececec").grid(
            row=1, column=0, padx=(0, 5), pady=(0, 15), sticky="e"
        )
        date_last_entry = ttk.Entry(top)
        date_last_entry.grid(row=1, column=1, padx=(0, 15), pady=(0, 15))

        ttk.Label(top, text="source", background="#ececec").grid(
            row=1, column=2, padx=(0, 5), pady=(0, 15), sticky="e"
        )
        source_entry = ttk.Entry(top)
        source_entry.grid(row=1, column=3, padx=(0, 15), pady=(0, 15))

        # function to select date from calendar
        def get_date(self):
            # update date_last_entry after date is selected
            def cal_done():
                date_last_entry.delete(0, tk.END)
                date_last_entry.insert(0, cal.selection_get())
                top2.destroy()

            # create a toplevel on existing toplevel
            top2 = tk.Toplevel(top)
            top2.configure(background="#cacaca")

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
            cal.grid(row=0, column=0)
            ttk.Button(top2, text="ok", command=cal_done).grid(row=1, column=0)

        # bind return in date_last_entry to get_date
        date_last_entry.bind("<Return>", get_date)

        # function to save new item to database
        def save_item():
            data_get = (
                description_entry.get(),
                frequency_entry.get(),
                period_entry.get(),
                date_last_entry.get(),
                source_entry.get(),
            )
            cur.execute(
                """
                INSERT INTO reminders (
                    description, frequency, period, date_last, source)
                VALUES (?, ?, ?, ?, ?)""",
                data_get,
            )
            con.commit()
            self.refresh()

            # clear entries in new item screen for another new item
            description_entry.delete(0, tk.END)
            frequency_entry.delete(0, tk.END)
            period_entry.delete(0, tk.END)
            date_last_entry.delete(0, tk.END)
            source_entry.delete(0, tk.END)

        def cancel():
            remove_toplevels(self)
            self.tree.focus()

        ttk.Button(top, text="Save", command=save_item).grid(
            row=2, column=1, padx=(33, 0), pady=(15, 0), sticky="w"
        )

        ttk.Button(top, text="Cancel", command=cancel).grid(
            row=2, column=3, padx=(0, 48), pady=(15, 0), sticky="e"
        )

    def pending(self):
        self.view_current = True
        self.refresh()

    # function to update treeview after change to database
    def refresh(self):
        # select data depending on the current view (all vs pending)
        if self.view_current:
            data = cur.execute("""
                SELECT * FROM reminders
                WHERE date_next >= DATE('now') OR date_next IS NULL
                ORDER BY date_next ASC
            """)
        else:
            data = cur.execute("""
                SELECT * FROM reminders
                ORDER BY date_next ASC
            """)

        for item in self.tree.get_children():
            self.tree.delete(item)

        insert_data(self, data)

        self.focus()
        self.refreshed = True

    def view_all(self):
        data = cur.execute("""
            SELECT * FROM reminders
            ORDER BY date_next ASC
        """)
        for item in self.tree.get_children():
            self.tree.delete(item)
        insert_data(self, data)
        self.focus()
        self.refreshed = True
        self.view_current = False

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
        top = tk.Toplevel(self, padx=20, pady=20)
        top.title("Selection")
        x = self.winfo_x()
        y = self.winfo_y()
        top.geometry("+%d+%d" % (x + 110, y + 335))

        # create entry labels and widgets for the top level
        ttk.Label(top, text="description", background="#ececec").grid(
            row=0, column=0, padx=(0, 5), pady=(0, 15), sticky="e"
        )
        description_entry = ttk.Entry(top)
        description_entry.grid(row=0, column=1, padx=(0, 15), pady=(0, 15))

        ttk.Label(top, text="frequency", background="#ececec").grid(
            row=0, column=2, padx=5, pady=(0, 15), sticky="e"
        )
        frequency_entry = ttk.Entry(top)
        frequency_entry.grid(row=0, column=3, padx=(0, 15), pady=(0, 15))

        ttk.Label(top, text="period", background="#ececec").grid(
            row=0, column=4, padx=5, pady=(0, 15), sticky="e"
        )
        period_entry = ttk.Entry(top)
        period_entry.grid(row=0, column=5, pady=(0, 15))

        ttk.Label(top, text="date_last", background="#ececec").grid(
            row=1, column=0, padx=(0, 5), pady=(0, 15), sticky="e"
        )
        date_last_entry = ttk.Entry(top)
        date_last_entry.grid(row=1, column=1, padx=(0, 15), pady=(0, 15))

        ttk.Label(top, text="source", background="#ececec").grid(
            row=1, column=2, padx=(0, 5), pady=(0, 15), sticky="e"
        )
        source_entry = ttk.Entry(top)
        source_entry.grid(row=1, column=3, padx=(0, 15), pady=(0, 15))

        # populate entries with data from the selection
        description_entry.insert(0, self.tree.item(selected_item)["values"][1])
        frequency_entry.insert(0, self.tree.item(selected_item)["values"][2])
        period_entry.insert(0, self.tree.item(selected_item)["values"][3])
        date_last_entry.insert(0, self.tree.item(selected_item)["values"][4])
        source_entry.insert(0, self.tree.item(selected_item)["values"][6])

        # update database
        def update_item():
            cur.execute(
                """
                UPDATE reminders
                SET (description, frequency, period, date_last, source) =
                    (?, ?, ?, ?, ?)
                WHERE id = ? """,
                (
                    description_entry.get(),
                    frequency_entry.get(),
                    period_entry.get(),
                    date_last_entry.get(),
                    source_entry.get(),
                    self.tree.item(selected_item)["values"][0],
                ),
            )
            con.commit()
            remove_toplevels(self)
            self.refresh()

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
            self.refresh()
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
