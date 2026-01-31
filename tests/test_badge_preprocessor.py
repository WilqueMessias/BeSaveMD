import unittest
import re
from src.utils.badge_preprocessor import tech_badge_preprocessor, TECH_COLORS

class TestTechBadgePreprocessor(unittest.TestCase):

    def test_no_badges(self):
        text = "This is a regular text without any tech skills."
        processed_text = tech_badge_preprocessor(text)
        self.assertEqual(processed_text, text)

    def test_single_badge(self):
        text = "- **Skills**: python"
        expected = f"- **Skills**: !{{python}}(https://img.shields.io/badge/python-{{color}}?style=flat-square&logo=python&logoColor=white)".format(color=TECH_COLORS['python'])
        processed_text = tech_badge_preprocessor(text)
        self.assertEqual(processed_text, expected)

    def test_multiple_badges(self):
        text = "- **Backend**: django, flask"
        expected = "- **Backend**: !{django}(https://img.shields.io/badge/django-{django_color}?style=flat-square&logo=django&logoColor=white) !{flask}(https://img.shields.io/badge/flask-{flask_color}?style=flat-square&logo=flask&logoColor=white)".format(django_color=TECH_COLORS['django'], flask_color=TECH_COLORS['flask'])
        processed_text = tech_badge_preprocessor(text)
        self.assertEqual(processed_text, expected)

    def test_mixed_badges_and_non_badges(self):
        text = "- **Languages**: python, java, c++"
        expected = f"- **Languages**: !{{python}}(https://img.shields.io/badge/python-{{python_color}}?style=flat-square&logo=python&logoColor=white) `java` `c++`".format(python_color=TECH_COLORS['python'])
        processed_text = tech_badge_preprocessor(text)
        self.assertEqual(processed_text, expected)

    def test_case_insensitivity_and_punctuation(self):
        text = "- **Frameworks**: React, NODE.JS."
        expected = f"- **Frameworks**: !{{React}}(https://img.shields.io/badge/React-{{react_color}}?style=flat-square&logo=react&logoColor=white) !{{NODE.JS}}(https://img.shields.io/badge/NODE.JS-{{nodejs_color}}?style=flat-square&logo=node.js&logoColor=white)".format(react_color=TECH_COLORS['react'], nodejs_color=TECH_COLORS['node.js'])
        processed_text = tech_badge_preprocessor(text)
        self.assertEqual(processed_text, expected)

    def test_empty_string(self):
        text = ""
        processed_text = tech_badge_preprocessor(text)
        self.assertEqual(processed_text, "")

    def test_line_without_category(self):
        text = "python, django, flask are great."
        processed_text = tech_badge_preprocessor(text)
        self.assertEqual(processed_text, text)

if __name__ == '__main__':
    unittest.main()
