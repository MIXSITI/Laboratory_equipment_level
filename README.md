# Roomly – система бронирования лабораторного оборудования и помещений

Система бронирования помещений и оборудования учебно-научной лаборатории на Python с веб-интерфейсом на Django.

## 1. Назначение проекта
Roomly – учебное веб-приложение для управления оборудованием, помещениями и их бронированием.
Проект позволяет просматривать каталог приборов и помещений, информацию об их готовности и доступности, данные пользователей, историю бронирований, искать свободные ресурсы на дату и просматривать аналитическую статистику через веб-интерфейс Django.
Проект развивается поэтапно: консольная версия приложения (ПР1–ПР3) дополнена веб-интерфейсом (ПР5), переведена на систему шаблонов Django (ПР6) и оснащена слоем реляционной базы данных SQLite и SQL-запросов (ПР7).

## 2. Используемые технологии
- Python 3;
- Django 5;
- SQLite 3 (стандартная библиотека `sqlite3`);
- SQL (Structured Query Language);
- Django Template Language (DTL);
- HTML5;
- CSS3;
- JavaScript;
- Bootstrap 5;
- JSON для исходного хранения данных;
- Git;
- pytest;
- flake8.

## 3. Предметная область
В системе используются три основные сущности:
- **Помещение (`Room`) / Оборудование (`Equipment`)** – идентификатор, название, инвентарный номер, ставка аренды, допуск, готовность и вместимость;
- **Пользователь (`User`)** – идентификатор, ФИО, email, роль (`Student`, `Staff`), уровень допуска и статус инструктажа;
- **Бронирование (`Booking`)** – номер заявки, ссылка на помещение/оборудование (`room_id`), ссылка на пользователя (`user_id`), период (`booking_date`, `duration_hours`), стоимость и статус активности.

Для предметной области реализованы собственные Python-классы в каталоге `models/`.
На текущем этапе ПР7 данные перенесены из JSON-файлов в реляционную базу данных SQLite `data/roomly.sqlite`. Django ORM пока не используется (запланирован на следующие практические работы).

## 4. Структура проекта
```text
work/
├── bookings/
│   ├── templates/
│   │   └── bookings/
│   │       ├── includes/
│   │       │   └── booking_status.html
│   │       ├── booking_detail.html
│   │       ├── booking_list.html
│   │       └── statistics.html
│   ├── urls.py
│   └── views.py
│
├── homepage/
│   ├── static/
│   │   └── homepage/
│   │       ├── css/
│   │       │   └── style.css
│   │       ├── img/
│   │       │   └── logo.png
│   │       └── js/
│   │           └── main.js
│   ├── templates/
│   │   └── homepage/
│   │       ├── 404.html
│   │       └── index.html
│   ├── urls.py
│   └── views.py
│
├── rooms/
│   ├── templates/
│   │   └── rooms/
│   │       ├── includes/
│   │       │   └── room_card.html
│   │       ├── available.html
│   │       ├── room_detail.html
│   │       └── room_list.html
│   ├── urls.py
│   └── views.py
│
├── equipment/
│   ├── templates/
│   │   └── equipment/
│   │       ├── includes/
│   │       │   └── equipment_card.html
│   │       ├── equipment_detail.html
│   │       └── equipment_list.html
│   ├── urls.py
│   └── views.py
│
├── templates/
│   ├── includes/
│   │   └── navigation.html
│   ├── 404.html
│   └── base.html
│
├── db/
│   ├── __init__.py
│   ├── database.py
│   ├── init_db.py
│   └── import_json.py
│
├── sql/
│   ├── queries.sql
│   └── schema.sql
│
├── models/
│   ├── __init__.py
│   ├── bookings.py
│   ├── equipment.py
│   ├── rooms.py
│   └── users.py
│
├── data/
│   ├── bookings.json
│   ├── equipment.json
│   ├── rooms.json
│   ├── users.json
│   └── roomly.sqlite
│
├── tests/
│   ├── test_bookings.py
│   ├── test_equipment.py
│   ├── test_users.py
│   └── test_web.py
│
├── roomly/
│   ├── settings.py
│   └── urls.py
│
├── main.py
├── storage.py
├── utils.py
├── manage.py
└── README.md
```

## 5. Веб-интерфейс
Веб-часть приложения реализована на Django.
Основные страницы:
- главная страница (`/`);
- каталог оборудования (`/equipment/`) и помещений (`/rooms/`);
- поиск свободных помещений на дату (`/rooms/available/`);
- подробная карточка отдельного помещения (`/rooms/<id>/`) или прибора (`/equipment/<id>/`);
- список активных бронирований (`/bookings/`);
- карточка отдельного бронирования (`/bookings/<id>/`);
- страница сводной статистики бронирований (`/bookings/statistics/`).

Для формирования страниц используются Django-шаблоны и данные из SQLite, передаваемые через контекст с помощью `render()`.

## 6. Django Template Language
Шаблоны используют возможности Django Template Language (DTL).

### Базовый шаблон
Общий каркас страниц: `templates/base.html`.
Содержит общую HTML-структуру страницы, тег `{% load static %}`, подключение стилей Bootstrap 5 и собственного `style.css`, подключение скрипта `main.js`, шапку с логотипом, навигацию `{% include "includes/navigation.html" %}`, футер и блоки переопределения:
```html
{% block title %}Roomly{% endblock %}
{% block content %}{% endblock %}
```

### Включаемые шаблоны
Повторяющиеся фрагменты вынесены в отдельные включаемые шаблоны:
- `templates/includes/navigation.html` – общая навигационная панель проекта;
- `rooms/includes/room_card.html` – карточка отдельного помещения;
- `equipment/includes/equipment_card.html` – карточка единицы оборудования;
- `bookings/includes/booking_status.html` – бейдж статуса заявки бронирования (активно / отменено).

## 7. Фильтры шаблонов
В шаблонах применяются стандартные фильтры Django:
- `{{ rooms|length }}` – вывод количества элементов коллекции;
- `{{ room.name|default:"Без названия" }}` – подстановка значения по умолчанию при отсутствии данных;
- `{{ summary.avg_cost|floatformat:2 }}` – форматирование средних сумм в статистике.

## 8. URL-маршрутизация
Для всех страниц используются именованные маршруты и пространства имён (`app_name`):
- `homepage:index`
- `rooms:list`, `rooms:detail`, `rooms:available`
- `equipment:equipment_list`, `equipment:equipment_detail`
- `bookings:bookings`, `bookings:detail`, `bookings:statistics`

Ссылки в шаблонах строятся с помощью тега `{% url %}`:
```html
{% url 'homepage:index' %}
{% url 'rooms:list' %}
{% url 'rooms:available' %}
{% url 'rooms:detail' room.id %}
{% url 'bookings:bookings' %}
{% url 'bookings:statistics' %}
{% url 'bookings:detail' booking.id %}
```

## 9. Статические файлы
Статические файлы проекта размещены в каталоге `homepage/static/homepage/`:
- `css/style.css` – собственные стили проекта (`.room-card`, `.booking-status`, `.roomly-logo`);
- `js/main.js` – клиентский скрипт для динамического отображения текущего года в футере сайта;
- `img/logo.png` – графический логотип проекта.

Подключение статики выполняется через теги:
```html
{% load static %}
<link rel="stylesheet" href="{% static 'homepage/css/style.css' %}">
<img src="{% static 'homepage/img/logo.png' %}" alt="Roomly" class="roomly-logo">
<script src="{% static 'homepage/js/main.js' %}"></script>
```

## 10. Реляционная база данных и SQL (ПР7)
В рамках ПР7 проект получил полноценный слой реляционного хранения данных на СУБД SQLite.

### 10.1. Структура базы данных (`sql/schema.sql`)
База данных `data/roomly.sqlite` включает следующие таблицы и представления:
- **`rooms`** – таблица помещений и оборудования (`id INTEGER PRIMARY KEY`, `name TEXT NOT NULL`, `inventory_number TEXT`, `capacity INTEGER NOT NULL DEFAULT 1`, `operational INTEGER`, `under_maintenance INTEGER`, `required_level INTEGER`, `hourly_rate REAL`);
- **`users`** – таблица пользователей (`id INTEGER PRIMARY KEY`, `name TEXT NOT NULL`, `email TEXT NOT NULL`, `role TEXT`, `access_level INTEGER`, `briefing_passed INTEGER`);
- **`bookings`** – таблица заявок бронирования (`id INTEGER PRIMARY KEY`, `room_id INTEGER NOT NULL`, `equipment_id INTEGER`, `user_id INTEGER NOT NULL`, `booking_date TEXT NOT NULL`, `duration_hours REAL`, `cost REAL`, `is_cancelled INTEGER`, внешние ключи `FOREIGN KEY (room_id) REFERENCES rooms(id)`, `FOREIGN KEY (user_id) REFERENCES users(id)`);
- **`equipment`** – SQL-представление (`VIEW equipment AS SELECT ... FROM rooms`), обеспечивающее полную совместимость с предметной областью.

### 10.2. Подключение к SQLite (`db/database.py`)
Модуль подключения гарантирует целостность внешних ключей:
```python
conn = sqlite3.connect("data/roomly.sqlite")
conn.execute("PRAGMA foreign_keys = ON")
```

### 10.3. Перенос данных из JSON (`db/import_json.py`)
Скрипт читает `data/rooms.json`, `data/users.json`, `data/bookings.json` и выполняет параметризованную вставку методом `executemany()` с контролем транзакций (`commit()`, `rollback()`).

### 10.4. SQL-запросы проекта (`sql/queries.sql`)
Разработано 13 документированных запросов всех требуемых категорий:
1. Выборка списков с сортировкой (`SELECT ... ORDER BY`);
2. Поиск по числовому критерию (`WHERE capacity >= 30`);
3. Фильтрация по статусу активности (`WHERE is_cancelled = 0`);
4. Фильтрация по диапазону цен (`WHERE hourly_rate BETWEEN ...`);
5. Соединение трёх таблиц (`JOIN rooms ON ... JOIN users ON ...`);
6. История бронирований конкретного пользователя;
7. Поиск свободных помещений на дату с подзапросом `WHERE id NOT IN (SELECT room_id ...)`;
8. Агрегатный подсчет количества активных бронирований (`COUNT(*)`);
9. Финансовая сводка (`SUM`, `AVG`, `MIN`, `MAX`);
10. Группировка количества бронирований по помещениям (`LEFT JOIN ... GROUP BY`);
11. Фильтрация групп с высоким спросом (`HAVING COUNT(...) > 1`);
12. Аналитика бронирований в разрезе категорий/ролей пользователей.

### 10.5. Интеграция с Django-представлениями
В `rooms/views.py` и `bookings/views.py` настроен `conn.row_factory = sqlite3.Row`, значения фильтров передаются параметрами `?` без строковой конкатенации. Реализованы сценарии:
- Список помещений из SQLite (`/rooms/`);
- Поиск свободных помещений по дате (`/rooms/available/?date=YYYY-MM-DD`);
- Список активных бронирований с объединенными данными (`/bookings/`);
- Страница агрегированной статистики бронирований (`/bookings/statistics/`).

## 11. Хранение данных
На текущем этапе данные синхронизированы между JSON-файлами (`data/*.json`) и базой данных SQLite (`data/roomly.sqlite`).
Консольная версия и модули `storage.py` сохранены из ПР3.

## 12. Тестирование
Автоматизированные тесты pytest находятся в каталоге `tests/`:
- `test_bookings.py`
- `test_equipment.py`
- `test_users.py`
- `test_web.py` (включая проверку `/rooms/available/` и `/bookings/statistics/`)

Запуск тестов:
```bash
pytest -v
```

## 13. Проверка качества кода
Проверка соответствия стандарту PEP 8 линтером `flake8`:
```bash
flake8 . --extend-exclude=venv
```
Системная проверка Django:
```bash
python manage.py check
```

## 14. Запуск проекта
Запуск сервера разработки Django:
```bash
python manage.py runserver
```
После запуска проект доступен по адресу:
```text
http://127.0.0.1:8000/
```

## 15. Работа с Git
Фиксация этапов выполнения проекта осуществляется коммитами с префиксом практической работы:
```bash
git add .
git commit -m "PR7: add SQLite database and SQL queries"
```

## 16. Текущее состояние проекта
На этапе завершения ПР7 реализовано:
- Спроектирована и создана реляционная база данных SQLite (`data/roomly.sqlite`);
- Описана структура схемы с первичными и внешними ключами (`sql/schema.sql`);
- Реализован модуль подключения с `PRAGMA foreign_keys = ON` (`db/database.py`);
- Разработан скрипт импорта данных из JSON в SQLite (`db/import_json.py`);
- Разработан и протестирован набор из 13 SQL-запросов (`sql/queries.sql`);
- Django-представления получают данные из базы через `sqlite3.Row`;
- Реализована страница поиска свободных помещений на выбранную дату (`/rooms/available/`);
- Реализована страница сводной аналитической статистики (`/bookings/statistics/`);
- Навигация обновлена с добавлением ссылки на статистику и поиск свободных ресурсов;
- 100% автотестов проходят успешно (43/43);
- Код соответствует PEP 8 без замечаний.

## 17. Дальнейшее развитие
В следующих практических работах (ПР8–ПР10) запланирован переход от прямых SQL-запросов через `sqlite3` к использованию моделей Django ORM, миграций, созданию веб-форм Django и реализации административной панели.
