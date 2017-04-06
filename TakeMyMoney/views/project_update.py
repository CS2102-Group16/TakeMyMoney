from django.db import connection, IntegrityError
from django.contrib import messages
from django.shortcuts import render, redirect
import datetime

import cloudinary
import cloudinary.uploader
import cloudinary.api

from utils import Helper, inject_user_data, ErrorMessages, authorize_modify_project


def add_new_project(request):
    context = dict()
    inject_user_data(request, context)
    if 'user_id' not in context:
        return redirect('/')

    with connection.cursor() as cursor:
        try:
            category_attrs = ['name']
            cursor.execute('SELECT ' + ', '.join(category_attrs) + ' FROM categories')
            rows = cursor.fetchall()
            categories = Helper.db_rows_to_dict(category_attrs, rows)
            context['categories'] = categories
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/addNewProject/')

    return render(request, 'add_new_project.html', context=context)


def store_project(request):
    upload_result = None
    context = dict()
    inject_user_data(request, context)

    if 'user_id' not in context:
        messages.add_message(request, messages.ERROR, ErrorMessages.UNAUTHORIZED)
        return redirect('/')

    if len(request.FILES) > 0:
       upload_result = cloudinary.uploader.upload(request.FILES['photo'])

    with connection.cursor() as cursor:
        try:
            start_date = datetime.datetime.strptime(request.POST['start_date'], "%Y-%m-%d")
            end_date = datetime.datetime.strptime(request.POST['end_date'], "%Y-%m-%d")

            if start_date > end_date:
                return redirect('/addNewProject/')

            if upload_result:
                sql = "INSERT INTO projects(title, description, target_fund, photo_url, start_date, end_date, user_id) " \
                      "VALUES (%s, %s, %s, %s, %s, %s, %s)"
                args = (request.POST['title'], request.POST['description'], request.POST['target_fund'],
                        upload_result['url'], request.POST['start_date'], request.POST['end_date'], context['user_id'])
            else:
                sql = "INSERT INTO projects(title, description, target_fund, start_date, end_date, user_id) " \
                      "VALUES (%s, %s, %s, %s, %s, %s)"
                args = (request.POST['title'], request.POST['description'], request.POST['target_fund'],
                        request.POST['start_date'], request.POST['end_date'], context['user_id'])

            cursor.execute(sql, args)
            connection.commit()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, ErrorMessages.ADD_FAIL)
            return redirect('/addNewProject/')

    with connection.cursor() as cursor:
        try:
            category_list = request.POST.getlist('category')
            cursor.execute('SELECT MAX(PID) FROM projects')
            last_id = cursor.fetchone()
            for cat in category_list:
                sql = "INSERT INTO projects_categories(category_name, pid) VALUES(%s, %s)"
                args = (cat, last_id)
                cursor.execute(sql, args)
                connection.commit()
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.ADD_CATEGORIES_FAIL)
            return redirect('/addNewProject/')

    return redirect('/')


def edit_project(request):
    context = dict()
    inject_user_data(request, context)

    if 'pid' not in request.GET:
        messages.add_message(request, messages.ERROR, ErrorMessages.PROJECT_NOT_FOUND)
        return redirect('/')

    context['pid'] = request.GET['pid']

    with connection.cursor() as cursor:
        try:
            sql = 'SELECT title, description, target_fund, start_date, end_date FROM projects WHERE pid = %s'
            args = (context['pid'], )
            cursor.execute(sql, args)
            rows = cursor.fetchall()
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/projectDetails/?pid=%s' % context['pid'])

    context['title'], context['description'], context['target_fund'], context['start_date'], context['end_date'] = rows[0]

    with connection.cursor() as cursor:
        try:
            category_attrs = ['name']
            cursor.execute('SELECT ' + ', '.join(category_attrs) + ' FROM categories')
            rows = cursor.fetchall()
            categories = Helper.db_rows_to_dict(category_attrs, rows)
            context['categories'] = categories
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/projectDetails/?pid=%s' % context['pid'])

    with connection.cursor() as cursor:
        try:
            projects_categories_attrs = ['name']
            sql = 'SELECT category_name FROM projects_categories WHERE pid = %s' % context['pid']
            cursor.execute(sql)
            rows = cursor.fetchall()
            projects_categories = Helper.db_rows_to_dict(projects_categories_attrs, rows)
            context['projects_categories'] = projects_categories
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/projectDetails/?pid=%s' % context['pid'])

    return render(request, 'edit_project.html', context=context)


def update_project(request):
    context = dict()
    inject_user_data(request, context)
    pid = request.GET.get('pid', None)

    if pid is None:
        messages.add_message(request, messages.ERROR, ErrorMessages.PROJECT_NOT_FOUND)
        return redirect('/')

    if not authorize_modify_project(context, pid):
        messages.add_message(request, messages.ERROR, ErrorMessages.UNAUTHORIZED)
        return redirect('/')

    with connection.cursor() as cursor:
        try:
            sql = 'UPDATE projects SET title = %s, description = %s, target_fund = %s, start_date = %s, end_date = %s ' \
                  'WHERE pid = %s'
            args = (request.POST['title'], request.POST['description'], request.POST['target_fund'],
                    request.POST['start_date'], request.POST['end_date'], pid)
            cursor.execute(sql, args)
            connection.commit()
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UPDATE_PROJECT_FAIL)
            return redirect('/projectDetails/?pid=%s' % pid)

    with connection.cursor() as cursor:
        try:
            category_list = request.POST.getlist('category')
            sql = 'SELECT category_name FROM projects_categories WHERE pid = %s' % pid
            cursor.execute(sql)
            rows = cursor.fetchall()
            projects_categories = list(sum(rows, ()))
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UPDATE_PROJECT_CATEGORIES_FAIL)
            return redirect('/projectDetails/?pid=%s' % pid)

        for cat in category_list:
            if cat not in projects_categories:
                try:
                    sql = 'INSERT INTO projects_categories(category_name, pid) VALUES(%s, %s)'
                    args = (cat, pid)
                    cursor.execute(sql, args)
                    connection.commit()
                except:
                    messages.add_message(request, messages.ERROR, ErrorMessages.UPDATE_PROJECT_CATEGORIES_FAIL)
                    return redirect('/projectDetails/?pid=%s' % pid)

        for cat in projects_categories:
            if cat not in category_list:
                try:
                    sql = 'DELETE FROM projects_categories WHERE category_name = %s AND pid = %s'
                    args = (cat, pid)
                    cursor.execute(sql, args)
                    connection.commit()
                except:
                    messages.add_message(request, messages.ERROR, ErrorMessages.UPDATE_PROJECT_CATEGORIES_FAIL)
                    return redirect('/projectDetails/?pid=%s' % pid)

    return redirect('/projectDetails/?pid=%s' % pid)


def delete_project(request):
    context = dict()
    inject_user_data(request, context)
    pid = request.GET.get('pid', None)

    if (pid is None) or not authorize_modify_project(context, pid):
        messages.add_message(request, messages.ERROR, ErrorMessages.UNAUTHORIZED)
        return redirect('/')

    with connection.cursor() as cursor:
        try:
            sql = 'DELETE FROM projects WHERE pid = %s'
            args = (pid, )
            cursor.execute(sql, args)
            connection.commit()
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.DELETE_PROJECT_FAIL)
            return redirect('/projectDetails/?pid=%s' % pid)

    return redirect('/')
