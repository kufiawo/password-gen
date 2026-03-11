import unittest
from unittest.mock import patch, mock_open
import random
import string


import test_code as pg


class TestGeneratePassword(unittest.TestCase):
    """Тесты для функции generate_password."""

    def test_only_lowercase(self):
        length = 10
        pwd = pg.generate_password(length)
        self.assertEqual(len(pwd), length)
        self.assertTrue(all(c in pg.LOWERCASE for c in pwd))

    def test_with_uppercase(self):
        length = 15
        pwd = pg.generate_password(length, use_uppercase=True)
        allowed = pg.LOWERCASE + pg.UPPERCASE
        self.assertTrue(all(c in allowed for c in pwd))

    def test_with_digits(self):
        length = 12
        pwd = pg.generate_password(length, use_digits=True)
        allowed = pg.LOWERCASE + pg.DIGITS
        self.assertTrue(all(c in allowed for c in pwd))

    def test_with_specials(self):
        length = 8
        pwd = pg.generate_password(length, use_specials=True)
        allowed = pg.LOWERCASE + pg.SPECIALS
        self.assertTrue(all(c in allowed for c in pwd))

    def test_all_options(self):
        length = 20
        pwd = pg.generate_password(length, use_uppercase=True, use_digits=True, use_specials=True)
        allowed = pg.LOWERCASE + pg.UPPERCASE + pg.DIGITS + pg.SPECIALS
        self.assertTrue(all(c in allowed for c in pwd))

    def test_different_lengths(self):
        for length in [1, 5, 10, 50]:
            pwd = pg.generate_password(length)
            self.assertEqual(len(pwd), length)

    def test_randomness(self):
        random.seed(42)
        pwd1 = pg.generate_password(10, use_uppercase=True, use_digits=True)
        random.seed(42)
        pwd2 = pg.generate_password(10, use_uppercase=True, use_digits=True)
        self.assertEqual(pwd1, pwd2)


class TestInputFunctions(unittest.TestCase):
    """Тесты для функций ввода input_integer и input_yes_no."""

    @patch('builtins.input')
    def test_input_integer_default(self, mock_input):
        mock_input.return_value = ""
        result = pg.input_integer("prompt", default=5, min_val=1, max_val=10)
        self.assertEqual(result, 5)

    @patch('builtins.input')
    def test_input_integer_valid(self, mock_input):
        mock_input.return_value = "7"
        result = pg.input_integer("prompt", default=5, min_val=1, max_val=10)
        self.assertEqual(result, 7)

    @patch('builtins.input')
    def test_input_integer_invalid_then_valid(self, mock_input):
        mock_input.side_effect = ["abc", "15", "8"]
        result = pg.input_integer("prompt", default=5, min_val=1, max_val=10)
        self.assertEqual(result, 8)

    @patch('builtins.input')
    def test_input_integer_out_of_range(self, mock_input):
        mock_input.side_effect = ["0", "11", "5"]
        result = pg.input_integer("prompt", default=5, min_val=1, max_val=10)
        self.assertEqual(result, 5)

    @patch('builtins.input')
    def test_input_yes_no_yes(self, mock_input):
        mock_input.return_value = "y"
        result = pg.input_yes_no("prompt")
        self.assertTrue(result)

    @patch('builtins.input')
    def test_input_yes_no_no(self, mock_input):
        mock_input.return_value = "n"
        result = pg.input_yes_no("prompt")
        self.assertFalse(result)

    @patch('builtins.input')
    def test_input_yes_no_invalid_then_valid(self, mock_input):
        mock_input.side_effect = ["maybe", "yes"]
        result = pg.input_yes_no("prompt")
        self.assertTrue(result)


class TestMenuGlobalState(unittest.TestCase):
    """Тесты для меню и глобальных переменных (только подмена input)."""

    def setUp(self):
        pg.last_password = ""
        pg.last_settings = ""

    @patch('builtins.input')
    def test_generate_only_lowercase(self, mock_input):
        # Последовательность ввода:
        # 1 (выбор генерации)
        # "" (длина по умолчанию)
        # "n" (цифры)
        # "n" (спецсимволы)
        # "n" (заглавные)
        # 3 (выход)
        mock_input.side_effect = ["1", "", "n", "n", "n", "3"]
        with patch('builtins.print'):
            pg.menu()
        self.assertEqual(pg.last_settings, "только строчные")
        self.assertEqual(len(pg.last_password), pg.DEFAULT_PASSWORD_LENGTH)

    @patch('builtins.input')
    def test_generate_all_options(self, mock_input):
        mock_input.side_effect = ["1", "12", "y", "y", "y", "3"]
        with patch('builtins.print'):
            pg.menu()
        self.assertEqual(pg.last_settings, "строчные + заглавные + цифры + спецсимволы")
        self.assertEqual(len(pg.last_password), 12)

    @patch('builtins.input')
    def test_generate_uppercase_and_digits(self, mock_input):
        mock_input.side_effect = ["1", "8", "y", "n", "y", "3"]
        with patch('builtins.print'):
            pg.menu()
        self.assertEqual(pg.last_settings, "строчные + заглавные + цифры")
        self.assertEqual(len(pg.last_password), 8)

    @patch('builtins.input')
    def test_generate_digits_and_specials(self, mock_input):
        mock_input.side_effect = ["1", "10", "y", "y", "n", "3"]
        with patch('builtins.print'):
            pg.menu()
        self.assertEqual(pg.last_settings, "строчные + цифры + спецсимволы")
        self.assertEqual(len(pg.last_password), 10)


class TestFileSaving(unittest.TestCase):
    """Тесты для сохранения в файл (только подмена input)."""

    def setUp(self):
        pg.last_password = "testpass"
        pg.last_settings = "testsettings"

    @patch('builtins.input')
    @patch("builtins.open", new_callable=mock_open)
    def test_save_success(self, mock_file, mock_input):
        mock_input.side_effect = ["2", "3"]
        with patch('builtins.print') as mock_print:
            pg.menu()
        mock_file.assert_called_once_with("passwords.txt", "a")
        handle = mock_file()
        handle.write.assert_called_once()
        written = handle.write.call_args[0][0]
        self.assertIn("testpass", written)
        self.assertIn("testsettings", written)
        mock_print.assert_any_call("Пароль сохранён в файл passwords.txt")

    @patch('builtins.input')
    @patch("builtins.open", side_effect=IOError("Disk error"))
    def test_save_io_error(self, mock_file, mock_input):
        pg.last_password = "somepass"
        mock_input.side_effect = ["2", "3"]
        with patch('builtins.print') as mock_print:
            pg.menu()
        mock_print.assert_any_call("Ошибка при сохранении в файл")

    @patch('builtins.input')
    def test_save_without_generation(self, mock_input):
        pg.last_password = ""
        mock_input.side_effect = ["2", "3"]
        with patch('builtins.print') as mock_print:
            pg.menu()
        mock_print.assert_any_call("Сначала сгенерируйте пароль!")


class TestMenuInvalidInput(unittest.TestCase):
    """Тесты на неверный выбор в меню."""

    @patch('builtins.input')
    def test_invalid_menu_choice(self, mock_input):
        mock_input.side_effect = ["99", "3"]
        with patch('builtins.print') as mock_print:
            pg.menu()
        mock_print.assert_any_call("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    unittest.main()