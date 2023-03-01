from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm
from apscheduler.schedulers.background import BackgroundScheduler
from django.db import connection
import requests

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
    return render(request, 'login.html')


@user_passes_test(lambda u: u.is_superuser, login_url='login')
def get_render_index(request):
    datas = {
        'dealuser': 'donato',
        'dealname': 'test'
    }

    def data():
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM sys_scheduler_tasks WHERE id = 2")
            row = cursor.fetchone()
            print(row)

    def action1():
        print('--function started--')
        job = scheduler.get_job('data')
        if job is None:
            scheduler.add_job(data, 'interval', seconds=5, id='data')
            is_active = True
        else:
            is_active = job.next_run_time is not None

        # Update the status variable based on whether the job is active or not
        if is_active:
            status = 'Running'
            # Set active to 1
            with connection.cursor() as cursor:
                cursor.execute("UPDATE sys_scheduler_tasks SET active = 1 WHERE id = 2")
        else:
            status = 'Stopped'

        # Curl request
        url = 'https://swissbix.freshdesk.com/api/v2/tickets/1007806'
        auth = ('CKSOYa2wpqgL1xTUQTHq', 'X')
        headers = {'Content-Type': 'application/json'}
        response = requests.get(url, headers=headers, auth=auth)
        print(response.text)

        return render(request, 'index.html', {'datas': datas, 'status': status})

    def stopAct1():
        print('--function stopped--')
        scheduler.remove_job('data')
        # Set active to 0
        with connection.cursor() as cursor:
            cursor.execute("UPDATE sys_scheduler_tasks SET active = 0 WHERE id = 2")

    if request.method == 'POST':
        if 'start' in request.POST:
            return action1()
        elif 'stop' in request.POST:
            stopAct1()

    # If the request is not a POST request, or if the 'start' or 'stop' button was not clicked,
    # simply render the index template with the current status
    job = scheduler.get_job('data')
    if job is None:
        status = 'Stopped'
    elif job.next_run_time is not None:
        status = 'Running'
    else:
        status = 'Stopped'


    with connection.cursor() as cursor:
        cursor.execute("SELECT funzione, status, active FROM sys_scheduler_tasks")
        rows = cursor.fetchall()
        nomi = [row[0] for row in rows]
        stati = [row[1] for row in rows]
        attivo = [row[2] for row in rows]
        data_functions = {
            'nome': nomi,
            'stato': stati,
            'attivo': attivo
            }

        context = {'data_functions': data_functions}

    return render(request, 'index.html', {'datas': datas, 'status': status, **context})



def change_status(request):



    return render(request, 'index.html')