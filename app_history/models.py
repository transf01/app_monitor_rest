from django.db import models

# Create your models here.
class User(models.Model):
    uuid = models.CharField(max_length=256, primary_key=True)
    name = models.CharField(max_length=256)
    cellphone = models.CharField(max_length=15)
    experiment_code = models.IntegerField()


class History(models.Model):
    uuid = models.ForeignKey(User, on_delete=models.CASCADE)
    app_name = models.CharField(max_length=256)
    package_name = models.CharField(max_length=256)
    start_date = models.DateField()
    start_time = models.TimeField()
    use_time = models.IntegerField()

    class Meta:
        unique_together = ('uuid', 'start_date', 'start_time')


class ExcludedPackage(models.Model):
    package_name = models.CharField(max_length=256)