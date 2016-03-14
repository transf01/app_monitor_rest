from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework import serializers, mixins

from blog.models import Post
# Create your views here.
def blog_page(request):
    post_list = Post.objects.all()

    return HttpResponse('Hello!' + post_list[0].title)

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post


class blog_api(GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin,):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_serializer(self, *args, **kwargs):
        if "data" in kwargs:
            data = kwargs["data"]

            if isinstance(data, list):
                kwargs["many"] = True

        return super(blog_api, self).get_serializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
