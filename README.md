# Roomly – система бронирования лабораторного оборудования и помещений

Система бронирования помещений и оборудования учебно-научной лаборатории на Python с веб-интерфейсом на Django.

## 1. Назначение проекта
Roomly – учебное веб-приложение для управления оборудованием, помещениями и их бронированием.
Проект позволяет просматривать каталог приборов и помещений, информацию об их готовности и доступности, данные пользователей и историю бронирований через веб-интерфейс Django.
Проект развивается поэтапно: консольная версия приложения (ПР1–ПР3) дополнена веб-интерфейсом (ПР5) и переведена на систему шаблонов Django (ПР6).

## 2. Используемые технологии
- Python 3;
- Django 5;
- Django Template Language (DTL);
- HTML5;
- CSS3;
- JavaScript;
- Bootstrap 5;
- JSON для хранения данных;
- Git;
- pytest;
- flake8.

## 3. Предметная область
В системе используются три основные сущности:
- **Помещение (`Room`) / Оборудование (`Equipment`)** – идентификатор, название, инвентарный номер, ставка аренды, допуск, готовность и вместимость;
- **Пользователь (`User`)** – идентификатор, ФИО, роль (`Student`, `Staff`), уровень допуска и статус инструктажа;
- **Бронирование (`Booking`)** – номер заявки, ссылка на оборудование, ссылка на пользователя, период (`booking_date`, `duration_hours`), стоимость и статус активности.

Для предметной области реализованы собственные Python-классы в каталоге `models/`.
На текущем этапе данные хранятся в JSON-файлах. Django ORM и база данных приложения пока не используются.

## 4. Структура проекта
```text
work/
├── bookings/
│   ├── templates/
│   │   └── bookings/
│   │       ├── includes/
│   │       │   └── booking_status.html
│   │       ├── booking_detail.html
│   │       └── booking_list.html
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
│   └── users.json
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
- подробная карточка отдельного помещения (`/rooms/<id>/`) или прибора (`/equipment/<id>/`);
- список бронирований (`/bookings/`);
- карточка отдельного бронирования (`/bookings/<id>/`).

Для формирования страниц используются Django-шаблоны.
Генерация HTML непосредственно в Python-коде веб-представлений устранена. Вспомогательная функция `page()` полностью удалена.
Представления подготавливают данные и передают их в шаблоны через контекст с помощью `render()`.

## 6. Django Template Language
Шаблоны используют возможности Django Template Language (DTL).

### Базовый шаблон
Общий каркас страниц: `templates/base.html`.
Он содержит общую HTML-структуру страницы, тег `{% load static %}`, подключение стилей Bootstrap 5 и собственного `style.css`, подключение скрипта `main.js`, шапку с логотипом, навигацию `{% include "includes/navigation.html" %}`, футер и блоки для переопределения дочерними страницами:
```html
{% block title %}Roomly{% endblock %}
{% block content %}{% endblock %}
```

Дочерние шаблоны используют наследование:
```html
{% extends "base.html" %}
```

### Включаемые шаблоны
Повторяющиеся фрагменты вынесены в отдельные включаемые шаблоны:
- `templates/includes/navigation.html` – общая навигационная панель проекта;
- `rooms/includes/room_card.html` – карточка отдельного помещения;
- `equipment/includes/equipment_card.html` – карточка единицы оборудования;
- `bookings/includes/booking_status.html` – бейдж статуса заявки бронирования (активно / отменено).

Подключение выполняется тегом:
```html
{% include "rooms/includes/room_card.html" %}
{% include "bookings/includes/booking_status.html" %}
```

### Контекст
Представления передают данные в шаблоны через словарь контекста:
```python
context = {
    "rooms": rooms_list,
}
return render(request, "rooms/room_list.html", context)
```
В шаблоне данные доступны по именам ключей: `{{ rooms }}`, `{{ room.name }}`, `{{ booking.status }}`.

### Циклы и условия
Для перебора списков используются циклы:
```html
{% for room in rooms %}
    {% include "rooms/includes/room_card.html" %}
{% empty %}
    <p>Помещения не найдены.</p>
{% endfor %}
```
Условные конструкции применяются для отображения различных состояний и обработки ошибок:
```html
{% if booking.is_cancelled %}
    <span class="badge bg-secondary booking-status booking-status-cancelled">Отменено</span>
{% else %}
    <span class="badge bg-success booking-status booking-status-active">Активно</span>
{% endif %}
```

## 7. Фильтры шаблонов
В шаблонах применяются стандартные фильтры Django:
- `{{ rooms|length }}` – вывод количества элементов коллекции;
- `{{ room.name|default:"Без названия" }}` – подстановка значения по умолчанию при отсутствии данных;
- `{{ item.inventory_number|default:"—" }}` – форматирование инвентарного номера.

Фильтры используются исключительно для представления данных в UI, не подменяя бизнес-логику предметной модели.

## 8. URL-маршрутизация
Для всех страниц используются именованные маршруты и пространства имён (`app_name`):
- `homepage:index`
- `rooms:list`, `rooms:detail`
- `equipment:equipment_list`, `equipment:equipment_detail`
- `bookings:bookings`, `bookings:detail`

Ссылки в шаблонах строятся с помощью тега `{% url %}`:
```html
{% url 'homepage:index' %}
{% url 'rooms:list' %}
{% url 'rooms:detail' room.id %}
{% url 'bookings:bookings' %}
{% url 'bookings:detail' booking.id %}
```
Жёстко заданные URL-адреса в разметке не используются.

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

## 10. Хранение данных
Данные хранятся в JSON-файлах каталога `data/`:
- `data/equipment.json`
- `data/users.json`
- `data/bookings.json`

Загрузка и сохранение данных осуществляются функциями модуля `storage.py`.
Объекты восстанавливаются на базе классов предметной области из каталога `models/`.
Django ORM на текущем этапе не используется.

## 11. Основные модули
- `storage.py` – загрузка и сохранение данных JSON;
- `models/` – классы `Equipment`/`Room`, `User` (`Student`, `Staff`), `Booking` (`Period`);
- `main.py` – консольный интерфейс (сохранен из ПР3);
- `utils.py` – утилиты ввода для консольного режима;
- `rooms/views.py` – view-функции каталога и карточки помещения;
- `equipment/views.py` – view-функции каталога оборудования;
- `bookings/views.py` – view-функции реестра и деталей бронирования;
- `homepage/views.py` – view-функции главной страницы и ошибки 404.

## 12. Тестирование
Автоматизированные тесты pytest находятся в каталоге `tests/`:
- `test_bookings.py`
- `test_equipment.py`
- `test_users.py`
- `test_web.py`

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
git commit -m "PR6: add Django templates and static files"
```

## 16. Текущее состояние проекта
На этапе завершения ПР6 реализовано:
- Предметная объектная модель (`Room`/`Equipment`, `User`, `Booking`);
- Консольная версия с полным набором операций;
- JSON-хранилище данных;
- Двухуровневая маршрутизация Django с пространствами имен;
- Полный переход веб-части на систему шаблонов Django (DTL);
- Базовый шаблон `base.html` и наследование (`{% extends %}`, `{% block %}`);
- Включаемые шаблоны (`{% include %}`);
- Циклы (`{% for ... empty %}`) и условия (`{% if %}`);
- Фильтры DTL (`length`, `default`);
- Формирование URL через `{% url %}`;
- Статические файлы: собственный CSS, JS-сценарий и графический логотип;
- Обработка ошибок 404 со статусом HTTP 404;
- Полный набор модульных и интеграционных тестов.

Модели Django ORM, миграции и формы Django в текущей версии не используются и запланированы на следующие практические работы.

## 17. Дальнейшее развитие
В следующих практических работах (ПР7–ПР12) запланирован переход от JSON-хранилища к реляционной базе данных и моделям Django ORM, создание интерактивных веб-форм для добавления и изменения бронирований, валидация данных, аутентификация пользователей и разработка REST API.
