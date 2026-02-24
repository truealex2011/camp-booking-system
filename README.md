# Система бронирования лагеря "Таежный"

Веб-приложение для онлайн-записи на услуги лагеря с административной панелью управления.

## Возможности

### Пользовательская часть
- Выбор услуги из доступных
- Интерактивный календарь для выбора даты и времени
- Автоматическая проверка доступности слотов (максимум 2 записи на слот)
- Форма с валидацией контактных данных
- Автоматическое форматирование номера телефона
- Страница подтверждения с номером бронирования и списком документов

### Административная панель
- Безопасная аутентификация администраторов
- Управление услугами (создание, редактирование, активация/деактивация)
- Управление бронированиями (просмотр, фильтрация, редактирование, отмена)
- Статистика по услугам и лагерям
- Печать расписания на текущий день
- Адаптивный дизайн для всех устройств

## Технологии

- **Backend**: Python 3.9+, Flask 3.0
- **Database**: SQLite 3
- **Frontend**: HTML5, CSS3 (custom), JavaScript ES6
- **Security**: Flask-WTF (CSRF), bcrypt (password hashing)
- **Testing**: pytest, hypothesis (property-based testing)

## Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd camp-booking-system
```

### 2. Создание виртуального окружения

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и настройте параметры:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Отредактируйте `.env`:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///instance/database.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-password
```

### 5. Инициализация базы данных

```bash
python init_db.py
```

Это создаст:
- Таблицы базы данных
- Администратора по умолчанию
- Три стандартные услуги

### 6. Запуск приложения

```bash
python run.py
```

Приложение будет доступно по адресу: `http://localhost:5000`

## Использование

### Пользовательский интерфейс

1. Откройте `http://localhost:5000`
2. Выберите услугу
3. Выберите дату и время в календаре
4. Заполните контактную информацию
5. Получите подтверждение с номером бронирования

### Административная панель

1. Откройте `http://localhost:5000/admin/login`
2. Войдите с учетными данными администратора
3. Используйте панель для управления системой

**Учетные данные по умолчанию:**
- Username: `admin`
- Password: `admin123`

⚠️ **ВАЖНО**: Измените пароль администратора после первого входа!

## Структура проекта

```
camp-booking-system/
├── app/
│   ├── __init__.py              # Фабрика приложения Flask
│   ├── models.py                # Модели базы данных
│   ├── routes/
│   │   ├── public.py            # Публичные маршруты
│   │   └── admin.py             # Административные маршруты
│   ├── services/
│   │   ├── auth_service.py      # Сервис аутентификации
│   │   ├── booking_service.py   # Сервис бронирования
│   │   └── service_manager.py   # Управление услугами
│   ├── templates/               # HTML шаблоны
│   ├── static/                  # CSS, JS, изображения
│   └── utils/                   # Утилиты и валидаторы
├── migrations/
│   └── init_db.sql             # SQL скрипт инициализации
├── config.py                    # Конфигурация приложения
├── run.py                       # Точка входа
├── init_db.py                   # Скрипт инициализации БД
├── requirements.txt             # Зависимости Python
└── README.md                    # Документация
```

## Конфигурация

### Временные слоты

По умолчанию доступны слоты: 09:00, 10:00, 11:00, 12:00, 13:00, 14:00, 15:00, 16:00, 17:00

Изменить можно в `config.py`:

```python
TIME_SLOTS = ['09:00', '10:00', '11:00', ...]
```

### Лагеря

Три лагеря настроены по умолчанию:
- Таежный 6 – Республика Чародеев
- Таежный 9 – Дружный
- Таежный 10 – Звездный

Изменить можно в `config.py`:

```python
CAMPS = ['Таежный 6 – Республика Чародеев', ...]
```

### Максимум записей на слот

По умолчанию: 2 записи на один временной слот

Изменить можно в `config.py`:

```python
MAX_BOOKINGS_PER_SLOT = 2
```

## Тестирование

### Запуск всех тестов

```bash
pytest
```

### Запуск с покрытием кода

```bash
pytest --cov=app --cov-report=html
```

### Запуск property-based тестов

```bash
pytest tests/property/
```

## Развертывание

### Подготовка к продакшену

1. Установите переменные окружения:

```env
FLASK_ENV=production
SECRET_KEY=<strong-random-secret-key>
DATABASE_URL=<production-database-url>
```

2. Используйте WSGI сервер (Gunicorn):

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

3. Настройте Nginx как reverse proxy

4. Настройте SSL сертификат (Let's Encrypt)

### Рекомендации по безопасности

- ✅ Используйте сильный SECRET_KEY
- ✅ Включите HTTPS в продакшене
- ✅ Измените пароль администратора
- ✅ Регулярно создавайте резервные копии БД
- ✅ Ограничьте доступ к админ-панели по IP (опционально)
- ✅ Настройте rate limiting для защиты от DDoS

## Резервное копирование

### Создание резервной копии

```bash
# Копирование файла базы данных
copy instance\database.db instance\database_backup.db  # Windows
cp instance/database.db instance/database_backup.db    # Linux/Mac
```

### Восстановление из резервной копии

```bash
copy instance\database_backup.db instance\database.db  # Windows
cp instance/database_backup.db instance/database.db    # Linux/Mac
```

## Поддержка

Для вопросов и поддержки обращайтесь к администратору системы.

## Лицензия

© 2026 МАОУ СШ 157 Красноярск. Все права защищены.
