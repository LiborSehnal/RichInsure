from django.shortcuts import render, redirect, reverse
from . import forms, models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.db.models import Q
from insurance import models as CMODEL
from insurance import forms as CFORM
from django.contrib.auth.models import User


def customerclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'customer/customerclick.html')


def customer_signup_view(request):
    userForm = forms.CustomerUserForm()
    customerForm = forms.CustomerForm()
    mydict = {'userForm': userForm, 'customerForm': customerForm}
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST)
        customerForm = forms.CustomerForm(request.POST, request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customer = customerForm.save(commit=False)
            customer.user = user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
        return HttpResponseRedirect('customerlogin')
    return render(request, 'customer/customersignup.html', context=mydict)


def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()


@login_required(login_url='customerlogin')
def customer_dashboard_view(request):
    dict = {
        'customer': models.Customer.objects.get(user_id=request.user.id),
        'available_policy': CMODEL.Policy.objects.all().count(),
        'applied_policy': CMODEL.PolicyRecord.objects.all().filter(status='Approved',
            customer=models.Customer.objects.get(user_id=request.user.id)).count(),
        'total_category': CMODEL.Category.objects.all().count(),
        'total_question': CMODEL.Question.objects.all().filter(
            customer=models.Customer.objects.get(user_id=request.user.id)).count(),
        'total_events': CMODEL.InsuranceEventRecord.objects.all().filter(
            customer=models.Customer.objects.get(user_id=request.user.id)).count(),

    }
    return render(request, 'customer/customer_dashboard.html', context=dict)


def apply_policy_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policies = CMODEL.Policy.objects.all().order_by('category', 'sum_assurance')
    return render(request, 'customer/apply_policy.html', {'policies': policies, 'customer': customer})


def apply_view(request, pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policy = CMODEL.Policy.objects.get(id=pk)
    policyrecord = CMODEL.PolicyRecord()
    policyrecord.Policy = policy
    policyrecord.customer = customer
    policyrecord.save()
    return redirect('apply-policy')


def my_products_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policies = CMODEL.PolicyRecord.objects.all().filter(customer=customer, status='Approved')
    total_sum = CMODEL.PolicyRecord.objects.filter(customer=customer).aggregate(sum=Sum('premium'))
    total_sum_number = total_sum['sum']
    return render(request, 'customer/myproducts.html', {'policies': policies, 'customer': customer, 'totalsum': total_sum_number})


def ask_question_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    questionForm = CFORM.QuestionForm()

    if request.method == 'POST':
        questionForm = CFORM.QuestionForm(request.POST)
        if questionForm.is_valid():
            question = questionForm.save(commit=False)
            question.customer = customer
            question.save()
            return redirect('question-history')
    return render(request, 'customer/ask_question.html', {'questionForm': questionForm, 'customer': customer})


def question_history_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    questions = CMODEL.Question.objects.all().filter(customer=customer)
    return render(request, 'customer/question_history.html', {'questions': questions, 'customer': customer})


# PŘÍDAT TŘÍDA INS EVENTS
def customer_event_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    events = CMODEL.InsuranceEventRecord.objects.all().filter(customer=customer).order_by('creation_date')
    return render(request, 'customer/customer_view_event.html', {'events': events, 'customer': customer})


def customer_event_add(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    eventForm = CFORM.EventForm()

    if request.method == 'POST':
        eventForm = CFORM.EventForm(request.POST)

        if eventForm.is_valid():
            question = eventForm.save(commit=False)
            question.customer = customer
            question.save()
            return redirect('customer-event-views')
    return render(request, 'customer/customer_event_add.html', {'eventForm': eventForm, 'customer': customer})