from pathlib import Path
import random
import tkinter as tk
from tkinter import messagebox, ttk


# Number ranges for each difficulty option
DIFFICULTY_RANGES = {
    1: ("Easy", 1, 9),
    2: ("Moderate", 10, 99),
    3: ("Advanced", 1000, 9999),
}

SCORES_FILE = Path(__file__).resolve().parent / "best_scores.txt"


def randomInt(level):
    """Return a random integer matching the selected difficulty level."""
    if level not in DIFFICULTY_RANGES:
        raise ValueError("Difficulty level must be 1, 2, or 3.")
    _, low, high = DIFFICULTY_RANGES[level]
    return random.randint(low, high)


def decideOperation():
    """Randomly pick addition or subtraction."""
    return random.choice(["+", "-"])


def isCorrect(user_answer, expected_answer, attempt):
    """Check the user's answer and return (correct, points, feedback)."""
    if user_answer == expected_answer:
        points = 10 if attempt == 1 else 5
        if attempt == 1:
            return True, points, "Correct! +10 points."
        return True, points, "Correct on your second try! +5 points."

    if attempt == 1:
        return False, 0, "Wrong answer. Have one more try for 5 points."
    return False, 0, f"Wrong again. The correct answer was {expected_answer}."


def get_grade(score):
    """Convert a score out of 100 into a rank."""
    if score > 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def load_best_scores(path=SCORES_FILE):
    scores = {}
    if not path.exists():
        return scores
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            name, value = line.split(":", 1)
            try:
                scores[name.strip()] = int(value.strip())
            except ValueError:
                pass
    return scores


def save_best_score(level_name, score, path=SCORES_FILE):
    scores = load_best_scores(path)
    if score > scores.get(level_name, -1):
        scores[level_name] = score
        lines = [f"{k}:{v}" for k, v in scores.items()]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return True
    return False


class MathsQuizApp:
    def __init__(self, root, scores_path=SCORES_FILE):
        self.root = root
        self.scores_path = scores_path
        self.root.title("Maths Quiz")
        self.root.geometry("600x500")
        self.root.configure(bg="#f4f6f9")

        self.difficulty = 1
        self.question_num = 0
        self.score = 0
        self.attempt = 1
        self.num1 = 0
        self.num2 = 0
        self.operator = "+"
        self.expected = 0
        self.results_log = []

        self.main_frame = tk.Frame(root, bg="#f4f6f9")
        self.main_frame.pack(fill="both", expand=True, padx=24, pady=20)

        self.displayMenu()

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def displayMenu(self):
        """Show the difficulty menu before starting a quiz."""
        self.clear_screen()
        best = load_best_scores(self.scores_path)

        tk.Label(
            self.main_frame,
            text="DIFFICULTY LEVEL",
            font=("Segoe UI", 18, "bold"),
            bg="#f4f6f9",
            fg="#1f2937",
        ).pack(pady=(12, 6))

        tk.Label(
            self.main_frame,
            text="Select a difficulty to start a 10-question quiz (10 pts 1st try, 5 pts 2nd try):",
            font=("Segoe UI", 10),
            bg="#f4f6f9",
            fg="#4b5563",
        ).pack(pady=(0, 18))

        options = [
            (1, "Easy", "1. Easy  (single-digit: 1 - 9)"),
            (2, "Moderate", "2. Moderate  (double-digit: 10 - 99)"),
            (3, "Advanced", "3. Advanced  (4-digit: 1000 - 9999)"),
        ]

        for level, name, label in options:
            row = tk.Frame(self.main_frame, bg="#ffffff", bd=1, relief="solid", padx=14, pady=10)
            row.pack(fill="x", pady=6)

            ttk.Button(
                row,
                text=label,
                width=34,
                command=lambda lvl=level: self.start_quiz(lvl),
            ).pack(side="left")

            best_txt = f"Best: {best[name]}/100" if name in best else "No score yet"
            tk.Label(
                row,
                text=best_txt,
                font=("Segoe UI", 9, "bold"),
                bg="#ffffff",
                fg="#047857" if name in best else "#6b7280",
            ).pack(side="right", padx=8)

    def start_quiz(self, level):
        self.difficulty = level
        self.question_num = 0
        self.score = 0
        self.results_log = []
        self.next_question()

    def next_question(self):
        if self.question_num >= 10:
            self.displayResults()
            return

        self.question_num += 1
        self.attempt = 1
        self.num1 = randomInt(self.difficulty)
        self.num2 = randomInt(self.difficulty)
        self.operator = decideOperation()
        self.expected = self.num1 + self.num2 if self.operator == "+" else self.num1 - self.num2
        self.displayProblem()

    def displayProblem(self):
        """Show the current arithmetic question and answer entry box."""
        self.clear_screen()
        level_name = DIFFICULTY_RANGES[self.difficulty][0]

        info_row = tk.Frame(self.main_frame, bg="#f4f6f9")
        info_row.pack(fill="x", pady=(0, 8))

        tk.Label(
            info_row,
            text=f"{level_name} | Question {self.question_num} of 10",
            font=("Segoe UI", 10, "bold"),
            bg="#f4f6f9",
            fg="#374151",
        ).pack(side="left")

        self.score_label = tk.Label(
            info_row,
            text=f"Score: {self.score}/100",
            font=("Segoe UI", 10, "bold"),
            bg="#f4f6f9",
            fg="#1d4ed8",
        )
        self.score_label.pack(side="right")

        progress = ttk.Progressbar(self.main_frame, maximum=10, value=self.question_num - 1)
        progress.pack(fill="x", pady=(0, 14))

        card = tk.Frame(self.main_frame, bg="#ffffff", bd=1, relief="solid", padx=24, pady=24)
        card.pack(fill="both", expand=True)

        self.attempt_label = tk.Label(
            card,
            text="Attempt 1 of 2 (10 points)",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#6b7280",
        )
        self.attempt_label.pack()

        tk.Label(
            card,
            text=f"{self.num1} {self.operator} {self.num2} =",
            font=("Consolas", 30, "bold"),
            bg="#ffffff",
            fg="#111827",
        ).pack(pady=18)

        entry_row = tk.Frame(card, bg="#ffffff")
        entry_row.pack(pady=(0, 12))

        self.answer_entry = tk.Entry(entry_row, font=("Consolas", 16), width=10, justify="center")
        self.answer_entry.pack(side="left", padx=(0, 10))
        self.answer_entry.focus()
        self.answer_entry.bind("<Return>", lambda event: self.check_answer())

        self.submit_btn = ttk.Button(entry_row, text="Submit", command=self.check_answer)
        self.submit_btn.pack(side="left")

        self.feedback_label = tk.Label(
            card,
            text="Type your answer and press Enter (negative numbers are allowed).",
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#4b5563",
        )
        self.feedback_label.pack(pady=(10, 0))

        ttk.Button(self.main_frame, text="Back to Menu", command=self.displayMenu).pack(
            anchor="w", pady=(10, 0)
        )

    def check_answer(self):
        raw = self.answer_entry.get().strip()
        try:
            # Allow negative values because subtraction can go below zero
            user_val = int(raw)
        except ValueError:
            self.feedback_label.config(text="Please enter a whole number.", fg="#b45309")
            return

        correct, points, msg = isCorrect(user_val, self.expected, self.attempt)
        problem_text = f"{self.num1} {self.operator} {self.num2} = {self.expected}"

        if correct:
            self.score += points
            self.results_log.append(f"Q{self.question_num}: {problem_text}  (+{points} pts)")
            self.score_label.config(text=f"Score: {self.score}/100")
            self.feedback_label.config(text=msg, fg="#047857")
            self.submit_btn.config(state="disabled")
            self.root.after(700, self.next_question)
        elif self.attempt == 1:
            self.attempt = 2
            self.attempt_label.config(text="Attempt 2 of 2 (5 points)", fg="#b45309")
            self.feedback_label.config(text=msg, fg="#b45309")
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.focus()
        else:
            self.results_log.append(
                f"Q{self.question_num}: {problem_text}  (your answer: {user_val}, +0 pts)"
            )
            self.feedback_label.config(text=msg, fg="#b91c1c")
            self.submit_btn.config(state="disabled")
            self.root.after(1000, self.next_question)

    def displayResults(self):
        """Show the final score, rank, summary list, and replay option."""
        self.clear_screen()
        level_name = DIFFICULTY_RANGES[self.difficulty][0]
        grade = get_grade(self.score)
        new_best = save_best_score(level_name, self.score, self.scores_path)

        heading = f"Quiz Finished - {level_name}"
        if new_best:
            heading += " (New Best!)"

        tk.Label(
            self.main_frame,
            text=heading,
            font=("Segoe UI", 17, "bold"),
            bg="#f4f6f9",
            fg="#047857" if new_best else "#111827",
        ).pack(pady=(6, 4))

        tk.Label(
            self.main_frame,
            text=f"Final Score: {self.score} / 100   |   Rank: {grade}",
            font=("Segoe UI", 14, "bold"),
            bg="#f4f6f9",
            fg="#1d4ed8",
        ).pack(pady=(0, 12))

        review_box = tk.Listbox(self.main_frame, font=("Consolas", 9), height=11)
        for line in self.results_log:
            review_box.insert(tk.END, line)
        review_box.pack(fill="both", expand=True, pady=(0, 14))

        btns = tk.Frame(self.main_frame, bg="#f4f6f9")
        btns.pack()

        ttk.Button(btns, text="Play Again", command=self.ask_replay).pack(side="left", padx=6)
        ttk.Button(btns, text="Change Level", command=self.displayMenu).pack(side="left", padx=6)
        ttk.Button(btns, text="Quit", command=self.root.destroy).pack(side="left", padx=6)

    def ask_replay(self):
        again = messagebox.askyesno("Play Again", "Would you like to play another round?")
        if again:
            self.start_quiz(self.difficulty)
        else:
            self.displayMenu()


def displayMenu(app):
    app.displayMenu()


def displayProblem(app):
    app.displayProblem()


def displayResults(app):
    app.displayResults()


if __name__ == "__main__":
    window = tk.Tk()
    MathsQuizApp(window)
    window.mainloop()
