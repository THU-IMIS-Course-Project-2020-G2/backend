# Generated by Django 3.1 on 2020-08-28 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_auto_20200828_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='order_detail',
            name='start_time',
            field=models.DateTimeField(null=True, verbose_name='开始下单时间'),
        ),
    ]
