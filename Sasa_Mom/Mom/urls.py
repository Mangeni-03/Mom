from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from . import views
from .views import update_next_visit

urlpatterns = [
    path('', views.landing, name='landing'),
    path('staffLogin/', auth_views.LoginView.as_view(template_name='Mom/staff_login.html'), name='staff_login'),
    path('register/', views.register_mother, name='register'),
    path('mother/<int:pk>/', views.motherPage, name='motherPage'),
    path("staffLogout/", LogoutView.as_view(next_page='staff_login'), name="staff_logout"),
    path('staffDashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('pregnancy/<int:pregnancy_id>/next-visit/', update_next_visit, name='update_next_visit'),
    path('vaccinations/', views.vaccination_list, name='vaccination_list'),
    path('vaccinationsAdd/', views.vaccination_create, name='vaccination_create'),
    path('child/<int:pk>/vaccination/schedule/', views.schedule_child_vaccination, name='schedule_child_vaccination'),
    path('childrenAdd/', views.add_child, name='add_child'),
    path('children/', views.child_list, name='child_list'),
    path('child/<int:pk>/', views.child_detail, name='child_detail'),
    path('mother/<int:mother_id>/child/add/', views.add_child_to_mother, name='add_child_to_mother'),
    path('vaccination/<int:pk>/complete/', views.complete_vaccination, name='complete_vaccination'),
    path('mpesaPayment/', views.mpesaPayment, name='mpesaPayment'),
]
