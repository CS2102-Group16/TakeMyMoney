from django.http import HttpResponse
from django.db import connection
from django.shortcuts import render, redirect

import cloudinary
import cloudinary.uploader
import cloudinary.api

def project_list(request):
    context = dict()
    with connection.cursor() as cursor:
        cursor.execute("SELECT title, description, target_fund, start_date, end_date FROM projects")
        row = cursor.fetchall()
        context['projects'] = row

    return render(request, 'project_list.html', context=context)

def add_new_project(request):
    return render(request, 'add_new_project.html', context=None)

def store_project(request):
    upload_result = cloudinary.uploader.upload(request.FILES['photo'])

    with connection.cursor() as cursor:
        #try:
            cursor.execute(
                "INSERT INTO projects(title, description, target_fund, photo_url, start_date, end_date) "
                "VALUES ('%s', '%s', '%s', '%s', '%s', '%s')"
                % (request.POST['title'],
                   request.POST['description'],
                   request.POST['target_fund'],
                   upload_result['url'],
                   request.POST['start_date'],
                   request.POST['end_date'])
            )
            connection.commit()
        # except Exception:
        #     return redirect('/addNewProject/')

    return redirect('/')


def search_project(request):
    return render(request, 'search_project.html', context=None)

def project_details(request):
    context = dict()
    with connection.cursor() as cursor:
        cursor.execute("SELECT title, description, target_fund, start_date, end_date FROM projects WHERE title = '%s'"
                       % (request.POST['search_title']))
        row = cursor.fetchall()
        context['projects'] = row

    return render(request, 'project_details.html', context=context)

def login(request):
    return render(request, 'login.html',context=None)

# placeholder method
def check_user(request):
    return redirect('/')

'''
def check_user(request):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT user_email, password FROM users"
                "WHERE user_email = '%s'"
                "AND password = '%s'"
            )
'''

def add_new_user(request):
    return render(request,'add_new_user.html',context=None)

def store_user(request):
    with connection.cursor() as cursor:
        #try:
            cursor.execute(
                "INSERT INTO users(user_email, password, role) VALUES ('%s', '%s', 'user')"
                % (request.POST['user_email'],
                   request.POST['password'])
            )
            connection.commit()
        # except Exception:
        #     return redirect('/userList/')

    return redirect('/userList/')

def user_list(request):
    context = dict()
    with connection.cursor() as cursor:
        cursor.execute("SELECT user_email, password, role FROM users")
        row = cursor.fetchall()
        context['users'] = row

    return render(request, 'user_list.html', context=context)