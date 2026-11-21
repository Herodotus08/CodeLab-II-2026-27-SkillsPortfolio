from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


MARKS_FILE = Path(__file__).resolve().parent.parent / "A1 - Resources" / "studentMarks.txt"


def calculate_grade(percentage):
    """Map an overall percentage out of 160 to grades A-F."""
    if percentage >= 70:
        return "A"
    if percentage >= 60:
        return "B"
    if percentage >= 50:
        return "C"
    if percentage >= 40:
        return "D"
    return "F"


class Student:
    def __init__(self, code, name, cw1, cw2, cw3, exam):
        self.code = int(code)
        self.name = name.strip()
        self.cw1 = int(cw1)
        self.cw2 = int(cw2)
        self.cw3 = int(cw3)
        self.exam = int(exam)

    def coursework_total(self):
        return self.cw1 + self.cw2 + self.cw3

    def overall_total(self):
        return self.coursework_total() + self.exam

    def percentage(self):
        return (self.overall_total() / 160) * 100

    def grade(self):
        return calculate_grade(self.percentage())

    def to_file_line(self):
        return f"{self.code},{self.name},{self.cw1},{self.cw2},{self.cw3},{self.exam}"

    def format_details(self):
        return (
            f"Name:                {self.name}\n"
            f"Student Number:      {self.code}\n"
            f"Coursework Total:    {self.coursework_total()} / 60 ({self.cw1}, {self.cw2}, {self.cw3})\n"
            f"Exam Mark:           {self.exam} / 100\n"
            f"Overall Percentage:  {self.percentage():.2f}%\n"
            f"Grade:               {self.grade()}"
        )


def load_students(file_path=MARKS_FILE):
    """Read studentMarks.txt (skipping the line-1 count) into Student objects."""
    if not file_path.exists():
        raise FileNotFoundError(f"Could not find file: {file_path}")

    lines = [ln.strip() for ln in file_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        return []

    start = 1 if lines[0].isdigit() else 0
    students = []
    for row in lines[start:]:
        parts = [p.strip() for p in row.split(",")]
        if len(parts) == 6:
            students.append(Student(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]))
    return students


def save_students(students, file_path=MARKS_FILE):
    """Write the student count on line 1 followed by each student CSV line."""
    lines = [str(len(students))] + [s.to_file_line() for s in students]
    file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class StudentManagerApp:
    def __init__(self, root, marks_path=MARKS_FILE):
        self.root = root
        self.marks_path = marks_path
        self.root.title("Student Manager")
        self.root.geometry("920x580")
        self.root.configure(bg="#f4f6f9")

        try:
            self.students = load_students(marks_path)
        except FileNotFoundError as err:
            messagebox.showerror("Missing File", str(err))
            self.students = []

        self.search_var = tk.StringVar()
        self.build_ui()
        self.view_all_students()

    def build_ui(self):
        sidebar = tk.Frame(self.root, bg="#1f2937", width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="Student Manager",
            font=("Segoe UI", 14, "bold"),
            bg="#1f2937",
            fg="#ffffff",
        ).pack(anchor="w", padx=16, pady=(18, 12))

        menu_buttons = [
            ("1. View All Students", self.view_all_students),
            ("2. View Individual Student", self.view_individual_student),
            ("3. Highest Total Score", self.view_highest_student),
            ("4. Lowest Total Score", self.view_lowest_student),
        ]
        for text, action in menu_buttons:
            tk.Button(
                sidebar,
                text=text,
                command=action,
                anchor="w",
                bg="#1f2937",
                fg="#f3f4f6",
                activebackground="#374151",
                activeforeground="#ffffff",
                relief="flat",
                padx=16,
                pady=8,
                font=("Segoe UI", 10),
            ).pack(fill="x")

        main = tk.Frame(self.root, bg="#f4f6f9")
        main.pack(side="left", fill="both", expand=True, padx=18, pady=16)

        self.title_label = tk.Label(
            main,
            text="All Student Records",
            font=("Segoe UI", 16, "bold"),
            bg="#f4f6f9",
            fg="#111827",
        )
        self.title_label.pack(anchor="w")

        self.summary_label = tk.Label(
            main,
            text="",
            font=("Segoe UI", 10),
            bg="#f4f6f9",
            fg="#4b5563",
        )
        self.summary_label.pack(anchor="w", pady=(2, 10))

        search_row = tk.Frame(main, bg="#f4f6f9")
        search_row.pack(fill="x", pady=(0, 10))

        tk.Label(search_row, text="Student (name or code):", bg="#f4f6f9").pack(side="left", padx=(0, 6))
        self.student_box = ttk.Combobox(search_row, textvariable=self.search_var, width=28)
        self.student_box.pack(side="left", padx=(0, 8))
        ttk.Button(search_row, text="View", command=self.show_selected_student).pack(side="left")

        cols = ("code", "name", "cw", "exam", "pct", "grade")
        self.tree = ttk.Treeview(main, columns=cols, show="headings", height=11)
        headings = [
            ("code", "Student No.", 90),
            ("name", "Name", 180),
            ("cw", "Coursework (/60)", 120),
            ("exam", "Exam (/100)", 90),
            ("pct", "Overall (%)", 95),
            ("grade", "Grade", 60),
        ]
        for col, heading, width in headings:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor="w" if col == "name" else "center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

        self.details_text = tk.Text(main, height=8, font=("Consolas", 10), bg="#ffffff", padx=10, pady=8)
        self.details_text.pack(fill="x", pady=(10, 0))
        self.details_text.config(state="disabled")

        self.refresh_dropdown()

    def refresh_dropdown(self):
        self.student_box["values"] = [f"{s.code} - {s.name}" for s in self.students]

    def show_table(self, student_list):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for s in student_list:
            self.tree.insert(
                "",
                "end",
                iid=str(s.code),
                values=(
                    s.code,
                    s.name,
                    f"{s.coursework_total()} ({s.cw1}/{s.cw2}/{s.cw3})",
                    s.exam,
                    f"{s.percentage():.2f}%",
                    s.grade(),
                ),
            )

    def set_details(self, text):
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert("1.0", text)
        self.details_text.config(state="disabled")

    def find_by_code(self, code):
        for s in self.students:
            if s.code == code:
                return s
        return None

    def class_average(self):
        if not self.students:
            return 0.0
        return sum(s.percentage() for s in self.students) / len(self.students)

    def on_select_row(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        student = self.find_by_code(int(selected[0]))
        if student:
            self.search_var.set(f"{student.code} - {student.name}")
            self.set_details(student.format_details())

    def view_all_students(self):
        self.title_label.config(text="1. All Student Records")
        avg = self.class_average()
        self.summary_label.config(
            text=f"Number of students: {len(self.students)}   |   Class average: {avg:.2f}%"
        )
        self.show_table(self.students)
        self.refresh_dropdown()
        self.set_details(
            f"Total students: {len(self.students)}\n"
            f"Average percentage mark: {avg:.2f}%\n"
            "Click any student row above to view their full breakdown."
        )

    def view_individual_student(self):
        self.title_label.config(text="2. View Individual Student Record")
        self.summary_label.config(text="Pick a student from the dropdown or type a name / code, then click View.")
        self.student_box.focus()
        if self.search_var.get().strip():
            self.show_selected_student()

    def show_selected_student(self):
        query = self.search_var.get().strip()
        if not query:
            messagebox.showinfo("Search", "Enter a student name or 4-digit student code first.")
            return

        code_part = query.split(" - ", 1)[0].strip()
        matches = []
        if code_part.isdigit():
            exact = self.find_by_code(int(code_part))
            if exact:
                matches = [exact]
        if not matches:
            q_lower = query.lower()
            matches = [s for s in self.students if q_lower in s.name.lower() or q_lower in str(s.code)]

        if not matches:
            messagebox.showwarning("Not Found", f"No student matched '{query}'.")
            return

        self.show_table(matches)
        self.summary_label.config(text=f"Found {len(matches)} matching student(s).")
        self.set_details("\n\n---\n\n".join(s.format_details() for s in matches))

    def view_highest_student(self):
        if not self.students:
            return
        self.title_label.config(text="3. Student With Highest Overall Mark")
        best_score = max(s.overall_total() for s in self.students)
        top = [s for s in self.students if s.overall_total() == best_score]
        self.show_table(top)
        self.summary_label.config(text=f"Highest score: {best_score} / 160 ({top[0].percentage():.2f}%)")
        self.set_details("\n\n---\n\n".join(s.format_details() for s in top))

    def view_lowest_student(self):
        if not self.students:
            return
        self.title_label.config(text="4. Student With Lowest Overall Mark")
        low_score = min(s.overall_total() for s in self.students)
        bottom = [s for s in self.students if s.overall_total() == low_score]
        self.show_table(bottom)
        self.summary_label.config(text=f"Lowest score: {low_score} / 160 ({bottom[0].percentage():.2f}%)")
        self.set_details("\n\n---\n\n".join(s.format_details() for s in bottom))


if __name__ == "__main__":
    window = tk.Tk()
    StudentManagerApp(window)
    window.mainloop()
