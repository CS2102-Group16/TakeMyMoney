from django.http import HttpResponse
from django.db import connection, IntegrityError
from django.contrib import messages
from django.shortcuts import render, redirect
import uuid
import datetime

import cloudinary
import cloudinary.uploader
import cloudinary.api

from helper import Helper


class ErrorMessages(object):
    UNKNOWN = "An unknown error has occurred."
    ADD_FAIL = "There was an error in creating your project. Please check your project data again."
    ADD_CATEGORIES_FAIL = "There was an error in setting your project categories."
    PROJECT_NOT_FOUND = "This project does not exist in the database."
    ALREADY_LOGGED_IN = "You are already logged in."
    USER_REGISTER_FAIL = "Failed to register."
    UNAUTHORIZED = "You are not authorized to view this page or make this change."
    MISSING_DATA = "Oops...did you forget to specify some required information?"
    WRONG_CREDENTIALS = "Please check your e-mail or password."
    LOGIN_FAILED = "Failed to log you in."
    LOGOUT_FAILED = "Failed to log you out."
    UPDATE_PROJECT_FAIL = "There was an error in updating your project."
    UPDATE_PROJECT_CATEGORIES_FAIL = "There was an error in updating your project categories."
    DELETE_PROJECT_FAIL = "There was an error in deleting your project."
    PLEDGE_FAIL = "Failed to pledge for your project."
    USER_NOT_FOUND = "This user does not exist in the database."
    MAKE_ADMIN_FAIL = "Failed to make user an admin."
    REVOKE_ADMIN_FAIL = "Failed to revoke user's admin status. " \
                        "Please make sure there is at least one admin in the system after revocation."

    def __setattr__(self, *_):
        pass


def authorize_modify_project(context, target_pid):
    """
    Returns a boolean indicating whether the user is allowed to
    modify (either update or delete) the target project, indicated
    by its pid.
    True - can modify
    False - cannot modify
    """

    if 'user_id' not in context or 'role' not in context:
        return False

    if context['role'] is 'admin':
        # Admins are authorized to do anything they want.
        return True

    with connection.cursor() as cursor:
        try:
            sql = 'SELECT 1 FROM projects WHERE user_id = %s AND pid = %s'
            args = (context['user_id'], target_pid)
            cursor.execute(sql, args)
        except:
            return False

        row = cursor.fetchone()
        return row is not None


def project_list(request):
    context = dict()
    inject_user_data(request, context)
    filtering = request.GET.get('filter', None)

    if filtering == 'owned' and 'user_id' in context:
        with connection.cursor() as cursor:
            try:
                project_attrs = ['title', 'description', 'target_fund', 'start_date', 'end_date', 'pid', 'category']
                cursor.execute("SELECT p.title, p.description, p.target_fund, p.start_date, p.end_date, p.pid,"
                               " string_agg(pc.category_name, ', ') FROM projects p"
                               " LEFT OUTER JOIN projects_categories pc ON pc.pid = p.pid"
                               " WHERE p.user_id = %s"
                               " GROUP BY p.pid"
                               " ORDER BY p.title ASC" % context['user_id'])
                rows = cursor.fetchall()
                projects = Helper.db_rows_to_dict(project_attrs, rows)
                context['projects'] = projects
            except:
                messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
                return redirect('/projectList/')

    elif filtering == 'pledged' and 'user_id' in context:
        with connection.cursor() as cursor:
            try:
                project_attrs = ['title', 'description', 'target_fund', 'start_date', 'end_date', 'pid', 'category']
                cursor.execute("SELECT p.title, p.description, p.target_fund, p.start_date, p.end_date, p.pid,"
                               " string_agg(pc.category_name, ', ') FROM projects p"
                               " LEFT OUTER JOIN projects_categories pc ON pc.pid = p.pid"
                               " INNER JOIN funding f ON p.pid = f.pid AND f.user_id = %s"
                               " GROUP BY p.pid"
                               " ORDER BY p.title ASC" % context['user_id'])
                rows = cursor.fetchall()
                projects = Helper.db_rows_to_dict(project_attrs, rows)
                context['projects'] = projects
            except:
                messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
                return redirect('/projectList/')

    elif filtering == 'search' and 'search' in request.POST:
        search_input = request.POST['search']

        with connection.cursor() as cursor:
            try:
                project_attrs = ['title', 'description', 'target_fund', 'start_date', 'end_date', 'pid', 'category']
                # Hidden dragon, crouching input sanitization.
                args = ('%' + search_input + '%', '%' + search_input + '%')
                cursor.execute("SELECT p.title, p.description, p.target_fund, p.start_date, p.end_date, p.pid,"
                               " string_agg(pc.category_name, ', ') FROM projects p"
                               " LEFT OUTER JOIN projects_categories pc ON pc.pid = p.pid"
                               " WHERE p.title ILIKE %s OR p.description ILIKE %s"
                               " GROUP BY p.pid"
                               " ORDER BY p.title", args)
                rows = cursor.fetchall()
                projects = Helper.db_rows_to_dict(project_attrs, rows)
                context['projects'] = projects
            except:
                messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
                return redirect('/projectList/')

    else:
        with connection.cursor() as cursor:
            try:
                category_attrs = ['name']
                cursor.execute("SELECT " + ", ".join(category_attrs) + " FROM categories")
                rows = cursor.fetchall()
                categories = Helper.db_rows_to_dict(category_attrs, rows)
                context['categories'] = categories
            except:
                messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
                return redirect('/projectList/')

        project_attrs = ['title', 'description', 'target_fund', 'start_date', 'end_date', 'pid', 'category']
        query_str = "SELECT p.title, p.description, p.target_fund, p.start_date, p.end_date, p.pid," \
                    " string_agg(pc.category_name, ', ') FROM projects p" \
                    " LEFT OUTER JOIN projects_categories pc ON p.pid = pc.pid" \
                    " GROUP BY p.pid" \
                    " ORDER BY p.title ASC"

        if 'category' in request.GET:
            category_name = request.GET['category']
            if not category_name == 'All':
                query_str = "SELECT p.title, p.description, p.target_fund, p.start_date, p.end_date, p.pid," \
                            " string_agg(pc.category_name, ', ') FROM projects p" \
                            " NATURAL JOIN projects_categories pc" \
                            " GROUP BY p.pid" \
                            " EXCEPT" \
                            " SELECT p2.title, p2.description, p2.target_fund, p2.start_date, p2.end_date, p2.pid," \
                            " string_agg(pc2.category_name, ', ')" \
                            " FROM projects p2" \
                            " NATURAL JOIN projects_categories pc2" \
                            " WHERE pc2.category_name <>'%s'" \
                            " GROUP BY p2.pid" % category_name

        with connection.cursor() as cursor:
            try:
                cursor.execute(query_str)
                rows = cursor.fetchall()
                projects = Helper.db_rows_to_dict(project_attrs, rows)
                context['projects'] = projects
            except:
                messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
                return redirect('/projectList/')

    return render(request, 'project_list.html', context=context)


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


def project_details(request):
    context = dict()
    inject_user_data(request, context)
    pid = request.GET['pid']

    with connection.cursor() as cursor:
        try:
            project_attrs = ['title', 'description', 'target_fund', 'photo_url', 'start_date', 'end_date', 'pid']
            sql = 'SELECT ' + ', '.join(project_attrs) + ' FROM projects WHERE pid = %s'
            args = (pid, )
            cursor.execute(sql, args)
            rows = cursor.fetchall()
            projects = Helper.db_rows_to_dict(project_attrs, rows)

            if len(projects) < 1:
                messages.add_message(request, messages.ERROR, ErrorMessages.PROJECT_NOT_FOUND)
                return redirect('/')

            context['project'] = projects[0]
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/projectList/')

    with connection.cursor() as cursor:
        try:
            projects_categories_attrs = ['category_name']
            sql = 'SELECT ' + ', '.join(projects_categories_attrs) + ' FROM projects_categories WHERE pid = %s'
            args = (pid, )
            cursor.execute(sql, args)
            rows = cursor.fetchall()
            project_categories = Helper.db_rows_to_dict(projects_categories_attrs, rows)
            context['project_categories'] = project_categories
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/projectList/')

    with connection.cursor() as cursor:
        try:
            funding_attrs = ['pledger_name', 'pledger_id', 'amount']
            sql = 'SELECT u.name, u.user_id, f.amount' \
                  ' FROM users u INNER JOIN funding f ON u.user_id = f.user_id' \
                  ' WHERE f.pid = %s'
            args = (pid, )
            cursor.execute(sql, args)
            rows = cursor.fetchall()
            pledges = Helper.db_rows_to_dict(funding_attrs, rows)
            context['pledges'] = pledges
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/projectList/')

    with connection.cursor() as cursor:
        try:
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
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/projectList/')

    return render(request, 'project_details.html', context=context)


def login(request):
    response = render(request, 'login.html', context=None)

    if 'session_id' in request.COOKIES:
        with connection.cursor() as cursor:
            try:
                sql = 'SELECT 1 FROM sessions WHERE session_id = %s'
                args = (request.COOKIES['session_id'], )
                cursor.execute(sql, args)
                row = cursor.fetchone()
                if row is not None:
                    messages.add_message(request, messages.ERROR, ErrorMessages.ALREADY_LOGGED_IN)
                    return redirect('/')
                else:
                    # session_id is in COOKIES, but it is an invalid one. So we delete it.
                    response.delete_cookie('session_id')
            except:
                messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
                return response

    return response


def add_new_user(request):
    return render(request, 'add_new_user.html', context=None)


def store_user(request):
    with connection.cursor() as cursor:
        try:
            sql = 'INSERT INTO users(user_email, password, name, role) VALUES (%s, %s, %s, \'user\')'
            args = (request.POST['user_email'], request.POST['password'], request.POST['name'])
            cursor.execute(sql, args)
            connection.commit()
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.USER_REGISTER_FAIL)

    return redirect('/userList/')


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


def attempt_login(request):
    if 'session_id' in request.COOKIES:
        messages.add_message(request, messages.ERROR, ErrorMessages.ALREADY_LOGGED_IN)
        redirect('/')

    # Validate login credentials
    if 'user_email' not in request.POST or 'password' not in request.POST:
        messages.add_message(request, messages.ERROR, ErrorMessages.MISSING_DATA)
        return redirect('/')
    with connection.cursor() as cursor:
        try:
            sql = 'SELECT user_id, password FROM users WHERE user_email = %s'
            args = (request.POST['user_email'], )
            cursor.execute(sql, args)
            rows = cursor.fetchall()
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/')
    if len(rows) == 0:
        messages.add_message(request, messages.ERROR, ErrorMessages.WRONG_CREDENTIALS)
        return redirect('/')

    user_id, password = rows[0]
    if password != request.POST['password']:
        messages.add_message(request, messages.ERROR, ErrorMessages.WRONG_CREDENTIALS)
        return redirect('/')

    # Construct new session
    session_id = uuid.uuid4()

    response = redirect('/')
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "INSERT INTO sessions (session_id, user_id) VALUES ('%s', %s)"
                % (session_id,
                   user_id)
            )
            connection.commit()
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.LOGIN_FAILED)
        else:
            response.set_cookie('session_id', session_id)

    return response


def logout(request):
    if 'session_id' not in request.COOKIES:
        return redirect('/')

    session_id = request.COOKIES['session_id']

    response = redirect('/')
    with connection.cursor() as cursor:
        try:
            sql = 'DELETE FROM sessions WHERE session_id = %s'
            args = (session_id, )
            cursor.execute(sql, args)
            connection.commit()
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.LOGOUT_FAILED)
        else:
            response.delete_cookie('session_id')

    return response


def inject_user_data(request, context):
    if 'session_id' not in request.COOKIES:
        return

    session_id = request.COOKIES['session_id']

    with connection.cursor() as cursor:
        try:
            user_attrs = ['user_email', 'user_id', 'name', 'role']
            sql = 'SELECT ' + ', '.join(['u.' + attr for attr in user_attrs]) + \
                  ' FROM users u NATURAL JOIN sessions s WHERE s.session_id = %s'
            args = (session_id, )
            cursor.execute(sql, args)
            rows = cursor.fetchall()
            users = Helper.db_rows_to_dict(user_attrs, rows)
        except:
            return

    if len(users) == 0:
        return

    context['user_email'] = users[0]['user_email']
    context['user_id'] = users[0]['user_id']
    context['role'] = users[0]['role']
    context['user_name'] = users[0]['name']


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

    return redirect('/projectDetails/?pid=%s' % pid)


def add_funding(request):
    pid = request.GET['pid']
    amount = request.POST['amount']

    with connection.cursor() as cursor:
        try:
            project_attrs = ['title']
            sql = 'SELECT title FROM projects WHERE pid = %s'
            args = (pid,)
            cursor.execute(sql, args)
            rows = cursor.fetchall()
            projects = Helper.db_rows_to_dict(project_attrs, rows)
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/projectDetails/?pid=%s' % pid)

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
    amount = request.GET['amount', None]

    if pid is None:
        messages.add_message(request, messages.ERROR, ErrorMessages.PROJECT_NOT_FOUND)
        return redirect('/')
    if 'amount' is None:
        messages.add_message(request, messages.ERROR, ErrorMessages.MISSING_DATA)
        return redirect('/projectDetails/?pid=%s' % pid)
    if 'user_id' not in context:
        messages.add_message(request, messages.ERROR, ErrorMessages.UNAUTHORIZED)
        return redirect('/projectDetails/?pid=%s' % pid)

    with connection.cursor() as cursor:
        try:
            sql = 'SELECT 1 FROM funding WHERE user_id = %s AND pid = %s'
            args = (context['user_id'], pid)
            cursor.execute(sql, args)
            rows = cursor.fetchall()
            funding_exists = len(rows) > 0
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/projectDetails/?pid=%s' % pid)

    if funding_exists:
        with connection.cursor() as cursor:
            try:
                sql = 'UPDATE funding SET amount = %s WHERE user_id = %s AND pid = %s'
                args = (amount, context['user_id'], pid)
                cursor.execute(sql, args)
                connection.commit()
            except:
                messages.add_message(request, messages.ERROR, ErrorMessages.PLEDGE_FAIL)
                return redirect('/projectDetails/?pid=%s' % pid)
    else:
        with connection.cursor() as cursor:
            try:
                sql = 'INSERT INTO funding (user_id, pid, amount) VALUES (%s, %s, %s)'
                args = (context['user_id'], pid, amount)
                cursor.execute(sql, args)
                connection.commit()
            except:
                messages.add_message(request, messages.ERROR, ErrorMessages.PLEDGE_FAIL)
                return redirect('/projectDetails/?pid=%s' % pid)

    return redirect('/projectDetails/?pid=%s' % pid)


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

    context['me'] = (str(user_id) == str(context['user_id']))

    return render(request, 'user_details.html', context=context)


def make_admin(request):
    context = dict()
    inject_user_data(request, context)
    user_id = request.GET.get('user_id', None)

    # Only an admin can elevate others to admin status.
    if (user_id is None) or ('role' not in context) or (context['role'] != 'admin'):
        messages.add_message(request, messages.ERROR, ErrorMessages.UNAUTHORIZED)
        return redirect('/')

    with connection.cursor() as cursor:
        try:
            sql = 'UPDATE users SET role=\'admin\' WHERE user_id = %s'
            args = (user_id, )
            cursor.execute(sql, args)
            connection.commit()
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.MAKE_ADMIN_FAIL)
            return redirect('/userDetails/?user_id=%s' % user_id)

    return redirect('/userDetails/?user_id=%s' % user_id)


def revoke_admin(request):
    context = dict()
    inject_user_data(request, context)

    # An admin can only revoke his own admin status.
    if 'role' not in context or context['role'] != 'admin':
        messages.add_message(request, messages.ERROR, ErrorMessages.UNAUTHORIZED)
        return redirect('/')

    with connection.cursor() as cursor:
        try:
            sql = 'UPDATE users SET role=\'user\' WHERE user_id = %s'
            args = (context['user_id'],)
            cursor.execute(sql, args)
            connection.commit()
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.REVOKE_ADMIN_FAIL)
            return redirect('/userDetails/?user_id=%s' % context['user_id'])

    return redirect('/userDetails/?user_id=%s' % context['user_id'])


def projects_log(request):
    context = dict()
    inject_user_data(request, context)

    if 'role' not in context or context['role'] != 'admin':
        messages.add_message(request, messages.ERROR, ErrorMessages.UNAUTHORIZED)
        return redirect('/')

    with connection.cursor() as cursor:
        log_args = ['pid', 'operation',
                    'prev_title', 'prev_description', 'prev_start_date', 'prev_end_date', 'prev_target_fund', 'prev_photo_url',
                    'next_title', 'next_description', 'next_start_date', 'next_end_date', 'next_target_fund', 'next_photo_url',
                    'transaction_date']
        sql = 'SELECT ' + ', '.join(log_args) + ' FROM projects_log ORDER BY transaction_date DESC'
        cursor.execute(sql)
        rows = cursor.fetchall()
        logs = Helper.db_rows_to_dict(log_args, rows)
        context['logs'] = logs

    return render(request, "projects_log.html", context=context)


def role_log(request):
    context = dict()
    inject_user_data(request, context)

    if 'role' not in context or context['role'] != 'admin':
        messages.add_message(request, messages.ERROR, ErrorMessages.UNAUTHORIZED)
        return redirect('/')

    with connection.cursor() as cursor:
        log_args = ['user_id', 'prev_role', 'next_role', 'transaction_date']
        sql = 'SELECT ' + ', '.join(log_args) + ' FROM role_log ORDER BY transaction_date DESC'
        cursor.execute(sql)
        rows = cursor.fetchall()
        logs = Helper.db_rows_to_dict(log_args, rows)
        context['logs'] = logs

    return render(request, "role_log.html", context=context)