from django.db import migrations
from django.utils.text import slugify
from unidecode import unidecode


def populate_room_slugs(apps, schema_editor):
    Room = apps.get_model("rooms", "Room")
    for room in Room.objects.all().order_by("pk"):
        transliterated_name = unidecode(room.name)
        base_slug = slugify(transliterated_name) or "room"
        room.slug = f"{base_slug}-{room.pk}"
        room.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0005_room_slug"),
    ]

    operations = [
        migrations.RunPython(
            populate_room_slugs,
            migrations.RunPython.noop,
        ),
    ]
