from pathlib import Path
import shutil
import tempfile
import unittest

import student_manager as sm


class TestStudentManager(unittest.TestCase):
    def copy_sample(self, folder):
        dest = Path(folder) / "studentMarks.txt"
        shutil.copyfile(sm.MARKS_FILE, dest)
        return dest

    def test_load_and_extremes(self):
        students = sm.load_students()
        self.assertEqual(len(students), 10)
        highest = max(students, key=lambda s: s.overall_total())
        lowest = min(students, key=lambda s: s.overall_total())
        self.assertEqual(highest.name, "Alan Shearer")
        self.assertEqual(highest.grade(), "A")
        self.assertEqual(lowest.name, "Gareth Southgate")
        self.assertEqual(lowest.grade(), "F")

    def test_grade_boundaries(self):
        self.assertEqual(sm.calculate_grade(70.0), "A")
        self.assertEqual(sm.calculate_grade(69.38), "B")
        self.assertEqual(sm.calculate_grade(60.0), "B")
        self.assertEqual(sm.calculate_grade(50.0), "C")
        self.assertEqual(sm.calculate_grade(40.0), "D")
        self.assertEqual(sm.calculate_grade(39.9), "F")

    def test_sort_add_update_delete_and_save(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.copy_sample(tmp)
            students = sm.load_students(path)

            ordered = sm.sort_student_list(students, by="percentage", descending=True)
            self.assertEqual(ordered[0].name, "Alan Shearer")
            self.assertEqual(ordered[-1].name, "Gareth Southgate")

            # Add a student and verify line-1 count updates
            students.append(sm.Student(4444, "Samira Patel", 18, 17, 19, 82))
            sm.save_students(students, path)
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines[0], "11")

            reloaded = sm.load_students(path)
            self.assertEqual(len(reloaded), 11)

            # Delete the added student and verify count returns to 10
            reloaded = [s for s in reloaded if s.code != 4444]
            sm.save_students(reloaded, path)
            self.assertEqual(path.read_text(encoding="utf-8").splitlines()[0], "10")


if __name__ == "__main__":
    unittest.main()
