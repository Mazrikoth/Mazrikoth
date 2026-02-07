import json
import re
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSET_DIR = BASE_DIR / "assets" / "images"
SAVE_DIR = BASE_DIR / "saves"

IMAGE_TOKEN_RE = re.compile(r"\[(.+?\.(?:png|gif))\]")

TABLE_FILES = {
    "Classes": "classes.json",
    "Races": "races.json",
    "Weapons": "weapons.json",
    "Armor": "armor.json",
    "Items": "items.json",
    "Story Intros": "story_intros.json",
    "Story Guidelines": "story_guidelines.json",
    "Images": "images.json",
    "Story": "story.json",
    "Save Codes": "save_codes.json",
}


def load_json(path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path, payload):
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


class CyoaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DragonZMind CYOA")
        self.geometry("900x700")

        SAVE_DIR.mkdir(exist_ok=True)

        self.story_data = load_json(DATA_DIR / "story.json", {})
        self.save_codes = set(
            load_json(DATA_DIR / "save_codes.json", {"codes": []}).get("codes", [])
        )
        self.current_node_id = None
        self.active_image = None
        self.save_unlocked = False

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill=tk.BOTH, expand=True)

        self.player_frame = ttk.Frame(self.tabs)
        self.creator_frame = ttk.Frame(self.tabs)

        self.tabs.add(self.player_frame, text="Player")
        self.tabs.add(self.creator_frame, text="Creator")

        self._build_player_tab()
        self._build_creator_tab()

        self.start_new_adventure()

    def _build_player_tab(self):
        control_frame = ttk.Frame(self.player_frame)
        control_frame.pack(fill=tk.X, padx=12, pady=8)

        ttk.Label(control_frame, text="Save Code:").pack(side=tk.LEFT)
        self.code_entry = ttk.Entry(control_frame, width=25)
        self.code_entry.pack(side=tk.LEFT, padx=6)
        ttk.Button(control_frame, text="Unlock Save", command=self.unlock_save).pack(
            side=tk.LEFT
        )

        ttk.Button(control_frame, text="Load Save", command=self.load_save).pack(
            side=tk.RIGHT, padx=6
        )
        ttk.Button(control_frame, text="Save", command=self.save_progress).pack(
            side=tk.RIGHT
        )

        self.story_text = tk.Text(self.player_frame, wrap=tk.WORD, height=12)
        self.story_text.pack(fill=tk.X, padx=12, pady=(0, 8))
        self.story_text.configure(state=tk.DISABLED)

        self.image_label = ttk.Label(self.player_frame, text="")
        self.image_label.pack(pady=4)

        self.choice_frame = ttk.Frame(self.player_frame)
        self.choice_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

    def _build_creator_tab(self):
        top_frame = ttk.Frame(self.creator_frame)
        top_frame.pack(fill=tk.X, padx=12, pady=8)

        ttk.Label(top_frame, text="Table:").pack(side=tk.LEFT)
        self.table_choice = ttk.Combobox(
            top_frame, values=list(TABLE_FILES.keys()), state="readonly"
        )
        self.table_choice.pack(side=tk.LEFT, padx=6)
        self.table_choice.bind("<<ComboboxSelected>>", self.load_table)

        ttk.Button(top_frame, text="Reload", command=self.load_table).pack(side=tk.LEFT)
        ttk.Button(top_frame, text="Save", command=self.save_table).pack(side=tk.LEFT)

        self.editor = tk.Text(self.creator_frame, wrap=tk.NONE)
        self.editor.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

    def start_new_adventure(self):
        if not self.story_data:
            messagebox.showerror("Missing Story", "Story data is not available.")
            return
        self.current_node_id = self.story_data.get("start")
        self.render_current_node()

    def render_current_node(self):
        node = self.story_data.get("nodes", {}).get(self.current_node_id)
        if not node:
            messagebox.showerror("Story Error", "Story node not found.")
            return

        text = node.get("text", "")
        image_match = IMAGE_TOKEN_RE.search(text)
        image_file = None
        if image_match:
            image_file = image_match.group(1)
            text = IMAGE_TOKEN_RE.sub("", text).strip()

        self.story_text.configure(state=tk.NORMAL)
        self.story_text.delete("1.0", tk.END)
        self.story_text.insert(tk.END, text)
        self.story_text.configure(state=tk.DISABLED)

        self._render_image(image_file)
        self._render_choices(node.get("choices", []))

    def _render_image(self, image_file):
        if not image_file:
            self.image_label.configure(text="", image="")
            self.active_image = None
            return

        image_path = ASSET_DIR / image_file
        if not image_path.exists():
            self.image_label.configure(
                text=f"Image not found: {image_file}", image=""
            )
            self.active_image = None
            return

        try:
            self.active_image = tk.PhotoImage(file=str(image_path))
            self.image_label.configure(image=self.active_image, text="")
        except tk.TclError:
            self.image_label.configure(
                text=f"Unsupported image format: {image_file}", image=""
            )
            self.active_image = None

    def _render_choices(self, choices):
        for widget in self.choice_frame.winfo_children():
            widget.destroy()

        if not choices:
            ttk.Label(
                self.choice_frame,
                text="The adventure ends here. Start a new adventure to play again.",
            ).pack(anchor=tk.W, pady=4)
            ttk.Button(
                self.choice_frame, text="Start New Adventure", command=self.start_new_adventure
            ).pack(anchor=tk.W, pady=4)
            return

        for choice in choices:
            label = choice.get("label", "Continue")
            next_node = choice.get("next")
            ttk.Button(
                self.choice_frame,
                text=label,
                command=lambda node_id=next_node: self._choose_next(node_id),
            ).pack(anchor=tk.W, fill=tk.X, pady=2)

    def _choose_next(self, node_id):
        if node_id not in self.story_data.get("nodes", {}):
            messagebox.showerror("Story Error", "Next story node not found.")
            return
        self.current_node_id = node_id
        self.render_current_node()

    def unlock_save(self):
        code = self.code_entry.get().strip()
        if not code:
            messagebox.showwarning("Missing Code", "Enter a save code.")
            return
        if code in self.save_codes:
            self.save_unlocked = True
            messagebox.showinfo("Unlocked", "Save and load are now enabled.")
        else:
            messagebox.showerror("Invalid Code", "That save code is not valid.")

    def save_progress(self):
        if not self.save_unlocked:
            messagebox.showwarning(
                "Save Locked", "Enter a valid save code to enable saving."
            )
            return

        save_payload = {
            "node_id": self.current_node_id,
        }
        save_json(SAVE_DIR / "latest_save.json", save_payload)
        messagebox.showinfo("Saved", "Progress saved.")

    def load_save(self):
        if not self.save_unlocked:
            messagebox.showwarning(
                "Load Locked", "Enter a valid save code to enable loading."
            )
            return

        save_path = SAVE_DIR / "latest_save.json"
        if not save_path.exists():
            messagebox.showwarning("No Save", "No saved game found.")
            return
        save_payload = load_json(save_path, {})
        node_id = save_payload.get("node_id")
        if not node_id:
            messagebox.showerror("Save Error", "Save file is missing node data.")
            return
        self.current_node_id = node_id
        self.render_current_node()

    def load_table(self, _event=None):
        table_name = self.table_choice.get()
        if not table_name:
            return
        table_path = DATA_DIR / TABLE_FILES[table_name]
        payload = load_json(table_path, {})
        self.editor.delete("1.0", tk.END)
        self.editor.insert(tk.END, json.dumps(payload, indent=2))

    def save_table(self):
        table_name = self.table_choice.get()
        if not table_name:
            messagebox.showwarning("No Table", "Select a table to save.")
            return
        table_path = DATA_DIR / TABLE_FILES[table_name]
        try:
            payload = json.loads(self.editor.get("1.0", tk.END))
        except json.JSONDecodeError as exc:
            messagebox.showerror("Invalid JSON", f"Fix JSON error: {exc}")
            return
        save_json(table_path, payload)
        if table_name == "Save Codes":
            self.save_codes = set(payload.get("codes", []))
        if table_name == "Story":
            self.story_data = payload
        messagebox.showinfo("Saved", f"{table_name} saved successfully.")


if __name__ == "__main__":
    app = CyoaApp()
    app.mainloop()
