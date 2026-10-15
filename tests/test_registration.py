import unittest
import sys
import os

# Добавляем путь к src, чтобы можно было импортировать registration
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from registration import validate_registration, mask_password


class TestRegistration(unittest.TestCase):

    # ========== Успешные случаи ==========

    def test_successful_registration_with_simple_login(self):
        success, message = validate_registration("good_user", "Пароль123!", "Пароль123!")
        self.assertTrue(success)
        self.assertEqual(message, "")

    def test_successful_registration_with_email(self):
        success, message = validate_registration("user@example.com", "Секрет456!", "Секрет456!")
        self.assertTrue(success)
        self.assertEqual(message, "")

    def test_successful_registration_with_phone(self):
        success, message = validate_registration("+7-999-123-4567", "Надёжный789!", "Надёжный789!")
        self.assertTrue(success)
        self.assertEqual(message, "")

    # ========== Пустые поля ==========

    def test_empty_login(self):
        success, message = validate_registration("", "Пароль123!", "Пароль123!")
        self.assertFalse(success)
        self.assertIn("Логин не может быть пустым", message)

    def test_login_only_spaces(self):
        success, message = validate_registration("   ", "Пароль123!", "Пароль123!")
        self.assertFalse(success)
        self.assertIn("Логин не может быть пустым", message)

    def test_empty_password(self):
        success, message = validate_registration("good_user", "", "")
        self.assertFalse(success)
        self.assertIn("Пароль не может быть пустым", message)

    def test_empty_password_confirm(self):
        success, message = validate_registration("good_user", "Пароль123!", "")
        self.assertFalse(success)
        self.assertIn("Подтверждение пароля не может быть пустым", message)

    # ========== Чёрный список ==========

    def test_blacklist_admin(self):
        success, message = validate_registration("admin", "Пароль123!", "Пароль123!")
        self.assertFalse(success)
        self.assertIn("чёрном списке", message)

    def test_blacklist_admin_uppercase(self):
        success, message = validate_registration("ADMIN", "Пароль123!", "Пароль123!")
        self.assertFalse(success)
        self.assertIn("чёрном списке", message)

    def test_blacklist_root(self):
        success, message = validate_registration("root", "Пароль123!", "Пароль123!")
        self.assertFalse(success)
        self.assertIn("чёрном списке", message)

    # ========== Неверный формат логина ==========

    def test_login_too_short(self):
        success, message = validate_registration("ab", "Пароль123!", "Пароль123!")
        self.assertFalse(success)
        self.assertIn("неверный формат", message)

    def test_login_with_invalid_characters(self):
        success, message = validate_registration("user@name!", "Пароль123!", "Пароль123!")
        self.assertFalse(success)
        self.assertIn("неверный формат", message)

    def test_login_with_cyrillic(self):
        success, message = validate_registration("пользователь", "Пароль123!", "Пароль123!")
        self.assertFalse(success)
        self.assertIn("неверный формат", message)

    # ========== Пароль: длина ==========

    def test_password_too_short(self):
        success, message = validate_registration("good_user", "Пароль", "Пароль")
        self.assertFalse(success)
        self.assertIn("минимум 7 символов", message)

    # ========== Пароль: только кириллица + цифры + спецсимволы ==========

    def test_password_with_latin_letters(self):
        success, message = validate_registration("good_user", "Password123!", "Password123!")
        self.assertFalse(success)
        self.assertIn("только кириллицу", message)

    # ========== Пароль: обязательные классы символов ==========

    def test_password_no_uppercase(self):
        success, message = validate_registration("good_user", "пароль123!", "пароль123!")
        self.assertFalse(success)
        self.assertIn("заглавную букву", message)

    def test_password_no_lowercase(self):
        success, message = validate_registration("good_user", "ПАРОЛЬ123!", "ПАРОЛЬ123!")
        self.assertFalse(success)
        self.assertIn("строчную букву", message)

    def test_password_no_digit(self):
        success, message = validate_registration("good_user", "Пароль!!", "Пароль!!")
        self.assertFalse(success)
        self.assertIn("цифру", message)

    def test_password_no_special_char(self):
        success, message = validate_registration("good_user", "Пароль123", "Пароль123")
        self.assertFalse(success)
        self.assertIn("спецсимвол", message)

    # ========== Совпадение паролей ==========

    def test_passwords_do_not_match(self):
        success, message = validate_registration("good_user", "Пароль123!", "Пароль123?")
        self.assertFalse(success)
        self.assertIn("не совпадают", message)

    # ========== Маскирование пароля ==========

    def test_mask_password_same_for_same_passwords(self):
        mask1 = mask_password("Секрет123!")
        mask2 = mask_password("Секрет123!")
        self.assertEqual(mask1, mask2)

    def test_mask_password_different_for_different_passwords(self):
        mask1 = mask_password("Секрет123!")
        mask2 = mask_password("Секрет123?")
        self.assertNotEqual(mask1, mask2)

    def test_mask_password_empty(self):
        mask = mask_password("")
        self.assertEqual(mask, "****")


if __name__ == "__main__":
    unittest.main()