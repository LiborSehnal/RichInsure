from django.contrib import admin
from django.urls import path
from insurance import views
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path, include

urlpatterns = [

    # ADMIN
    path('admin/', admin.site.urls),

    # INDEX a LOGY
    path('customer/', include('customer.urls')),
    path('', views.home_view, name=''),
    path('logout', LogoutView.as_view(template_name='insurance/logout.html'), name='logout'),
    path('afterlogin', views.afterlogin_view, name='afterlogin'),
    path('adminlogin', LoginView.as_view(template_name='insurance/adminlogin.html'), name='adminlogin'),

    # DASH
    path('admin-dashboard', views.admin_dashboard_view, name='admin-dashboard'),

    # ZÁKAZNÍK
    path('admin-view-customer', views.admin_view_customer_view, name='admin-view-customer'),
    path('update-customer/<int:pk>', views.update_customer_view, name='update-customer'),
    path('customer-detail/<int:pk>', views.admin_customer_detail_view, name='customer-detail'),
    path('delete-customer/<int:pk>', views.delete_customer_view, name='delete-customer'),

    # KATEGORIE
    path('admin-view-category', views.admin_view_category_view, name='admin-view-category'),
    path('update-category/<int:pk>', views.update_category_view, name='update-category'),
    path('admin-add-category', views.admin_add_category_view, name='admin-add-category'),
    path('delete-category/<int:pk>', views.delete_category_view, name='delete-category'),

    # PRODUKTY
    path('category-detail/<int:pk>', views.admin_policy_detail_view, name='category-detail'),
    path('admin-add-policy', views.admin_add_policy_view, name='admin-add-policy'),
    path('admin-view-policy', views.admin_view_policy_view, name='admin-view-policy'),
    path('update-policy/<int:pk>', views.update_policy_view, name='update-policy'),
    path('update-customer-policy/<int:pk>', views.update_policy_customer_view, name='update-customer-policy'),
    path('delete-policy/<int:pk>', views.delete_policy_view, name='delete-policy'),
    path('policy-detail/<int:pk>', views.admin_policy_detail_view, name='policy-detail'),
    path('delete-user-policy/<int:pk>', views.delete_user_policy_view, name='delete-user-policy'),

    # POŽADAVKY
    path('admin-view-policy-holder', views.admin_view_policy_holder_view, name='admin-view-policy-holder'),
    path('admin-view-approved-policy-holder', views.admin_view_approved_policy_holder_view,
         name='admin-view-approved-policy-holder'),
    path('admin-view-disapproved-policy-holder', views.admin_view_disapproved_policy_holder_view,
         name='admin-view-disapproved-policy-holder'),
    path('approve-request/<int:pk>', views.approve_request_view, name='approve-request'),
    path('reject-request/<int:pk>', views.disapprove_request_view, name='reject-request'),

    # OTÁZKY
    path('admin-question', views.admin_question_view, name='admin-question'),
    path('update-question/<int:pk>', views.update_question_view, name='update-question'),

    # STATISTIKA
    path('view-stats', views.admin_view_stats, name='view-stats'),
    path('generate-clients', views.admin_generate_clients, name='clients'),
    path('generate-stats', views.admin_generate_stats, name='stats-stats'),
    
    # POJ UDALOSTI
    path('event-view', views.admin_events_view, name='event-view'),
    path('accept-event/<int:pk>', views.accept_event, name='accept-event'),
    path('close-event/<int:pk>', views.close_event, name='close-event'),
    path('event-detail-view/<int:pk>', views.admin_event_detail_view, name='event-detail-view'),


]
