from django.db import models

# Create your models here.
class History(models.Model):
    uuid = models.CharField(max_length=256)
    app_name = models.CharField(max_length=256)
    package_name = models.CharField(max_length=256)
    start_date = models.DateField()
    start_time = models.TimeField()
    use_time = models.IntegerField()

    class Meta:
        unique_together = ('uuid', 'start_date', 'start_time')


class User(models.Model):
    uuid = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    cellphone = models.CharField(max_length=15)