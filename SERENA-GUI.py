import os
import json
import traceback
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()
import preprocess
from tkinter import Tk, Label, Button, Entry, filedialog, ttk, messagebox, Frame
from tkinterweb import HtmlFrame  # Ensure `tkinterweb` is installed



# JSON Table Column Mapping
KEY_COLUMNS = [
    "Service Name",
    "Action Datetime",
    "Message Datetime",
    "Action Keyword",
    "Address1",
    "Address2",
    "Amount",
    "Item"
]

KEY_MAPPING = {
    "service_name": "Service Name",
    "action_datetime": "Action Datetime",
    "message_datetime": "Message Datetime",
    "action_keyword": "Action Keyword",
    "address1": "Address1",
    "address2": "Address2",
    "amount": "Amount",
    "item": "Item"
}


KEY_COLORS = {
    "service_name": "yellow",
    "action_datetime": "lightgreen",
    "message_datetime": "lightblue",
    "action_keyword": "pink",
    "address1": "silver",
    "address2": "plum",
    "amount": "peachpuff",
    "item": "lavender",
    "mobile_number": "magenta"
}


class TextToHtmlApp:
    def __init__(self, master):
        self.master = master
        master.title("SERENA - Your Forensic AI-Assistant")
        master.geometry("1200x650")  

        # ✅ Initialize extracted JSON storage
        self.normalized_json_list = None

        self.left_frame = self.create_frame(master, "left")
        self.right_frame = self.create_frame(master, "right")

        # Left Panel (File Selection & Processing)
        self.input_folder_entry = self.create_labeled_entry(self.left_frame, "Select Folder:")
        self.create_button(self.left_frame, "📂 Browse", self.browse_json_folder, bg="#4CAF50", fg="white")
        self.create_button(self.left_frame, "🌟 Highlight All HTML Files", self.highlight_all_html, bg="#008CBA", fg="white")
        self.create_button(self.left_frame, "🔍 Highlight Selected File", self.highlight_selected_file, bg="#f44336", fg="white")

        # Tree view for HTML files
        self.tree_label = Label(self.left_frame, text="📄 HTML Files in Folder:", font=("Arial", 11, "bold"))
        self.tree_label.pack(pady=5)
        self.file_tree = self.create_file_tree(self.left_frame)
        self.create_button(self.left_frame, "🔄 Refresh File Tree", self.refresh_file_tree, bg="#555", fg="white")

        # Right Panel (HTML Viewer & JSON Table)
        self.html_viewer = HtmlFrame(self.right_frame)
        self.html_viewer.pack(fill="both", expand=False, pady=5, ipady=30)  

        # ✅ Added Horizontal Legend Below HTML Viewer
        self.legend_frame = self.create_legend(self.right_frame)

        # ✅ JSON Table Label
        self.json_table_label = Label(self.right_frame, text="Extracted JSON Data:", font=("Arial", 11, "bold"))
        self.json_table_label.pack(pady=(5, 5))

        # ✅ Move "Load JSON Data" button ABOVE JSON Table
        self.load_json_button = Button(
            self.right_frame, text="📥 Load JSON Data", command=self.load_json_table,
            bg="#FF9800", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5
        )
        self.load_json_button.pack(pady=(5, 5))  

        # ✅ Create the JSON Table (Only Once)
        self.json_table = self.create_json_table(self.right_frame)

    def create_frame(self, parent, side):
        """Creates a frame for UI layout."""
        frame = ttk.Frame(parent)
        frame.pack(side=side, fill="both", expand=True, padx=10, pady=5)
        return frame

    def create_labeled_entry(self, parent, label_text):
        """Creates an entry field with a label."""
        Label(parent, text=label_text, font=("Arial", 11)).pack()
        entry = Entry(parent, width=50, font=("Arial", 10))
        entry.pack()
        return entry

    def create_button(self, parent, text, command, bg="#333", fg="white"):
        """Creates a styled button."""
        Button(parent, text=text, command=command, bg=bg, fg=fg, font=("Arial", 10, "bold"), padx=10, pady=3).pack(pady=5)

    def create_file_tree(self, parent):
        """Creates a tree view to display HTML files."""
        tree = ttk.Treeview(parent, columns=("Files"), show="headings", height=10)
        tree.heading("Files", text="HTML Files")
        tree.bind("<Double-1>", self.open_html_file)
        tree.pack(fill='both', expand=True)
        return tree

    def create_legend(self, parent):
        """Creates a horizontal color legend."""
        legend_frame = Frame(parent, bg="white", pady=5)
        legend_frame.pack(fill="x", padx=10, pady=5)

        for key, color in KEY_COLORS.items():
            label_frame = Frame(legend_frame, padx=5, pady=2, bg="white")
            label_frame.pack(side="left", padx=5)

            color_box = Label(label_frame, width=2, height=1, bg=color, relief="solid", borderwidth=1)
            color_box.pack(side="left", padx=3)

            text_label = Label(label_frame, text=KEY_MAPPING.get(key, key), font=("Arial", 10), bg="white")
            text_label.pack(side="left")

        return legend_frame

    def create_json_table(self, parent):
        """Creates a table to display JSON data."""
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        table = ttk.Treeview(frame, columns=KEY_COLUMNS, show="headings", height=3)
        table.pack(fill="both", expand=True)

        for column in KEY_COLUMNS:
            table.heading(column, text=column)
            table.column(column, width=130, anchor="center")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
        scrollbar.pack(side="right", fill="y")
        table.configure(yscrollcommand=scrollbar.set)

        return table

    def browse_json_folder(self):
        """Allows the user to select a folder and process JSON & HTML files."""
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder_entry.delete(0, 'end')
            self.input_folder_entry.insert(0, folder)
            self.json_folder_entry, self.html_folder_entry = preprocess.preprocess(folder)
            self.refresh_file_tree()

    def refresh_file_tree(self):
        """Refreshes the file tree to display available HTML files."""
        self.file_tree.delete(*self.file_tree.get_children())
        if hasattr(self, "html_folder_entry") and os.path.exists(self.html_folder_entry):
            for file_name in os.listdir(self.html_folder_entry):
                if file_name.endswith('.html'):
                    self.file_tree.insert("", "end", values=(file_name,))

    def highlight_all_html(self):
        """Applies highlighting to all HTML files in the directory."""
        if hasattr(self, "html_folder_entry") and hasattr(self, "json_folder_entry"):
            for file_name in os.listdir(self.html_folder_entry):
                if file_name.endswith('.html'):
                    highlighted_content = self.load_and_highlight_html(file_name)
                    if highlighted_content:
                        with open(os.path.join(self.html_folder_entry, file_name), 'w', encoding='utf-8') as html_file:
                            html_file.write(highlighted_content)
            self.refresh_file_tree()

    def highlight_selected_file(self):
        """Applies highlighting to the selected HTML file."""
        selected_item = self.file_tree.selection()
        if selected_item:
            file_name = self.file_tree.item(selected_item, 'values')[0]
            highlighted_content = self.load_and_highlight_html(file_name)
            if highlighted_content:
                with open(os.path.join(self.html_folder_entry, file_name), 'w', encoding='utf-8') as html_file:
                    html_file.write(highlighted_content)
        self.refresh_file_tree()

    def open_html_file(self, event):
        """Opens and displays an HTML file when selected from the tree view."""
        selected_item = self.file_tree.selection()
        if selected_item:
            file_name = self.file_tree.item(selected_item, 'values')[0]
            highlighted_content = self.load_and_highlight_html(file_name)
            soup = BeautifulSoup(highlighted_content, 'html5lib')
            clean_html = str(soup)
            self.html_viewer.load_html(
                highlighted_content if highlighted_content else "<html><body><p>No highlights applied.</p></body></html>")

    def load_and_highlight_html(self, file_name):
        """Loads an HTML file, finds the corresponding JSON data, and applies highlights."""
        json_dir = getattr(self, "json_folder_entry", "")
        html_dir = getattr(self, "html_folder_entry", "")

        if json_dir and html_dir:
            for json_file_name in os.listdir(json_dir):
                if json_file_name.endswith('.json'):
                    json_file_path = os.path.join(json_dir, json_file_name)
                    with open(json_file_path, 'r', encoding='utf-8') as json_file:
                        json_data = json.load(json_file)

                    source_path = json_data.get("source_path", "")
                    if os.path.basename(source_path).replace('.txt', '.html') == file_name:
                        html_file_path = os.path.join(html_dir, file_name)
                        if os.path.exists(html_file_path):
                            with open(html_file_path, 'r', encoding='utf-8') as html_file:
                                return self.highlight_json_in_html_content(html_file.read(), json_data)
        return None

    def highlight_json_in_html_content(self, html_content, json_data):
        """Highlights JSON values in the HTML content while avoiding tag attributes and redundant span tags."""
        soup = BeautifulSoup(html_content, "html.parser")

        def highlight_text(text, value, color):
            """Highlights text only if it's not already inside a <span>."""
            if value in text and f'<span' not in text:
                return text.replace(value, f'<span style="background-color: {color};">{value}</span>')
            return text

        # JSON 값이 있는 경우에만 하이라이트 적용
        for key, color in KEY_COLORS.items():
            value = json_data.get(key)
            if isinstance(value, str) and value.strip():  # 값이 문자열이고 공백이 아닐 때만 실행
                for text_node in soup.find_all(string=True):
                    if text_node.parent.name not in ['script', 'style'] and not text_node.parent.attrs:
                        updated_text = highlight_text(text_node, value, color)
                        if updated_text != text_node:
                            text_node.replace_with(BeautifulSoup(updated_text, "html.parser"))

        return str(soup)


    def load_json_table(self):
        """Loads extracted and normalized JSON data into the table."""
        self.json_table.delete(*self.json_table.get_children())

        if not hasattr(self, "json_folder_entry") or not os.path.exists(self.json_folder_entry):
            messagebox.showerror("Error", "JSON folder is not selected or does not exist.")
            return

        if not hasattr(self, "normalized_json_list"):
            self.normalized_json_list = []

        if self.normalized_json_list:
            print(f"DEBUG: Using cached JSON data ({len(self.normalized_json_list)} objects)")
        else:
            print(f"DEBUG: Calling extract_keywords() for folder -> {self.json_folder_entry}")

            from named_entitiy_recognition import extract_keywords
            extracted_data = extract_keywords([self.json_folder_entry], self.json_folder_entry)

            if extracted_data:
                self.normalized_json_list = extracted_data
                print(f"✅ Cached {len(self.normalized_json_list)} JSON objects.")
            else:
                print("⚠ No new data extracted, keeping previous cache.")

        if not self.normalized_json_list:
            messagebox.showwarning("Warning", "No valid data extracted from files.")
            return

        for i, json_data in enumerate(self.normalized_json_list):
            row = [json_data.get(key, "") for key in KEY_MAPPING.keys()]
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.json_table.insert("", "end", values=row, tags=(tag,))

        self.json_table.tag_configure("evenrow", background="#f2f2f2")
        self.json_table.tag_configure("oddrow", background="white")


def main():
    """Starts the Tkinter GUI application."""
    root = Tk()
    app = TextToHtmlApp(root)
    root.mainloop()


if __name__ == "__main__":
    main() 
