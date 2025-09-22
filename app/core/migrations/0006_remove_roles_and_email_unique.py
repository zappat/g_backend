# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_user_roles'),
    ]

    operations = [
        # Add username field without unique constraint first
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default='temp', max_length=255),
            preserve_default=False,
        ),
        
        # Remove unique constraint from email
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=255),
        ),
        
        # Remove roles field
        migrations.RemoveField(
            model_name='user',
            name='roles',
        ),
        
        # Add unique constraint on email + role
        migrations.AlterUniqueTogether(
            name='user',
            unique_together={('email', 'role')},
        ),
        
        # Update existing users to have proper usernames
        migrations.RunPython(
            code=lambda apps, schema_editor: update_existing_usernames(apps, schema_editor),
            reverse_code=migrations.RunPython.noop,
        ),
        
        # Now make username field unique
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]


def update_existing_usernames(apps, schema_editor):
    """Update existing users to have proper usernames based on email and role"""
    User = apps.get_model('core', 'User')
    
    for user in User.objects.all():
        if not user.username or user.username == 'temp':
            user.username = f"{user.email}_{user.role}"
            user.save()
