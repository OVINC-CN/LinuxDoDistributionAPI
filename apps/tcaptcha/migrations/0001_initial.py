# Generate# pylint: disable=C0103,R0801d by Django 4.2.21 on 2025-05-25 05:32

import django.db.models.deletion
import ovinc_client.core.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TCaptchaBlackList",
            fields=[
                (
                    "id",
                    models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tcaptcha_blacklist",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "TCaptcha Blacklist",
                "verbose_name_plural": "TCaptcha Blacklist",
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="TCaptchaHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID"),
                ),
                (
                    "client_ip",
                    models.GenericIPAddressField(db_index=True, verbose_name="Client IP"),
                ),
                (
                    "is_success",
                    models.BooleanField(db_index=True, default=False, verbose_name="Is Success"),
                ),
                ("params", models.JSONField(default=dict, verbose_name="Params")),
                ("result", models.JSONField(default=dict, verbose_name="Result")),
                (
                    "verify_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Verify At"),
                ),
                (
                    "user",
                    ovinc_client.core.models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tcaptcha_histories",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "TCaptcha History",
                "verbose_name_plural": "TCaptcha History",
                "ordering": ["-id"],
                "indexes": [
                    models.Index(
                        fields=["user", "verify_at", "is_success", "client_ip"],
                        name="tcaptcha_tc_user_id_8c49a2_idx",
                    )
                ],
            },
        ),
    ]
