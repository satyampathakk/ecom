# Generated by Django 4.2.5 on 2023-10-22 08:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecom', '0005_order_payment_delete_contact_order_payment_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='razorpay_status',
        ),
    ]
