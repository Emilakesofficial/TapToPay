# Generated by Django 5.1.3 on 2025-04-28 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Passcode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("passcode", models.CharField(max_length=6)),
            ],
        ),
        migrations.AddField(
            model_name="profile",
            name="passcode",
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
