# Generated by Django 4.1.7 on 2023-03-29 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0007_remove_toy_dogs_dog_toys'),
    ]

    operations = [
        migrations.AlterField(
            model_name='toy',
            name='color',
            field=models.CharField(choices=[('B', 'Blue'), ('Y', 'Yellow'), ('P', 'Purple'), ('R', 'Red'), ('G', 'Green')], default='B', max_length=1),
        ),
    ]
