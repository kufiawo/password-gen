import unittest
from unittest.mock import patch, mock_open, MagicMock
import string
import tempfile
import os
import time
import runpy
import coverage

if __name__ == "__main__":
    # Запускаем coverage до импорта тестируемого модуля
    cov = coverage.Coverage(source=["test_code"])
    cov.start()

    # Теперь импортируем тестируемый модуль
    from test_code import (
        PasswordManager, MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH, DEFAULT_PASSWORD_LENGTH,
        input_integer, input_yes_no, LOWERCASE, UPPERCASE, DIGITS, SPECIALS, menu
    )

    # ---------- Тесты для PasswordManager ----------
    class TestPasswordManager(unittest.TestCase):
        def setUp(self):
            self.manager = PasswordManager()

        def test_generate_only_lowercase(self):
            length = 10
            pwd = self.manager.generate(length)
            self.assertEqual(len(pwd), length)
            self.assertTrue(all(c in string.ascii_lowercase for c in pwd))
            self.assertEqual(self.manager.last_password, pwd)

        def test_generate_with_uppercase(self):
            length = 15
            pwd = self.manager.generate(length, use_uppercase=True)
            self.assertEqual(len(pwd), length)
            allowed = string.ascii_lowercase + string.ascii_uppercase
            self.assertTrue(all(c in allowed for c in pwd))

        def test_generate_with_digits(self):
            length = 12
            pwd = self.manager.generate(length, use_digits=True)
            self.assertEqual(len(pwd), length)
            allowed = string.ascii_lowercase + string.digits
            self.assertTrue(all(c in allowed for c in pwd))

        def test_generate_with_specials(self):
            length = 8
            pwd = self.manager.generate(length, use_specials=True)
            self.assertEqual(len(pwd), length)
            allowed = string.ascii_lowercase + SPECIALS
            self.assertTrue(all(c in allowed for c in pwd))

        def test_generate_all_options(self):
            length = 20
            pwd = self.manager.generate(length, use_uppercase=True, use_digits=True, use_specials=True)
            self.assertEqual(len(pwd), length)
            allowed = LOWERCASE + UPPERCASE + DIGITS + SPECIALS
            self.assertTrue(all(c in allowed for c in pwd))

        def test_generate_invalid_length(self):
            with self.assertRaises(ValueError):
                self.manager.generate(0)

        def test_generate_updates_last_settings(self):
            self.manager.generate(5, use_uppercase=True, use_digits=False, use_specials=True)
            expected = PasswordManager._format_settings(True, False, True)
            self.assertEqual(self.manager.last_settings, expected)

        def test_format_settings(self):
            cases = [
                ((False, False, False), "только строчные"),
                ((True, False, False), "строчные + заглавные"),
                ((False, True, False), "строчные + цифры"),
                ((False, False, True), "строчные + спецсимволы"),
                ((True, True, False), "строчные + заглавные + цифры"),
                ((True, False, True), "строчные + заглавные + спецсимволы"),
                ((False, True, True), "строчные + цифры + спецсимволы"),
                ((True, True, True), "строчные + заглавные + цифры + спецсимволы"),
            ]
            for (upp, dig, spec), expected in cases:
                with self.subTest(upp=upp, dig=dig, spec=spec):
                    self.assertEqual(PasswordManager._format_settings(upp, dig, spec), expected)

        @patch("builtins.open", new_callable=mock_open)
        def test_save_to_file_success(self, mock_file):
            pwd = self.manager.generate(8)
            result = self.manager.save_to_file("test.txt")
            mock_file.assert_called_once_with("test.txt", "a")
            handle = mock_file()
            handle.write.assert_called_once()
            self.assertIn("Пароль сохранён", result)

        def test_save_to_file_without_generation(self):
            result = self.manager.save_to_file()
            self.assertEqual(result, "Сначала сгенерируйте пароль!")

        @patch("builtins.open", side_effect=IOError("Disk full"))
        def test_save_to_file_io_error(self, mock_file):
            self.manager.generate(8)
            result = self.manager.save_to_file()
            self.assertIn("Ошибка ввода-вывода: Disk full", result)

        @patch("builtins.open", side_effect=TypeError("Wrong type"))
        def test_save_to_file_unexpected_error(self, mock_file):
            self.manager.generate(8)
            result = self.manager.save_to_file()
            self.assertIn("Неожиданная ошибка: Wrong type", result)

        def test_save_to_file_real_file(self):
            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
                filename = tmp.name
            try:
                self.manager.generate(10)
                result = self.manager.save_to_file(filename)
                self.assertIn("Пароль сохранён", result)
                with open(filename, "r") as f:
                    content = f.read()
                self.assertIn(self.manager.last_password, content)
            finally:
                os.unlink(filename)

    # ---------- Тесты для функций ввода ----------
    class TestInputFunctions(unittest.TestCase):
        @patch('builtins.input')
        def test_input_integer_default(self, mock_input):
            mock_input.return_value = ""
            result = input_integer("prompt", default=5, min_val=1, max_val=10)
            self.assertEqual(result, 5)

        @patch('builtins.input')
        def test_input_integer_valid(self, mock_input):
            mock_input.return_value = "7"
            result = input_integer("prompt", default=5, min_val=1, max_val=10)
            self.assertEqual(result, 7)

        @patch('builtins.input')
        def test_input_integer_min_max(self, mock_input):
            mock_input.side_effect = ["1", "10"]
            result1 = input_integer("prompt", default=5, min_val=1, max_val=10)
            result2 = input_integer("prompt", default=5, min_val=1, max_val=10)
            self.assertEqual(result1, 1)
            self.assertEqual(result2, 10)

        @patch('builtins.input')
        def test_input_integer_invalid_then_valid(self, mock_input):
            mock_input.side_effect = ["abc", "15", "8"]
            result = input_integer("prompt", default=5, min_val=1, max_val=10)
            self.assertEqual(result, 8)

        @patch('builtins.input')
        def test_input_yes_no_yes_variants(self, mock_input):
            for ans in ('y', 'yes', 'да'):
                with self.subTest(ans=ans):
                    mock_input.return_value = ans
                    self.assertTrue(input_yes_no("prompt"))

        @patch('builtins.input')
        def test_input_yes_no_no_variants(self, mock_input):
            for ans in ('n', 'no', 'нет'):
                with self.subTest(ans=ans):
                    mock_input.return_value = ans
                    self.assertFalse(input_yes_no("prompt"))

        @patch('builtins.input')
        def test_input_yes_no_invalid_then_valid(self, mock_input):
            mock_input.side_effect = ["maybe", "yes"]
            result = input_yes_no("prompt")
            self.assertTrue(result)

    # ---------- Интеграционные тесты для меню ----------
    class TestMenuIntegration(unittest.TestCase):
        @patch('builtins.input')
        @patch('builtins.print')
        def test_menu_generate_default_length(self, mock_print, mock_input):
            """Пользователь вводит пустую строку для длины (по умолчанию 8)."""
            # Имитация ввода: выбор 1, Enter (пустая строка), затем 'n' на все запросы, потом 3 для выхода
            mock_input.side_effect = ["1", "", "n", "n", "n", "3"]
            manager = PasswordManager()
            with patch.object(manager, 'generate', wraps=manager.generate) as mock_generate:
                menu(manager)
                mock_generate.assert_called_once_with(8, False, False, False)

        @patch('builtins.input')
        @patch('builtins.print')
        def test_menu_generate_with_values(self, mock_print, mock_input):
            """Пользователь вводит конкретную длину и включает все опции."""
            mock_input.side_effect = ["1", "12", "y", "y", "y", "3"]
            manager = PasswordManager()
            with patch.object(manager, 'generate', wraps=manager.generate) as mock_generate:
                menu(manager)
                mock_generate.assert_called_once_with(12, True, True, True)

        @patch('builtins.input')
        @patch('builtins.print')
        def test_menu_save_after_generate(self, mock_print, mock_input):
            """Генерация, затем сохранение."""
            mock_input.side_effect = ["1", "8", "n", "n", "n", "2", "3"]
            manager = PasswordManager()
            with patch.object(manager, 'save_to_file', return_value="OK") as mock_save:
                menu(manager)
                mock_save.assert_called_once()

        @patch('builtins.input')
        @patch('builtins.print')
        def test_menu_save_without_generate(self, mock_print, mock_input):
            """Сохранение без предварительной генерации."""
            mock_input.side_effect = ["2", "3"]
            manager = PasswordManager()
            menu(manager)
            mock_print.assert_any_call("Сначала сгенерируйте пароль!")

        @patch('builtins.input')
        @patch('builtins.print')
        def test_menu_invalid_choice(self, mock_print, mock_input):
            """Неверный пункт меню."""
            mock_input.side_effect = ["4", "3"]
            manager = PasswordManager()
            menu(manager)
            mock_print.assert_any_call("Неверный выбор. Попробуйте снова.")

        @patch('builtins.input')
        @patch('builtins.print')
        def test_menu_exit(self, mock_print, mock_input):
            """Выход по выбору 3."""
            mock_input.side_effect = ["3"]
            manager = PasswordManager()
            menu(manager)
            mock_print.assert_called_with("До свидания!")

        @patch('test_code.input_integer')
        @patch('test_code.input_yes_no')
        @patch('builtins.input')
        @patch('builtins.print')
        def test_menu_generate_value_error(self, mock_print, mock_input, mock_yes_no, mock_integer):
            """Генерация с недопустимой длиной (обработка ValueError)."""
            mock_input.side_effect = ["1", "3"]
            mock_integer.return_value = 0  # недопустимая длина
            mock_yes_no.side_effect = [False, False, False]
            manager = PasswordManager()
            with patch.object(manager, 'generate', side_effect=ValueError("Длина должна быть >= 1")):
                menu(manager)
                mock_print.assert_any_call("Ошибка: Длина должна быть >= 1")

        def test_main_block(self):
            """Покрытие блока if __name__ == '__main__' в test_code.py."""
            with patch('builtins.input', side_effect=['3']):  # сразу выход
                with patch('builtins.print') as mock_print:
                    # Запускаем модуль как __main__
                    runpy.run_module('test_code', run_name='__main__')
                    mock_print.assert_any_call("До свидания!")

    # Запуск тестов
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPasswordManager)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestInputFunctions))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMenuIntegration))
    runner = unittest.TextTestRunner()
    result = runner.run(suite)

    cov.stop()
    cov.save()
    print()  # пустая строка для разделения
    cov.report(show_missing=True)

    # Завершаем с соответствующим кодом возврата
    