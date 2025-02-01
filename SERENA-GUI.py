import os
import json
import preprocess
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox, ttk, Frame
from tkinterweb import HtmlFrame  # Import HtmlFrame from tkinterweb

# Function to highlight JSON values in HTML content with different colors
def highlight_json_in_html_content(html_content, json_data):
    key_colors = {
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

    for key, color in key_colors.items():
        value = json_data.get(key, None)

        if isinstance(value, str) and value in html_content:
            html_content = html_content.replace(
                value, f'<span style="background-color: {color};">{value}</span>'
            )

    # Highlight items if "item" is a list
    if isinstance(json_data.get("item"), list):
        for item in json_data["item"]:
            item_name = item.get("name", "")

            # Highlight item name
            if item_name and item_name in html_content:
                html_content = html_content.replace(
                    item_name, f'<span style="background-color: lavender;">{item_name}</span>'
                )

    return html_content


# Function to load and highlight JSON data in an HTML file
def load_and_highlight_html(html_dir, json_dir, file_name):
    highlighted_content = None
    for json_file_name in os.listdir(json_dir):
        if json_file_name.endswith('.json'):
            json_file_path = os.path.join(json_dir, json_file_name)
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                json_data = json.load(json_file)

            source_path = json_data.get("source_path")
            if not source_path or os.path.basename(source_path).replace('.txt', '.html') != file_name:
                continue

            html_file_path = os.path.join(html_dir, file_name)
            if os.path.exists(html_file_path):
                with open(html_file_path, 'r', encoding='utf-8') as html_file:
                    html_content = html_file.read()
                    highlighted_content = highlight_json_in_html_content(html_content, json_data)
                break
    return highlighted_content

# GUI application class
class TextToHtmlApp:
    def __init__(self, master):
        self.master = master
        master.title("SERENA, Your Forensic Assistant")

        # Layout frames
        self.left_frame = ttk.Frame(master)
        self.left_frame.pack(side="left", fill="y")

        self.right_frame = ttk.Frame(master)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Legend frame
        self.legend_frame = ttk.Frame(self.right_frame, relief="solid", borderwidth=1)
        self.legend_frame.pack(side="bottom", fill="x", padx=5, pady=5)

        self.json_folder_entry = ""
        self.html_folder_entry = ""
        # Add legends
        self.add_legends()

        # Output folder
        self.label_output = Label(self.left_frame, text="Select the folder:")
        self.label_output.pack()

        self.input_folder_entry = Entry(self.left_frame, width=50)
        self.input_folder_entry.pack()

        self.browse_input_folder_button = Button(self.left_frame, text="Browse", command=self.browse_json_folder)
        self.browse_input_folder_button.pack()

        self.highlight_button = Button(self.left_frame, text="Highlight All HTML Files", command=self.highlight_all_html)
        self.highlight_button.pack()

        # File-specific highlight button
        self.highlight_file_button = Button(self.left_frame, text="Highlight Selected File", command=self.highlight_selected_file)
        self.highlight_file_button.pack()

        # HTML file tree
        self.tree_label = Label(self.left_frame, text="HTML Files in Folder:")
        self.tree_label.pack()

        self.file_tree = ttk.Treeview(self.left_frame, columns=("Files"), show="headings")
        self.file_tree.heading("Files", text="HTML Files")
        self.file_tree.bind("<Double-1>", self.open_html_file)
        self.file_tree.pack(fill='both', expand=True)

        self.refresh_tree_button = Button(self.left_frame, text="Refresh File Tree", command=self.refresh_file_tree)
        self.refresh_tree_button.pack()

        # HTML content viewer
        self.viewer_label = Label(self.right_frame, text="HTML Content Viewer:")
        self.viewer_label.pack()

        self.html_viewer = HtmlFrame(self.right_frame)  # Use HtmlFrame for rendering HTML content
        self.html_viewer.pack(fill="both", expand=True)

        # JSON table viewer
        self.json_table_label = Label(self.right_frame, text="JSON Data View")
        self.json_table_label.pack()

        self.json_table = ttk.Treeview(self.right_frame, columns=("Service Name", "Action Datetime", "Message Datetime", "Action Keyword", "Address1", "Address2", "Amount", "Item"), show="headings")
        self.json_table.pack(fill="both", expand=True)

        for column in self.json_table['columns']:
            self.json_table.heading(column, text=column)
            self.json_table.column(column, width=100, anchor="center")

        self.load_json_table_button = Button(self.right_frame, text="Load JSON Data", command=self.load_json_table)
        self.load_json_table_button.pack()

    def add_legends(self):
        """Add color legends for keys."""
        key_colors = {
            "service_name": "yellow",
            "action_datetime": "lightgreen",
            "message_datetime": "lightblue",
            "action_keyword": "pink",
            "address1": "silver",
            "address2": "plum",
            "amount": "peachpuff",
            "item": "lavender"
        }

        Label(self.legend_frame, text="Visualization Legends:").pack(anchor="w", pady=5)
        legend_row = Frame(self.legend_frame)
        legend_row.pack(anchor="w", padx=5, pady=2, fill="x")

        for key, color in key_colors.items():
            color_box = Frame(legend_row, width=20, height=20, bg=color, relief="solid", borderwidth=1)
            color_box.pack(side="left", padx=5)

            Label(legend_row, text=key, anchor="w").pack(side="left", padx=10)

    def browse_json_folder(self):
        folder = filedialog.askdirectory()
        self.input_folder_entry.delete(0, 'end')
        self.input_folder_entry.insert(0, folder)
        self.json_folder_entry, self.html_folder_entry = preprocess.preprocess(folder)
        self.refresh_file_tree()

    def refresh_file_tree(self):
        self.file_tree.delete(*self.file_tree.get_children())
        html_dir = self.html_folder_entry

        if os.path.exists(html_dir):
            for file_name in os.listdir(html_dir):
                if file_name.endswith('.html'):
                    self.file_tree.insert("", "end", values=(file_name,))

    def open_html_file(self, event):
        selected_item = self.file_tree.selection()
        if not selected_item:
            return

        file_name = self.file_tree.item(selected_item, 'values')[0]
        html_dir = self.html_folder_entry
        json_dir = self.json_folder_entry

        if os.path.exists(html_dir) and os.path.exists(json_dir):
            highlighted_content = load_and_highlight_html(html_dir, json_dir, file_name)
            if highlighted_content:
                self.show_html_content(highlighted_content)
            else:
                self.show_html_content(f"<html><body><p>No highlights applied or JSON data not found for {file_name}.</p></body></html>")

    def highlight_all_html(self):
        html_dir = self.html_folder_entry
        json_dir = self.json_folder_entry

        if not os.path.exists(html_dir) or not os.path.exists(json_dir):
            messagebox.showerror("Error", "HTML or JSON folder does not exist.")
            return

        for file_name in os.listdir(html_dir):
            if file_name.endswith('.html'):
                highlighted_content = load_and_highlight_html(html_dir, json_dir, file_name)
                if highlighted_content:
                    with open(os.path.join(html_dir, file_name), 'w', encoding='utf-8') as html_file:
                        html_file.write(highlighted_content)

        messagebox.showinfo("Success", "All HTML files have been highlighted.")
        self.refresh_file_tree()

    def highlight_selected_file(self):
        selected_item = self.file_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No file selected.")
            return

        file_name = self.file_tree.item(selected_item, 'values')[0]

        html_dir = self.html_folder_entry
        json_dir = self.json_folder_entry

        if not os.path.exists(html_dir) or not os.path.exists(json_dir):
            messagebox.showerror("Error", "HTML or JSON folder does not exist.")
            return

        highlighted_content = load_and_highlight_html(html_dir, json_dir, file_name)
        if highlighted_content:
            with open(os.path.join(html_dir, file_name), 'w', encoding='utf-8') as html_file:
                html_file.write(highlighted_content)
            messagebox.showinfo("Success", f"File '{file_name}' has been highlighted.")
            self.refresh_file_tree()
        else:
            messagebox.showinfo("Info", f"No highlights applied or JSON data not found for {file_name}.")

    def show_html_content(self, content):
        self.html_viewer.load_html(content)  # Render the highlighted HTML content

    def load_json_table(self):
        self.json_table.delete(*self.json_table.get_children())
        json_dir = self.json_folder_entry

        if not os.path.exists(json_dir):
            messagebox.showerror("Error", "JSON folder does not exist.")
            return

        for json_file_name in os.listdir(json_dir):
            if json_file_name.endswith('.json'):
                json_file_path = os.path.join(json_dir, json_file_name)
                try:
                    with open(json_file_path, 'r', encoding='utf-8') as json_file:
                        json_data = json.load(json_file)

                    row = [
                        json_data.get("service_name", ""),
                        json_data.get("action_datetime", ""),
                        json_data.get("message_datetime", ""),
                        json_data.get("action_keyword", ""),
                        json_data.get("address1", ""),
                        json_data.get("address2", ""),
                        json_data.get("amount", ""),
                        json_data.get("item", "")
                    ]
                    self.json_table.insert("", "end", values=row)
                except Exception as e:
                    print(f"Error loading JSON file {json_file_name}: {e}")

if __name__ == "__main__":
    root = Tk()
    app = TextToHtmlApp(root)
    root.mainloop()