import unittest

import alexa_joke as aj


class TestAlexaJoke(unittest.TestCase):
    def test_load_all_jokes(self):
        jokes = aj.load_jokes()
        self.assertEqual(len(jokes), 37)
        for setup, punchline in jokes:
            self.assertTrue(setup.endswith("?"))
            self.assertTrue(len(punchline) > 0)

    def test_filter_jokes_by_keyword_and_favourites(self):
        jokes = aj.load_jokes()
        pizza = aj.filter_jokes(jokes, keyword="pizza")
        self.assertGreaterEqual(len(pizza), 2)

        favs = {pizza[0]}
        only_favs = aj.filter_jokes(jokes, favourites=favs, favourites_only=True)
        self.assertEqual(only_favs, [pizza[0]])


if __name__ == "__main__":
    unittest.main()
