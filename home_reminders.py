import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk  # noqa: F401

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

# select data for display
data = cur.execute("""
    SELECT * FROM reminders
    WHERE date_next >= DATE('now')
    ORDER BY date_next ASC
""")


class App(tk.Tk):
    def __init__(self, **kw):
        super().__init__(**kw)

        self.title("Home Reminders")
        self.geometry("1000x300")
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # create variable to prevent activation of
        # treeview_on_selection_changed after refresh
        self.refreshed = False

        # create main screen
        self.btn = ttk.Button(
            self, text="New Item", command=self.create_new
        ).grid(row=1, column=0, padx=20, pady=(40, 0), sticky="n")
        self.btn = ttk.Button(self, text="Refresh", command=self.refresh).grid(
            row=1, column=0, padx=20, sticky="ew"
        )
        self.btn = ttk.Button(
            self, text="Quit", command=self.quit_program
        ).grid(row=1, column=0, padx=20, pady=(0, 40), sticky="s")
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
        self.tree = self.create_tree_widget()

    def create_tree_widget(self):
        """
        Create treeview to display data from database

        Returns:
            ttk.Treeview
        """
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

        # add data from database to the treeview
        for item in data:
            tree.insert("", tk.END, values=item)

        return tree

    # function to destroy existing toplevels to prevent them from accumulating.
    def remove_toplevels(self):
        for widget in self.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()

    # create top level window for entry of data for new item
    def create_new(self):
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

        def save_item():
            data_get = (
                description_entry.get(),
                frequency_entry.get(),
                period_entry.get(),
                date_last_entry.get(),
                source_entry.get(),
            )
            cur.execute(
                "INSERT INTO reminders (description, frequency, period, date_last, source) VALUES (?, ?, ?, ?, ?)",  # noqa: E501
                data_get,
            )
            con.commit()
            self.refresh()
            description_entry.delete(0, tk.END)
            frequency_entry.delete(0, tk.END)
            period_entry.delete(0, tk.END)
            date_last_entry.delete(0, tk.END)
            source_entry.delete(0, tk.END)

        def cancel():
            self.remove_toplevels()
            self.tree.focus()

        ttk.Button(top, text="Save", command=save_item).grid(
            row=2, column=1, padx=(33, 0), pady=(15, 0), sticky="w"
        )

        ttk.Button(top, text="Cancel", command=cancel).grid(
            row=2, column=3, padx=(0, 48), pady=(15, 0), sticky="e"
        )

    def refresh(self):
        data = cur.execute("""
            SELECT * FROM reminders
            WHERE date_next >= DATE('now')
            ORDER BY date_next ASC
        """)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for item in data:
            self.tree.insert("", tk.END, values=item)
        self.focus()
        self.refreshed = True

    def quit_program(self):
        self.destroy()

    def on_treeview_selection_changed(self, event):
        """
        Create TopLevel to manage selected row(s)

        :param event
        :return: None
        """
        if self.refreshed:
            self.refreshed = False
            return

        selected_item = self.tree.focus()

        top = tk.Toplevel(self, padx=20, pady=20)
        top.title("Selection")
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

        description_entry.insert(0, self.tree.item(selected_item)["values"][1])
        frequency_entry.insert(0, self.tree.item(selected_item)["values"][2])
        period_entry.insert(0, self.tree.item(selected_item)["values"][3])
        date_last_entry.insert(0, self.tree.item(selected_item)["values"][4])
        source_entry.insert(0, self.tree.item(selected_item)["values"][6])

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
            self.remove_toplevels()
            self.refresh()

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
            self.remove_toplevels()

        def cancel():
            self.remove_toplevels()

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
