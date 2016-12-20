from django.db.models import Sum, Count
from django.http import HttpResponse
from rest_framework.generics import GenericAPIView
from rest_framework import serializers, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta
from app_history.models import History, User, ExcludedPackage, ExperimentInfo, Goal


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal


class GoalView(GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


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
            all_user_history = History.objects.filter(start_date=date).values('start_date').annotate(all_user_use=Sum('use_time'))
            users = History.objects.raw('select * from '+History._meta.db_table+' where start_date=\''+ date.date().__str__() +'\' group by start_date, uuid_id')

            if len(all_user_history) > 0:
                avgs.append(all_user_history[0]['all_user_use']/len(list(users)))
            else:
                avgs.append(0)
        avg_data = {"type" : "spline", "name":"전체 사용자 평균", "data":avgs}
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


class InterventionListView(APIView):
    def get(self, request, *args, **kwargs):
        uuids = [
            '00000000-0305-eeb5-1835-82de565968b4',
            '00000000-0306-3060-f2f4-7a2955ebae4c',
            '00000000-02a4-bb8b-744d-530755c49a10',
            '00000000-029e-bd0d-476f-d5b256176612',
            '00000000-02da-3838-70e1-b8c955dd6ff6',
            '00000000-02ed-d18c-f1f7-cda9560d391e',
            '00000000-02d9-0073-ef21-0e0655a1c207',
            '00000000-02d9-78e4-4ea3-d8b555ef3d84',
            '00000000-0302-65e0-b6dc-9c5c5963b3af',
            '00000000-0305-9978-1470-c0c2578bda98',
            '00000000-02dd-b9f8-b55c-9e8378d3c079',
            '00000000-0306-2ab4-12b2-e91278d83687',
            '00000000-02a1-a378-421e-207256046bbd',
            '00000000-02d7-c0e0-dabe-176e55b6a3ca',]

        query_date = datetime.strptime(kwargs['query_date'], '%Y-%m-%d')
        end_date = query_date - timedelta(days=1)

        result = ""
        for uuid in uuids:
            user = User.objects.filter(uuid=uuid)[0]
            days = (query_date.date() - user.experiment_start_date).days
            total = History.objects.filter(uuid=uuid, start_date__range=(user.experiment_start_date, end_date)).values('uuid').annotate(total_use=Sum('use_time'))
            oneday = History.objects.filter(uuid=uuid, start_date=query_date).values('uuid').annotate(total_use=Sum('use_time'))

            if len(total) == 0:
                result += '<br>' + user.name + '(' + user.cellphone + ") : " + "사용 기록이 없습니다."
                continue

            if len(oneday) == 0:
                result += '<br>' + user.name + '(' + user.cellphone + ") : " + "당일 사용 기록이 없습니다."
                continue

            if days < 14:
                result += '<br>' + user.name + '(' + user.cellphone + ") : " + "실험을 시작한지 " + str(days) + "일 되었습니다."
                continue

            result += '<br> <a href="../' + uuid + '/date/' + query_date.strftime("%Y-%m-%d") + '" > '\
                      + user.name + '(' + user.cellphone + ') </a>: ' \
                      + str(timedelta(seconds=round(total[0]['total_use']/days))) \
                      + " => " + str(timedelta(seconds=round(oneday[0]['total_use'])))

        return HttpResponse(result)


class InterventionUserView(APIView):
    def get(self, request, *args, **kwargs):
        query_date = datetime.strptime(kwargs['query_date'], '%Y-%m-%d')
        user = User.objects.filter(uuid=kwargs['uuid'])[0]
        end_date = query_date - timedelta(days=1)
        apps = History.objects.filter(uuid=kwargs['uuid'], start_date__range=(user.experiment_start_date, end_date)).values('app_name').annotate(total_use=Sum('use_time')).order_by('-total_use')[0:5]
        total = History.objects.filter(uuid=kwargs['uuid'], start_date__range=(user.experiment_start_date, end_date)).values('uuid').annotate(total_use=Sum('use_time'))[0]
        oneday = History.objects.filter(uuid=kwargs['uuid'], start_date=query_date).values('uuid').annotate(total_use=Sum('use_time'))[0]
        oneday_apps = History.objects.filter(uuid=kwargs['uuid'], start_date=query_date).values('app_name').annotate(total_use=Sum('use_time')).order_by('-total_use')[0:5]

        days = (query_date.date() - user.experiment_start_date).days

        result = "참가자 :" + user.name
        result += "<br>실험시작일 : " + user.experiment_start_date.__str__()
        result += "<br> 경과일 : " +  days.__str__()
        result += "<br> 상위 5개 1일 평균 사용량: "
        for app in apps:
            result += "<br>" + app['app_name']+' : '+str(timedelta(seconds=round(app['total_use']/days)))
        result += '<br><br> <font face="Arial Black" color="blue">하루 평균 사용량: ' + str(timedelta(seconds=round(total['total_use']/days))) + '</font>'
        result += '<br><br> <hr align=left color="red" width=200> 날짜 : ' + query_date.strftime("%Y-%m-%d")
        result += '<br> <font face="Arial Black" color="blue"> 총사용량 : ' + str(timedelta(seconds=round(oneday['total_use']))) + '</font><br>'
        for app in oneday_apps:
            result += "<br>" + app['app_name']+' : '+str(timedelta(seconds=round(app['total_use'])))
        return HttpResponse(result);