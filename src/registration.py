import re
import hashlib
import logging

# Чёрный список логинов
BLACKLIST = {
    "admin", "administrator", "root", "user", "test",
    "guest", "superuser", "moderator", "support", "system"
}


def mask_password(password: str) -> str:
    """
    Маскирование пароля.
    Одинаковые пароли дают одинаковую маску,
    разные пароли — разную.
    """
    if not password:
        return "****"
    # Берём первые 8 символов SHA-256 хеша
    hash_part = hashlib.sha256(password.encode("utf-8")).hexdigest()[:8]
    return f"***{hash_part}***"


def validate_registration(login: str, password: str, password_confirm: str) -> tuple[bool, str]:
    """
    Комплексная валидация данных при регистрации.
    Возвращает (True, "") при успехе или (False, "текст ошибки") при ошибке.
    """
    logging.debug(f"Начало валидации. Login: '{login}', Password: {mask_password(password)}, Confirm: {mask_password(password_confirm)}")

    # 1. Проверка на пустые поля
    if not login or not login.strip():
        return False, "Логин не может быть пустым"
    if not password:
        return False, "Пароль не может быть пустым"
    if not password_confirm:
        return False, "Подтверждение пароля не может быть пустым"

    login = login.strip()

    # 2. Проверка чёрного списка
    if login.lower() in BLACKLIST:
        return False, f"Логин '{login}' находится в чёрном списке"

    # 3. Определение типа логина и валидация
    phone_pattern = r"^\+\d-\d{3}-\d{3}-\d{4}$"
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    login_string_pattern = r"^[a-zA-Z0-9_]{5,}$"

    is_phone = bool(re.fullmatch(phone_pattern, login))
    is_email = bool(re.fullmatch(email_pattern, login))
    is_simple_login = bool(re.fullmatch(login_string_pattern, login))

    if not (is_phone or is_email or is_simple_login):
        return False, "Логин имеет неверный формат (должен быть телефон +x-xxx-xxx-xxxx, email или строка от 5 символов: латиница, цифры, _)"

    # 4. Проверка пароля: минимальная длина
    if len(password) < 7:
        return False, "Пароль должен содержать минимум 7 символов"

    # 5. Пароль должен состоять ТОЛЬКО из кириллицы, цифр и спецсимволов
    # (латиница запрещена)
    allowed_password_pattern = r"^[а-яА-ЯёЁ0-9!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]+$"
    if not re.fullmatch(allowed_password_pattern, password):
        return False, "Пароль может содержать только кириллицу, цифры и спецсимволы (латиница запрещена)"

    # 6. Проверка наличия обязательных типов символов
    has_upper = bool(re.search(r"[А-ЯЁ]", password))
    has_lower = bool(re.search(r"[а-яё]", password))
    has_digit = bool(re.search(r"[0-9]", password))
    has_special = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password))

    if not has_upper:
        return False, "Пароль должен содержать хотя бы одну заглавную букву кириллицы"
    if not has_lower:
        return False, "Пароль должен содержать хотя бы одну строчную букву кириллицы"
    if not has_digit:
        return False, "Пароль должен содержать хотя бы одну цифру"
    if not has_special:
        return False, "Пароль должен содержать хотя бы один спецсимвол"

    # 7. Совпадение пароля и подтверждения
    if password != password_confirm:
        return False, "Пароль и подтверждение пароля не совпадают"

    # Всё успешно
    return True, ""