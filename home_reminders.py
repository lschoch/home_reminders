import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk  # noqa: F401

con = sqlite3.connect("home_reminders.db")
cur = con.cursor()

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

data = cur.execute("SELECT * FROM reminders ORDER BY id DESC")


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Home Reminders")
        self.geometry("1000x300")
        self.style = ttk.Style()
        self.style.theme_use("clam")
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
            text="Select a row to update or delete.",
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
        tree.heading("description", text="Item")
        tree.heading("frequency", text="Frequency")
        tree.heading("period", text="Period")
        tree.heading("date_last", text="Last")
        tree.heading("date_next", text="Next")
        tree.heading("source", text="Source")
        tree.column("id", width=50, anchor="center")
        tree.column("description", anchor="center")
        tree.column("frequency", width=65, anchor="center")
        tree.column("period", width=75, anchor="center")
        tree.column("date_last", width=100, anchor="center")
        tree.column("date_next", width=100, anchor="center")
        tree.column("source", width=200, anchor="w")

        tree.bind("<<TreeviewSelect>>", self.item_selected)
        tree.grid(row=1, column=1)

        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=2, pady=20, sticky="ns")

        # add data to the treeview
        for item in data:
            tree.insert("", tk.END, values=item)

        return tree

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
            print(data_get)
            cur.execute(
                "INSERT INTO reminders (description, frequency, period, date_last, source) VALUES (?, ?, ?, ?, ?)",  # noqa: E501
                data_get,
            )
            con.commit()
            self.refresh()
            top.destroy()

        def cancel():
            top.destroy()

        ttk.Button(top, text="Save", command=save_item).grid(
            row=2, column=1, padx=(33, 0), pady=(15, 0), sticky="w"
        )

        ttk.Button(top, text="Cancel", command=cancel).grid(
            row=2, column=3, padx=(0, 48), pady=(15, 0), sticky="e"
        )

    def refresh(self):
        data = cur.execute("SELECT * FROM reminders ORDER BY id DESC")
        for item in self.tree.get_children():
            self.tree.delete(item)
        for item in data:
            self.tree.insert("", tk.END, values=item)

    def quit_program(self):
        self.destroy()

    def item_selected(self, event):
        pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
