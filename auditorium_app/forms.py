from django import forms
from .models import Building, Room


class BuildingForm(forms.ModelForm):
    """Форма для создания и редактирования корпусов"""
    
    class Meta:
        model = Building
        fields = ['name', 'address', 'floors_count', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название корпуса'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите адрес корпуса'
            }),
            'floors_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Описание корпуса (необязательно)'
            }),
        }
        labels = {
            'name': 'Название корпуса',
            'address': 'Адрес',
            'floors_count': 'Количество этажей',
            'description': 'Описание',
        }

    def clean_floors_count(self):
        floors_count = self.cleaned_data.get('floors_count')
        if floors_count <= 0:
            raise forms.ValidationError("Количество этажей должно быть положительным числом")
        if floors_count > 100:
            raise forms.ValidationError("Количество этажей не может превышать 100")
        return floors_count


class RoomForm(forms.ModelForm):
    """Форма для создания и редактирования помещений"""
    
    class Meta:
        model = Room
        fields = [
            'building', 'room_number', 'floor', 'location_in_building',
            'width', 'length', 'ceiling_height', 'purpose', 'room_type',
            'department', 'description'
        ]
        widgets = {
            'building': forms.Select(attrs={'class': 'form-control'}),
            'room_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Л-101, С-205'
            }),
            'floor': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 50
            }),
            'location_in_building': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Крыло А, 2 этаж'
            }),
            'width': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.1',
                'max': '100'
            }),
            'length': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.1',
                'max': '100'
            }),
            'ceiling_height': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '1.0',
                'max': '10'
            }),
            'purpose': forms.Select(attrs={'class': 'form-control'}),
            'room_type': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание помещения (необязательно)'
            }),
        }
        labels = {
            'building': 'Корпус',
            'room_number': 'Номер комнаты',
            'floor': 'Этаж',
            'location_in_building': 'Расположение в корпусе',
            'width': 'Ширина (м)',
            'length': 'Длина (м)',
            'ceiling_height': 'Высота потолков (м)',
            'purpose': 'Назначение',
            'room_type': 'Вид помещения',
            'department': 'Закрепленное подразделение',
            'description': 'Описание',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поле подразделения необязательным
        self.fields['department'].required = False
        self.fields['description'].required = False

    def clean_width(self):
        width = self.cleaned_data.get('width')
        if width <= 0:
            raise forms.ValidationError("Ширина должна быть положительным числом")
        return width

    def clean_length(self):
        length = self.cleaned_data.get('length')
        if length <= 0:
            raise forms.ValidationError("Длина должна быть положительным числом")
        return length

    def clean_ceiling_height(self):
        ceiling_height = self.cleaned_data.get('ceiling_height')
        if ceiling_height <= 0:
            raise forms.ValidationError("Высота потолков должна быть положительным числом")
        return ceiling_height

    def clean_floor(self):
        floor = self.cleaned_data.get('floor')
        building = self.cleaned_data.get('building')
        
        if floor <= 0:
            raise forms.ValidationError("Этаж должен быть положительным числом")
        
        if building and floor > building.floors_count:
            raise forms.ValidationError(
                f"Этаж не может быть больше количества этажей в корпусе ({building.floors_count})"
            )
        
        return floor

    def clean(self):
        cleaned_data = super().clean()
        building = cleaned_data.get('building')
        room_number = cleaned_data.get('room_number')
        
        # Проверка уникальности номера комнаты в корпусе
        if building and room_number:
            existing_room = Room.objects.filter(
                building=building,
                room_number=room_number
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_room.exists():
                raise forms.ValidationError(
                    f"Комната с номером '{room_number}' уже существует в корпусе '{building.name}'"
                )
        
        return cleaned_data
