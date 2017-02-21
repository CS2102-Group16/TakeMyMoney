from django.http import HttpResponse
from django.db import connection
from django.shortcuts import render, redirect
import uuid


def project_list(request):
    context = dict()
    inject_user_data(request, context)

    with connection.cursor() as cursor:
        cursor.execute("SELECT title, description, target_fund, start_date, end_date, pid FROM projects")
        row = cursor.fetchall()
        context['projects'] = row

    return render(request, 'project_list.html', context=context)


def add_new_project(request):
    if 'session_id' not in request.COOKIES:
        return redirect('/')

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
    pid = request.GET['pid']

    with connection.cursor() as cursor:
        cursor.execute("SELECT title, description, target_fund, start_date, end_date, pid FROM projects WHERE pid = %s"
                       % pid)
        rows = cursor.fetchall()
        context['project'] = rows[0]

    return render(request, 'project_details.html', context=context)


def login(request):
    if 'session_id' in request.COOKIES:
        return redirect('/')

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
    inject_user_data(request, context)

    with connection.cursor() as cursor:
        cursor.execute("SELECT user_email, user_id, password, role FROM users")
        row = cursor.fetchall()
        context['users'] = row

    return render(request, 'user_list.html', context=context)


def attempt_login(request):
    if 'session_id' in request.COOKIES:
        redirect('/')

    # Validate login credentials
    if 'user_email' not in request.POST or 'password' not in request.POST:
        return redirect('/')
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT user_id, password FROM users WHERE user_email = '%s'" % request.POST['user_email']
        )
        rows = cursor.fetchall()
    if len(rows) == 0:
        return redirect('/')

    user_id, password = rows[0]
    if password != request.POST['password']:
        return redirect('/')

    # Construct new session
    session_id = uuid.uuid4()

    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO sessions (session_id, user_id) VALUES ('%s', %s)"
            % (session_id,
               user_id)
        )
        connection.commit()

    response = redirect('/')
    response.set_cookie('session_id', session_id)
    return response


def logout(request):
    if 'session_id' not in request.COOKIES:
        return redirect('/')

    session_id = request.COOKIES['session_id']

    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM sessions WHERE session_id = '%s'" % session_id
        )
        connection.commit()

    response = redirect('/')
    response.delete_cookie('session_id')
    return response


def inject_user_data(request, context):
    if 'session_id' not in request.COOKIES:
        return

    session_id = request.COOKIES['session_id']

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT u.user_email FROM users u NATURAL JOIN sessions s WHERE s.session_id = '%s'"
            % session_id
        )
        rows = cursor.fetchall()

    if len(rows) == 0:
        return

    user_email = rows[0][0]
    context['user_email'] = user_email


def edit_project(request):
    context = dict()
    context['pid'] = request.GET['pid']

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT title, description, target_fund, start_date, end_date FROM projects WHERE pid = %s"
            % context['pid']
        )
        rows = cursor.fetchall()

    context['title'], context['description'], context['target_fund'], context['start_date'], context['end_date'] = rows[0]

    return render(request, 'edit_project.html', context=context)


def update_project(request):
    pid = request.GET['pid']
    with connection.cursor() as cursor:
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
    pid = request.GET['pid']
    with connection.cursor() as cursor:
        #try:
            cursor.execute(
                "DELETE FROM projects WHERE pid = %s"
                % (pid)
            )
            connection.commit()

    return redirect('/')
