import random
import tkinter as tk
from tkinter import messagebox, ttk


# Number ranges for each difficulty option
DIFFICULTY_RANGES = {
    1: ("Easy", 1, 9),
    2: ("Moderate", 10, 99),
    3: ("Advanced", 1000, 9999),
}


def randomInt(level):
    """Return a random integer matching the selected difficulty level."""
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


class MathsQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maths Quiz")
        self.root.geometry("560x440")
        self.root.configure(bg="#f4f6f9")

        self.difficulty = 1
        self.question_num = 0
        self.score = 0
        self.attempt = 1
        self.num1 = 0
        self.num2 = 0
        self.operator = "+"
        self.expected = 0

        self.main_frame = tk.Frame(root, bg="#f4f6f9")
        self.main_frame.pack(fill="both", expand=True, padx=24, pady=20)

        self.displayMenu()

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def displayMenu(self):
        """Show the difficulty menu before starting a quiz."""
        self.clear_screen()

        tk.Label(
            self.main_frame,
            text="DIFFICULTY LEVEL",
            font=("Segoe UI", 18, "bold"),
            bg="#f4f6f9",
            fg="#1f2937",
        ).pack(pady=(10, 6))

        tk.Label(
            self.main_frame,
            text="Choose a level to begin a 10-question arithmetic quiz:",
            font=("Segoe UI", 10),
            bg="#f4f6f9",
            fg="#4b5563",
        ).pack(pady=(0, 18))

        options = [
            (1, "1. Easy  (single-digit: 1 - 9)"),
            (2, "2. Moderate  (double-digit: 10 - 99)"),
            (3, "3. Advanced  (4-digit: 1000 - 9999)"),
        ]

        for level, label in options:
            ttk.Button(
                self.main_frame,
                text=label,
                width=36,
                command=lambda lvl=level: self.start_quiz(lvl),
            ).pack(pady=6, ipady=6)

    def start_quiz(self, level):
        self.difficulty = level
        self.question_num = 0
        self.score = 0
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
        info_row.pack(fill="x", pady=(0, 14))

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
            font=("Consolas", 28, "bold"),
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
            text="Type your answer and press Enter.",
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#4b5563",
        )
        self.feedback_label.pack(pady=(10, 0))

    def check_answer(self):
        raw = self.answer_entry.get().strip()
        try:
            # Signed integers are valid because subtraction can give negative results
            user_val = int(raw)
        except ValueError:
            self.feedback_label.config(text="Please enter a whole number.", fg="#b45309")
            return

        correct, points, msg = isCorrect(user_val, self.expected, self.attempt)

        if correct:
            self.score += points
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
            self.feedback_label.config(text=msg, fg="#b91c1c")
            self.submit_btn.config(state="disabled")
            self.root.after(1000, self.next_question)

    def displayResults(self):
        """Show the final score, rank, and ask if the user wants to play again."""
        self.clear_screen()
        grade = get_grade(self.score)

        tk.Label(
            self.main_frame,
            text="Quiz Finished!",
            font=("Segoe UI", 20, "bold"),
            bg="#f4f6f9",
            fg="#111827",
        ).pack(pady=(20, 10))

        tk.Label(
            self.main_frame,
            text=f"Final Score: {self.score} / 100",
            font=("Segoe UI", 16, "bold"),
            bg="#f4f6f9",
            fg="#1d4ed8",
        ).pack(pady=4)

        tk.Label(
            self.main_frame,
            text=f"Rank: {grade}",
            font=("Segoe UI", 14, "bold"),
            bg="#f4f6f9",
            fg="#047857",
        ).pack(pady=(0, 22))

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
