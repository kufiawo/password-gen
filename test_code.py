import random
import time


LOWERCASE = 'abcdefghijklmnopqrstuvwxyz'
UPPERCASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
DIGITS = '0123456789'
SPECIALS = '!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

MIN_PASSWORD_LENGTH = 1
MAX_PASSWORD_LENGTH = 50    
DEFAULT_PASSWORD_LENGTH = 8

def input_integer(prompt, default, min_val, max_val):
    # Запрашивает у пользователя целое число в диапазоне [min_val, max_val].
    # При пустом вводе возвращает значение по умолчанию.
    # При неверном вводе выводит сообщение и повторяет запрос.
    while True:
        user_input = input(prompt).strip()
        if user_input == "":
            return default
        try:
            value = int(user_input)
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Ошибка: число должно быть от {min_val} до {max_val}.")
        except ValueError:
            print("Ошибка: введите целое число.")

def input_yes_no(prompt): 
    # Запрашивает у пользователя ответ 'y' или 'n'.
    # Повторяет запрос до получения корректного ответа.
    # Возвращает True для 'y', False для 'n'.
    
    while True:
        answer = input(prompt).strip().lower()
        if answer in ('y', 'yes', 'да'):
            return True
        elif answer in ('n', 'no', 'нет'):
            return False
        else:
            print("Пожалуйста, введите 'y' или 'n'.")
    
class PasswordManager:
    # Управляет состоянием генератора паролей
    
    def __init__(self):
        self.last_password = ""
        self.last_settings = ""
    
    def generate(self, length, use_uppercase=False, use_digits=False, use_specials=False):
        # Генерирует пароль
        chars = LOWERCASE
        if use_uppercase:
            chars += UPPERCASE
        if use_digits:
            chars += DIGITS
        if use_specials:
            chars += SPECIALS
        
        if length < MIN_PASSWORD_LENGTH:
            raise ValueError(f"Длина должна быть >= {MIN_PASSWORD_LENGTH}")
        
        password = ''.join(random.choice(chars) for _ in range(length))
        self.last_password = password
        self.last_settings = self._format_settings(use_uppercase, use_digits, use_specials)
        
        return password
    
    @staticmethod
    def _format_settings(use_uppercase, use_digits, use_specials):
        settings_parts = []
        if use_uppercase:
            settings_parts.append("заглавные")
        if use_digits:
            settings_parts.append("цифры")
        if use_specials:
            settings_parts.append("спецсимволы")
        
        return "только строчные" if not settings_parts else "строчные + " + " + ".join(settings_parts)
    
    def save_to_file(self, filename="passwords.txt"):
        # Сохраняет пароль в файл
        if not self.last_password:
            return "Сначала сгенерируйте пароль!"
        try:
            with open(filename, "a") as f:
                f.write(f"{time.ctime()} - {self.last_password} ({self.last_settings})\n")
            return f"Пароль сохранён в файл {filename}"
        except IOError as e:
            return f"Ошибка ввода-вывода: {e}"
        except Exception as e:
            return f"Неожиданная ошибка: {e}"
                
def menu(manager):
    # Интерактивное меню
    while True:
        print("\n___ Генератор паролей ___")
        print("1. Сгенерировать пароль")
        print("2. Сохранить последний пароль в файл")
        print("3. Выход")
        choice = input("\nВыберите пункт: ")

        if choice == "1":
            length = input_integer(
                f"Введите длину пароля (от {MIN_PASSWORD_LENGTH} до {MAX_PASSWORD_LENGTH}, по умолчанию {DEFAULT_PASSWORD_LENGTH}): ",
                default=DEFAULT_PASSWORD_LENGTH,
                min_val=MIN_PASSWORD_LENGTH,
                max_val=MAX_PASSWORD_LENGTH
            )
            use_digits = input_yes_no("Включить цифры? (y/n): ")
            use_specials = input_yes_no("Включить спецсимволы? (y/n): ")
            use_uppercase = input_yes_no("Включить заглавные буквы? (y/n): ")
        
            try:
                password = manager.generate(length, use_uppercase, use_digits, use_specials)
                print(f"Сгенерированный пароль: {password}")
                print(f"Настройки: {manager.last_settings}")
            except ValueError as e:
                print(f"Ошибка: {e}")

        elif choice == "2":
            print(manager.save_to_file())

        elif choice == "3":
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    manager = PasswordManager()
    menu(manager)