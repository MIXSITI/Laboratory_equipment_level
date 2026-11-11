import re

from django.apps import AppConfig
from django.db.backends.signals import connection_created


def _unicode_like(
    pattern: str | None,
    value: str | None,
    escape: str | None = None,
) -> bool:
    if pattern is None or value is None:
        return False
    esc = escape or ""
    regex_parts: list[str] = []
    idx = 0
    length = len(pattern)
    while idx < length:
        char = pattern[idx]
        if esc and char == esc and idx + 1 < length:
            regex_parts.append(re.escape(pattern[idx + 1]))
            idx += 2
        elif char == "%":
            regex_parts.append(".*")
            idx += 1
        elif char == "_":
            regex_parts.append(".")
            idx += 1
        else:
            regex_parts.append(re.escape(char))
            idx += 1
    regex = "".join(regex_parts)
    flags = re.IGNORECASE | re.DOTALL
    return re.fullmatch(regex, str(value), flags=flags) is not None


def _register_sqlite_unicode_functions(sender, connection, **kwargs) -> None:
    if connection.vendor == "sqlite":
        connection.connection.create_function("like", 2, _unicode_like)
        connection.connection.create_function("like", 3, _unicode_like)


class RoomsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rooms"
    verbose_name = "Помещения и оборудование"

    def ready(self) -> None:
        connection_created.connect(_register_sqlite_unicode_functions)
