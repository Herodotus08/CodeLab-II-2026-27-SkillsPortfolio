from pathlib import Path
import tempfile
import unittest

import maths_quiz as mq


class TestMathsQuiz(unittest.TestCase):
    def test_random_int_ranges(self):
        for _ in range(50):
            self.assertTrue(1 <= mq.randomInt(1) <= 9)
            self.assertTrue(10 <= mq.randomInt(2) <= 99)
            self.assertTrue(1000 <= mq.randomInt(3) <= 9999)

    def test_decide_operation(self):
        ops = {mq.decideOperation() for _ in range(50)}
        self.assertEqual(ops, {"+", "-"})

    def test_is_correct_scoring(self):
        self.assertEqual(mq.isCorrect(54, 54, 1)[:2], (True, 10))
        self.assertEqual(mq.isCorrect(-54, -54, 2)[:2], (True, 5))
        self.assertEqual(mq.isCorrect(10, -54, 1)[:2], (False, 0))
        ok, pts, msg = mq.isCorrect(10, -54, 2)
        self.assertFalse(ok)
        self.assertEqual(pts, 0)
        self.assertIn("-54", msg)

    def test_grades_and_best_score(self):
        self.assertEqual(mq.get_grade(95), "A+")
        self.assertEqual(mq.get_grade(80), "A")
        self.assertEqual(mq.get_grade(70), "B")
        self.assertEqual(mq.get_grade(40), "F")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "best.txt"
            self.assertTrue(mq.save_best_score("Easy", 85, path))
            self.assertFalse(mq.save_best_score("Easy", 70, path))
            self.assertEqual(mq.load_best_scores(path)["Easy"], 85)


if __name__ == "__main__":
    unittest.main()
