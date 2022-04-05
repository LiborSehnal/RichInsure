from django.shortcuts import render, redirect, reverse
from reportlab.pdfbase import pdfmetrics

from . import forms, models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, FileResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth.models import User
from customer import models as CMODEL
from customer import forms as CFORM
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from .models import PolicyRecord

# LOGIN VIEWS
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'insurance/index.html')

# ověření autentikace
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()

# přesměrování na admin/user sekci
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer/customer-dashboard')
    else:
        return redirect('admin-dashboard')


def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')

# admin base view - DASHBOARD. Načte nástěnku, ukáže základní menu + počty
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    dict = {
        'total_user': CMODEL.Customer.objects.all().count(),
        'total_policy': models.Policy.objects.all().count(),
        'total_category': models.Category.objects.all().count(),
        'total_question': models.Question.objects.all().count(),
        'total_policy_holder': models.PolicyRecord.objects.all().filter(status='Pending').count(),
        'approved_policy_holder': models.PolicyRecord.objects.all().filter(status='Approved').count(),
        'disapproved_policy_holder': models.PolicyRecord.objects.all().filter(status='Disapproved').count(),
        'waiting_policy_holder': models.PolicyRecord.objects.all().filter(status='Pending').count(),
        'total_events': models.InsuranceEventRecord.objects.all().count()
    }
    return render(request, 'insurance/admin_dashboard.html', context=dict)


#  UPRAVIT ADMIN-CUSTOMER ClASS
# admin pohled na zákazníky
@login_required(login_url='adminlogin')
def admin_view_customer_view(request):
    customers = CMODEL.Customer.objects.all()
    return render(request, 'insurance/admin_view_customer.html', {'customers': customers})

# admin pohled na detail zákazníka
@login_required(login_url='adminlogin')
def admin_customer_detail_view(request, pk):
    customers = CMODEL.Customer.objects.get(id=pk)
    user = CMODEL.User.objects.get(id=customers.user_id)
    policy = models.PolicyRecord.objects.filter(customer_id=pk, status="Approved")
    total_sum = models.PolicyRecord.objects.filter(customer=customers).aggregate(sum=Sum('premium'))
    total_sum_number = total_sum['sum']
    return render(request, 'insurance/customer_detail.html', {'customers': customers, "user": user, "policy": policy, 'totalsum': total_sum_number})

# admin update karty zákazníka + konkrétních produktů
@login_required(login_url='adminlogin')
def update_customer_view(request, pk):
    customer = CMODEL.Customer.objects.get(id=pk)
    user = CMODEL.User.objects.get(id=customer.user_id)
    userForm = CFORM.CustomerUserForm(instance=user)
    customerForm = CFORM.CustomerForm(instance=customer)
    mydict = {'userForm': userForm, 'customerForm': customerForm}
    if request.method == 'POST':
        userForm = CFORM.CustomerUserForm(request.POST, instance=user)
        customerForm = CFORM.CustomerForm(request.POST, request.FILES, instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('admin-view-customer')
    return render(request, 'insurance/update_customer.html', context=mydict)

# admin vymazání zákazníka
@login_required(login_url='adminlogin')
def delete_customer_view(request, pk):
    customer = CMODEL.Customer.objects.get(id=pk)
    user = User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return HttpResponseRedirect('/admin-view-customer')


# PŘIDAT CATEGORY CLASS
# přidání kategorie produktů
def admin_add_category_view(request):
    categoryForm = forms.CategoryForm()
    if request.method == 'POST':
        categoryForm = forms.CategoryForm(request.POST)
        if categoryForm.is_valid():
            categoryForm.save()
            return redirect('admin-view-category')
    return render(request, 'insurance/admin_add_category.html', {'categoryForm': categoryForm})

# přehled kategorií
def admin_view_category_view(request):
    categories = models.Category.objects.filter().order_by('category_name')
    return render(request, 'insurance/admin_view_category.html', {'categories': categories})

# vymazání kategorie
def delete_category_view(request, pk):
    category = models.Category.objects.get(id=pk)
    category.delete()
    return redirect('admin-view-category')

# update kategorie
@login_required(login_url='adminlogin')
def update_category_view(request, pk):
    category = models.Category.objects.get(id=pk)
    categoryForm = forms.CategoryForm(instance=category)
    if request.method == 'POST':
        categoryForm = forms.CategoryForm(request.POST, instance=category)
        if categoryForm.is_valid():
            categoryForm.save()
            return redirect('admin-view-category')
    return render(request, 'insurance/update_category.html', {'categoryForm': categoryForm})


# PŘÍDAT PRODUCT CLASS

# detail vytvořeného pojištění
def admin_policy_detail_view(request, pk):
    policy = models.Policy.objects.get(id=pk)
    policyForm = forms.PolicyForm(instance=policy)
    return render(request, 'insurance/admin_view_policy_detail.html', {"policy": policy, 'policyForm': policyForm})

# přidání nového pojištění
def admin_add_policy_view(request):
    policyForm = forms.PolicyForm()

    if request.method == 'POST':
        policyForm = forms.PolicyForm(request.POST)
        if policyForm.is_valid():
            categoryid = request.POST.get('category')
            category = models.Category.objects.get(id=categoryid)

            policy = policyForm.save(commit=False)
            policy.category = category
            policy.save()
            return redirect('admin-view-policy')
    return render(request, 'insurance/admin_add_policy.html', {'policyForm': policyForm})

# celkový přehled pojištění
def admin_view_policy_view(request):
    policies = models.Policy.objects.filter().order_by('category', 'sum_assurance')
    return render(request, 'insurance/admin_view_policy.html', {'policies': policies})


def admin_update_policy_view(request):
    policies = models.Policy.objects.all()
    return render(request, 'insurance/admin_update_policy.html', {'policies': policies})


@login_required(login_url='adminlogin')
def update_policy_view(request, pk):
    policy = models.Policy.objects.get(id=pk)
    policyForm = forms.PolicyForm(instance=policy)

    if request.method == 'POST':
        policyForm = forms.PolicyForm(request.POST, instance=policy)

        if policyForm.is_valid():
            categoryid = request.POST.get('category')
            category = models.Category.objects.get(id=categoryid)

            policy = policyForm.save(commit=False)
            policy.category = category
            policy.save()

            return redirect('admin-view-policy')
    return render(request, 'insurance/update_policy.html', {'policyForm': policyForm})

# update pojištění zákazníka
@login_required(login_url='adminlogin')
def update_policy_customer_view(request, pk):
    policy = models.PolicyRecord.objects.get(id=pk)
    policyForm = forms.CustomerPolicyForm(instance=policy)

    if request.method == 'POST':
        policyForm = forms.CustomerPolicyForm(request.POST, instance=policy)

        if policyForm.is_valid():
            categoryid = request.POST.get('category')
            category = models.Category.objects.get(id=categoryid)

            policy = policyForm.save(commit=False)
            policy.category = category
            policy.save()

            return redirect('admin-view-customer')
    return render(request, 'insurance/admin_update_policy_customer.html', {'policyForm': policyForm})

# vymazání pojištění - obecné
def delete_policy_view(request, pk):
    policy = models.Policy.objects.get(id=pk)
    policy.delete()
    return redirect('admin-view-policy')

# vymazání pojištění - zákazník
def delete_user_policy_view(request, pk):
    policy = models.PolicyRecord.objects.get(id=pk)
    policy.delete()
    return redirect('admin-view-customer')

# výpis pojištění konkrétního zákazníka
def admin_view_policy_holder_view(request):
    policyrecords = models.PolicyRecord.objects.all().filter(status='Pending')
    return render(request, 'insurance/admin_view_policy_holder.html', {'policyrecords': policyrecords})

# schválené produkty
def admin_view_approved_policy_holder_view(request):
    policyrecords = models.PolicyRecord.objects.all().filter(status='Approved')
    return render(request, 'insurance/admin_view_approved_policy_holder.html', {'policyrecords': policyrecords})

# odmítnuté produkty
def admin_view_disapproved_policy_holder_view(request):
    policyrecords = models.PolicyRecord.objects.all().filter(status='Disapproved')
    return render(request, 'insurance/admin_view_disapproved_policy_holder.html', {'policyrecords': policyrecords})

# žádosti o pojištění čekající na schválení
def admin_view_waiting_policy_holder_view(request):
    policyrecords = models.PolicyRecord.objects.all().filter(status='Pending')
    return render(request, 'insurance/admin_view_waiting_policy_holder.html', {'policyrecords': policyrecords})


def approve_request_view(request, pk):
    policyrecords = models.PolicyRecord.objects.get(id=pk)
    policyrecords.status = 'Approved'
    policyrecords.save()
    return redirect('admin-view-policy-holder')


def disapprove_request_view(request, pk):
    policyrecords = models.PolicyRecord.objects.get(id=pk)
    policyrecords.status = 'Disapproved'
    policyrecords.save()
    return redirect('admin-view-policy-holder')

# PŘÍDAT EVENTS CLASS
# přehled pojistných událostí
def admin_events_view(request):
    events = models.InsuranceEventRecord.objects.all().order_by('status')
    return render(request, 'insurance/admin_view_events.html', {'events': events})

# detail konkrétní pojistné události
def admin_event_detail_view(request, pk):
    events = models.InsuranceEventRecord.objects.get(id=pk)
    eventForm = forms.EventAnswerForm(instance=events)

    if request.method == 'POST':
        questionForm = forms.EventAnswerForm(request.POST, instance=events)

        if questionForm.is_valid():
            admin_comment = request.POST.get('admin_comment')

            question = questionForm.save(commit=False)
            question.admin_comment = admin_comment
            question.save()
            return redirect('event-view')
    return render(request, 'insurance/admin_event_detail_view.html', {"events": events, 'eventForm': eventForm})

# potvrzení zpracování PU
def accept_event(request, pk):
    eventrecords = models.InsuranceEventRecord.objects.get(id=pk)
    eventrecords.status = 'Přijato'
    eventrecords.save()
    return redirect('event-view')

# uzavření PU
def close_event(request, pk):
    eventrecords = models.InsuranceEventRecord.objects.get(id=pk)
    eventrecords.status = 'Uzavřeno'
    eventrecords.save()
    return redirect('event-view')


# PŘIDAT QUESTIONS CLASS

# celkový přehled dotazů
def admin_question_view(request):
    questions = models.Question.objects.all().order_by('asked_date')
    return render(request, 'insurance/admin_question.html', {'questions': questions})

# odpověď na dotaz
def update_question_view(request, pk):
    question = models.Question.objects.get(id=pk)
    questionForm = forms.QuestionForm(instance=question)

    if request.method == 'POST':
        questionForm = forms.QuestionForm(request.POST, instance=question)

        if questionForm.is_valid():
            admin_comment = request.POST.get('admin_comment')

            question = questionForm.save(commit=False)
            question.admin_comment = admin_comment
            question.save()

            return redirect('admin-question')
    return render(request, 'insurance/update_question.html', {'questionForm': questionForm})


# PŘIDAT STATISTICS CLASS

# statistika - přehled
def admin_view_stats(request):
    total_user = CMODEL.Customer.objects.all().count()
    total_policy = models.Policy.objects.all().count()
    total_sold_policy = models.PolicyRecord.objects.filter(status='Approved').count()
    total_category = models.Category.objects.all().count()
    total_events = models.InsuranceEventRecord.objects.all().count()
    total_premium = models.PolicyRecord.objects.all().aggregate(sum=Sum('premium'))
    total_premium_number = total_premium['sum']
    average_products_customer = float(total_sold_policy / total_user)
    return render(request, 'insurance/admin_view_stats.html', {'total_premium_number': total_premium_number, 'total_user': total_user,
                                                               'total_policy': total_policy, 'total_sold_policy': total_sold_policy,
                                                               'total_category': total_category, 'average_products_customer': average_products_customer,
                                                               'total_events': total_events})

# generování PDF s kontakty klientů
def admin_generate_clients(request):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    textob.setFont('Vera', 12)
    customersrep = CMODEL.Customer.objects.all()
    lines = []

    for customer in customersrep:
        lines.append(customer.get_name)
        lines.append(customer.address)
        lines.append(customer.mobile)
        lines.append(customer.mail)
        lines.append(" ")

    for line in lines:
        textob.textLine(line)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='report.pdf')

# generování statistik pojišťovny
def admin_generate_stats(request):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    textob.setFont('Vera', 12)

    datas = []
    total_user = CMODEL.Customer.objects.all().count()
    datas.append(str("Počet uživatelů:"))
    datas.append(str(total_user))
    total_policy = models.Policy.objects.all().count()
    datas.append(str("Počet produktů: "))
    datas.append(str(total_policy))
    total_sold_policy = models.PolicyRecord.objects.filter(status='Approved').count()
    datas.append(str("Sjednaných produktů:"))
    datas.append(str(total_sold_policy))
    total_category = models.Category.objects.all().count()
    datas.append(str("Počet kategorií:"))
    datas.append(str(total_category))
    total_premium = models.PolicyRecord.objects.all().aggregate(sum=Sum('premium'))
    total_premium_number = total_premium['sum']
    datas.append(str("Celkové pojistné:"))
    datas.append(str(total_premium_number))
    average_products_customer = float(total_sold_policy / total_user)
    datas.append(str("Pruměr produktů na zákazníka:"))
    datas.append(str(average_products_customer))

    for data in datas:
        textob.textLine(data)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='report.pdf')


