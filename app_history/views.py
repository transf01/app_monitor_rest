from django.db.models import Sum, Count, Avg
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework import serializers, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta

# Create your views here.
from app_history.models import History, User, ExcludedPackage, ExperimentInfo


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


class UserDetailView(GenericAPIView, mixins.RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = ('uuid')

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class HistoryByUserView(GenericAPIView, mixins.ListModelMixin):
    serializer_class = HistorySerializer

    def get_queryset(self):
        return History.objects.filter(**self.kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class LastHistoryView(GenericAPIView, mixins.ListModelMixin):
    serializer_class = HistorySerializer

    def get_queryset(self):
        return History.objects.raw('select * from '+History._meta.db_table+' group by uuid_id order by start_date')

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TotalUseField(serializers.CharField):
    def to_representation(self, value):
        return '%s' %(str(timedelta(seconds=value)))

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


class StatPeriodView(APIView):
    def get(self, request, *args, **kwargs):
        start_date = datetime.strptime(kwargs['start_date'], '%Y-%m-%d')
        end_date = start_date+ timedelta(days=7)
        apps = History.objects.filter(uuid=kwargs['uuid'], start_date__range=(start_date, end_date)).values('app_name').annotate(total_use=Sum('use_time')).order_by('-total_use')[0:5]
        graph_datas = []
        #app별 1주일간
        for app in apps:
            app_data = {"type" :"column"}

            app_data["name"] = app['app_name']
            use_times = []
            for i in range(0,7):
                date = start_date + timedelta(days=i)
                history = History.objects.filter(uuid=kwargs['uuid'], start_date=date, app_name=app['app_name']).values('app_name').annotate(total_use=Sum('use_time'))
                if len(history) > 0:
                    use_times.append(history[0]['total_use'])
                else:
                    use_times.append(0)
            app_data['data'] = use_times
            graph_datas.append(app_data)
        #1주일간 전체 사용자의 시간 평균
        avgs = []
        for i in range(0, 7):
            date = start_date + timedelta(days=i)
            history = History.objects.filter(start_date=date).values('start_date').annotate(average=Avg('use_time'))
            if len(history) > 0:
                avgs.append(history[0]['average'])
            else:
                avgs.append(0)
        avg_data = {"type" : "spline", "name":"Average", "data":avgs}
        graph_datas.append(avg_data)
        return Response({"series":graph_datas})


class ExcludedPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcludedPackage
        exclude = ('id',)

class ExcludedPackageView(GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = ExcludedPackage.objects.all()
    serializer_class = ExcludedPackageSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ExperimentInfoSerializier(serializers.ModelSerializer):
    class Meta:
        model = ExperimentInfo

class ExperimentInfoDetailView(GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = ExperimentInfo.objects.all()
    serializer_class = ExperimentInfoSerializier
    lookup_field = ('type')

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ExperimentInfoView(GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = ExperimentInfo.objects.all()
    serializer_class = ExperimentInfoSerializier

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)



