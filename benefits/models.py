from django.db import models
from django.core.validators import MinValueValidator
from workers.models import ArchivedWorker

class Benefit(models.Model):
    # Workers.sicil_no (unique) 
    worker = models.ForeignKey(
        'workers.Workers',
        to_field='sicil_no',
        on_delete=models.CASCADE,
        db_column='sicil_no',
        related_name='benefits',
        verbose_name='Sicil No'
    )

    

    period = models.DateField(verbose_name="Benefit Period") 
    aile_yakacak       = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Family")
    erzak              = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Provision")
    altin              = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Gold")
    bayram             = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Holiday")
    dogum_evlenme      = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Birth & Marriage")
    fon                = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Funding")
    harcirah           = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Subsistence")
    yol_parasi         = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Fare")
    prim               = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Premium")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'benefits'
        unique_together = ('worker', 'period')  # Aynı aya tekrar kayıt engeli
        ordering = ['worker', 'period']


    def __str__(self):
        return f"{self.worker.sicil_no} - {self.worker.name_surname}"

    @property
    def name_surname(self):
        return self.worker.name_surname

    @property
    def cost_center_id(self):
        return self.worker.s_no_id  

    @property
    def group_name(self):
        return str(self.worker.group) if self.worker.group else ""


class ArchivedBenefit(models.Model):
    archived_worker = models.ForeignKey(ArchivedWorker, on_delete=models.CASCADE, related_name='archived_benefits')
    sicil_no = models.CharField(max_length=50)
    period = models.DateField()
    aile_yakacak = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    erzak = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    altin = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bayram = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dogum_evlenme = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fon = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    harcirah = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    yol_parasi = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prim = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "archived_benefits"

    def __str__(self):
        return f"{self.sicil_no} - {self.name_surname} ({self.period})"
