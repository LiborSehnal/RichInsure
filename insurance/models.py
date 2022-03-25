from django.db import models
from django.contrib.auth.models import User
from customer.models import Customer

class Category(models.Model):
    category_name = models.CharField(max_length=20)
    creation_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.category_name


class Policy(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    policy_name = models.CharField(max_length=200)
    sum_assurance = models.PositiveIntegerField()
    premium = models.PositiveIntegerField()
    creation_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.policy_name

    class Meta:
        ordering = ['policy_name']


class PolicyRecord(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    Policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    status = models.CharField(max_length=100,default='Pending')
    creation_date = models.DateField(auto_now=True)
    sum_assurance = models.PositiveIntegerField(default='0')
    premium = models.PositiveIntegerField(default='0')

    def __str__(self):
        return self.policy


class InsuranceEventRecord(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, default='Odesláno')
    creation_date = models.DateField(auto_now=True)
    description = models.CharField(max_length=500)
    admin_comment = models.CharField(max_length=500, default=' ')

    def __str__(self):
        return self.description


class Question(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    description = models.CharField(max_length=500)
    admin_comment = models.CharField(max_length=200, default=' ')
    asked_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.description