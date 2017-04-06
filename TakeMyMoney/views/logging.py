from django.db import connection, IntegrityError
from django.contrib import messages
from django.shortcuts import render, redirect

from utils import Helper, inject_user_data, ErrorMessages


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
