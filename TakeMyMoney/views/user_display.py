from django.db import connection, IntegrityError
from django.contrib import messages
from django.shortcuts import render, redirect

from utils import Helper, inject_user_data, ErrorMessages


def user_list(request):
    context = dict()
    inject_user_data(request, context)

    if 'role' not in context or context['role'] != 'admin':
        messages.add_message(request, messages.ERROR, ErrorMessages.UNAUTHORIZED)
        return redirect('/')

    with connection.cursor() as cursor:
        try:
            user_attrs = ['user_email', 'user_id', 'role']
            cursor.execute('SELECT ' + ', '.join(user_attrs) + ' FROM users')
            rows = cursor.fetchall()
            users = Helper.db_rows_to_dict(user_attrs, rows)
            context['users'] = users
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/userList/')

    return render(request, 'user_list.html', context=context)


def user_details(request):
    context = dict()
    inject_user_data(request, context)
    user_id = request.GET.get('user_id', None)

    if user_id is None:
        messages.add_message(request, messages.ERROR, ErrorMessages.USER_NOT_FOUND)
        return redirect('/')

    with connection.cursor() as cursor:
        try:
            user_attrs = ['user_email', 'user_id', 'name', 'role']
            sql = 'SELECT ' + ', '.join(user_attrs) + ' FROM users WHERE user_id = %s'
            args = (user_id, )
            cursor.execute(sql, args)
            rows = cursor.fetchall()
            if len(rows) < 1:
                messages.add_message(request, messages.ERROR, ErrorMessages.USER_NOT_FOUND)
                return redirect('/')
            users = Helper.db_rows_to_dict(user_attrs, rows)
            context['target_role'] = users[0]['role']
            context['target_email'] = users[0]['user_email']
            context['target_id'] = users[0]['user_id']
            context['target_name'] = users[0]['name']
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/')

    with connection.cursor() as cursor:
        try:
            project_attrs = ['title', 'description', 'photo_url', 'target_fund', 'start_date', 'end_date', 'pid',
                             'category']
            cursor.execute("SELECT p.title, p.description, p.photo_url, p.target_fund, p.start_date, p.end_date, p.pid,"
                           " string_agg(pc.category_name, ', ') FROM projects p"
                           " LEFT OUTER JOIN projects_categories pc ON pc.pid = p.pid"
                           " WHERE p.user_id = %s"
                           " GROUP BY p.pid"
                           " ORDER BY p.title ASC" % context['target_id'])
            rows = cursor.fetchall()
            context['owned_projects'] = Helper.db_rows_to_dict(project_attrs, rows)
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/projectList/')

    with connection.cursor() as cursor:
        try:
            project_attrs = ['title', 'description', 'photo_url', 'target_fund', 'start_date', 'end_date', 'pid',
                             'category']
            cursor.execute("SELECT p.title, p.description, p.photo_url, p.target_fund, p.start_date, p.end_date, p.pid,"
                           " string_agg(pc.category_name, ', ') FROM projects p"
                           " LEFT OUTER JOIN projects_categories pc ON pc.pid = p.pid"
                           " INNER JOIN funding f ON p.pid = f.pid"
                           " WHERE f.user_id = %s"
                           " GROUP BY p.pid"
                           " ORDER BY p.title ASC" % context['target_id'])
            rows = cursor.fetchall()
            context['pledged_projects'] = Helper.db_rows_to_dict(project_attrs, rows)
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/projectList/')

    context['me'] = (str(user_id) == str(context['user_id']))

    return render(request, 'user_details.html', context=context)
