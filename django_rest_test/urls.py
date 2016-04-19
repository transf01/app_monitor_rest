"""django_rest_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from app_history.views import HistoryView, UserView, HistoryByUserView, StatView, LastHistoryView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/history$', HistoryView.as_view()),
    url(r'^api/user$', UserView.as_view()),
    url(r'^api/history/(?P<uuid>.+)/date/(?P<start_date>.+)$', HistoryByUserView.as_view()),
    url(r'^api/history/(?P<uuid>.+)$', HistoryByUserView.as_view()),
    url(r'^api/stat$', StatView.as_view()),
    url(r'^api/stat/(?P<uuid>.+)/date/(?P<start_date>.+)$', StatView.as_view()),
    url(r'^api/stat/(?P<uuid>.+)$', StatView.as_view()),
    url(r'^api/last_history/', LastHistoryView.as_view()),
]
