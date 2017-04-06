from django.db import connection, IntegrityError
from django.contrib import messages
from django.shortcuts import render, redirect

from utils import inject_user_data, ErrorMessages


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
