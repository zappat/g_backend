# Generated manually for user roles field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='roles',
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('renter', 'Renter'), ('merchant', 'Merchant')], default='renter', help_text='Legacy field - use roles instead', max_length=20),
        ),
    ]