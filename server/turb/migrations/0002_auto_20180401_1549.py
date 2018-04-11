# Generated by Django 2.0.2 on 2018-04-01 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('turb', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flight',
            name='aircraft',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='turb.Aircraft'),
        ),
        migrations.AlterField(
            model_name='flight',
            name='destination',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dest', to='turb.Airport'),
        ),
        migrations.AlterField(
            model_name='flight',
            name='origin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origin', to='turb.Airport'),
        ),
        migrations.AlterField(
            model_name='weatherreport',
            name='flight',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='turb.Flight'),
        ),
    ]
