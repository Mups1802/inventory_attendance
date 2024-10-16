from django.urls import path
from . import views

urlpatterns = [
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('attendance-history/', views.attendance_history, name='attendance_history'),
    path('add-update-item/', views.add_update_item, name='add_update_item'),
    path('get-inventory/', views.get_inventory, name='get_inventory'),
    path('get-item/<str:item_id>/', views.get_item, name='get_item'),
    path('delete-item/', views.delete_item, name='delete_item'),
    path('inventory/', views.inventory, name='inventory'),
    path('attendance/', views.attendance, name='attendance'),
    path('get-attendance-history/', views.get_attendance_history, name='get_attendance_history'),
    path('record-attendance/', views.record_attendance, name='record_attendance'),  # Ensure this line is present
]
