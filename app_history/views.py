from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework import serializers, mixins

# Create your views here.
from app_history.models import History, User


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = History

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

class HistoryView(GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin,):
    queryset = History.objects.all()
    serializer_class = PostSerializer

    def get_serializer(self, *args, **kwargs):
        if "data" in kwargs:
            data = kwargs["data"]

            if isinstance(data, list):
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
