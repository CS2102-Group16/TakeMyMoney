from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db import connection, IntegrityError
from django.contrib import messages
from django.shortcuts import render, redirect

from utils import Helper, inject_user_data, ErrorMessages


def project_list(request):
    context = dict()
    inject_user_data(request, context)
    filtering = request.GET.get('filter', None)

    if filtering == 'search' and 'search' in request.POST:
        search_input = request.POST['search']

        with connection.cursor() as cursor:
            try:
                project_attrs = ['title', 'description', 'photo_url', 'target_fund', 'start_date', 'end_date', 'pid', 'category']
                # Hidden dragon, crouching input sanitization.
                args = ('%' + search_input + '%', '%' + search_input + '%')
                cursor.execute("SELECT p.title, p.description, p.photo_url, p.target_fund, p.start_date, p.end_date, p.pid,"
                               " string_agg(pc.category_name, ', ') FROM projects p"
                               " LEFT OUTER JOIN projects_categories pc ON pc.pid = p.pid"
                               " WHERE p.title ILIKE %s OR p.description ILIKE %s"
                               " GROUP BY p.pid"
                               " ORDER BY p.title", args)
                rows = cursor.fetchall()
                projects = Helper.db_rows_to_dict(project_attrs, rows)
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

        project_attrs = ['title', 'description', 'photo_url', 'target_fund', 'start_date', 'end_date', 'pid', 'category']
        query_str = "SELECT p.title, p.description, p.photo_url, p.target_fund, p.start_date, p.end_date, p.pid," \
                    " string_agg(pc.category_name, ', ') FROM projects p" \
                    " LEFT OUTER JOIN projects_categories pc ON p.pid = pc.pid" \
                    " GROUP BY p.pid" \
                    " ORDER BY p.title ASC"

        if 'category' in request.GET:
            category_name = request.GET['category']
            if not category_name == 'All':
                query_str = "SELECT p.title, p.description, p.photo_url, p.target_fund, p.start_date, p.end_date, p.pid," \
                            " string_agg(pc.category_name, ', ') FROM projects p" \
                            " NATURAL JOIN projects_categories pc" \
                            " GROUP BY p.pid" \
                            " EXCEPT" \
                            " SELECT p2.title, p2.description, p2.photo_url, p2.target_fund, p2.start_date, p2.end_date, p2.pid," \
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
            except:
                messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
                return redirect('/projectList/')

    paginator = Paginator(projects, 20)  # Show 20 projects per page

    page = request.GET.get('page')
    try:
        projects_in_page = paginator.page(page)
    except EmptyPage:
        projects_in_page = paginator.page(paginator.num_pages)
    except InvalidPage:
        projects_in_page = paginator.page(1)

    context['projects'] = projects_in_page.object_list
    context['page'] = projects_in_page

    return render(request, 'project_list.html', context=context)


def project_details(request):
    context = dict()
    inject_user_data(request, context)
    pid = request.GET.get('pid', None)

    if pid is None:
        messages.add_message(request, messages.ERROR, ErrorMessages.PROJECT_NOT_FOUND)
        return redirect('/')

    with connection.cursor() as cursor:
        try:
            project_attrs = ['title', 'description', 'target_fund', 'photo_url', 'start_date', 'end_date', 'pid', 'user_id']
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
            related_project_attrs = ['title', 'description', 'target_fund', 'photo_url', 'start_date', 'end_date', 'pid']
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

    with connection.cursor() as cursor:
        try:
            sql = 'SELECT sum(f.amount) FROM funding f WHERE f.pid = %s'
            args = (pid, )
            cursor.execute(sql, args)
            rows = cursor.fetchall()
            funded_amount = rows[0][0] or 0
            context['funded_amount'] = funded_amount
            context['funded_percentage'] = int(round(min(funded_amount * 100.0 / context['project']['target_fund'], 100.0)))
        except:
            messages.add_message(request, messages.ERROR, ErrorMessages.UNKNOWN)
            return redirect('/projectList/')

    return render(request, 'project_details.html', context=context)
