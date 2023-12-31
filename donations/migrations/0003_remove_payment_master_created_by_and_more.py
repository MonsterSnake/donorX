# Generated by Django 4.2.3 on 2023-07-31 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0002_rename_checksum_payment_details_requested_checksum_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment_master',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='payment_master',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='payment_master',
            name='updated_on',
        ),
        migrations.AddField(
            model_name='payment_master',
            name='amount',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='payment_master',
            name='requested_checksum',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='payment_master',
            name='responsed_checksum',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='payment_master',
            name='created_on',
            field=models.DateTimeField(),
        ),
        migrations.DeleteModel(
            name='payment_details',
        ),
    ]
