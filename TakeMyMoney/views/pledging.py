from django.db import connection, IntegrityError
from django.contrib import messages
from django.shortcuts import render, redirect

from utils import Helper, inject_user_data, ErrorMessages


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
    inject_user_data(request, context)

    return render(request, 'add_funding.html', context=context)


def store_funding(request):
    context = dict()
    inject_user_data(request, context)
    pid = request.GET.get('pid', None)
    amount = request.GET.get('amount', None)

    if pid is None:
        messages.add_message(request, messages.ERROR, ErrorMessages.PROJECT_NOT_FOUND)
        return redirect('/')
    if amount is None:
        messages.add_message(request, messages.ERROR, ErrorMessages.MISSING_DATA)
        return redirect('/projectDetails/?pid=%s' % pid)
    if 'user_id' not in context:
        messages.add_message(request, messages.ERROR, ErrorMessages.UNAUTHORIZED)
        return redirect('/projectDetails/?pid=%s' % pid)
    try:
        int(amount)
    except:
        messages.add_message(request, messages.ERROR, ErrorMessages.MISSING_DATA)
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
        if int(amount) > 0:
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
                    sql = 'DELETE FROM funding WHERE user_id = %s AND pid = %s'
                    args = (context['user_id'], pid)
                    cursor.execute(sql, args)
                    connection.commit()
                except:
                    messages.add_message(request, messages.ERROR, ErrorMessages.PLEDGE_FAIL)
                    return redirect('/projectDetails/?pid=%s' % pid)
    elif int(amount) > 0:
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
