import unittest
from django.core.exceptions import ValidationError

from auditorium_app.models import Building, Department, Room, BuildingFloor


class BusinessLogicUnitTests(unittest.TestCase):
    """
    Юнит-тесты бизнес-логики без доступа к БД (unittest).
    Создаем несохраненные инстансы моделей и проверяем чистые методы.
    """

    def test_room_area_volume_capacity_and_full_name(self):
        building = Building(name="Корпус А", address="Адрес", floors_count=5, description="")
        room = Room(
            building=building,
            room_number="Л-101",
            floor=1,
            location_in_building="Крыло А",
            width=12.0,
            length=8.0,
            ceiling_height=3.2,
            purpose="lecture",
            room_type="auditorium",
            description="",
        )

        self.assertAlmostEqual(room.get_area(), 96.0)
        self.assertAlmostEqual(room.get_volume(), 307.2)
        self.assertEqual(room.get_capacity_estimate(), int(96.0 / 2))
        self.assertEqual(room.get_full_name(), "Корпус А, 1 этаж, комната Л-101")

    def test_room_clean_validation(self):
        building = Building(name="Корпус Б", address="Адрес", floors_count=3, description="")
        # width <= 0
        bad_room = Room(
            building=building,
            room_number="S-1",
            floor=1,
            location_in_building="Крыло B",
            width=0,
            length=5.0,
            ceiling_height=2.5,
            purpose="office",
            room_type="office",
            description="",
        )
        with self.assertRaises(ValidationError):
            bad_room.clean()

        # height <= 0
        bad_room2 = Room(
            building=building,
            room_number="S-2",
            floor=0,  # invalid
            location_in_building="Крыло B",
            width=5.0,
            length=5.0,
            ceiling_height=0,
            purpose="office",
            room_type="office",
            description="",
        )
        with self.assertRaises(ValidationError):
            bad_room2.clean()

    def test_department_full_path(self):
        university = Department(name="Университет", department_type="university")
        faculty = Department(name="Факультет", parent=university, department_type="faculty")
        department = Department(name="Кафедра", parent=faculty, department_type="department")

        self.assertEqual(university.get_full_path(), "Университет")
        self.assertEqual(faculty.get_full_path(), "Университет → Факультет")
        self.assertEqual(department.get_full_path(), "Университет → Факультет → Кафедра")

    def test_buildingfloor_str(self):
        building = Building(name="Корпус В", address="Адрес", floors_count=2, description="")
        floor = BuildingFloor(building=building, floor_number=2, ceiling_height=2.7, description="")
        self.assertEqual(str(floor), "Корпус В, 2 этаж")


