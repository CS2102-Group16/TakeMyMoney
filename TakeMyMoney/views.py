from django.http import HttpResponse
from django.db import connection
from django.shortcuts import render, redirect

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
    with connection.cursor() as cursor:
        #try:
            cursor.execute(
                "INSERT INTO projects(title, description, target_fund, start_date, end_date) VALUES ('%s', '%s', '%s', '%s', '%s')"
                % (
                   request.POST['title'],
                   request.POST['description'],
                   request.POST['target_fund'],
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

def edit_project(request):
    return render(request, 'edit_project.html', context=None)

def update_project(request):
    pid = request.POST['pid']
    with connection.cursor() as cursor:
        #try:
            cursor.execute(
                "UPDATE projects SET title = '%s', description = '%s', target_fund = %s, start_date = '%s', end_date = '%s' WHERE pid = %s"
                % (request.POST['title'],
                   request.POST['description'],
                   request.POST['target_fund'],
                   request.POST['start_date'],
                   request.POST['end_date'],
                   pid)
            )
            connection.commit()

    return redirect('/')

def delete_project(request):
    pid = request.POST['pid']
    with connection.cursor() as cursor:
        #try:
            cursor.execute(
                "DELETE FROM projects WHERE pid = %s"
                % (pid)
            )
            connection.commit()

    return redirect('/')
