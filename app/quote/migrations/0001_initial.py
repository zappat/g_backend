from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("core", "0004_alter_user_role"),
        ("rfq", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Quote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quote", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.user"),
                ),
                (
                    "rfq",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="rfq.rfq"),
                ),
            ],
        ),
    ]

