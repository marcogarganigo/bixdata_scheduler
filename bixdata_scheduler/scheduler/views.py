from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm
from apscheduler.schedulers.background import BackgroundScheduler
from django.db import connection
import requests
import time
import json
from datetime import datetime


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# Scheduler
scheduler = BackgroundScheduler()
scheduler.start()


def get_render_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def get_render_logout(request):
    logout(request)
    return redirect('login')


@user_passes_test(lambda u: u.is_superuser, login_url='login')
def get_render_index(request):
    datas = {
        'dealuser': 'donato',
        'dealname': 'test'
    }

    def data():
        sync_company()

    def sync_company():
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO user_system_log(date, hour, note, function) values (now(), now(), 'ok', 'funzionetest2')")

    def action1():
        print('--function started--')
        job = scheduler.get_job('data')
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, status, active FROM sys_scheduler_tasks")
            rows = cursor.fetchall()
            for row in rows:
                id = row[0]
                status = row[1]
                active = row[2]
                if status == 'active':
                    cursor.execute("UPDATE sys_scheduler_tasks SET active = 1 WHERE id = %s", [id])
                else:
                    print('non attivata')
        if job is None:
            scheduler.add_job(data, 'interval', seconds=5, id='data')
            is_active = True
        else:
            is_active = job.next_run_time is not None

        # Create a list to hold log messages
        log = []

        # Add log messages during execution of background job
        log.append('Curl request started')
        url = 'https://swissbix.freshdesk.com/api/v2/tickets/1007806'
        auth = ('CKSOYa2wpqgL1xTUQTHq', 'X')
        headers = {'Content-Type': 'application/json'}
        response = requests.get(url, headers=headers, auth=auth)
        log.append(f'Curl request completed with status code {response.status_code}')

        # Update the status variable based on whether the job is active or not
        if is_active:
            status_func = 'Running'
        else:
            status_func = 'Stopped'

        with connection.cursor() as cursor:
            cursor.execute("SELECT funzione, id, status, active FROM sys_scheduler_tasks")
            rows = dictfetchall(cursor)
            data_functions = {'functions': rows}
            print(data_functions)

        # Pass log messages to template context
        return render(request, 'index.html',
                      {'datas': datas, 'status_func': status_func, 'data_functions': data_functions, 'log': log})

    def stopAct1():
        print('--function stopped--')
        scheduler.remove_job('data')
        # Set active to 0
        with connection.cursor() as cursor:
            cursor.execute("UPDATE sys_scheduler_tasks SET active = 0")

    if request.method == 'POST':
        if 'start' in request.POST:
            return action1()
        elif 'stop' in request.POST:
            stopAct1()

    # If the request is not a POST request, or if the 'start' or 'stop' button was not clicked,
    # simply render the index template with the current status
    job = scheduler.get_job('data')
    if job is None:
        status_func = 'Stopped'
    elif job.next_run_time is not None:
        status_func = 'Running'
    else:
        status_func = 'Stopped'

    with connection.cursor() as cursor:
        cursor.execute("SELECT funzione, id, status, active FROM sys_scheduler_tasks")
        rows = dictfetchall(cursor)
        data_functions = {

            'functions': rows
        }
        print(data_functions)

    return render(request, 'index.html', {'datas': datas, 'status_func': status_func, 'data_functions': data_functions})


def change_status(request):
    if request.method == 'POST':
        status = request.POST.get('status')
        id = request.POST.get('id')
        if status == 'active':
            status = 'inactive'
        else:
            status = 'active'

        with connection.cursor() as cursor:
            cursor.execute("UPDATE sys_scheduler_tasks SET status = %s WHERE id = %s", [status, id])

        with connection.cursor() as cursor:
            cursor.execute("SELECT funzione, status, active FROM sys_scheduler_tasks")
            rows = dictfetchall(cursor)
            data_functions = {

                'functions': rows
            }
            print(data_functions)

    return render(request, 'index.html', data_functions)


def get_log(request):
    function = request.POST.get('function_name')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user_system_log where function = %s", [function])
        rows = cursor.fetchall()

        text = ""
        for row in rows:
            text += ",".join(str(value) for value in row)

        text = text.split(",")[-4:]
        text = " ".join(text)

        data_log = {
            'log': text
        }
        print(text)

        return JsonResponse(data_log, safe=False)


