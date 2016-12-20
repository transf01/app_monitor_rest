from django.db import models


class User(models.Model):
    uuid = models.CharField(max_length=256, primary_key=True)
    name = models.CharField(max_length=256)
    cellphone = models.CharField(max_length=15)
    experiment_code = models.IntegerField()
    experiment_start_date = models.DateField()


class History(models.Model):
    uuid = models.ForeignKey(User, on_delete=models.CASCADE)
    app_name = models.CharField(max_length=256)
    package_name = models.CharField(max_length=256)
    start_date = models.DateField()
    start_time = models.TimeField()
    use_time = models.IntegerField()

    class Meta:
        unique_together = ('uuid', 'start_date', 'start_time')


class Goal(models.Model):
    uuid = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_date = models.DateField();
    confidence = models.IntegerField();
    importance = models.IntegerField();
    goal = models.IntegerField();


class ExcludedPackage(models.Model):
    package_name = models.CharField(max_length=256, unique=True)


class ExperimentInfo(models.Model):
    type = models.CharField(max_length=15, primary_key=True)
    period = models.IntegerField()