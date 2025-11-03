from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Building, Department, Room
from .forms import BuildingForm, RoomForm
import django.db.backends

def index(request):
    """Главная страница с общей статистикой"""
    # Общая статистика
    total_buildings = Building.objects.count()
    total_rooms = Room.objects.count()
    total_departments = Department.objects.count()
    
    # Расчет общих площадей и объемов
    rooms = Room.objects.all()
    total_area = sum(room.get_area() for room in rooms)
    total_volume = sum(room.get_volume() for room in rooms)
    
    # Статистика по корпусам
    buildings_stats = []
    for building in Building.objects.all():
        building_rooms = building.rooms.all()
        building_area = sum(room.get_area() for room in building_rooms)
        building_volume = sum(room.get_volume() for room in building_rooms)
        buildings_stats.append({
            'building': building,
            'rooms_count': building_rooms.count(),
            'area': building_area,
            'volume': building_volume
        })
    
    # Статистика по типам помещений
    room_types_stats = {}
    for room in rooms:
        room_type = room.get_room_type_display()
        if room_type not in room_types_stats:
            room_types_stats[room_type] = {'count': 0, 'area': 0}
        room_types_stats[room_type]['count'] += 1
        room_types_stats[room_type]['area'] += room.get_area()
    
    # Расчет оценочной вместимости
    estimated_capacity = int(total_area / 2)
    
    context = {
        'total_buildings': total_buildings,
        'total_rooms': total_rooms,
        'total_departments': total_departments,
        'total_area': total_area,
        'total_volume': total_volume,
        'estimated_capacity': estimated_capacity,
        'buildings_stats': buildings_stats,
        'room_types_stats': room_types_stats,
    }
    return render(request, 'auditorium_app/index.html', context)


def buildings_list(request):
    """Список всех корпусов"""
    buildings = Building.objects.all().order_by('name')
    
    # Добавляем статистику для каждого корпуса
    total_rooms_count = 0
    total_area_sum = 0
    total_volume_sum = 0
    
    for building in buildings:
        building.rooms_count = building.rooms.count()
        building.total_area = sum(room.get_area() for room in building.rooms.all())
        building.total_volume = sum(room.get_volume() for room in building.rooms.all())
        
        total_rooms_count += building.rooms_count
        total_area_sum += building.total_area
        total_volume_sum += building.total_volume
    
    context = {
        'buildings': buildings,
        'total_rooms_count': total_rooms_count,
        'total_area_sum': total_area_sum,
        'total_volume_sum': total_volume_sum,
    }
    return render(request, 'auditorium_app/buildings_list.html', context)


def building_detail(request, building_id):
    """Детальная информация о корпусе"""
    building = get_object_or_404(Building, id=building_id)
    
    # Получаем все помещения корпуса
    rooms = building.rooms.all().order_by('floor', 'room_number')
    
    # Статистика по этажам
    floors_stats = {}
    for room in rooms:
        floor = room.floor
        if floor not in floors_stats:
            floors_stats[floor] = {'rooms': 0, 'area': 0, 'volume': 0}
        floors_stats[floor]['rooms'] += 1
        floors_stats[floor]['area'] += room.get_area()
        floors_stats[floor]['volume'] += room.get_volume()
    
    # Получаем структуру подразделений в корпусе
    departments_in_building = Department.objects.filter(
        room__building=building
    ).distinct().order_by('name')
    
    # Статистика по подразделениям
    departments_stats = []
    for dept in departments_in_building:
        dept_rooms = rooms.filter(department=dept)
        dept_area = sum(room.get_area() for room in dept_rooms)
        dept_volume = sum(room.get_volume() for room in dept_rooms)
        departments_stats.append({
            'department': dept,
            'rooms_count': dept_rooms.count(),
            'area': dept_area,
            'volume': dept_volume
        })
    
    # Пагинация для помещений
    paginator = Paginator(rooms, 20)
    page_number = request.GET.get('page')
    rooms_page = paginator.get_page(page_number)
    
    context = {
        'building': building,
        'rooms': rooms_page,
        'floors_stats': floors_stats,
        'departments_stats': departments_stats,
        'total_rooms': rooms.count(),
        'total_area': sum(room.get_area() for room in rooms),
        'total_volume': sum(room.get_volume() for room in rooms),
    }
    return render(request, 'auditorium_app/building_detail.html', context)


def rooms_list(request):
    """Список всех помещений"""
    rooms = Room.objects.select_related('building', 'department').all().order_by('building', 'floor', 'room_number')
    
    # Фильтрация
    building_filter = request.GET.get('building')
    purpose_filter = request.GET.get('purpose')
    room_type_filter = request.GET.get('room_type')
    
    if building_filter:
        rooms = rooms.filter(building_id=building_filter)
    if purpose_filter:
        rooms = rooms.filter(purpose=purpose_filter)
    if room_type_filter:
        rooms = rooms.filter(room_type=room_type_filter)
    
    # Пагинация
    paginator = Paginator(rooms, 25)
    page_number = request.GET.get('page')
    rooms_page = paginator.get_page(page_number)
    
    # Данные для фильтров
    buildings = Building.objects.all().order_by('name')
    
    context = {
        'rooms': rooms_page,
        'buildings': buildings,
        'building_filter': building_filter,
        'purpose_filter': purpose_filter,
        'room_type_filter': room_type_filter,
        'purpose_choices': Room.PURPOSE_CHOICES,
        'room_type_choices': Room.ROOM_TYPE_CHOICES,
    }
    return render(request, 'auditorium_app/rooms_list.html', context)


def room_detail(request, room_id):
    """Детальная информация о помещении"""
    room = get_object_or_404(Room, id=room_id)
    
    # Похожие помещения в том же корпусе
    similar_rooms = Room.objects.filter(
        building=room.building,
        purpose=room.purpose
    ).exclude(id=room_id)[:5]
    
    context = {
        'room': room,
        'similar_rooms': similar_rooms,
    }
    return render(request, 'auditorium_app/room_detail.html', context)


def departments_list(request):
    """Список подразделений с иерархией"""
    # Получаем корневые подразделения (без родителя)
    root_departments = Department.objects.filter(parent=None).order_by('name')
    
    def get_department_tree(dept, level=0):
        """Рекурсивно строим дерево подразделений"""
        children = Department.objects.filter(parent=dept).order_by('name')
        result = {
            'department': dept,
            'level': level,
            'children': []
        }
        
        for child in children:
            result['children'].append(get_department_tree(child, level + 1))
        
        return result
    
    departments_tree = []
    for root_dept in root_departments:
        departments_tree.append(get_department_tree(root_dept))
    
    context = {
        'departments_tree': departments_tree,
    }
    return render(request, 'auditorium_app/departments_list.html', context)


def department_detail(request, department_id):
    """Детальная информация о подразделении"""
    department = get_object_or_404(Department, id=department_id)
    
    # Помещения подразделения
    rooms = Room.objects.filter(department=department).order_by('building', 'floor', 'room_number')
    
    # Дочерние подразделения
    children = Department.objects.filter(parent=department).order_by('name')
    
    # Статистика
    total_area = sum(room.get_area() for room in rooms)
    total_volume = sum(room.get_volume() for room in rooms)
    
    context = {
        'department': department,
        'rooms': rooms,
        'children': children,
        'total_rooms': rooms.count(),
        'total_area': total_area,
        'total_volume': total_volume,
    }
    return render(request, 'auditorium_app/department_detail.html', context)


def building_faculties(request, building_id):
    """Получить структуру факультетов в корпусе"""
    building = get_object_or_404(Building, id=building_id)
    
    # Получаем все подразделения, которые имеют помещения в этом корпусе
    departments_in_building = Department.objects.filter(
        room__building=building
    ).distinct()
    
    # Строим иерархию
    def build_hierarchy(departments):
        hierarchy = {}
        for dept in departments:
            if dept.parent is None:
                # Корневое подразделение
                if dept.id not in hierarchy:
                    hierarchy[dept.id] = {
                        'department': dept,
                        'children': []
                    }
            else:
                # Находим родителя в иерархии
                parent_id = dept.parent.id
                if parent_id not in hierarchy:
                    hierarchy[parent_id] = {
                        'department': dept.parent,
                        'children': []
                    }
                hierarchy[parent_id]['children'].append({
                    'department': dept,
                    'children': []
                })
        return hierarchy
    
    hierarchy = build_hierarchy(departments_in_building)
    
    context = {
        'building': building,
        'hierarchy': hierarchy,
    }
    return render(request, 'auditorium_app/building_faculties.html', context)


# CRUD операции для корпусов
def building_create(request):
    """Создание нового корпуса"""
    if request.method == 'POST':
        form = BuildingForm(request.POST)
        if form.is_valid():
            building = form.save()
            messages.success(request, f'Корпус "{building.name}" успешно создан!')
            return redirect('auditorium_app:building_detail', building_id=building.id)
    else:
        form = BuildingForm()
    
    context = {
        'form': form,
        'title': 'Создание нового корпуса',
    }
    return render(request, 'auditorium_app/building_form.html', context)


def building_edit(request, building_id):
    """Редактирование корпуса"""
    building = get_object_or_404(Building, id=building_id)
    
    if request.method == 'POST':
        form = BuildingForm(request.POST, instance=building)
        if form.is_valid():
            building = form.save()
            messages.success(request, f'Корпус "{building.name}" успешно обновлен!')
            return redirect('auditorium_app:building_detail', building_id=building.id)
    else:
        form = BuildingForm(instance=building)
    
    context = {
        'form': form,
        'building': building,
        'title': f'Редактирование корпуса "{building.name}"',
    }
    return render(request, 'auditorium_app/building_form.html', context)


def building_delete(request, building_id):
    """Удаление корпуса"""
    building = get_object_or_404(Building, id=building_id)
    
    if request.method == 'POST':
        building_name = building.name
        building.delete()
        messages.success(request, f'Корпус "{building_name}" успешно удален!')
        return redirect('auditorium_app:buildings_list')
    
    context = {
        'building': building,
    }
    return render(request, 'auditorium_app/building_confirm_delete.html', context)


# CRUD операции для помещений
def room_create(request):
    """Создание нового помещения"""
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Помещение "{room.room_number}" в корпусе "{room.building.name}" успешно создано!')
            return redirect('auditorium_app:room_detail', room_id=room.id)
    else:
        form = RoomForm()
    
    context = {
        'form': form,
        'title': 'Создание нового помещения',
    }
    return render(request, 'auditorium_app/room_form.html', context)


def room_edit(request, room_id):
    """Редактирование помещения"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Помещение "{room.room_number}" успешно обновлено!')
            return redirect('auditorium_app:room_detail', room_id=room.id)
    else:
        form = RoomForm(instance=room)
    
    context = {
        'form': form,
        'room': room,
        'title': f'Редактирование помещения "{room.room_number}"',
    }
    return render(request, 'auditorium_app/room_form.html', context)


def room_delete(request, room_id):
    """Удаление помещения"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        room_info = f"{room.room_number} в корпусе {room.building.name}"
        room.delete()
        messages.success(request, f'Помещение "{room_info}" успешно удалено!')
        return redirect('auditorium_app:rooms_list')
    
    context = {
        'room': room,
    }
    return render(request, 'auditorium_app/room_confirm_delete.html', context)


# API для AJAX запросов
def api_room_calculations(request, room_id):
    """API для получения расчетов помещения"""
    room = get_object_or_404(Room, id=room_id)
    
    data = {
        'area': room.get_area(),
        'volume': room.get_volume(),
        'capacity_estimate': room.get_capacity_estimate(),
    }
    
    return JsonResponse(data)


def api_building_statistics(request, building_id):
    """API для получения статистики корпуса"""
    building = get_object_or_404(Building, id=building_id)
    
    rooms = building.rooms.all()
    total_area = sum(room.get_area() for room in rooms)
    total_volume = sum(room.get_volume() for room in rooms)
    
    # Статистика по типам помещений
    room_types = {}
    for room in rooms:
        room_type = room.get_room_type_display()
        if room_type not in room_types:
            room_types[room_type] = {'count': 0, 'area': 0}
        room_types[room_type]['count'] += 1
        room_types[room_type]['area'] += room.get_area()
    
    data = {
        'total_rooms': rooms.count(),
        'total_area': total_area,
        'total_volume': total_volume,
        'room_types': room_types,
    }
    
    return JsonResponse(data)