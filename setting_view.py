import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from page_view import AudioPage, LanguagePage


class SettingsView(ttk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)

        # Key: setting name (such as 'Language' or 'Audio')
        # Value: Page object (ttk.Frame)
        self.pages = {}

        # Give row 0 and column 1 as much room as it needs
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.create_frame_treeview().grid(row=0, column=0, sticky="ens")
        self.create_frame_page().grid(row=0, column=1)

    def create_frame_page(self) -> ttk.Frame:
        """
        Create the frame that will show the current setting page.

        :return: ttk.Frame
        """
        self.frame_page = ttk.Frame(self)
        return self.frame_page

    def create_frame_treeview(self) -> ttk.Frame:
        """
        Create the frame that will hold the settings treeview widget
        and also instantiate the Settingstreeview class

        :return ttk.Frame
        """
        self.frame_treeview = ttk.Frame(self)
        self.treeview_settings = SettingsTreeview(self.frame_treeview)
        self.treeview_settings.bind(
            "<<TreeviewSelect>>", self.on_treeview_selection_changed
        )
        self.treeview_settings.pack(fill=tk.BOTH, expand=True)
        return self.frame_treeview

    def on_treeview_selection_changed(self, event):
        """
        Switch to the frame related to the newly selected setting.

        :param event
        :return: None
        """
        selected_item = self.treeview_settings.focus()
        setting_name = self.treeview_settings.item(selected_item).get("text")
        self.show_page(setting_name)

    def show_page(self, setting_name: str):
        """
        pack_forget() all pages and pack the given page name.

        :param setting_name: the setting/page to show
        :return: None
        """
        for page_name in self.pages.keys():
            self.pages[page_name].pack_forget()
        self.pages[setting_name].pack(fill=tk.BOTH, expand=True)

    def add_page(self, image_path: str, setting_name: str, page):
        """
        Instantiate a page frame and add it to the pages dictionary.

        :param image_path: a path to an image file
        :param setting_name: (str)
        :param page: a Page clasdass
        :return: None
        """
        # Load the image and convert it to a photo image
        with Image.open(image_path) as img:
            # Convert it to a photo image
            photo_image = ImageTk.PhotoImage(img)

        # Add page to dictionary so we can show it when needed
        self.pages[setting_name] = page(self.frame_page)

        # Keep a reference to the image so that it doesn't get garbage
        # collected
        self.pages[setting_name].image = photo_image

        # Insert the setting name into the settings treeview.
        self.treeview_settings.add_setting(
            image=photo_image, section_text=setting_name
        )


class SettingsTreeview(ttk.Treeview):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)

        self.heading("#0", text="Settings")

    def add_setting(self, image, section_text: str):
        """
        Insert a row

        :param imate: photo image
        :param section_text: str
        : return: None
        """
        self.insert(parent="", index=tk.END, image=image, text=section_text)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("640x480")
    root.title("Page Switcher")
    style = ttk.Style()
    style.configure("Treeview.Heading", relief="flat", background="white")
    style.configure("Treeview", rowheight=28)
    style.map(
        "Treeview",
        foreground=[("selected", "darkgreen")],
        background=[("selected", "lightgreen")],
    )
    style.configure("TLabel", font=("tkDefaultFont", 18))
    settings = SettingsView(root, relief="flat")
    settings.add_page(
        image_path="image.png",
        setting_name="   Language",
        page=LanguagePage,
    )
    settings.add_page(
        image_path="image.png",
        setting_name="   Audio",
        page=AudioPage,
    )
    settings.pack(fill=tk.BOTH, expand=True)

    root.mainloop()
