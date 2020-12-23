import json
import unittest

from multporn import Multporn

class TestHentai(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = "https://multporn.net/comics/between_friends"
        cls.test_response = Multporn(url)
        with open("Between Friends.json", mode='r') as fh:
            cls.test_reference = json.load(fh)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_url(self):
        self.assertEqual(self.test_reference["url"],
                         self.test_response.url, msg=str(self.test_response))

    def test_name(self):
        self.assertEqual(self.test_reference["name"], self.test_response.name, msg=str(
            self.test_response))

    def test_tags(self):
        self.assertEqual(self.test_reference["tags"],
                         self.test_response.tags, msg=str(self.test_response))

    def test_character(self):
        self.assertEqual(self.test_reference["characters"],
                         self.test_response.characters, msg=str(self.test_response))

    def test_artists(self):
        self.assertEqual(self.test_reference["artists"],
                         self.test_response.artists, msg=str(self.test_response))

    def test_Sections(self):
        self.assertEqual(self.test_reference["sections"],
                         self.test_response.sections, msg=str(self.test_response))

    def test_pageCount(self):
        self.assertEqual(self.test_reference["pageCount"],
                         self.test_response.pageCount, msg=str(self.test_response))

    def test_image_urls(self):
        self.assertEqual(self.test_reference["imageUrls"],
                         self.test_response.imageUrls, msg=str(self.test_response))

    def test_exists(self):
        self.assertTrue(self.test_response.exists, msg=str(self.test_response))
        self.assertFalse(Multporn("https://google.com").exists,
                         msg=f"Should have failed:{'https://google.com'}")


if(__name__ == '__main__'):
    unittest.main()
