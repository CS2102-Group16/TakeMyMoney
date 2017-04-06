from django.db import connection, IntegrityError
from django.contrib import messages
from django.shortcuts import render, redirect
import uuid

from utils import ErrorMessages


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
            return redirect('/')

    return attempt_login(request)


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
