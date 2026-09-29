"""Представления приложения главной страницы."""

from django.http import HttpResponse


def page(title: str, content: str) -> str:
    """Сформировать единый HTML-каркас страницы с подключением Bootstrap."""
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
        "/dist/css/bootstrap.min.css"
    )
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="{bootstrap}">
</head>
<body>
    <nav class="nav p-3 mb-4 bg-light border-bottom">
        <div class="container d-flex">
            <a class="nav-link text-dark fw-bold" href="/">ЛабБронь</a>
            <a class="nav-link" href="/">Главная</a>
            <a class="nav-link" href="/equipment/">Оборудование</a>
            <a class="nav-link" href="/bookings/">Бронирования</a>
        </div>
    </nav>
    <main class="container">{content}</main>
</body>
</html>"""


def index(request) -> HttpResponse:
    """Главная страница проекта."""
    content = """
<h1 class="display-4">Лабораторное оборудование</h1>
<p class="lead">Система бронирования лабораторного оборудования.</p>
<p>Основные разделы:</p>
<a href="/equipment/" class="btn btn-primary me-2">Оборудование</a>
<a href="/bookings/" class="btn btn-secondary">Бронирования</a>
"""
    return HttpResponse(page("Лабораторное оборудование", content))
