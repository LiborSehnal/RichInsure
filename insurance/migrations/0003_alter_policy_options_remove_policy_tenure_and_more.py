# Generated by Django 4.0.3 on 2022-03-18 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_customer_mail'),
        ('insurance', '0002_alter_policyrecord_premium_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='policy',
            options={'ordering': ['policy_name']},
        ),
        migrations.RemoveField(
            model_name='policy',
            name='tenure',
        ),
        migrations.AlterField(
            model_name='question',
            name='admin_comment',
            field=models.CharField(default=' ', max_length=200),
        ),
        migrations.CreateModel(
            name='InsuranceEventRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='Pending', max_length=100)),
                ('creation_date', models.DateField(auto_now=True)),
                ('description', models.CharField(max_length=500)),
                ('admin_comment', models.CharField(default=' ', max_length=500)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.customer')),
                ('policy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='insurance.policy')),
            ],
        ),
    ]