# Generated by Django 2.2 on 2020-07-27 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20200727_1638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
