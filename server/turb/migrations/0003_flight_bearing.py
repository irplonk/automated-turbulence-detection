# Generated by Django 2.0.4 on 2018-04-14 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('turb', '0002_auto_20180401_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='bearing',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=9),
            preserve_default=False,
        ),
    ]