# Generated by Django 5.0.4 on 2024-04-20 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals_auth', '0003_alter_customuser_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='id',
            field=models.CharField(default='5429d9e72e9b48de947a0083fcd1217a', max_length=64, primary_key=True, serialize=False),
        ),
    ]
