from django.test import TestCase, override_settings

from auditorium_app.forms import BuildingForm, RoomForm
from auditorium_app.models import Building, Department, Room


SQLITE_DB = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}


@override_settings(DATABASES=SQLITE_DB)
class FormsTests(TestCase):
    def test_building_form_validation(self):
        # floors_count <= 0 -> error
        form = BuildingForm(data={'name': 'A', 'address': 'addr', 'floors_count': 0, 'description': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('floors_count', form.errors)

        # floors_count > 100 -> error
        form2 = BuildingForm(data={'name': 'A', 'address': 'addr', 'floors_count': 101, 'description': ''})
        self.assertFalse(form2.is_valid())
        self.assertIn('floors_count', form2.errors)

        # valid
        form3 = BuildingForm(data={'name': 'A', 'address': 'addr', 'floors_count': 5, 'description': ''})
        self.assertTrue(form3.is_valid())

    def test_room_form_floor_and_uniqueness(self):
        building = Building.objects.create(name='B', address='addr', floors_count=2, description='')
        dept = Department.objects.create(name='Dept', department_type='department')
        Room.objects.create(
            building=building,
            room_number='101',
            floor=1,
            location_in_building='A',
            width=5.0,
            length=4.0,
            ceiling_height=2.5,
            purpose='office',
            room_type='office',
            department=dept,
            description='',
        )

        # floor > building.floors_count -> error
        form = RoomForm(
            data={
                'building': building.id,
                'room_number': '102',
                'floor': 3,
                'location_in_building': 'A',
                'width': 5.0,
                'length': 4.0,
                'ceiling_height': 2.5,
                'purpose': 'office',
                'room_type': 'office',
                'department': dept.id,
                'description': '',
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('floor', form.errors)

        # duplicate room_number in same building -> non-field error
        form2 = RoomForm(
            data={
                'building': building.id,
                'room_number': '101',
                'floor': 1,
                'location_in_building': 'A',
                'width': 5.0,
                'length': 4.0,
                'ceiling_height': 2.5,
                'purpose': 'office',
                'room_type': 'office',
                'department': dept.id,
                'description': '',
            }
        )
        self.assertFalse(form2.is_valid())
        self.assertIn('__all__', form2.errors)

        # valid new room
        form3 = RoomForm(
            data={
                'building': building.id,
                'room_number': '102',
                'floor': 2,
                'location_in_building': 'A',
                'width': 5.0,
                'length': 4.0,
                'ceiling_height': 2.5,
                'purpose': 'office',
                'room_type': 'office',
                'department': dept.id,
                'description': '',
            }
        )
        self.assertTrue(form3.is_valid())


