# Generated by Django 5.0.10 on 2025-01-23 02:17

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_folder', '0009_seqmst_offdaydata_ap_no_offdaydata_attach2_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SettingMst',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('host_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='ホストメールアドレス')),
                ('request_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='申請承認済宛先')),
                ('offday_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='勤怠承認済宛先')),
                ('ap_digit', models.IntegerField(default=0, verbose_name='承認番号桁')),
                ('ap_str', models.CharField(blank=True, max_length=2, null=True)),
                ('od_str', models.CharField(blank=True, max_length=2, null=True)),
            ],
            options={
                'verbose_name_plural': '設定マスタ',
                'db_table': 'SettingMst',
            },
        ),
    ]
