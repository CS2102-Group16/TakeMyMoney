from django.http import HttpResponse
from django.db import connection
from django.shortcuts import render, redirect

def project_list(request):
    context = dict()
    with connection.cursor() as cursor:
        cursor.execute("SELECT title, description, target_fund, start_date, end_date FROM project")
        row = cursor.fetchall()
        context['projects'] = row

    return render(request, 'project_list.html', context=context)

def add_new_project(request):
    return render(request, 'add_new_project.html', context=None)

def store_project(request):
    with connection.cursor() as cursor:
        #try:
            cursor.execute(
                "INSERT INTO project(title, description, target_fund, start_date, end_date) VALUES ('%s', '%s', '%s', '%s', '%s')"
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