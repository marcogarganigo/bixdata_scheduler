from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
import os
import customtkinter as ctk

root = ctk.CTk()
root.title("Bixdata Scheduler")
root.geometry("400x200")


def data():
    print(datetime.now())


scheduler = BackgroundScheduler()
scheduler.start()

status_label = ctk.CTkLabel(root, text="Status: inactive", bg_color="#ff2646")
status_label.place(x=50, y=150)


def action1():
    global scheduler
    print('--function started--')
    status_label.configure(text="Status: active")
    status_label.configure(bg_color="green")  # set label background to green
    scheduler.add_job(data, 'interval', seconds=5, id='data')


def stopAct1():
    global scheduler
    status_label.configure(text="Status: inactive")
    status_label.configure(bg_color="#ff2646")  # set label background to red
    scheduler.remove_job('data')
    print('--function stopped--')


act1_start = ctk.CTkButton(root, text="Start Action 1", command=action1)
act1_stop = ctk.CTkButton(root, text="Stop Action 1", command=stopAct1)

act1_start.place(x=50, y=50)
act1_stop.place(x=50, y=100)

root.mainloop()

scheduler.shutdown()
