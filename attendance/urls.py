# attendance/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # example homepage
    path('add-student/', views.add_student, name='add_student'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('mark-attendance-page/', views.mark_attendance_page, name='mark_attendance_page'),
    # path('attendance-page/', views.attendance_page, name='attendance_page'),
]
