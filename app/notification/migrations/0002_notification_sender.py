# Generated manually for notification sender field

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_user_role'),
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='sender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_notifications', to='core.user'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('quote', 'New Quote'), ('message', 'New Message'), ('following', 'New Follower'), ('review', 'New Review'), ('rfq_expired', 'RFQ Expired'), ('rfq_expiring', 'RFQ Expiring'), ('rfq_new', 'New RFQ')], default='general', max_length=20),
        ),
    ]