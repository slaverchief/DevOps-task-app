from django.contrib import admin
from .models import Building, Department, Room, BuildingFloor


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'floors_count', 'created_at']
    list_filter = ['floors_count', 'created_at']
    search_fields = ['name', 'address']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'address', 'floors_count')
        }),
        ('Дополнительно', {
            'fields': ('description',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'department_type', 'parent', 'created_at']
    list_filter = ['department_type', 'parent', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'department_type', 'parent')
        }),
        ('Дополнительно', {
            'fields': ('description',)
        }),
        ('Временные метки', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'building', 'floor', 'purpose', 'room_type', 'get_area_display']
    list_filter = ['building', 'floor', 'purpose', 'room_type', 'department']
    search_fields = ['room_number', 'building__name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('building', 'room_number', 'floor', 'location_in_building')
        }),
        ('Размеры', {
            'fields': ('width', 'length', 'ceiling_height')
        }),
        ('Назначение', {
            'fields': ('purpose', 'room_type', 'department')
        }),
        ('Дополнительно', {
            'fields': ('description',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_area_display(self, obj):
        return f"{obj.get_area():.1f} кв.м"
    get_area_display.short_description = 'Площадь'


@admin.register(BuildingFloor)
class BuildingFloorAdmin(admin.ModelAdmin):
    list_display = ['building', 'floor_number', 'ceiling_height']
    list_filter = ['building', 'floor_number']
    search_fields = ['building__name', 'description']


# Настройка админки
admin.site.site_header = "Управление аудиторным фондом МГУ"
admin.site.site_title = "Аудиторный фонд"
admin.site.index_title = "Панель администратора"