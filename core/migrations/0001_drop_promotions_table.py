from django.db import migrations


def drop_promotions_table(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS promotions_promotion;")
        cursor.execute("DELETE FROM django_migrations WHERE app = %s", ["promotions"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.RunPython(drop_promotions_table, noop),
    ]
