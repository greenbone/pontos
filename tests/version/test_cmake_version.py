import unittest
from pathlib import Path
from unittest.mock import MagicMock
from pontos.version import CMakeVersionParser, VersionError, CMakeVersionCommand


class CMakeVersionCommandTestCase(unittest.TestCase):
    def test_raise_exception_file_not_exists(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = 'CMakeLists.txt'
        fake_path.exists.return_value = False
        with self.assertRaises(VersionError):
            CMakeVersionCommand(cmake_lists_path=fake_path)

    def test_raise_exception_no_project(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = 'CMakeLists.txt'
        fake_path.exists.return_value = True
        fake_path.read_text.return_value = ""
        with self.assertRaises(ValueError):
            CMakeVersionCommand(cmake_lists_path=fake_path).run(args=['show'])
        fake_path.read_text.assert_called_with()

    def test_return_error_string_incorrect_version_on_verify(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = 'CMakeLists.txt'
        fake_path.exists.return_value = True
        fake_path.read_text.return_value = ""
        result = CMakeVersionCommand(cmake_lists_path=fake_path).run(
            args=['verify', 'su_much_version_so_much_wow']
        )
        self.assertTrue(
            isinstance(result, str), "expected result to be an error string"
        )

    def test_return_0_correct_version_on_verify(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = 'CMakeLists.txt'
        fake_path.exists.return_value = True
        fake_path.read_text.return_value = ""
        result = CMakeVersionCommand(cmake_lists_path=fake_path).run(
            args=['verify', '21.4']
        )
        self.assertEqual(0, result)

    def test_should_call_print_current_version_without_raising_exception(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = 'CMakeLists.txt'
        fake_path.exists.return_value = True
        fake_path.read_text.return_value = "project(VERSION 21)"
        CMakeVersionCommand(cmake_lists_path=fake_path).run(args=['show'])
        fake_path.read_text.assert_called_with()

    def test_raise_update_version(self):
        fake_path_class = MagicMock(spec=Path)
        fake_path = fake_path_class.return_value
        fake_path.__str__.return_value = 'CMakeLists.txt'
        fake_path.exists.return_value = True
        fake_path.read_text.return_value = "project(VERSION 21)"
        CMakeVersionCommand(cmake_lists_path=fake_path).run(
            args=['update', '22']
        )
        fake_path.read_text.assert_called_with()
        fake_path.write_text.assert_called_with('project(VERSION 22)')


class CMakeVersionParserTestCase(unittest.TestCase):
    def test_get_current_version_single_line_project(self):
        under_test = CMakeVersionParser("project(VERSION 2.3.4)")
        self.assertEqual(under_test.get_current_version(), '2.3.4')

    def test_update_version_project(self):
        under_test = CMakeVersionParser("project(VERSION 2.3.4)")
        self.assertEqual(
            under_test.update_version('2.3.5'), "project(VERSION 2.3.5)"
        )

    def test_update_raise_exception_when_version_is_incorrect(self):
        under_test = CMakeVersionParser("project(VERSION 2.3.4)")
        with self.assertRaises(VersionError):
            under_test.update_version('su_much_version_so_much_wow')

    def test_not_confuse_version_outside_project(self):
        under_test = CMakeVersionParser(
            "non_project(VERSION 2.3.5)\nproject(VERSION 2.3.4)"
        )
        self.assertEqual(under_test.get_current_version(), '2.3.4')

    def test_get_current_version_multiline_project(self):
        under_test = CMakeVersionParser("project\n(\nVERSION\n\t    2.3.4)")
        self.assertEqual(under_test.get_current_version(), '2.3.4')

    def test_get_current_version_multiline_project_combined_token(self):
        under_test = CMakeVersionParser(
            "project\n(\nDESCRIPTION something VERSION 2.3.4 LANGUAGES c\n)"
        )
        self.assertEqual(under_test.get_current_version(), '2.3.4')

    def test_raise_exception_project_no_version(self):
        with self.assertRaises(ValueError) as context:
            CMakeVersionParser("project(DESCRIPTION something LANGUAGES c)")
        self.assertEqual(
            str(context.exception), 'unable to find cmake version in project.'
        )

    def test_raise_exception_no_project(self):
        with self.assertRaises(ValueError) as context:
            CMakeVersionParser("non_project(VERSION 2.3.5)",)

        self.assertEqual(
            str(context.exception), 'unable to find cmake project.'
        )
