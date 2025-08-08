from django.db import models
from django.core.validators import MinValueValidator

class Benefit(models.Model):
    # Workers.sicil_no (unique) 
    worker = models.OneToOneField(
        'workers.Workers',
        to_field='sicil_no',
        on_delete=models.CASCADE,
        db_column='sicil_no',
        related_name='benefits',
        verbose_name='Sicil No'
    )

    yurtici_harcirah   = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0, verbose_name="Yurtiçi Harcırah")
    yurtdisi_harcirah  = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0, verbose_name="Yurtdışı Harcırah")
    yol_yardimi        = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0, verbose_name="Yol Yardımı")
    yemek_ticket       = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0, verbose_name="Yemek & Ticket")
    dogum_yardimi      = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0, verbose_name="Doğum Yardımı")
    evlenme_yardimi    = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0, verbose_name="Evlenme Yardımı")

    class Meta:
        db_table = 'benefits'

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
