# Roomly – система бронирования лабораторного оборудования и помещений

Система бронирования помещений и оборудования учебно-научной лаборатории на Python с веб-интерфейсом на Django и доступом к данным через Django ORM.

## 1. Назначение проекта
Roomly – учебное веб-приложение для управления оборудованием, помещениями и их бронированием.
Проект позволяет просматривать каталог приборов и помещений, информацию об их готовности и доступности, данные пользователей, историю бронирований, искать свободные ресурсы на дату, фильтровать, сортировать и просматривать постранично список заявок, а также получать сводную аналитическую статистику через веб-интерфейс Django.
Проект развивается поэтапно: консольная версия приложения (ПР1–ПР3) дополнена веб-интерфейсом (ПР5), переведена на систему шаблонов Django (ПР6), исследована на уровне прямых SQL-запросов к SQLite (ПР7) и переведена на полноценный слой доступа к данным через Django ORM (ПР9).

## 2. Используемые технологии
- Python 3;
- Django 5;
- Django ORM (Object-Relational Mapping);
- SQLite 3 (база данных `db.sqlite3`);
- Django Template Language (DTL);
- HTML5;
- CSS3;
- JavaScript;
- Bootstrap 5;
- JSON и SQLite для исходного хранения данных;
- Git;
- pytest;
- flake8.

## 3. Предметная область и модели Django ORM (ПР9)
В системе описаны следующие ORM-модели:
- **`Room` (`rooms/models.py`)** — помещения и лабораторное оборудование:
  - `name` (`CharField`) — название помещения/оборудования;
  - `capacity` (`PositiveIntegerField`) — вместимость;
  - `inventory_number` (`CharField`) — инвентарный номер;
  - `operational` (`BooleanField`) — признак исправности;
  - `under_maintenance` (`BooleanField`) — признак нахождения на ТО;
  - `required_level` (`PositiveIntegerField`) — требуемый допуск;
  - `hourly_rate` (`FloatField`) — почасовая ставка аренды;
  - Метод `is_suitable_for(people_count)`.
- **`User` (`users/models.py`)** — пользователи лаборатории:
  - `name` (`CharField`) — ФИО пользователя;
  - `email` (`EmailField`) — адрес электронной почты;
  - `role` (`CharField`) — роль (студент, сотрудник);
  - `access_level` (`PositiveIntegerField`) — уровень допуска;
  - `briefing_passed` (`BooleanField`) — отметка о прохождении инструктажа.
- **`Booking` (`bookings/models.py`)** — бронирования:
  - `room` (`ForeignKey(Room, on_delete=models.PROTECT, related_name="bookings")`) — ссылка на помещение;
  - `user` (`ForeignKey(User, on_delete=models.PROTECT, related_name="bookings")`) — ссылка на пользователя;
  - `booking_date` (`DateField`) — дата бронирования;
  - `duration_hours` (`FloatField`) — длительность в часах;
  - `cost` (`FloatField`) — стоимость бронирования;
  - `is_cancelled` (`BooleanField`) — признак отмены;
  - Метод `cancel()` для отмены бронирования;
  - Свойство `status` («Отменено» / «Активно»).

## 4. Структура проекта
```text
work/
├── bookings/
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── templates/
│   │   └── bookings/
│   │       ├── includes/
│   │       │   └── booking_status.html
│   │       ├── booking_detail.html
│   │       ├── booking_list.html
│   │       └── statistics.html
│   ├── models.py
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
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── templates/
│   │   └── rooms/
│   │       ├── includes/
│   │       │   └── room_card.html
│   │       ├── available.html
│   │       ├── room_detail.html
│   │       └── room_list.html
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── users/
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── models.py
│   └── apps.py
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
│   ├── import_json.py
│   ├── import_sqlite_to_orm.py
│   ├── init_db.py
│   └── inspect_source_db.py
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
├── db.sqlite3
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
- каталог помещений (`/rooms/`) и оборудования (`/equipment/`);
- поиск свободных помещений на выбранную дату (`/rooms/available/`);
- детальная карточка помещения (`/rooms/<id>/`) или оборудования (`/equipment/<id>/`);
- список бронирований с фильтрацией, сортировкой и пагинацией (`/bookings/`);
- детальная карточка бронирования (`/bookings/<id>/`);
- страница сводной аналитической статистики (`/bookings/statistics/`).

Все страницы получают данные через методы Django ORM и передают их в шаблоны DTL.

## 6. Фильтрация, сортировка и пагинация бронирований (ПР9)
- **Фильтрация**: реализован отбор активных бронирований по дате (`?date=YYYY-MM-DD`), конкретному помещению (`?room=<id>`) и пользователю (`?user=<id>`).
- **Сортировка**: динамический порядок отображения по дате, названию помещения или имени пользователя (`?sort=date|room|user`).
- **Пагинация**: разбиение списка по 5 записей на страницу с помощью `Paginator` и сохранение параметров GET-запроса при пагинации через `{% querystring %}`.

## 7. Перенос данных из SQLite в Django ORM
Перенос данных из базы данных ПР7 (`data/roomly.sqlite`) в управляемую Django базу данных `db.sqlite3` выполняется скриптом `db/import_sqlite_to_orm.py`:
```bash
python db/import_sqlite_to_orm.py
```
Скрипт использует `update_or_create()` в рамках атомарной транзакции `transaction.atomic()`, гарантируя сохранение идентификаторов и внешних ключей.

## 8. Тестирование
Автоматизированные тесты pytest находятся в каталоге `tests/`:
- `test_bookings.py`
- `test_equipment.py`
- `test_users.py`
- `test_web.py` (включая проверку фильтрации, сортировки, пагинации, обработки 404 и аналитики)

Запуск тестов:
```bash
pytest -v
```

## 9. Проверка качества кода
Проверка соответствия стандарту PEP 8 линтером `flake8`:
```bash
flake8 . --extend-exclude=venv
```
Системная проверка Django:
```bash
python manage.py check
```

## 10. Запуск проекта
1. Применить миграции:
```bash
python manage.py migrate
```
2. Выполнить перенос данных (при необходимости):
```bash
python db/import_sqlite_to_orm.py
```
3. Запустить сервер разработки:
```bash
python manage.py runserver
```
Веб-интерфейс доступен по адресу:
```text
http://127.0.0.1:8000/
```

## 11. Текущее состояние проекта
На этапе завершения ПР9 реализовано:
- Описаны модели Django ORM `Room`, `User`, `Booking` с внешними ключами `ForeignKey`;
- Настроены параметры связей `on_delete=models.PROTECT` и `related_name="bookings"`;
- Созданы и применены миграции `0001_initial.py`;
- Исходные данные успешно перенесены в ORM-базу `db.sqlite3`;
- Представления переведены на использование менеджеров ORM (`all`, `filter`, `exclude`, `select_related`, `annotate`, `values`, `order_by`, `aggregate`, `Count`, `Sum`, `Avg`);
- Реализована параметрическая фильтрация, сортировка и пагинация списка бронирований;
- Поиск свободных помещений реализован через ORM с исключением занятых объектов;
- Страница статистики рассчитывает аналитику методами `annotate()` и `aggregate()`;
- 100% автотестов проходят успешно (44/44);
- Код полностью соответствует PEP 8.
