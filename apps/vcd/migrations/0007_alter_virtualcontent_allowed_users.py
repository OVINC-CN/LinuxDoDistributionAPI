# pylint: disable=C0103,R0801
# Generated by Django 4.2.21 on 2025-05-29 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "vcd",
            "0006_rename_virtualcontent_created_by_created_at_vcd_virtual_created_e03cfc_idx_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="virtualcontent",
            name="allowed_users",
            field=models.JSONField(blank=True, default=list, verbose_name="Allowed Users"),
        ),
    ]
