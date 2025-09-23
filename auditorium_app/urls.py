from django.urls import path
from . import views

app_name = 'auditorium_app'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),
    
    # Корпуса
    path('buildings/', views.buildings_list, name='buildings_list'),
    path('buildings/<int:building_id>/', views.building_detail, name='building_detail'),
    path('buildings/<int:building_id>/faculties/', views.building_faculties, name='building_faculties'),
    path('buildings/create/', views.building_create, name='building_create'),
    path('buildings/<int:building_id>/edit/', views.building_edit, name='building_edit'),
    path('buildings/<int:building_id>/delete/', views.building_delete, name='building_delete'),
    
    # Помещения
    path('rooms/', views.rooms_list, name='rooms_list'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/create/', views.room_create, name='room_create'),
    path('rooms/<int:room_id>/edit/', views.room_edit, name='room_edit'),
    path('rooms/<int:room_id>/delete/', views.room_delete, name='room_delete'),
    
    # Подразделения
    path('departments/', views.departments_list, name='departments_list'),
    path('departments/<int:department_id>/', views.department_detail, name='department_detail'),
    
    # API
    path('api/rooms/<int:room_id>/calculations/', views.api_room_calculations, name='api_room_calculations'),
    path('api/buildings/<int:building_id>/statistics/', views.api_building_statistics, name='api_building_statistics'),
]
