# pylint: disable=C0103,R0801
# Generated by Django 4.2.21 on 2025-05-28 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vcd", "0004_alter_virtualcontent_desc"),
    ]

    operations = [
        migrations.AlterField(
            model_name="virtualcontent",
            name="end_time",
            field=models.DateTimeField(db_index=True, verbose_name="End Time"),
        ),
    ]
