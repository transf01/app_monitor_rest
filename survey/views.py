from django.core.serializers import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core import urlresolvers
from django.contrib import messages
import datetime
from django_rest_test import settings

from survey.models import Question, Survey, Category, AnswerRadio
from survey.forms import ResponseForm

from django.contrib.auth.models import User


def Index(request):
    # received_uuid = request.GET.get('r_uuid')  ##UUID 받기
    # print (received_uuid)   ##UUID 받아서 찍기
    return render(request, 'survey/index.html')  # , {'received_uuid': received_uuid})


def SurveyDetail(request, id):
    survey = Survey.objects.get(id=id)
    category_items = Category.objects.filter(survey=survey)
    categories = [c.name for c in category_items]

    if request.method == 'POST':
        form = ResponseForm(request.POST, survey=survey)

        if form.is_valid():
            response = form.save()
            return HttpResponseRedirect("/survey/confirm/%s" % response.interview_uuid)
    else:
        form = ResponseForm(initial={'user_id': request.GET.get('user_id')}, survey=survey)

        # print(form)
        # TODO sort by category

    print(form)
    return render(request, 'survey/survey.html',
                  {'response_form': form, 'survey': survey, 'categories': categories })


def Confirm(request, uuid):
    email = settings.support_email
    return render(request, 'survey/confirm.html', {'uuid': uuid, "email": email})


def privacy(request):
    return render(request, 'survey/privacy.html')

# ## registration
# def register_page(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             user = User.objects.create_user(
#                 username=form.cleaned_data['username'],
#                 email=form.cleaned_data['email'],
#                 password=form.cleaned_data['password1']
#             )
#             return HttpResponseRedirect('/login/')
#     else:
#         form = RegistrationForm()
#
#     variables = RequestContext(request, {
#         'form': form
#     })
#     return render_to_response('registration/register.html', variables)
