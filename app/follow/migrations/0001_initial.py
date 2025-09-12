# Generated manually for follow app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid
from core.mixins import UUIDBase


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0005_user_roles'),  # Adjust based on your latest core migration
    ]

    operations = [
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('follower', models.ForeignKey(
                    help_text='User who is following',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='following',
                    to=settings.AUTH_USER_MODEL
                )),
                ('following', models.ForeignKey(
                    help_text='User who is being followed',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='followers',
                    to=settings.AUTH_USER_MODEL
                )),
                ('mode', models.IntegerField(
                    choices=[(1, 'Renter to Merchant'), (2, 'Merchant to Renter')],
                    default=1,
                    help_text='1 for renter following merchant, 2 for merchant following renter'
                )),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Follow',
                'verbose_name_plural': 'Follows',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together={('follower', 'following', 'mode')},
        ),
    ]