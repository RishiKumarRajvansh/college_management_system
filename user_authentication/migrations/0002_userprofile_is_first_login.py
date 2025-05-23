from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_authentication', '0001_initial'),  # This may need to be adjusted based on existing migrations
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_first_login',
            field=models.BooleanField(default=True),
        ),
    ]
