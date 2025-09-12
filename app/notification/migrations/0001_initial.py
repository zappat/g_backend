# Generated manually for notification app

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0004_alter_user_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('notification_type', models.CharField(choices=[('quote', 'New Quote'), ('message', 'New Message'), ('following', 'New Follower'), ('review', 'New Review'), ('rfq_expired', 'RFQ Expired'), ('rfq_expiring', 'RFQ Expiring'), ('rfq_new', 'New RFQ')], default='quote', max_length=20)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('related_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('related_object_type', models.CharField(blank=True, max_length=50, null=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='core.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]