from django.db import models
from django.core.exceptions import ValidationError


class Building(models.Model):
    """Модель корпуса университета"""
    name = models.CharField(max_length=200, verbose_name="Наименование корпуса")
    address = models.TextField(verbose_name="Адрес корпуса")
    floors_count = models.PositiveIntegerField(verbose_name="Количество этажей")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Корпус"
        verbose_name_plural = "Корпуса"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_total_area(self):
        """Получить общую площадь корпуса"""
        return sum(room.get_area() for room in self.rooms.all())

    def get_total_volume(self):
        """Получить общий объем корпуса"""
        return sum(room.get_volume() for room in self.rooms.all())


class Department(models.Model):
    """Модель подразделения университета (иерархическая структура)"""
    name = models.CharField(max_length=200, verbose_name="Название подразделения")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              verbose_name="Родительское подразделение")
    department_type = models.CharField(
        max_length=50,
        choices=[
            ('university', 'Университет'),
            ('faculty', 'Факультет'),
            ('department', 'Кафедра'),
            ('laboratory', 'Лаборатория'),
            ('center', 'Центр'),
            ('institute', 'Институт'),
        ],
        verbose_name="Тип подразделения"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_full_path(self):
        """Получить полный путь подразделения"""
        path = [self.name]
        current = self.parent
        while current:
            path.insert(0, current.name)
            current = current.parent
        return ' → '.join(path)

    def get_children(self):
        """Получить все дочерние подразделения"""
        return Department.objects.filter(parent=self)

    def get_all_descendants(self):
        """Получить все подчиненные подразделения"""
        descendants = []
        for child in self.get_children():
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants


class Room(models.Model):
    """Модель помещения в корпусе"""
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='rooms',
                                verbose_name="Корпус")
    room_number = models.CharField(max_length=20, verbose_name="Номер комнаты")
    floor = models.PositiveIntegerField(verbose_name="Этаж")
    location_in_building = models.CharField(max_length=200, verbose_name="Расположение в корпусе")
    width = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Ширина (м)")
    length = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Длина (м)")
    ceiling_height = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Высота потолков (м)")
    
    PURPOSE_CHOICES = [
        ('lecture', 'Лекционная аудитория'),
        ('seminar', 'Семинарская аудитория'),
        ('laboratory', 'Лаборатория'),
        ('office', 'Кабинет'),
        ('library', 'Библиотека'),
        ('conference', 'Конференц-зал'),
        ('computer', 'Компьютерный класс'),
        ('storage', 'Складское помещение'),
        ('utility', 'Вспомогательное помещение'),
        ('recreation', 'Комната отдыха'),
    ]
    
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES, verbose_name="Назначение")
    
    ROOM_TYPE_CHOICES = [
        ('auditorium', 'Аудитория'),
        ('office', 'Офис'),
        ('laboratory', 'Лаборатория'),
        ('storage', 'Склад'),
        ('utility', 'Вспомогательное'),
        ('recreation', 'Отдых'),
    ]
    
    room_type = models.CharField(max_length=50, choices=ROOM_TYPE_CHOICES, verbose_name="Вид помещения")
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name="Закрепленное подразделение")
    
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Помещение"
        verbose_name_plural = "Помещения"
        ordering = ['building', 'floor', 'room_number']
        unique_together = ['building', 'room_number']

    def __str__(self):
        return f"{self.building.name}, комната {self.room_number}"

    def clean(self):
        """Валидация данных"""
        if self.width is not None and self.length is not None:
            if self.width <= 0 or self.length <= 0:
                raise ValidationError("Ширина и длина должны быть положительными числами")
        if self.ceiling_height is not None:
            if self.ceiling_height <= 0:
                raise ValidationError("Высота потолков должна быть положительным числом")
        if self.floor is not None:
            if self.floor < 1:
                raise ValidationError("Этаж должен быть положительным числом")

    def get_area(self):
        """Получить площадь помещения в квадратных метрах"""
        return float(self.width * self.length)

    def get_volume(self):
        """Получить объем помещения в кубических метрах"""
        return float(self.width * self.length * self.ceiling_height)

    def get_capacity_estimate(self):
        """Оценочная вместимость помещения (примерно 2 кв.м на человека)"""
        return int(self.get_area() / 2)

    def get_full_name(self):
        """Получить полное название помещения"""
        return f"{self.building.name}, {self.floor} этаж, комната {self.room_number}"


class BuildingFloor(models.Model):
    """Модель для хранения информации о высоте потолков по этажам"""
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors',
                                verbose_name="Корпус")
    floor_number = models.IntegerField(verbose_name="Номер этажа")
    ceiling_height = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Высота потолков (м)")
    description = models.TextField(blank=True, verbose_name="Описание этажа")

    class Meta:
        verbose_name = "Этаж корпуса"
        verbose_name_plural = "Этажи корпусов"
        unique_together = ['building', 'floor_number']
        ordering = ['building', 'floor_number']

    def __str__(self):
        return f"{self.building.name}, {self.floor_number} этаж"