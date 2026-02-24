"""Script to create a new admin user."""
import sys
import getpass
from app import create_app
from app.services.auth_service import AuthService


def create_admin_user():
    """Interactive script to create admin user."""
    print("="*50)
    print("Создание нового администратора")
    print("="*50)
    print()
    
    # Get username
    while True:
        username = input("Введите имя пользователя: ").strip()
        if len(username) < 3:
            print("❌ Имя пользователя должно содержать минимум 3 символа")
            continue
        break
    
    # Get password
    while True:
        password = getpass.getpass("Введите пароль: ")
        if len(password) < 6:
            print("❌ Пароль должен содержать минимум 6 символов")
            continue
        
        password_confirm = getpass.getpass("Подтвердите пароль: ")
        if password != password_confirm:
            print("❌ Пароли не совпадают")
            continue
        break
    
    # Create admin
    app = create_app()
    with app.app_context():
        admin = AuthService.create_admin(username, password)
        
        if admin:
            print()
            print("="*50)
            print("✓ Администратор успешно создан!")
            print("="*50)
            print(f"Имя пользователя: {username}")
            print(f"ID: {admin.id}")
            print()
            print("Теперь вы можете войти в админ-панель:")
            print("http://localhost:5000/admin/login")
        else:
            print()
            print("="*50)
            print("❌ Ошибка создания администратора")
            print("="*50)
            print("Пользователь с таким именем уже существует")
            sys.exit(1)


if __name__ == '__main__':
    create_admin_user()
