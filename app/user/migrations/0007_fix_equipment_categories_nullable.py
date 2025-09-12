# Generated manually to fix equipment_categories column

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_merchantprofile_views'),
    ]

    operations = [
        migrations.AlterField(
            model_name='merchantprofile',
            name='equipment_categories',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
