from django.db import connection


class Helper:
    @staticmethod
    def db_rows_to_dict(attrs, rows):
        """
        Convert DB rows to a list of dicts
        NOTE: you must ensure that the sequence in attrs matches that of the rows

        :param attrs: Attributes to be SELECTed
        :param rows: rows returned by the db
        :return: list of dicts
        """
        objects = []
        for row in rows:
            object = {}
            for i in range(len(attrs)):
                object[attrs[i]] = row[i]
            objects.append(object)
        return objects


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

    if context['role'] == 'admin':
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