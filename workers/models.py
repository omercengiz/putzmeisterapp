# models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import datetime
import calendar
from .lookups import (
    Group, ShortClass, DirectorName, Currency,
    WorkClass, ClassName, Department, CostCenter, ExitReason
)



class BaseWorker(models.Model):

    """
    These are templates that will be inherited by Workers and ArchivedWorkers,
    List has been updated as a lookup tables on db
    They will be deleted at the end of the development phase issue -> Drop list(inner tuples) all #8
    """
    GROUP_CHOICES = [
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

    COST_CENTER_CHOICES = [
        ("30000", "GENEL MÜDÜRLÜK"),
        ("30001", "GENEL MÜDÜRLÜK / SATIŞ EXC."),
        ("30100", "FİNANS DİREKTÖRLÜĞÜ"),
        ("30120", "FİNANS / MUHASEBE"),
        ("30140", "BÜTÇE PLANLAMA VE KONTROL"),
        ("30200", "BİLGİ İŞLEM"),
        ("30420", "BİNA İNŞAAT"),
        ("30490", "BAKIM"),
        ("30500", "SATINALMA"),
        ("30510", "LOJİSTİK"),
        ("30520", "DEPO"),
        ("30550", "MALZEME PLANLAMA"),
        ("30560", "KALİTE YÖNETİMİ"),
        ("30600", "KAYNAK OKULU"),
        ("30700", "İNSAN KAYNAKLARI VE İDARİ İŞLER"),
        ("30830", "ÇIRAK / STAJYER"),
        ("31000", "PAZARLAMA"),
        ("31020", "PAZARLAMA BP"),
        ("31030", "PAZARLAMA EKS"),
        ("31100", "YEDEK PARÇA"),
        ("31250", "SANY YEDEK PARÇA"),
        ("31300", "SATIŞ DESTEK"),
        ("31320", "İSTANBUL SATIŞ BP"),
        ("31450", "SATIŞ - İHRACAT"),
        ("35000", "TEKNİK DİREKTÖRLÜK"),
        ("35040", "TEKNİK KOORDİNASYON"),
        ("35200", "MÜHENDİSLİK"),
        ("35300", "METOD ŞEFLİĞİ"),
        ("36010", "ÜRETİM PLANLAMA VE KONTROL"),
        ("36020", "MEKANİK ATÖLYE"),
        ("36030", "KAYNAK MONTAJI"),
        ("36040", "KAYNAK"),
        ("36041", "KAYNAK ROBOTU 1 (REIS-1)"),
        ("36042", "KAYNAK ROBOTU 2 (IGM)"),
        ("36043", "KAYNAK ROBOTU 3 (REIS-2)"),
        ("36044", "KAYNAK ROBOTU 4 (REIS-4)"),
        ("36045", "KAYNAK ROBOTU 5"),
        ("36046", "KAYNAK ROBOTU 6"),
        ("36047", "KAYNAK ROBOTU 7"),
        ("36048", "KAYNAK ROBOTU 8"),
        ("36050", "İŞLEME MERKEZİ 1"),
        ("36051", "İŞLEME MERKEZİ 2"),
        ("36052", "İŞLEME MERKEZİ 3"),
        ("36053", "İŞLEME MERKEZİ 4"),
        ("36054", "İŞLEME MERKEZİ 5"),
        ("36060", "BOYA HAZIRLIK"),
        ("36061", "BOYAMA – ASTARLAMA"),
        ("36080", "TEST BÖLÜMÜ"),
        ("36090", "KAZAN HİDROLİK MONTAJ"),
        ("36091", "ÖN MONTAJ"),
        ("36092", "KOL MONTAJI"),
        ("36093", "ANA MONTAJ"),
        ("36094", "SON MONTAJ"),
        ("36095", "BSA MONTAJ"),
        ("36096", "BORU BÜKME"),
        ("36097", "DOCH ve PUMİ MONTAJ"),
        ("36098", "ELEKTRİK – MONTAJ"),
        ("36099", "OPTİMİZASYON"),
        ("36120", "BETON BORU KAYNAĞI"),
        ("38110", "SERVİS HADIMKÖY"),
        ("38112", "SANY SERVİS HADIMKÖY"),
        ("38120", "SERVİS İZMİR"),
        ("38121", "SANY SERVİS İZMİR"),
        ("38122", "SANY SERVİS ANKARA"),
        ("38130", "SERVİS ANKARA"),
        ("38132", "SANY SERVİS ANKARA"),
        ("38140", "SERVİS ESKİŞEHİR"),
        ("38142", "SANY SERVİS ESKİŞEHİR"),
        ("38150", "TEKNİK DESTEK PM"),
        ("38151", "TEKNİK DESTEK SANY"),
        ("38200", "İZMİR SATIŞ BP"),
        ("38520", "EXCAVATOR SATIŞ-Hadımköy"),
        ("38521", "EXCAVATOR SATIŞ-Ataşehir"),
        ("38522", "EXCAVATOR SATIŞ-İzmir"),
        ("38523", "EXCAVATOR SATIŞ-Ankara"),
        ("38540", "EXCAVATOR SATIŞ-Adana"),
        ("39000", "ANKARA SATIŞ BP"),
        ("39001", "PMA WORKER"),
        ("39002", "PCP WORKER"),
        ("39003", "PMH WORKER"),
        ("39004", "PEG WORKER"),
        ("39005", "SANY YENİLENEBİLİR ENERJİ"),
        ("39010", "PLANNING PCP"),
        ("39011", "QUALITY PCP"),
        ("39012", "SALES DISTRIBUTION"),
        ("39013", "CONTROLLING PCP"),
        ("39014", "ENGINEERING PCP"),
        ("39015", "PRE SALES EXCELLENCE SAB"),
        ("39020", "PURCHASING PMH"),
        ("39021", "AUDITING PMH"),
        ("39022", "QUALITY PMH"),
        ("39023", "ENGINEERING PMH"),
        ("39024", "SERVICE OPERATION PMH"),
        ("39030", "ENGINEERING PMA")
    ]


    author = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, verbose_name="Group")
    sicil_no = models.CharField(max_length=50, verbose_name="Sicil No", unique=True)
    short_class = models.ForeignKey(ShortClass, on_delete=models.SET_NULL, null=True, verbose_name="Status")
    department_short_name = models.ForeignKey(DirectorName, on_delete=models.SET_NULL, null=True, verbose_name="Directorships")
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    work_class = models.ForeignKey(WorkClass, on_delete=models.SET_NULL, null=True)
    class_name = models.ForeignKey(ClassName, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, verbose_name="Department")
    s_no = models.ForeignKey(CostCenter, on_delete=models.SET_NULL, null=True, verbose_name="CostCenter")
    name_surname = models.CharField(max_length=100)
    date_of_recruitment = models.DateTimeField()
    gross_payment_hourly = models.DecimalField(max_digits=15, decimal_places=2)
    total_work_hours = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True, default=225, verbose_name="Total Work Hours")
    update_date_user = models.DateField(null=True, blank=True)
    gross_payment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    
    bonus = models.IntegerField(validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])

    class Meta:
        abstract = True


class Workers(BaseWorker):
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "workers"

    def __str__(self):
        return self.name_surname

    def save(self, *args, **kwargs):
        from decimal import Decimal

        is_update = self.pk is not None

        # total_work_hours boşsa default 225
        if not self.total_work_hours:
            self.total_work_hours = Decimal("225")

        # 🟢 Maaşı total_work_hours'a böl → saatlik maaş
        if self.gross_payment and self.total_work_hours:
            total_hours = (
                self.total_work_hours
                if isinstance(self.total_work_hours, Decimal)
                else Decimal(str(self.total_work_hours))
            )

            self.gross_payment_hourly = (
                Decimal(str(self.gross_payment)) / total_hours
            ).quantize(Decimal("0.01"))

        super().save(*args, **kwargs)

        # update_date_user yoksa veya yeni kayıtsa monthly oluşturma
        if not is_update or not self.update_date_user:
            return

        update_year = self.update_date_user.year
        start_month = self.update_date_user.month

        # 🟢 Seçilen aydan yıl sonuna kadar WorkerGrossMonthly senkronu
        for month in range(start_month, 13):
            salary_obj, created = WorkerGrossMonthly.objects.get_or_create(
                worker=self,
                year=update_year,
                month=month,
                defaults={
                    "gross_salary_hourly": self.gross_payment_hourly,
                    "currency": self.currency,
                    "sicil_no": self.sicil_no,
                }
            )

            salary_obj.gross_salary_hourly = self.gross_payment_hourly
            salary_obj.currency = self.currency
            salary_obj.sicil_no = self.sicil_no
            salary_obj.save()  # burada 7,5 × gün sayısı ile gross_payment hesaplanıyor



class ArchivedWorker(BaseWorker):
    original_id = models.IntegerField()
    created_date = models.DateTimeField()
    deleted_at = models.DateTimeField(auto_now_add=True)
    exit_date = models.DateField(null=True, blank=True) # İşçinin çıkış tarihi olacak
    exit_reason = models.ForeignKey(ExitReason, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "archived_workers"

    def __str__(self):
        return f"Archived - {self.name_surname}"
    

class WorkerGrossMonthly(models.Model):
    worker = models.ForeignKey(
        Workers,
        on_delete=models.CASCADE,
        related_name="monthly_gross_salaries"
    )

    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )

    gross_salary_hourly = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.ForeignKey("Currency", null=True, blank=True, on_delete=models.SET_NULL)  # 🔑 burası eklendi
    sicil_no = models.CharField(max_length=50, null=True, blank=True)
    gross_payment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Varsayılan günlük çalışma saati 7.5 bunu bütçe işleri için kullanıyoruz.
    DAILY_WORK_HOURS = Decimal("7.5") 

    class Meta:
        db_table = "worker_gross_monthly"
        unique_together = ("worker", "year", "month")

    def __str__(self):
        return f"{self.worker.name_surname} ({self.worker.sicil_no}) - {self.month}/{self.year}: {self.gross_salary_hourly}"

    @property
    def worker_sicil_no(self):
        return self.worker.sicil_no

    @property
    def worker_name_surname(self):
        return self.worker.name_surname
    
    @property
    def month_name(self):
        return calendar.month_name[self.month]
    
    def save(self, *args, **kwargs):
        if self.worker and not self.sicil_no:
            self.sicil_no = self.worker.sicil_no

        days = calendar.monthrange(self.year, self.month)[1]

        # Saatlik ücret → günlük 7.5 saat * gün sayısı
        if self.gross_salary_hourly:
            self.gross_payment = (
                Decimal(str(self.gross_salary_hourly)) * Decimal("7.5") * days
            ).quantize(Decimal("0.01"))

        super().save(*args, **kwargs)



class ArchivedWorkerGrossMonthly(models.Model):
    archived_worker = models.ForeignKey(
        ArchivedWorker,
        on_delete=models.CASCADE,
        related_name="archived_monthly_salaries"
    )

    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    gross_salary_hourly = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.ForeignKey("Currency", null=True, blank=True, on_delete=models.SET_NULL)
    sicil_no = models.CharField(max_length=50, null=True, blank=True)
    gross_payment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "archived_worker_gross_monthly"

    def __str__(self):
        return f"Archived Salary: {self.sicil_no} - {self.month}/{self.year}"
