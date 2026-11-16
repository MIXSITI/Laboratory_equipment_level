# Roomly – система бронирования лабораторного оборудования и помещений

Система бронирования помещений и специализированного оборудования учебно-научной лаборатории (вариант 209) на Python с веб-интерфейсом на Django, доступом к данным через Django ORM и настроенной административной панелью Django Admin.

## 1. Назначение проекта
Roomly – сквозное учебное веб-приложение для управления лабораторным оборудованием, помещениями и заявками на их бронирование.
Проект позволяет:
- управлять помещениями/оборудованием, пользователями и бронированиями через локализованную административную панель Django Admin (`/admin/`) с встроенными таблицами (`TabularInline`), редактированием в списке (`list_editable`), автодополнением (`autocomplete_fields`), иерархией по датам (`date_hierarchy`) и массовыми действиями (`actions`);
- открывать карточки помещений по человекочитаемому транслитерированному URL (`<slug:slug>`, `get_absolute_url()`) и определять крупные помещения через вычисляемое базой данных поле `GeneratedField` (`is_large`);
- централизованно выводить общие данные сайта и счётчик ресурсов через контекстный процессор `rooms.context_processors.room_context`;
- работать с тремя статусами бронирования через `Booking.Status(TextChoices)` (`ACTIVE`, `CANCELLED`, `COMPLETED`) и методы пользовательского менеджера `Booking.objects.active()`, `.cancelled()`, `.completed()`, `.for_date()`;
- искать свободные и исправные ресурсы на дату, фильтровать, сортировать и просматривать постранично список бронирований, а также анализировать статистику и SQL-запросы через **Django Debug Toolbar**.

Проект развивался поэтапно: консольное ООП-приложение с JSON-хранилищем (ПР1–ПР3) -> базовый веб-интерфейс Django (ПР5) -> система шаблонов DTL и статика (ПР6) -> реляционная БД SQLite и SQL-запросы (ПР7) -> модели, миграции и запросы Django ORM (ПР9) -> Django Admin, `TextChoices`, пользовательский менеджер `QuerySet`, `GeneratedField`, `slug` и контекстный процессор (ПР10).

## 2. Используемые технологии
- Python 3.11+;
- Django 5.2 (MTV, Django ORM, `GeneratedField`, `TextChoices`, миграции схемы и данных `RunPython`, фикстуры, Django Admin);
- Unidecode (транслитерация кириллицы для автогенерации `slug`);
- Django Debug Toolbar (инспекция и оптимизация SQL-запросов в режиме отладки);
- SQLite 3 (`db.sqlite3` – целевая база Django ORM; `data/roomly.sqlite` – исходная база ПР7);
- Django Template Language (DTL), HTML5, CSS3, JavaScript, Bootstrap 5.3;
- pytest, pytest-django, Django `TestCase`, flake8;
- Git и GitHub.

## 3. Модели данных Django ORM (ПР9–ПР10)
- **`Room` (`rooms/models.py`)** – лабораторное оборудование и помещения:
  - `name` (`CharField`) – наименование прибора / помещения;
  - `slug` (`SlugField`, `unique=True`, `editable=False`) – уникальный англоязычный URL-идентификатор (генерируется автоматически через `unidecode` + `slugify` + `pk`);
  - `capacity` (`PositiveIntegerField`, `default=1`, `help_text=...`) – вместимость;
  - `is_large` (`GeneratedField`, `db_persist=True`) – признак большого помещения (`capacity >= 50`), вычисляемый на стороне СУБД;
  - `inventory_number` (`CharField`, `blank=True`, `default=""`) – инвентарный номер;
  - `operational` (`BooleanField`, `default=True`), `under_maintenance` (`BooleanField`, `default=False`), `required_level` (`1..3`), `hourly_rate` (`FloatField`);
  - методы `get_absolute_url()`, `check_readiness()`, `is_suitable_for()`, `is_suitable_for_level()`, свойство `is_ready`.
- **`User` (`users/models.py`)** – пользователи предметной области лаборатории:
  - `name` (`CharField`), `email` (`EmailField`), `role` (`CharField`, `choices`: `студент` / `сотрудник`), `access_level` (`1..3`), `briefing_passed` (`BooleanField`);
  - методы `has_access(required_level)`, `is_student()`.
- **`Booking` (`bookings/models.py`)** – заявки на бронирование:
  - `Status(models.TextChoices)`: `ACTIVE` (`"active"`, «Активно»), `CANCELLED` (`"cancelled"`, «Отменено»), `COMPLETED` (`"completed"`, «Завершено»);
  - `room` (`ForeignKey(Room, on_delete=models.PROTECT, related_name="bookings")`);
  - `user` (`ForeignKey(User, on_delete=models.PROTECT, related_name="bookings")`);
  - `booking_date` (`DateField`), `duration_hours` (`FloatField`), `cost` (`FloatField`), `status` (`CharField`, `choices=Status.choices`, `default=Status.ACTIVE`), `notes` (`TextField`, `blank=True`, `null=True`);
  - пользовательский `BookingQuerySet` и `BookingManager` (`objects`): методы `active()`, `cancelled()`, `completed()`, `for_date(selected_date)`;
  - метод `cancel()` (`self.status = self.Status.CANCELLED; self.save(update_fields=["status"])`).

## 4. Административная панель Django Admin (`/admin/`)
- **`RoomAdmin` (`rooms/admin.py`)**: столбцы с аннотированным счётчиком `active_bookings_count` (`get_queryset` без проблемы `N+1`), `is_large`, ссылкой `site_link` и кнопкой «Посмотреть на сайте» (`view_on_site = True`); редактирование вместимости в списке (`list_editable = ("capacity",)`), `readonly_fields = ("id", "slug", "is_large")`, встроенная таблица заявок `BookingInline`.
- **`UserAdmin` (`users/admin.py`)**: поиск по имени и `email`, фильтры по роли, допуску и инструктажу, `readonly_fields = ("id",)`, встроенная таблица заявок `UserBookingInline`.
- **`BookingAdmin` (`bookings/admin.py`)**: оптимизация `list_select_related = ("room", "user")`, вычисляемый столбец `room_capacity` с сортировкой `room__capacity`, поиск по `room__name` и `user__name`, фильтры по дате и статусу, `date_hierarchy = "booking_date"`, `autocomplete_fields = ("room", "user")`, массовые действия «Отменить выбранные бронирования» и «Вернуть в активные».

## 5. Основные веб-страницы и маршруты
- `/` – главная страница с топ-3 готовых ресурсов и ближайших активных заявок (срез `QuerySet [:3]`, `select_related`);
- `/rooms/` и `/equipment/` – каталоги ресурсов с регистронезависимым поиском (`Q(name__icontains=q) | Q(inventory_number__icontains=q)`, а в `/rooms/` также по числовой вместимости), фильтрами и динамической сортировкой (`sort=name|capacity`, `direction=asc|desc`);
- `/rooms/<slug:slug>/` – детальная карточка помещения по `slug` (`get_object_or_404`, `get_absolute_url()`, редирект со старых `/rooms/<int:room_id>/`);
- `/equipment/<int:equipment_id>/` – детальная карточка лабораторного прибора;
- `/rooms/available/` – поиск свободных и исправных ресурсов на дату (учитываются только брони со статусом `ACTIVE`);
- `/bookings/` – список бронирований с фильтрацией по статусу (`active|cancelled|completed|all`), дате, ресурсу, пользователю и его роли, поиском по связанным полям, сортировкой (`sort_fields`), `annotate(F(...))`, `values(...)` и `Paginator` с `{% querystring %}`;
- `/bookings/<int:booking_id>/` – детальная карточка бронирования (`select_related("room", "user")`);
- `/bookings/statistics/` – аналитическая сводка по всем статусам (`ACTIVE`, `CANCELLED`, `COMPLETED`) и выручке;
- `/admin/` – административная панель Django.

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
4. Применить миграции и создать суперпользователя (для входа в `/admin/`):
```bash
python manage.py migrate
python manage.py createsuperuser
```
5. Наполнить базу `db.sqlite3` данными:
```bash
python manage.py loaddata data/fixtures/initial_data.json
```
6. Запустить сервер разработки:
```bash
python manage.py runserver
```
Приложение доступно по адресу `http://127.0.0.1:8000/`, административная панель — `http://127.0.0.1:8000/admin/`.

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
