from django.test import TestCase, Client, override_settings
from django.urls import reverse

from auditorium_app.models import Building, Department, Room


SQLITE_DB = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INMEM_TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': False,
        'OPTIONS': {
            'loaders': [
                (
                    'django.template.loaders.locmem.Loader',
                    {
                        # Пустые шаблоны для всех используемых во views
                        'auditorium_app/index.html': '',
                        'auditorium_app/buildings_list.html': '',
                        'auditorium_app/building_detail.html': '',
                        'auditorium_app/rooms_list.html': '',
                        'auditorium_app/room_detail.html': '',
                        'auditorium_app/departments_list.html': '',
                        'auditorium_app/department_detail.html': '',
                        'auditorium_app/building_faculties.html': '',
                        'auditorium_app/building_form.html': '',
                        'auditorium_app/room_form.html': '',
                        'auditorium_app/building_confirm_delete.html': '',
                        'auditorium_app/room_confirm_delete.html': '',
                    },
                )
            ]
        },
    }
]


@override_settings(DATABASES=SQLITE_DB, TEMPLATES=INMEM_TEMPLATES)
class EndpointsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Departments
        cls.university = Department.objects.create(name="Университет", department_type="university")
        cls.faculty = Department.objects.create(
            name="Факультет", parent=cls.university, department_type="faculty"
        )
        cls.dept = Department.objects.create(
            name="Кафедра", parent=cls.faculty, department_type="department"
        )

        # Building
        cls.building = Building.objects.create(
            name="Корпус А", address="Москва", floors_count=5, description=""
        )

        # Rooms
        cls.room1 = Room.objects.create(
            building=cls.building,
            room_number="Л-101",
            floor=1,
            location_in_building="Крыло А",
            width=10.0,
            length=8.0,
            ceiling_height=3.0,
            purpose="lecture",
            room_type="auditorium",
            department=cls.dept,
            description="",
        )
        cls.room2 = Room.objects.create(
            building=cls.building,
            room_number="С-202",
            floor=2,
            location_in_building="Крыло Б",
            width=6.0,
            length=5.0,
            ceiling_height=2.8,
            purpose="seminar",
            room_type="auditorium",
            department=None,
            description="",
        )

        cls.client = Client()

    def test_index_page(self):
        resp = self.client.get(reverse('auditorium_app:index'))
        self.assertEqual(resp.status_code, 200)
        # Проверяем, что контекст содержит ключевые метрики
        self.assertIn('total_buildings', resp.context)
        self.assertIn('total_rooms', resp.context)
        self.assertIn('total_departments', resp.context)
        self.assertGreaterEqual(resp.context['total_rooms'], 2)

    def test_buildings_list_page(self):
        resp = self.client.get(reverse('auditorium_app:buildings_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('buildings', resp.context)
        buildings = list(resp.context['buildings'])
        self.assertTrue(any(b.name == "Корпус А" for b in buildings))

    def test_building_detail_page(self):
        url = reverse('auditorium_app:building_detail', args=[self.building.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('floors_stats', resp.context)
        stats = resp.context['floors_stats']
        self.assertIn(1, stats)
        self.assertIn(2, stats)

    def test_rooms_list_filters(self):
        url = reverse('auditorium_app:rooms_list')
        # Без фильтров
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.context['rooms'].paginator.count, 2)

        # С фильтрами
        resp2 = self.client.get(
            url,
            {
                'building': self.building.id,
                'purpose': 'lecture',
                'room_type': 'auditorium',
            },
        )
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.context['rooms'].paginator.count, 1)

    def test_room_detail_page(self):
        url = reverse('auditorium_app:room_detail', args=[self.room1.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['room'].id, self.room1.id)

    def test_departments_list_page(self):
        resp = self.client.get(reverse('auditorium_app:departments_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('departments_tree', resp.context)
        self.assertGreaterEqual(len(resp.context['departments_tree']), 1)

    def test_department_detail_page(self):
        url = reverse('auditorium_app:department_detail', args=[self.dept.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['department'].id, self.dept.id)
        self.assertGreaterEqual(resp.context['total_rooms'], 1)

    def test_building_faculties_page(self):
        url = reverse('auditorium_app:building_faculties', args=[self.building.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('hierarchy', resp.context)
        self.assertEqual(resp.context['building'].id, self.building.id)

    def test_api_room_calculations(self):
        url = reverse('auditorium_app:api_room_calculations', args=[self.room1.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('area', data)
        self.assertIn('volume', data)
        self.assertIn('capacity_estimate', data)
        self.assertGreater(data['area'], 0)

    def test_api_building_statistics(self):
        url = reverse('auditorium_app:api_building_statistics', args=[self.building.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('total_rooms', data)
        self.assertIn('total_area', data)
        self.assertIn('room_types', data)
        self.assertGreaterEqual(data['total_rooms'], 2)


