# Generated by Django 5.1.1 on 2024-10-31 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistic', '0005_alter_order_tracking_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=128),
        ),
    ]
