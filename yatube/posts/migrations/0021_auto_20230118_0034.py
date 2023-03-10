# Generated by Django 2.2.16 on 2023-01-17 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0020_auto_20230115_2313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='posts/', verbose_name='Картинка'),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_following'),
        ),
    ]
