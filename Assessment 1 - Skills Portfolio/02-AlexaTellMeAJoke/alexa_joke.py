from pathlib import Path
import random
import tkinter as tk
from tkinter import messagebox, ttk


JOKES_FILE = Path(__file__).resolve().parent.parent / "A1 - Resources" / "randomJokes.txt"


def load_jokes(file_path=JOKES_FILE):
    """Read randomJokes.txt and split each line into a (setup, punchline) pair."""
    if not file_path.exists():
        raise FileNotFoundError(f"Could not find jokes file: {file_path}")

    jokes = []
    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if "?" not in line:
            continue
        setup, punchline = line.split("?", 1)
        setup = setup.strip() + "?"
        punchline = punchline.strip()
        if punchline:
            jokes.append((setup, punchline))
    return jokes


class JokeApp:
    def __init__(self, root, jokes_path=JOKES_FILE):
        self.root = root
        self.root.title("Alexa - Tell Me a Joke")
        self.root.geometry("620x400")
        self.root.configure(bg="#eef2f7")

        try:
            self.jokes = load_jokes(jokes_path)
        except FileNotFoundError as err:
            messagebox.showerror("Missing File", str(err))
            self.jokes = []

        self.current_joke = None
        self.build_ui()

    def build_ui(self):
        box = tk.Frame(self.root, bg="#eef2f7")
        box.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(
            box,
            text="Alexa Joke Assistant",
            font=("Segoe UI", 18, "bold"),
            bg="#eef2f7",
            fg="#1e293b",
        ).pack(anchor="w")

        card = tk.Frame(box, bg="#ffffff", bd=1, relief="solid", padx=22, pady=24)
        card.pack(fill="both", expand=True, pady=(14, 16))

        self.setup_label = tk.Label(
            card,
            text='Press "Alexa tell me a Joke" to begin.',
            font=("Segoe UI", 14, "bold"),
            bg="#ffffff",
            fg="#111827",
            wraplength=520,
            justify="center",
        )
        self.setup_label.pack(pady=(20, 14))

        self.punchline_label = tk.Label(
            card,
            text="",
            font=("Segoe UI", 13, "italic"),
            bg="#ffffff",
            fg="#047857",
            wraplength=520,
            justify="center",
        )
        self.punchline_label.pack(pady=(4, 10))

        btn_row = tk.Frame(box, bg="#eef2f7")
        btn_row.pack(fill="x")

        ttk.Button(
            btn_row,
            text="Alexa tell me a Joke",
            command=self.tell_joke,
        ).pack(side="left", padx=(0, 8))

        self.punchline_btn = ttk.Button(
            btn_row,
            text="Show Punchline",
            command=self.show_punchline,
            state="disabled",
        )
        self.punchline_btn.pack(side="left", padx=6)

        self.next_btn = ttk.Button(
            btn_row,
            text="Next Joke",
            command=self.tell_joke,
            state="disabled",
        )
        self.next_btn.pack(side="left", padx=6)

        ttk.Button(btn_row, text="Quit", command=self.root.destroy).pack(side="right")

    def tell_joke(self):
        if not self.jokes:
            return
        self.current_joke = random.choice(self.jokes)
        self.setup_label.config(text=self.current_joke[0])
        self.punchline_label.config(text="")
        self.punchline_btn.config(state="normal")
        self.next_btn.config(state="normal")

    def show_punchline(self):
        if self.current_joke is None:
            return
        self.punchline_label.config(text=self.current_joke[1])
        self.punchline_btn.config(state="disabled")


if __name__ == "__main__":
    window = tk.Tk()
    JokeApp(window)
    window.mainloop()
