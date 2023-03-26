from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.contrib.auth import logout, login, authenticate
from django.db.models.lookups import YearExact
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_list_or_404
from django.views.generic.base import TemplateView
from .forms import *
from django.db.models.functions import *
from django.db.models import Count, Sum
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .models import *
from .profile import *
import subprocess
import requests
import datetime
import logging
import json
import sys


def userLogout(request):
    logout(request)
    return redirect('index')


def index(request):
    # If user authenticated redirect him to dashboard page
    if request.user.is_authenticated:
        return redirect('dashboard')

    Regform = NewUserForm()
    err = None
    if request.method == "POST":        
        # Form for the user registration
        if request.POST.get('submit') == "register":
            form = NewUserForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                print(User.objects.filter(username=username))
                # If user exists redirect him else create him
                try:
                    User.objects.get(username=username)
                except User.DoesNotExist:
                    user = User.objects.create_user(username=username, password=password)

                    # create user
                    AppUser.objects.create(user=user)

                    # create user's session with login()
                    login(request, user)

                    return redirect('dashboard')
            else:
                err = form.error_messages
                print(err)

        # Form for the user log in
        if request.POST.get('submit') == "login":
            username = request.POST.get('login_username')
            password = request.POST.get('login_password')

            # check if given credentials are valid and redirect user to dashboard page
            user = authenticate(request, username=username, password=password)
            if user is not None:

                # create user's session with login()
                login(request, user)

                return redirect('dashboard')
            else:
                err = "Username or Password is wrong."
                print(err)

    context = {'Regform': Regform, 'err': err}
    return render(request, 'index.html', context)


@login_required(login_url='index')
def dashboard(request):
    # get user
    app_user = AppUser.objects.get(user=request.user)

    try:
        # get papers per year (where author id = app user's scopus id)
        paper = (Papers.objects.filter(author_id = app_user.user_scopus_id)
                .values('paper_year')
                .annotate(Documents = Count('paper_title'))
                .order_by('paper_year')
                )
        print(paper)
        labels = [] # year axis
        documents = [] # document axis
        for i in paper:
            print(i)
            labels.append(i['paper_year'])
            documents.append(i['Documents'])

        json = {"documents":documents,"labels":labels}

    except ObjectDoesNotExist:
        paper = None
        json = {""}

    context = {'AppUser': app_user ,'paper':paper,"json":json}
    return render(request, 'authed/dashboard.html', context)


@login_required(login_url='index')
def profile(request):
    app_user = AppUser.objects.get(user=request.user)

    print(request.POST)

    pform = ProfileForm(initial={
        'user_email': app_user.user_email,
        'user_firstname': app_user.user_firstname,
        'user_lastname': app_user.user_lastname,
        'user_rank': app_user.user_rank,
        'apps_id': app_user.apps_id,
        })

    mform = MetricsForm(initial={
        'user_scopus_id': app_user.user_scopus_id,
        'user_orc_id': app_user.user_orc_id,
        'user_scholar_id': app_user.user_scholar_id,
        'user_researcher_id': app_user.user_researcher_id,
    })
    if request.POST.get('submit') == "profile":
        pform = ProfileForm(request.POST,instance=request.user)
        if pform.is_valid():
            cd = pform.cleaned_data
            profileForm(app_user,cd)
            messages.success(request, 'Your profile is updated successfully')


    elif request.POST.get('submit') == "metrics":
        mform = MetricsForm(request.POST,instance=request.user)
        if mform.is_valid():
            cd = mform.cleaned_data
            metricsForm(app_user,cd)

            # get the data from our SCOPUS API
            if app_user.user_scopus_id != None:  # scopus ID form
                # get author data
                scopus_author_API = ScopusAuthor.objects.get(scopus_auid=app_user.user_scopus_id)
                # insert data to app
                app_author(app_user,scopus_author_API)
                # get paper data
                scopus_paper_API = ScopusPaper.objects.filter(author_id=app_user.user_scopus_id)
                # insert papers to app
                app_paper(app_user,scopus_paper_API)
            
            messages.success(request, 'Your metrics updated successfully')
            return HttpResponseRedirect(reverse('dashboard'))
        #     # create data from cron-job
        #     else:
        #         return HttpResponseRedirect(reverse('dashboard'))
        # return HttpResponseRedirect(reverse('dashboard'))
    context = {"AppUser": app_user, "form_1":pform, "form_2":mform}    

    return render(request, 'authed/profile.html', context)


@login_required(login_url='index')
def documents(request):
    app_user = AppUser.objects.get(user=request.user)

    # get user's papers
    paper = Papers.objects.filter(author_id = app_user.user_scopus_id)
    print(paper)
    context = {"AppUser": app_user, "papers":paper}
    return render(request, 'authed/documents.html', context)


@login_required(login_url='index')
def paper(request, sid, title):
    app_user = AppUser.objects.get(user=request.user)

    paper = Papers.objects.get(paper_id=sid)
    context = {"AppUser": app_user, "paper": paper}

    return render(request, 'authed/paper.html', context)

@login_required(login_url='index')
def testing(request):
    app_user = AppUser.objects.get(user = request.user)
    paper = Papers.objects.filter(author_id = app_user.user_scopus_id)
    context = {"AppUser":app_user, "papers":paper}
    return(render(request, 'authed/testing.html',context))