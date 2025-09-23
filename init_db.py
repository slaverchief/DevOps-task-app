#!/usr/bin/env python
"""
Скрипт инициализации базы данных с тестовыми данными
для приложения учета аудиторного фонда университета
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_auditorium.settings')
django.setup()

from auditorium_app.models import Building, Department, Room, BuildingFloor


def create_departments():
    """Создание подразделений университета"""
    print("Создание подразделений...")
    
    # Университет
    university = Department.objects.create(
        name="Московский государственный университет",
        department_type="university",
        description="Ведущий университет России"
    )
    
    # Факультеты
    faculty_math = Department.objects.create(
        name="Механико-математический факультет",
        parent=university,
        department_type="faculty",
        description="Один из старейших факультетов университета"
    )
    
    faculty_physics = Department.objects.create(
        name="Физический факультет",
        parent=university,
        department_type="faculty",
        description="Факультет физики и астрономии"
    )
    
    faculty_cs = Department.objects.create(
        name="Факультет вычислительной математики и кибернетики",
        parent=university,
        department_type="faculty",
        description="Факультет ВМК"
    )
    
    # Кафедры
    dept_algebra = Department.objects.create(
        name="Кафедра высшей алгебры",
        parent=faculty_math,
        department_type="department",
        description="Кафедра алгебры и теории чисел"
    )
    
    dept_analysis = Department.objects.create(
        name="Кафедра математического анализа",
        parent=faculty_math,
        department_type="department",
        description="Кафедра математического анализа"
    )
    
    dept_quantum = Department.objects.create(
        name="Кафедра квантовой теории",
        parent=faculty_physics,
        department_type="department",
        description="Кафедра квантовой механики"
    )
    
    dept_programming = Department.objects.create(
        name="Кафедра системного программирования",
        parent=faculty_cs,
        department_type="department",
        description="Кафедра программирования"
    )
    
    # Лаборатории
    lab_algebra = Department.objects.create(
        name="Лаборатория алгебраической геометрии",
        parent=dept_algebra,
        department_type="laboratory",
        description="Научно-исследовательская лаборатория"
    )
    
    lab_quantum = Department.objects.create(
        name="Лаборатория квантовых вычислений",
        parent=dept_quantum,
        department_type="laboratory",
        description="Лаборатория квантовых технологий"
    )
    
    return {
        'university': university,
        'faculty_math': faculty_math,
        'faculty_physics': faculty_physics,
        'faculty_cs': faculty_cs,
        'dept_algebra': dept_algebra,
        'dept_analysis': dept_analysis,
        'dept_quantum': dept_quantum,
        'dept_programming': dept_programming,
        'lab_algebra': lab_algebra,
        'lab_quantum': lab_quantum,
    }


def create_buildings():
    """Создание корпусов университета"""
    print("Создание корпусов...")
    
    buildings = []
    
    # Главное здание
    main_building = Building.objects.create(
        name="Главное здание МГУ",
        address="Ленинские горы, д. 1",
        floors_count=36,
        description="Главное здание Московского государственного университета на Воробьёвых горах"
    )
    buildings.append(main_building)
    
    # Корпус физического факультета
    physics_building = Building.objects.create(
        name="Корпус физического факультета",
        address="Ленинские горы, д. 1, стр. 2",
        floors_count=12,
        description="Корпус физического факультета МГУ"
    )
    buildings.append(physics_building)
    
    # Корпус ВМК
    cs_building = Building.objects.create(
        name="Корпус факультета ВМК",
        address="Ленинские горы, д. 1, стр. 52",
        floors_count=8,
        description="Корпус факультета вычислительной математики и кибернетики"
    )
    buildings.append(cs_building)
    
    # Корпус мехмата
    math_building = Building.objects.create(
        name="Корпус механико-математического факультета",
        address="Ленинские горы, д. 1, стр. 1",
        floors_count=10,
        description="Корпус механико-математического факультета"
    )
    buildings.append(math_building)
    
    # Библиотечный корпус
    library_building = Building.objects.create(
        name="Библиотечный корпус",
        address="Ленинские горы, д. 1, стр. 3",
        floors_count=6,
        description="Научная библиотека МГУ"
    )
    buildings.append(library_building)
    
    return buildings


def create_building_floors(buildings):
    """Создание информации о этажах корпусов"""
    print("Создание информации о этажах...")
    
    for building in buildings:
        for floor in range(1, building.floors_count + 1):
            # Высота потолков варьируется в зависимости от этажа
            if floor <= 3:
                height = 3.2  # Первые этажи - выше
            elif floor <= 10:
                height = 2.8  # Средние этажи
            else:
                height = 2.5  # Верхние этажи
            
            BuildingFloor.objects.create(
                building=building,
                floor_number=floor,
                ceiling_height=height,
                description=f"{floor} этаж корпуса {building.name}"
            )


def create_rooms(buildings, departments):
    """Создание помещений в корпусах"""
    print("Создание помещений...")
    
    # Главное здание
    main_building = buildings[0]
    
    # Лекционные аудитории
    for i in range(1, 21):
        Room.objects.create(
            building=main_building,
            room_number=f"Л-{i:02d}",
            floor=(i-1) // 5 + 1,
            location_in_building=f"Крыло А, {((i-1) // 5 + 1)} этаж",
            width=12.0,
            length=8.0,
            ceiling_height=3.2,
            purpose="lecture",
            room_type="auditorium",
            department=departments['faculty_math'] if i % 2 == 0 else departments['faculty_physics'],
            description=f"Лекционная аудитория №{i}"
        )
    
    # Семинарские аудитории
    for i in range(1, 16):
        Room.objects.create(
            building=main_building,
            room_number=f"С-{i:02d}",
            floor=(i-1) // 4 + 2,
            location_in_building=f"Крыло Б, {((i-1) // 4 + 2)} этаж",
            width=8.0,
            length=6.0,
            ceiling_height=2.8,
            purpose="seminar",
            room_type="auditorium",
            department=departments['faculty_cs'],
            description=f"Семинарская аудитория №{i}"
        )
    
    # Корпус физического факультета
    physics_building = buildings[1]
    
    # Лаборатории
    for i in range(1, 11):
        Room.objects.create(
            building=physics_building,
            room_number=f"Лаб-{i:02d}",
            floor=(i-1) // 3 + 1,
            location_in_building=f"Лабораторный корпус, {((i-1) // 3 + 1)} этаж",
            width=10.0,
            length=8.0,
            ceiling_height=3.0,
            purpose="laboratory",
            room_type="laboratory",
            department=departments['lab_quantum'],
            description=f"Лаборатория физики №{i}"
        )
    
    # Корпус ВМК
    cs_building = buildings[2]
    
    # Компьютерные классы
    for i in range(1, 8):
        Room.objects.create(
            building=cs_building,
            room_number=f"КК-{i:02d}",
            floor=(i-1) // 2 + 1,
            location_in_building=f"Компьютерный корпус, {((i-1) // 2 + 1)} этаж",
            width=15.0,
            length=10.0,
            ceiling_height=2.8,
            purpose="computer",
            room_type="auditorium",
            department=departments['dept_programming'],
            description=f"Компьютерный класс №{i}"
        )
    
    # Корпус мехмата
    math_building = buildings[3]
    
    # Кабинеты преподавателей
    for i in range(1, 25):
        Room.objects.create(
            building=math_building,
            room_number=f"К-{i:02d}",
            floor=(i-1) // 5 + 1,
            location_in_building=f"Корпус мехмата, {((i-1) // 5 + 1)} этаж",
            width=4.0,
            length=3.0,
            ceiling_height=2.5,
            purpose="office",
            room_type="office",
            department=departments['dept_algebra'] if i % 2 == 0 else departments['dept_analysis'],
            description=f"Кабинет преподавателя №{i}"
        )
    
    # Библиотечный корпус
    library_building = buildings[4]
    
    # Библиотечные залы
    for i in range(1, 6):
        Room.objects.create(
            building=library_building,
            room_number=f"ЧЗ-{i:02d}",
            floor=i,
            location_in_building=f"Библиотека, {i} этаж",
            width=20.0,
            length=15.0,
            ceiling_height=3.0,
            purpose="library",
            room_type="auditorium",
            department=departments['university'],
            description=f"Читальный зал №{i}"
        )


def main():
    """Основная функция инициализации"""
    print("Начинаем инициализацию базы данных...")
    
    # Очистка существующих данных
    print("Очистка существующих данных...")
    Room.objects.all().delete()
    BuildingFloor.objects.all().delete()
    Building.objects.all().delete()
    Department.objects.all().delete()
    
    # Создание данных
    departments = create_departments()
    buildings = create_buildings()
    create_building_floors(buildings)
    create_rooms(buildings, departments)
    
    print("\n" + "="*50)
    print("Инициализация завершена успешно!")
    print("="*50)
    
    # Статистика
    print(f"Создано подразделений: {Department.objects.count()}")
    print(f"Создано корпусов: {Building.objects.count()}")
    print(f"Создано этажей: {BuildingFloor.objects.count()}")
    print(f"Создано помещений: {Room.objects.count()}")
    
    # Общая статистика по площадям
    total_area = sum(room.get_area() for room in Room.objects.all())
    total_volume = sum(room.get_volume() for room in Room.objects.all())
    
    print(f"\nОбщая площадь всех помещений: {total_area:.2f} кв.м")
    print(f"Общий объем всех помещений: {total_volume:.2f} куб.м")
    
    print("\nДля запуска приложения выполните:")
    print("python manage.py runserver")


if __name__ == "__main__":
    main()
