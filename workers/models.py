# models.py
from django.db import models
from django.contrib.auth.models import User

class BaseWorker(models.Model):
    GROUP_CHOICES = [
        ('', 'Please select a group'),
        ('PTR', 'PTR'),
        ('SNY', 'SNY'),
    ]

    SHORT_CLASS_CHOICES = [
        ('B', 'B'),
        ('W', 'W')
    ]

    DIRECTOR_NAME = [
        ('T', 'T'),
        ('S', 'S'),
        ('F', 'F')
    ]

    CURRENCY_CHOICES = [
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('TRY', 'TRY'),
    ]

    WORK_CLASS_CHOICES = [
        ('Quality', 'Quality'),
        ('Accounting', 'Accounting'),
        ('Admin', 'Admin'),
        ('Bohrwerk', 'Bohrwerk'),
        ('BSA Montage', 'BSA Montage'),
        ('Design', 'Design'),
        ('Electrical M.', 'Electrical M.'),
        ('Export', 'Export'),
        ('Human Resources', 'Human Resources'),
        ('Industrial Pump', 'Industrial Pump'),
        ('IT', 'IT'),
        ('Maintenance', 'Maintenance'),
        ('Management', 'Management'),
        ('Marketing', 'Marketing'),
        ('Material Planning', 'Material Planning'),
        ('Metod', 'Metod'),
        ('Montage', 'Montage'),
        ('Paint Shop', 'Paint Shop'),
        ('PM Sales East', 'PM Sales East'),
        ('PM Sales İzmir', 'PM Sales İzmir'),
        ('PM Sales Support', 'PM Sales Support'),
        ('PM Sales West', 'PM Sales West'),
        ('PM Service Ankara', 'PM Service Ankara'),
        ('PM Service Asia', 'PM Service Asia'),
        ('PM Service Europe', 'PM Service Europe'),
        ('PM Service İzmir', 'PM Service İzmir'),
        ('PM Service Support', 'PM Service Support'),
        ('PM Spare Parts', 'PM Spare Parts'),
        ('Production Planning', 'Production Planning'),
        ('Project', 'Project'),
        ('Purchasing', 'Purchasing'),
        ('SNY Sales Adana', 'SNY Sales Adana'),
        ('SNY Sales East', 'SNY Sales East'),
        ('SNY Sales İzmir', 'SNY Sales İzmir'),
        ('SNY Sales Support', 'SNY Sales Support'),
        ('SNY Sales West', 'SNY Sales West'),
        ('SNY Service Ankara', 'SNY Service Ankara'),
        ('SNY Service Asia', 'SNY Service Asia'),
        ('SNY Service Europe', 'SNY Service Europe'),
        ('SNY Service İzmir', 'SNY Service İzmir'),
        ('SNY Service Support', 'SNY Service Support'),
        ('SNY Spare Parts', 'SNY Spare Parts'),
        ('T.Coordination', 'T.Coordination'),
        ('Test', 'Test'),
        ('Used Machine', 'Used Machine'),
        ('W.Robot', 'W.Robot'),
        ('Warehouse', 'Warehouse'),
        ('Welding', 'Welding'),
    ]

    CLASS_CHOICES = [
        ('Şef', 'Şef'),
        ('Engelli', 'Engelli'),
        ('Müdür', 'Müdür'),
        ('Formen', 'Formen'),
        ('İşçi', 'İşçi'),
        ('T.Lideri', 'T.Lideri'),
        ('Memur', 'Memur'),
    ]

    DEPARTMENT_CLASS = [
        ('Quality', 'Quality'),
        ('Montage', 'Montage'),
        ('Technic Office', 'Technic Office'),
        ('Metod', 'Metod'),
        ('Spare Parts', 'Spare Parts'),
        ('S.Structure', 'S.Structure'),
        ('Production Pln.', 'Production Pln.'),
        ('Warehouse', 'Warehouse'),
        ('Sales East', 'Sales East'),
        ('Sales İzmir', 'Sales İzmir'),
        ('Service', 'Service'),
        ('Acco&Finance', 'Acco&Finance'),
        ('Maintenance', 'Maintenance'),
        ('Project', 'Project'),
        ('Marketing', 'Marketing'),
        ('Sales Support', 'Sales Support'),
        ('Used Machine', 'Used Machine'),
        ('Sales West', 'Sales West'),
        ('Service Support', 'Service Support'),
        ('Material Pln.', 'Material Pln.'),
        ('Purchasing', 'Purchasing'),
        ('HR', 'HR'),
        ('IT', 'IT'),
        ('Technic Mng.', 'Technic Mng.'),
        ('Finance Mng.', 'Finance Mng.'),
        ('Sales Adana', 'Sales Adana')        
    ]

    author = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1)
    group = models.CharField(max_length=50, choices=GROUP_CHOICES, blank=True, null=True)
    sicil_no = models.CharField(max_length=50)
    s_no = models.IntegerField()
    department_short_name = models.CharField(max_length=100, choices=DIRECTOR_NAME, default='T')
    department = models.CharField(max_length=100, choices=DEPARTMENT_CLASS, default='Quality')
    short_class = models.CharField(max_length=50, choices=SHORT_CLASS_CHOICES, default='B')
    name_surname = models.CharField(max_length=100)
    date_of_recruitment = models.DateTimeField()
    work_class = models.CharField(max_length=50, choices=WORK_CLASS_CHOICES, default='Quality')
    class_name = models.CharField(max_length=50, choices=CLASS_CHOICES, default='İşçi')
    gross_payment = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='TRY')
    bonus = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class Workers(BaseWorker):
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "workers"

    def __str__(self):
        return self.name_surname


class ArchivedWorker(BaseWorker):
    original_id = models.IntegerField()
    created_date = models.DateTimeField()
    deleted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "archived_workers"

    def __str__(self):
        return f"Archived - {self.name_surname}"
