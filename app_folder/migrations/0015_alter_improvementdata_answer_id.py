# Generated by Django 5.0.10 on 2025-02-03 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_folder', '0014_seqmst_imp_no_settingmst_imp_str_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='improvementdata',
            name='answer_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='回答者'),
        ),
    ]
