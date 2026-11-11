# Roomly – система бронирования лабораторного оборудования и помещений

Система бронирования помещений и специализированного оборудования учебно-научной лаборатории (вариант 209) на Python с веб-интерфейсом на Django и слоем доступа к данным на основе Django ORM.

## 1. Назначение проекта
Roomly – сквозное учебное веб-приложение для управления лабораторным оборудованием, помещениями и заявками на их бронирование.
Проект позволяет:
- просматривать каталог оборудования и помещений с учётом исправности, нахождения на ТО, требуемого уровня допуска и почасовой ставки;
- выполнять регистронезависимый поиск (включая кириллицу) по названию и инвентарному номеру;
- искать свободные и исправные ресурсы на выбранную дату;
- фильтровать список бронирований по дате, ресурсу, пользователю, роли связанного пользователя и поисковой строке, сортировать результаты и просматривать их постранично;
- просматривать детальные карточки объектов с обработкой отсутствующих записей (`get_object_or_404`) и сводную аналитическую статистику.

Проект развивался поэтапно: консольное ООП-приложение с JSON-хранилищем (ПР1–ПР3) -> базовый веб-интерфейс Django (ПР5) -> система шаблонов DTL и статика (ПР6) -> реляционная БД SQLite и SQL-запросы (ПР7) -> модели, миграции и запросы Django ORM (ПР9).

## 2. Используемые технологии
- Python 3.11+;
- Django 5.2 (MTV, Django ORM, миграции, фикстуры, Django Admin);
- Django Debug Toolbar (инспекция SQL-запросов в режиме отладки);
- SQLite 3 (`db.sqlite3` – база Django ORM; `data/roomly.sqlite` – исходная база ПР7);
- Django Template Language (DTL), HTML5, CSS3, JavaScript, Bootstrap 5.3;
- pytest, pytest-django, Django `TestCase`, flake8;
- Git и GitHub.

## 3. Модели данных Django ORM (ПР9)
- **`Room` (`rooms/models.py`)** – лабораторное оборудование и помещения:
  - `name` (`CharField`) – наименование прибора / помещения;
  - `capacity` (`PositiveIntegerField`, `default=1`) – вместимость;
  - `inventory_number` (`CharField`, `blank=True`, `default=""`) – инвентарный номер;
  - `operational` (`BooleanField`, `default=True`) – признак исправности;
  - `under_maintenance` (`BooleanField`, `default=False`) – нахождение на техобслуживании;
  - `required_level` (`PositiveIntegerField`, `validators=[1..3]`) – требуемый уровень допуска;
  - `hourly_rate` (`FloatField`, `MinValueValidator(0.0)`) – почасовая ставка;
  - свойство `is_ready`, методы `check_readiness()`, `is_suitable_for()`, `is_suitable_for_level()`.
- **`User` (`users/models.py`)** – пользователи лаборатории:
  - `name` (`CharField`) – ФИО пользователя;
  - `email` (`EmailField`) – электронная почта;
  - `role` (`CharField`, `choices`: `студент` / `сотрудник`) – роль пользователя;
  - `access_level` (`PositiveIntegerField`, `validators=[1..3]`) – уровень допуска;
  - `briefing_passed` (`BooleanField`, `default=True`) – отметка о прохождении инструктажа по ТБ;
  - методы `has_access(required_level)`, `is_student()`.
- **`Booking` (`bookings/models.py`)** – заявки на бронирование:
  - `room` (`ForeignKey(Room, on_delete=models.PROTECT, related_name="bookings")`);
  - `user` (`ForeignKey(User, on_delete=models.PROTECT, related_name="bookings")`);
  - `booking_date` (`DateField`) – дата бронирования;
  - `duration_hours` (`FloatField`, `MinValueValidator(0.5)`) – длительность в часах;
  - `cost` (`FloatField`, `MinValueValidator(0.0)`) – стоимость бронирования;
  - `is_cancelled` (`BooleanField`, `default=False`) – признак отмены;
  - `notes` (`TextField`, `blank=True`, `null=True`) – необязательное примечание;
  - метод `cancel()` (`save(update_fields=["is_cancelled"])`) и свойство `status`.

## 4. Основные веб-страницы и ORM-операции
- `/` – главная страница с подборками топ-3 готовых приборов и ближайших заявок (срез `QuerySet [:3]`, `select_related`);
- `/rooms/` и `/equipment/` – каталоги ресурсов с поиском по строковым полям (`Q(name__icontains=q) | Q(inventory_number__icontains=q)`), фильтрацией по вместимости / уровню допуска и готовности;
- `/rooms/<id>/` и `/equipment/<id>/` – карточки ресурсов (`get_object_or_404`, обратная связь `room.bookings`, `.exists()`);
- `/rooms/available/` – поиск свободных и исправных ресурсов на дату (`filter` + `values_list` + `exclude`);
- `/bookings/` – список активных бронирований с фильтрацией по дате, помещению, пользователю, полям связанных моделей (`user__role`, `room__name`, `user__name`), безопасной сортировкой (`sort_fields`), `annotate(F(...))`, `values(...)` и пагинацией (`Paginator` + `{% querystring %}`);
- `/bookings/<id>/` – детальная карточка бронирования (`get_object_or_404` + `select_related("room", "user")`);
- `/bookings/statistics/` – аналитическая сводка (`Room.objects.annotate(Count(..., filter=Q(...)), Sum(...))` и `aggregate(Count, Sum, Avg, Min, Max)`);
- `/admin/` – панель администратора Django с зарегистрированными моделями `Room`, `User`, `Booking`.

## 5. Структура проекта
```text
work/
├── bookings/                 # Приложение бронирований (models, views, urls, admin, templates, migrations, tests)
├── equipment/                # Приложение каталога лабораторного оборудования (views, urls, templates, tests)
├── homepage/                 # Главная страница, обработчик 404 и статика (CSS, JS, логотип)
├── rooms/                    # Приложение помещений/ресурсов (models, views, urls, admin, apps, templates, migrations, tests)
├── users/                    # Приложение пользователей предметной области (models, admin, migrations, tests)
├── roomly/                   # Конфигурация Django-проекта (settings.py, urls.py, wsgi.py, asgi.py)
├── templates/                # Базовый шаблон base.html, 404.html и навигация includes/navigation.html
├── db/                       # Скрипты работы с БД ПР7 и переноса в ORM (import_sqlite_to_orm.py, inspect_source_db.py)
├── sql/                      # SQL-схема (schema.sql) и SQL-запросы ПР7 (queries.sql)
├── data/                     # Исходные JSON, база ПР7 (roomly.sqlite) и фикстура Django (fixtures/initial_data.json)
├── models/                   # Классы предметной области консольной версии ПР1–ПР3
├── tests/                    # Автотесты pytest (модели ПР3 и веб-интеграция test_web.py)
├── main.py                   # Консольное приложение ПР1–ПР3
├── storage.py                # Модуль JSON-хранилища ПР1–ПР3
├── utils.py                  # Вспомогательные функции ввода и инспекции
├── manage.py                 # Утилита управления Django-проектом
├── pytest.ini                # Конфигурация pytest и pytest-django
└── requirements.txt          # Зависимости проекта
```

## 6. Установка и запуск проекта
1. Клонировать репозиторий и перейти в каталог проекта:
```bash
git clone https://github.com/MIXSITI/Laboratory_equipment_level.git
cd Laboratory_equipment_level
```
2. Создать и активировать виртуальное окружение:
```bash
python -m venv venv
venv\Scripts\activate
```
3. Установить зависимости:
```bash
pip install -r requirements.txt
```
4. Применить миграции Django:
```bash
python manage.py migrate
```
5. Наполнить базу `db.sqlite3` исходными данными (любым из двух способов):
```bash
# Способ 1: перенос из базы ПР7 data/roomly.sqlite скриптом ORM
python db/import_sqlite_to_orm.py

# Способ 2: загрузка подготовленной фикстуры Django
python manage.py loaddata data/fixtures/initial_data.json
```
6. Запустить сервер разработки:
```bash
python manage.py runserver
```
Приложение будет доступно по адресу `http://127.0.0.1:8000/` (в режиме `DEBUG=True` справа отображается панель **Django Debug Toolbar** для просмотра SQL-запросов).

## 7. Проверка и тестирование
```bash
python manage.py check
python manage.py makemigrations --check
python manage.py showmigrations
python manage.py test
pytest -v
flake8 . --extend-exclude=venv
```

## 8. Автор
- **Кобылянский С.С.**, группа **ЭФБО-10-24** (РТУ МИРЭА).
