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
        self.validate()

    def validate(self):
        if not (1000 <= self.code <= 9999):
            raise ValueError("Student code must be between 1000 and 9999.")
        if not self.name or "," in self.name:
            raise ValueError("Student name cannot be empty or contain commas.")
        for label, mark in (("Coursework 1", self.cw1), ("Coursework 2", self.cw2), ("Coursework 3", self.cw3)):
            if not (0 <= mark <= 20):
                raise ValueError(f"{label} must be between 0 and 20.")
        if not (0 <= self.exam <= 100):
            raise ValueError("Exam mark must be between 0 and 100.")

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


def sort_student_list(students, by="percentage", descending=True):
    """Return a sorted copy of the student list."""
    if by == "name":
        return sorted(students, key=lambda s: s.name.lower(), reverse=descending)
    if by == "code":
        return sorted(students, key=lambda s: s.code, reverse=descending)
    return sorted(students, key=lambda s: s.overall_total(), reverse=descending)


class StudentManagerApp:
    def __init__(self, root, marks_path=MARKS_FILE):
        self.root = root
        self.marks_path = marks_path
        self.root.title("Student Manager")
        self.root.geometry("980x620")
        self.root.configure(bg="#f4f6f9")

        try:
            self.students = load_students(marks_path)
        except FileNotFoundError as err:
            messagebox.showerror("Missing File", str(err))
            self.students = []

        self.search_var = tk.StringVar()
        self.sort_by_var = tk.StringVar(value="percentage")
        self.sort_order_var = tk.StringVar(value="Descending")

        self.build_ui()
        self.view_all_students()

    def build_ui(self):
        sidebar = tk.Frame(self.root, bg="#1f2937", width=225)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="Student Manager",
            font=("Segoe UI", 14, "bold"),
            bg="#1f2937",
            fg="#ffffff",
        ).pack(anchor="w", padx=16, pady=(18, 10))

        menu_buttons = [
            ("1. View All Students", self.view_all_students),
            ("2. View Individual Student", self.view_individual_student),
            ("3. Highest Total Score", self.view_highest_student),
            ("4. Lowest Total Score", self.view_lowest_student),
            ("5. Sort Student Records", self.sort_records),
            ("6. Add a Student Record", self.open_add_window),
            ("7. Delete a Student Record", self.delete_student),
            ("8. Update a Student Record", self.open_update_window),
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
                font=("Segoe UI", 9, "bold"),
            ).pack(fill="x")

        main = tk.Frame(self.root, bg="#f4f6f9")
        main.pack(side="left", fill="both", expand=True, padx=18, pady=16)

        self.title_label = tk.Label(
            main,
            text="1. All Student Records",
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

        # Search and sort controls
        toolbar = tk.Frame(main, bg="#f4f6f9")
        toolbar.pack(fill="x", pady=(0, 10))

        tk.Label(toolbar, text="Student:", bg="#f4f6f9").pack(side="left", padx=(0, 6))
        self.student_box = ttk.Combobox(toolbar, textvariable=self.search_var, width=24)
        self.student_box.pack(side="left", padx=(0, 6))
        self.student_box.bind("<Return>", lambda event: self.show_selected_student())
        ttk.Button(toolbar, text="View", command=self.show_selected_student).pack(side="left", padx=(0, 14))

        tk.Label(toolbar, text="Sort:", bg="#f4f6f9").pack(side="left", padx=(0, 6))
        ttk.Combobox(
            toolbar,
            textvariable=self.sort_by_var,
            values=("percentage", "name", "code"),
            state="readonly",
            width=11,
        ).pack(side="left", padx=(0, 6))
        ttk.Combobox(
            toolbar,
            textvariable=self.sort_order_var,
            values=("Descending", "Ascending"),
            state="readonly",
            width=11,
        ).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="Sort", command=self.sort_records).pack(side="left")

        cols = ("code", "name", "cw", "exam", "pct", "grade")
        self.tree = ttk.Treeview(main, columns=cols, show="headings", height=11)
        headings = [
            ("code", "Student No.", 90),
            ("name", "Name", 180),
            ("cw", "Coursework (/60)", 125),
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
        self.details_text.pack(fill="x", pady=(10, 4))
        self.details_text.config(state="disabled")

        self.grades_label = tk.Label(
            main,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg="#f4f6f9",
            fg="#1f2937",
        )
        self.grades_label.pack(anchor="w")

        self.refresh_dropdown()

    def refresh_dropdown(self):
        self.student_box["values"] = [f"{s.code} - {s.name}" for s in self.students]

    def update_grade_counts(self):
        counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for s in self.students:
            counts[s.grade()] += 1
        parts = [f"{g}: {counts[g]}" for g in ("A", "B", "C", "D", "F")]
        self.grades_label.config(text="Grade Breakdown  ->  " + "  |  ".join(parts))

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

    def get_selected_student(self):
        """Return the highlighted table student or the student typed in the search box."""
        selected = self.tree.selection()
        if selected:
            found = self.find_by_code(int(selected[0]))
            if found:
                return found

        query = self.search_var.get().strip()
        if query:
            code_part = query.split(" - ", 1)[0].strip()
            if code_part.isdigit():
                found = self.find_by_code(int(code_part))
                if found:
                    return found
            matches = [s for s in self.students if query.lower() in s.name.lower()]
            if len(matches) == 1:
                return matches[0]

        messagebox.showinfo("Select Student", "Click a student in the table or choose one from the dropdown first.")
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

    # --- Menu Items 1 to 4 (Core) ---

    def view_all_students(self):
        self.title_label.config(text="1. All Student Records")
        avg = self.class_average()
        self.summary_label.config(
            text=f"Number of students: {len(self.students)}   |   Class average: {avg:.2f}%"
        )
        self.show_table(self.students)
        self.refresh_dropdown()
        self.update_grade_counts()
        self.set_details(
            f"Total students: {len(self.students)}\n"
            f"Average percentage mark: {avg:.2f}%\n"
            "Click any student row above to view their complete breakdown."
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

    # --- Menu Items 5 to 8 (Extension Problems) ---

    def sort_records(self):
        descending = self.sort_order_var.get() == "Descending"
        by = self.sort_by_var.get()
        ordered = sort_student_list(self.students, by=by, descending=descending)
        self.title_label.config(text=f"5. Sorted Student Records ({by.title()} - {self.sort_order_var.get()})")
        self.summary_label.config(
            text=f"Total students: {len(ordered)}   |   Class average: {self.class_average():.2f}%"
        )
        self.show_table(ordered)
        if ordered:
            self.set_details(
                f"Sorted by {by} ({self.sort_order_var.get()}).\n"
                f"First record: {ordered[0].name} ({ordered[0].percentage():.2f}%, Grade {ordered[0].grade()})"
            )

    def open_add_window(self):
        popup = tk.Toplevel(self.root)
        popup.title("6. Add a Student Record")
        popup.resizable(False, False)
        popup.grab_set()

        fields = [
            ("Student Code (1000-9999):", tk.StringVar()),
            ("Student Name:", tk.StringVar()),
            ("Coursework 1 (0-20):", tk.StringVar()),
            ("Coursework 2 (0-20):", tk.StringVar()),
            ("Coursework 3 (0-20):", tk.StringVar()),
            ("Exam Mark (0-100):", tk.StringVar()),
        ]
        for idx, (label, var) in enumerate(fields):
            tk.Label(popup, text=label).grid(row=idx, column=0, sticky="w", padx=12, pady=5)
            tk.Entry(popup, textvariable=var, width=24).grid(row=idx, column=1, padx=12, pady=5)

        def save_new():
            try:
                new_student = Student(
                    fields[0][1].get(),
                    fields[1][1].get(),
                    fields[2][1].get(),
                    fields[3][1].get(),
                    fields[4][1].get(),
                    fields[5][1].get(),
                )
                if self.find_by_code(new_student.code) is not None:
                    raise ValueError(f"Student code {new_student.code} already exists.")
            except ValueError as err:
                messagebox.showerror("Invalid Input", str(err), parent=popup)
                return

            self.students.append(new_student)
            save_students(self.students, self.marks_path)
            popup.destroy()
            self.view_all_students()
            self.set_details("Added and saved to studentMarks.txt:\n\n" + new_student.format_details())

        ttk.Button(popup, text="Save Student", command=save_new).grid(
            row=len(fields), column=0, columnspan=2, pady=12
        )

    def delete_student(self):
        target = self.get_selected_student()
        if target is None:
            return

        confirm = messagebox.askyesno(
            "Delete Student",
            f"Delete {target.name} ({target.code}) from studentMarks.txt?",
        )
        if not confirm:
            return

        self.students = [s for s in self.students if s.code != target.code]
        save_students(self.students, self.marks_path)
        self.search_var.set("")
        self.view_all_students()
        self.set_details(f"Deleted {target.name} ({target.code}) and updated studentMarks.txt.")

    def open_update_window(self):
        target = self.get_selected_student()
        if target is None:
            return

        popup = tk.Toplevel(self.root)
        popup.title(f"8. Update {target.name} ({target.code})")
        popup.resizable(False, False)
        popup.grab_set()

        # Sub-menu letting the user choose which field to update
        tk.Label(popup, text="Choose field to update:", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 4)
        )
        field_choice = tk.StringVar(value="Exam Mark")
        field_menu = ttk.Combobox(
            popup,
            textvariable=field_choice,
            values=("Student Name", "Coursework 1", "Coursework 2", "Coursework 3", "Exam Mark"),
            state="readonly",
            width=22,
        )
        field_menu.grid(row=0, column=1, padx=12, pady=(10, 4))

        tk.Label(popup, text="New value:").grid(row=1, column=0, sticky="w", padx=12, pady=6)
        new_value_var = tk.StringVar(value=str(target.exam))
        value_entry = tk.Entry(popup, textvariable=new_value_var, width=25)
        value_entry.grid(row=1, column=1, padx=12, pady=6)

        def fill_current(event):
            mapping = {
                "Student Name": target.name,
                "Coursework 1": str(target.cw1),
                "Coursework 2": str(target.cw2),
                "Coursework 3": str(target.cw3),
                "Exam Mark": str(target.exam),
            }
            new_value_var.set(mapping[field_choice.get()])

        field_menu.bind("<<ComboboxSelected>>", fill_current)

        def apply_update():
            choice = field_choice.get()
            raw = new_value_var.get().strip()
            name, cw1, cw2, cw3, exam = target.name, target.cw1, target.cw2, target.cw3, target.exam
            try:
                if choice == "Student Name":
                    name = raw
                elif choice == "Coursework 1":
                    cw1 = int(raw)
                elif choice == "Coursework 2":
                    cw2 = int(raw)
                elif choice == "Coursework 3":
                    cw3 = int(raw)
                elif choice == "Exam Mark":
                    exam = int(raw)
                updated = Student(target.code, name, cw1, cw2, cw3, exam)
            except ValueError as err:
                messagebox.showerror("Invalid Input", str(err), parent=popup)
                return

            idx = self.students.index(target)
            self.students[idx] = updated
            save_students(self.students, self.marks_path)
            popup.destroy()
            self.search_var.set(f"{updated.code} - {updated.name}")
            self.view_all_students()
            self.set_details("Updated and saved to studentMarks.txt:\n\n" + updated.format_details())

        ttk.Button(popup, text="Save Change", command=apply_update).grid(
            row=2, column=0, columnspan=2, pady=12
        )


if __name__ == "__main__":
    window = tk.Tk()
    StudentManagerApp(window)
    window.mainloop()
