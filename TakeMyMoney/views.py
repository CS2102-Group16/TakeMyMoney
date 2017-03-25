from django.http import HttpResponse
from django.db import connection
from django.shortcuts import render, redirect

import uuid

from psycopg2 import Binary

import cloudinary
import cloudinary.uploader
import cloudinary.api

from helper import Helper


def project_list(request):
    context = dict()
    inject_user_data(request, context)
    filtering = request.GET.get('filter', None)

    if filtering == 'owned':
        with connection.cursor() as cursor:
            project_attrs = ['title', 'description', 'target_fund', 'start_date', 'end_date', 'pid']
            cursor.execute('SELECT ' +
                           ', '.join(['p.' + project_attr for project_attr in project_attrs]) +
                           ' FROM projects p WHERE p.user_id = %s' % context['user_id'])
            rows = cursor.fetchall()
            projects = Helper.db_rows_to_dict(project_attrs, rows)
            context['projects'] = projects
    elif filtering == 'pledged':
        with connection.cursor() as cursor:
            project_attrs = ['title', 'description', 'target_fund', 'start_date', 'end_date', 'pid']
            cursor.execute('SELECT ' +
                           ', '.join(['p.' + project_attr for project_attr in project_attrs]) +
                           ' FROM projects p INNER JOIN funding f ON p.pid = f.pid AND f.user_id = %s' % context['user_id'])
            rows = cursor.fetchall()
            projects = Helper.db_rows_to_dict(project_attrs, rows)
            context['projects'] = projects
    elif filtering == 'search':
        search_input = request.POST.get('search', None)

        if search_input is None:
            return redirect('/')

        with connection.cursor() as cursor:
            project_attrs = ['title', 'description', 'target_fund', 'start_date', 'end_date', 'pid']
            args = ('%' + search_input + '%', )  # Hidden dragon, crouching input sanitization.
            cursor.execute('SELECT ' +
                           ', '.join(['p.' + project_attr for project_attr in project_attrs]) +
                           ' FROM projects p WHERE p.title ILIKE %s', args)
            rows = cursor.fetchall()
            projects = Helper.db_rows_to_dict(project_attrs, rows)
            context['projects'] = projects
    else:
        with connection.cursor() as cursor:
            category_attrs = ['name']
            cursor.execute('SELECT ' + ', '.join(category_attrs) + ' FROM categories')
            rows = cursor.fetchall()
            categories = Helper.db_rows_to_dict(category_attrs, rows)
            context['categories'] = categories

        project_attrs = ['title', 'description', 'target_fund', 'start_date', 'end_date', 'pid', 'category']
        query_str = "SELECT p.title, p.description, p.target_fund, p.start_date, p.end_date, p.pid," \
                    " string_agg(pc.category_name, ', ') FROM projects p" \
                    " LEFT OUTER JOIN projects_categories pc ON p.pid = pc.pid" \
                    " GROUP BY p.pid" \
                    " ORDER BY p.pid ASC"

        if 'category' in request.GET:
            category_name = request.GET['category']
            if not category_name == 'All':
                query_str = "SELECT p.title, p.description, p.target_fund, p.start_date, p.end_date, p.pid," \
                            " string_agg(pc.category_name, ', ') FROM projects p" \
                            " INNER JOIN projects_categories pc ON p.pid = pc.pid" \
                            " INNER JOIN categories c ON pc.category_name = c.name WHERE c.name = '%s'" \
                            " GROUP BY p.pid" \
                            " ORDER BY p.pid ASC" % category_name

        with connection.cursor() as cursor:
            cursor.execute(query_str)
            rows = cursor.fetchall()
            projects = Helper.db_rows_to_dict(project_attrs, rows)
            context['projects'] = projects

    return render(request, 'project_list.html', context=context)


def add_new_project(request):
    context = dict()
    inject_user_data(request, context)
    if 'user_id' not in context:
        return redirect('/')

    with connection.cursor() as cursor:
        category_attrs = ['name']
        cursor.execute('SELECT ' + ', '.join(category_attrs) + ' FROM categories')
        rows = cursor.fetchall()
        categories = Helper.db_rows_to_dict(category_attrs, rows)
        context['categories'] = categories

    return render(request, 'add_new_project.html', context=context)


def store_project(request):
    upload_result = None
    context = dict()
    inject_user_data(request, context)
    if 'user_id' not in context:
        redirect('/')
    if len(request.FILES) > 0:
       upload_result = cloudinary.uploader.upload(request.FILES['photo'])

    with connection.cursor() as cursor:
        #try:
        # ugly copy-and-paste for now

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

    with connection.cursor() as cursor:
            category_list = request.POST.getlist('category')
            cursor.execute('SELECT MAX(PID) FROM projects')
            last_id = cursor.fetchone()
            print last_id
            for cat in category_list:
                sql = "INSERT INTO projects_categories(category_name, pid) VALUES(%s, %s)"
                args = (cat, last_id)
                cursor.execute(sql, args)
                connection.commit()
        # except Exception:
        #     return redirect('/addNewProject/')

    return redirect('/')


def search_project(request):
    return render(request, 'search_project.html', context=None)


def project_details(request):
    context = dict()
    inject_user_data(request, context)
    pid = request.GET['pid']

    with connection.cursor() as cursor:
        project_attrs = ['title', 'description', 'target_fund', 'photo_url', 'start_date', 'end_date', 'pid']
        sql = 'SELECT ' + ', '.join(project_attrs) + ' FROM projects WHERE pid = %s'
        args = (pid, )
        cursor.execute(sql, args)
        rows = cursor.fetchall()
        projects = Helper.db_rows_to_dict(project_attrs, rows)
        context['project'] = projects[0]

    with connection.cursor() as cursor:
        funding_attrs = ['pledger', 'amount']
        sql = 'SELECT u.name, f.amount FROM users u INNER JOIN funding f ON u.user_id = f.user_id AND f.pid = %s'
        args = (pid, )
        cursor.execute(sql, args)
        rows = cursor.fetchall()
        pledges = Helper.db_rows_to_dict(funding_attrs, rows)
        context['pledges'] = pledges

    with connection.cursor() as cursor:
        related_project_attrs = ['title', 'description']
        # The subquery selects the pids of projects that are not the current one (left
        # side of the WHERE) and shares the same category as the current one.
        sql = 'SELECT ' + ', '.join(['p.' + project_attr for project_attr in related_project_attrs]) + (
              ' FROM projects p'
              ' WHERE p.pid IN ('
                ' SELECT pc1.pid'
                ' FROM projects_categories pc1 INNER JOIN projects_categories pc2'
                ' ON pc1.category_name = pc2.category_name'
                ' WHERE pc1.pid <> %s AND pc2.pid = %s'
              ' )')
        args = (pid, pid)
        cursor.execute(sql, args)
        rows = cursor.fetchall()
        related = Helper.db_rows_to_dict(related_project_attrs, rows)
        context['related'] = related

    return render(request, 'project_details.html', context=context)


def login(request):
    response = render(request, 'login.html', context=None)

    if 'session_id' in request.COOKIES:
        with connection.cursor() as cursor:
            sql = 'SELECT 1 FROM sessions WHERE session_id = %s'
            args = (request.COOKIES['session_id'], )
            cursor.execute(sql, args)
            row = cursor.fetchone()
            if row is not None:
                return redirect('/')
            else:
                # session_id is in COOKIES, but it is an invalid one. So we delete it.
                response.delete_cookie('session_id')

    return response


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
            sql = 'INSERT INTO users(user_email, password, name, role) VALUES (%s, %s, %s, \'user\')'
            args = (request.POST['user_email'], request.POST['password'], request.POST['name'])
            cursor.execute(sql, args)
            connection.commit()
        # except Exception:
        #     return redirect('/userList/')

    return redirect('/userList/')


def user_list(request):
    context = dict()
    inject_user_data(request, context)

    with connection.cursor() as cursor:
        user_attrs = ['user_email', 'user_id', 'role']
        cursor.execute('SELECT ' + ', '.join(user_attrs) + ' FROM users')
        rows = cursor.fetchall()
        users = Helper.db_rows_to_dict(user_attrs, rows)
        context['users'] = users

    return render(request, 'user_list.html', context=context)


def attempt_login(request):
    if 'session_id' in request.COOKIES:
        redirect('/')

    # Validate login credentials
    if 'user_email' not in request.POST or 'password' not in request.POST:
        return redirect('/')
    with connection.cursor() as cursor:
        sql = 'SELECT user_id, password FROM users WHERE user_email = %s'
        args = (request.POST['user_email'], )
        cursor.execute(sql, args)
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
        sql = 'DELETE FROM sessions WHERE session_id = %s'
        args = (session_id, )
        cursor.execute(sql, args)
        connection.commit()

    response = redirect('/')
    response.delete_cookie('session_id')
    return response


def inject_user_data(request, context):
    if 'session_id' not in request.COOKIES:
        return

    session_id = request.COOKIES['session_id']

    with connection.cursor() as cursor:
        user_attrs = ['user_email', 'user_id']
        sql = 'SELECT u.user_email, u.user_id FROM users u NATURAL JOIN sessions s WHERE s.session_id = %s'
        args = (session_id, )
        cursor.execute(sql, args)
        rows = cursor.fetchall()
        users = Helper.db_rows_to_dict(user_attrs, rows)

    if len(users) == 0:
        return

    user_email = users[0]['user_email']
    user_id = users[0]['user_id']
    context['user_email'] = user_email
    context['user_id'] = user_id


def edit_project(request):
    context = dict()
    context['pid'] = request.GET['pid']

    with connection.cursor() as cursor:
        sql = 'SELECT title, description, target_fund, start_date, end_date FROM projects WHERE pid = %s'
        args = (context['pid'], )
        cursor.execute(sql, args)
        rows = cursor.fetchall()

    context['title'], context['description'], context['target_fund'], context['start_date'], context['end_date'] = rows[0]

    return render(request, 'edit_project.html', context=context)


def update_project(request):
    pid = request.GET['pid']
    with connection.cursor() as cursor:
        sql = 'UPDATE projects SET title = %s, description = %s, target_fund = %s, start_date = %s, end_date = %s ' \
              'WHERE pid = %s'
        args = (request.POST['title'], request.POST['description'], request.POST['target_fund'],
               request.POST['start_date'], request.POST['end_date'], pid)
        cursor.execute(sql, args)
        connection.commit()

    return redirect('/')


def delete_project(request):
    pid = request.GET['pid']
    with connection.cursor() as cursor:
        #try:
            sql =  'DELETE FROM projects WHERE pid = %s'
            args = (pid, )
            cursor.execute(sql, args)
            connection.commit()

    return redirect('/')


def add_funding(request):
    pid = request.GET['pid']
    amount = request.POST['amount']

    with connection.cursor() as cursor:
        # try:
        project_attrs = ['title']
        sql = 'SELECT title FROM projects WHERE pid = %s'
        args = (pid,)
        cursor.execute(sql, args)
        rows = cursor.fetchall()
        projects = Helper.db_rows_to_dict(project_attrs, rows)

    context = {
        'title': projects[0]['title'],
        'amount': amount,
        'pid': pid,
    }

    return render(request, 'add_funding.html', context=context)


def store_funding(request):
    context = dict()
    inject_user_data(request, context)
    pid = request.GET.get('pid', None)
    amount = request.GET['amount']
    if pid is None:
        return redirect('/')
    if 'user_id' not in context:
        return redirect('/projectDetails/?pid=%s' % pid)

    with connection.cursor() as cursor:
        sql = 'SELECT 1 FROM funding WHERE user_id = %s AND pid = %s'
        args = (context['user_id'], pid)
        cursor.execute(sql, args)
        rows = cursor.fetchall()
        funding_exists = len(rows) > 0

    if funding_exists:
        with connection.cursor() as cursor:
            sql = 'UPDATE funding SET amount = %s WHERE user_id = %s AND pid = %s'
            args = (amount, context['user_id'], pid)
            cursor.execute(sql, args)
            connection.commit()
    else:
        with connection.cursor() as cursor:
            sql = 'INSERT INTO funding (user_id, pid, amount) VALUES (%s, %s, %s)'
            args = (context['user_id'], pid, amount)
            cursor.execute(sql, args)
            connection.commit()

    return redirect('/projectDetails/?pid=%s' % pid)


def search(request):
    search_string = request.POST.get('search')
    if search_string is None:
        return redirect('/')

    with connection.cursor() as cursor:
        sql = 'SELECT '
