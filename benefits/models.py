from django.db import models

# Create your models here.

class Benefit(models.Model):
    sicil_no = models.CharField(max_length=50, unique=True, verbose_name="Sicil No")
    name_surname = models.CharField(max_length=100, verbose_name="Adı Soyadı")
    job_start_date = models.DateField(verbose_name="İşe Giriş Tarihi")
    location = models.CharField(max_length=100, verbose_name="Görev Yeri")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cost")
    group = models.CharField(max_length=50, verbose_name="Group")
    department = models.CharField(max_length=100, verbose_name="Department")
    title = models.CharField(max_length=100, verbose_name="Title")
    directorships = models.CharField(max_length=100, verbose_name="Directorships")
    total_work_days = models.IntegerField(verbose_name="Total Work Days")
    kidem_alti = models.CharField(max_length=100, verbose_name="Kıdem Altı")
    kidem_tarihi = models.DateField(verbose_name="Kıdem Tarihi")
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Gross Salary")
    bonus = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Bonus")
    account_date = models.DateField(verbose_name="Account Date")

    def __str__(self):
        return f"{self.sicil_no} - {self.name_surname}"