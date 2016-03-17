import datetime
from django.db.models import Sum, Count
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework import serializers, mixins

# Create your views here.
from app_history.models import History, User


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

class HistoryView(GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin,):
    queryset = History.objects.all()
    serializer_class = HistorySerializer

    def get_serializer(self, *args, **kwargs):
        if "data" in kwargs:
            if isinstance( kwargs["data"], list):
                kwargs["many"] = True
        return super(HistoryView, self).get_serializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class UserView(GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class HistoryByUserView(GenericAPIView, mixins.ListModelMixin):
    serializer_class = HistorySerializer

    def get_queryset(self):
        return History.objects.filter(**self.kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class TotalUseField(serializers.CharField):
    def to_representation(self, value):
        return '%s' %(str(datetime.timedelta(seconds=value)))

class StatSerializer(serializers.Serializer):
    uuid = serializers.CharField(max_length=256)
    start_date = serializers.DateField()
    app_name = serializers.CharField(max_length=256)
    total_use = TotalUseField()
    count = serializers.IntegerField()


class StatView(GenericAPIView, mixins.ListModelMixin):
    serializer_class = StatSerializer

    def get_queryset(self):
        return History.objects.filter(**self.kwargs).values('uuid', 'start_date', 'app_name').annotate(total_use=Sum('use_time'), count=Count('use_time'))

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)