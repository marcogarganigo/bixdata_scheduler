from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm
from apscheduler.schedulers.background import BackgroundScheduler
from django.db import connection

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


@login_required(login_url='/login/')
def get_render_logout(request):
    logout(request)
    return render(request, 'login.html')


@user_passes_test(lambda u: u.is_superuser)
def get_render_index(request):
    datas = {
        'dealuser': 'donato',
        'dealname': 'test'
    }

    def data():
        dealuser_toinsert = datas['dealuser']
        dealname_toinsert = datas['dealname']

        # check if the data already exists in the db and if not, insert it
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO test (dealname, dealuser) VALUES (%s, %s)", [dealuser_toinsert, dealname_toinsert])
        print('data added')

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
        else:
            status = 'Stopped'

        return render(request, 'index.html', {'datas': datas, 'status': status})

    def stopAct1():
        print('--function stopped--')
        scheduler.remove_job('data')

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

    return render(request, 'index.html', {'datas': datas, 'status': status})
