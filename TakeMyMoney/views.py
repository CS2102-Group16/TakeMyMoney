from django.http import HttpResponse
from django.db import connection
from django.shortcuts import render, redirect

def project_list(request):
    context = dict()
    category_name = 'All'

    if 'category' in request.GET:
        category_name = request.GET['category']

    if category_name == 'All':
        query_str = "SELECT title, description, target_fund, start_date, end_date, category FROM projects"
    else:
        query_str = "SELECT p.title, p.description, p.target_fund, p.start_date, p.end_date, p.category FROM projects p "\
                    "INNER JOIN categories c ON p.category = c.name WHERE c.name ='"+category_name+"'"

    with connection.cursor() as cursor:
        cursor.execute(query_str)
        row = cursor.fetchall()
        context['projects'] = row
        cursor.execute("SELECT name FROM categories")
        row = cursor.fetchall()
        context['categories'] = row

    return render(request, 'project_list.html', context=context)

def add_new_project(request):
    return render(request, 'add_new_project.html', context=None)

def store_project(request):
    with connection.cursor() as cursor:
        #try:
            cursor.execute(
                "INSERT INTO projects(title, description, target_fund, start_date, end_date) VALUES ('%s', '%s', '%s', '%s', '%s')"
                % (request.POST['title'],
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