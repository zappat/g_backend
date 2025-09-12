from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('training', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL - drop and recreate column
            sql="""
            ALTER TABLE training_trainingcourse DROP COLUMN created_by_id;
            ALTER TABLE training_trainingcourse ADD COLUMN created_by_id integer;
            """,
            # Reverse SQL
            reverse_sql="""
            ALTER TABLE training_trainingcourse DROP COLUMN created_by_id;
            ALTER TABLE training_trainingcourse ADD COLUMN created_by_id uuid;
            """
        ),
    ]