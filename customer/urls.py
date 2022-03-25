from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    # LOGIN A VŠE KOLEM
    path('customerclick', views.customerclick_view, name='customerclick'),
    path('customersignup', views.customer_signup_view, name='customersignup'),
    path('customer-dashboard', views.customer_dashboard_view, name='customer-dashboard'),
    path('customerlogin', LoginView.as_view(template_name='insurance/adminlogin.html'), name='customerlogin'),

    # PRODUKTY
    path('apply-policy', views.apply_policy_view, name='apply-policy'),
    path('apply/<int:pk>', views.apply_view, name='apply'),
    path('my-products', views.my_products_view, name='my-products'),

    # DOTAZY
    path('ask-question', views.ask_question_view, name='ask-question'),
    path('question-history', views.question_history_view, name='question-history'),

    # POJISTNÉ UDÁLOSTI
    path('customer-event-views', views.customer_event_view, name='customer-event-views'),
    path('customer-event-add', views.customer_event_add, name='customer-event-add')

]