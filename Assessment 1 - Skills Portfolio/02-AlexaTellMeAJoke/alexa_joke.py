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


def filter_jokes(jokes, keyword="", favourites=None, favourites_only=False):
    """Return jokes matching an optional search term and favourites toggle."""
    result = list(jokes)
    if favourites_only:
        fav_set = favourites or set()
        result = [j for j in result if j in fav_set]
    term = keyword.strip().lower()
    if term:
        result = [j for j in result if term in j[0].lower() or term in j[1].lower()]
    return result


class JokeApp:
    def __init__(self, root, jokes_path=JOKES_FILE):
        self.root = root
        self.root.title("Alexa - Tell Me a Joke")
        self.root.geometry("640x450")
        self.root.configure(bg="#eef2f7")

        try:
            self.jokes = load_jokes(jokes_path)
        except FileNotFoundError as err:
            messagebox.showerror("Missing File", str(err))
            self.jokes = []

        self.remaining_deck = []
        self.favourites = set()
        self.seen = set()
        self.current_joke = None

        self.search_var = tk.StringVar()
        self.fav_only_var = tk.BooleanVar(value=False)

        self.build_ui()

    def build_ui(self):
        box = tk.Frame(self.root, bg="#eef2f7")
        box.pack(fill="both", expand=True, padx=24, pady=20)

        header = tk.Frame(box, bg="#eef2f7")
        header.pack(fill="x")

        tk.Label(
            header,
            text="Alexa Joke Assistant",
            font=("Segoe UI", 18, "bold"),
            bg="#eef2f7",
            fg="#1e293b",
        ).pack(side="left")

        self.counter_label = tk.Label(
            header,
            text=f"0 / {len(self.jokes)} seen",
            font=("Segoe UI", 9, "bold"),
            bg="#eef2f7",
            fg="#475569",
        )
        self.counter_label.pack(side="right", pady=(6, 0))

        # Optional search and favourites filter bar
        filter_row = tk.Frame(box, bg="#eef2f7")
        filter_row.pack(fill="x", pady=(10, 12))

        tk.Label(
            filter_row,
            text="Filter:",
            font=("Segoe UI", 9),
            bg="#eef2f7",
            fg="#334155",
        ).pack(side="left", padx=(0, 6))

        search_entry = tk.Entry(filter_row, textvariable=self.search_var, width=24)
        search_entry.pack(side="left", padx=(0, 12))
        search_entry.bind("<Return>", lambda event: self.tell_joke())

        tk.Checkbutton(
            filter_row,
            text="Favourites only",
            variable=self.fav_only_var,
            bg="#eef2f7",
            fg="#334155",
            command=self.reset_deck,
        ).pack(side="left")

        card = tk.Frame(box, bg="#ffffff", bd=1, relief="solid", padx=22, pady=20)
        card.pack(fill="both", expand=True, pady=(0, 16))

        card_top = tk.Frame(card, bg="#ffffff")
        card_top.pack(fill="x")

        self.fav_btn = ttk.Button(
            card_top,
            text="Save Favourite",
            command=self.toggle_favourite,
            state="disabled",
        )
        self.fav_btn.pack(side="right")

        self.setup_label = tk.Label(
            card,
            text='Press "Alexa tell me a Joke" to hear a setup.',
            font=("Segoe UI", 14, "bold"),
            bg="#ffffff",
            fg="#111827",
            wraplength=540,
            justify="center",
        )
        self.setup_label.pack(pady=(24, 16))

        self.punchline_label = tk.Label(
            card,
            text="",
            font=("Segoe UI", 13, "italic"),
            bg="#ffffff",
            fg="#047857",
            wraplength=540,
            justify="center",
        )
        self.punchline_label.pack(pady=(4, 12))

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

    def reset_deck(self):
        self.remaining_deck = []

    def next_from_deck(self):
        pool = filter_jokes(
            self.jokes,
            keyword=self.search_var.get(),
            favourites=self.favourites,
            favourites_only=self.fav_only_var.get(),
        )
        if not pool:
            return None

        # Keep only items still inside the active filter
        self.remaining_deck = [j for j in self.remaining_deck if j in pool]
        if not self.remaining_deck:
            self.remaining_deck = list(pool)
            random.shuffle(self.remaining_deck)
            # Prevent showing the exact same joke twice across a reshuffle
            if len(self.remaining_deck) > 1 and self.remaining_deck[-1] == self.current_joke:
                self.remaining_deck[0], self.remaining_deck[-1] = (
                    self.remaining_deck[-1],
                    self.remaining_deck[0],
                )
        return self.remaining_deck.pop()

    def tell_joke(self):
        chosen = self.next_from_deck()
        if chosen is None:
            self.setup_label.config(text="No jokes match that filter. Clear the filter and try again.")
            self.punchline_label.config(text="")
            self.punchline_btn.config(state="disabled")
            return

        self.current_joke = chosen
        self.seen.add(chosen)
        self.setup_label.config(text=chosen[0])
        self.punchline_label.config(text="")
        self.punchline_btn.config(state="normal")
        self.next_btn.config(state="normal")
        self.update_fav_button()
        self.counter_label.config(
            text=f"{len(self.seen)} / {len(self.jokes)} seen  |  {len(self.favourites)} saved"
        )

    def show_punchline(self):
        if self.current_joke is None:
            return
        self.punchline_label.config(text=self.current_joke[1])
        self.punchline_btn.config(state="disabled")

    def toggle_favourite(self):
        if self.current_joke is None:
            return
        if self.current_joke in self.favourites:
            self.favourites.remove(self.current_joke)
        else:
            self.favourites.add(self.current_joke)
        self.update_fav_button()
        self.counter_label.config(
            text=f"{len(self.seen)} / {len(self.jokes)} seen  |  {len(self.favourites)} saved"
        )

    def update_fav_button(self):
        if self.current_joke is None:
            self.fav_btn.config(text="Save Favourite", state="disabled")
        elif self.current_joke in self.favourites:
            self.fav_btn.config(text="Saved *", state="normal")
        else:
            self.fav_btn.config(text="Save Favourite", state="normal")


if __name__ == "__main__":
    window = tk.Tk()
    JokeApp(window)
    window.mainloop()
