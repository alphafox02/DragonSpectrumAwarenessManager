import threading
import tkinter as tk
from tkinter import filedialog
import subprocess
import os
# create window object
root = tk.Tk()
root.title('Map Manager')
# position window in center of screen
windowWidth = root.winfo_reqwidth()
windowHeight = root.winfo_reqheight()
positionRight = int(root.winfo_screenwidth()/2 - windowWidth/2)
positionDown = int(root.winfo_screenheight()/2 - windowHeight/2)
root.geometry("+{}+{}".format(positionRight, positionDown))

# global variables
start_geoserver_thread_started = False
start_df_aggregator_thread_started = False
start_photon_thread_started = False
db_file_global = ""


def create_geoserver_thread():
    start_geoserver_thread = threading.Thread(target=start_geoserver)
    start_geoserver_thread.start()


def create_df_aggregator_thread():
    start_df_aggregator_thread = threading.Thread(target=start_df_aggregator)
    start_df_aggregator_thread.start()


def create_photon_thread():
    start_photon_thread = threading.Thread(target=start_photon)
    start_photon_thread.start()


def start_photon():
    global start_photon_thread_started
    photon_status.config(text="Photon Map Started", fg="green")
    if start_photon_thread_started == False:
        start_photon_thread_started = True
        os.chdir('/usr/src/photonmap/html/')
        subprocess.call(['python3', '-m', 'http.server', '8082'])
    else:
        print("Photon Map already started")


def stop_photon():
    photon_status.config(text="Photon Map Stopped", fg="red")
    find = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
    grep = subprocess.Popen(['grep', 'http.server'],
                            stdin=find.stdout, stdout=subprocess.PIPE)
    find.stdout.close()
    output = grep.communicate()[0]
    output = output.decode("utf-8")
    output = output.split()
    subprocess.call(['kill', '-9', output[1]])


def start_geoserver():
    global start_geoserver_thread_started
    statusLabel.config(text="GeoServer Started", fg="green")
    if start_geoserver_thread_started == False:
        start_geoserver_thread_started = True
        os.chdir('/usr/src/geoserver/bin')
        subprocess.call(['sudo', 'sh', 'startup.sh'])
    else:
        print("GeoServer already started")


def stop_geoserver():
    statusLabel.config(text="GeoServer Stopped", fg="red")
    os.chdir('/usr/src/geoserver/bin')
    subprocess.call(['sudo', 'sh', 'shutdown.sh'])


def launch_geoserver_interface():
    if statusLabel["text"] == "GeoServer Started":
        subprocess.call(['firefox', 'localhost:8080/geoserver'])
    else:
        statusLabel.config(text="Start GeoServer First", fg="red")


def launch_dfa_interface():
    subprocess.call(['firefox', 'localhost:8081/'])


def launch_photon_interface():
    subprocess.call(['firefox', 'localhost:8082/'])


def create_database():
    db_file = filedialog.asksaveasfilename(initialdir="~")
    if db_file:
        subprocess.call(['touch', db_file])
    elif db_file == "":
        print("No file selected")


def select_database():
    global db_file_global
    db_file = filedialog.askopenfilename(initialdir="~")
    if db_file:
        db_file_global = db_file
        print(db_file_global)
    elif db_file == "":
        print("No file selected")


def start_df_aggregator():
    global start_df_aggregator_thread_started
    dfa_status.config(text="DF-Aggregator Started", fg="green")
    # this is not working as intended, meaning it will start df-aggregator even if no database is selected
    if db_file_global == "":
        print("No database selected")
        # exit function
        return
    elif db_file_global != "" and start_df_aggregator_thread_started == False:
        start_df_aggregator_thread_started = True
        os.chdir('/usr/src/df-aggregator')
        subprocess.call(
            ['python3', '/usr/src/df-aggregator/df-aggregator.py', '-d', db_file_global, '-o', '--port', '8081'])
    elif db_file_global != "" and start_df_aggregator_thread_started == True:
        print("DF-Aggregator already started")


def stop_df_aggregator():
    dfa_status.config(text="DF-Aggregator Stopped", fg="red")
    # find process id of df-aggregator with ps aux | grep df-aggregator
    # kill process with kill -9 <process id>
    find = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
    grep = subprocess.Popen(['grep', 'df-aggregator'],
                            stdin=find.stdout, stdout=subprocess.PIPE)
    find.stdout.close()
    output = grep.communicate()[0]
    output = output.decode("utf-8")
    output = output.split()
    subprocess.call(['kill', '-9', output[1]])


def edit_photon_layers():
    subprocess.call(['sudo', 'gedit', '/usr/src/photonmap/html/index.html'])


def edit_dfa_layers():
    subprocess.call(
        ['sudo', 'gedit', '/usr/src/df-aggregator/views/cesium.tpl'])


start_geoserver_button = tk.Button(
    root, text="Start GeoServer", command=create_geoserver_thread)
start_geoserver_button.grid(row=1, column=0, padx=5, pady=5)

stop_geoserver_button = tk.Button(
    root, text="Stop GeoServer", command=stop_geoserver)
stop_geoserver_button.grid(row=1, column=1, padx=5, pady=5)

launch_geoserver_button = tk.Button(
    root, text="GeoSever Configuration", command=launch_geoserver_interface)
launch_geoserver_button.grid(row=1, column=2, padx=5, pady=5)

statusLabel = tk.Label(root, text="GeoServer Stopped", fg="red")
statusLabel.grid(row=0, columnspan=2, padx=5, pady=5)

dfa_status = tk.Label(root, text="DF-Aggregator Stopped", fg="red")
dfa_status.grid(row=2, columnspan=2, padx=5, pady=5)

photon_status = tk.Label(root, text="Photon Map Stopped", fg="red")
photon_status.grid(row=5, columnspan=2, padx=5, pady=5)

create_database_button = tk.Button(
    root, text="Create Database", command=create_database)
create_database_button.grid(row=4, column=0, padx=5, pady=5)

select_database_button = tk.Button(
    root, text="Select Database", command=select_database)
select_database_button.grid(row=4, column=1, padx=5, pady=5)

start_df_aggregator_button = tk.Button(
    root, text="Start DF-Aggregator", command=create_df_aggregator_thread)
start_df_aggregator_button.grid(row=3, column=0, padx=5, pady=5)

stop_df_aggregator_button = tk.Button(
    root, text="Stop DF-Aggregator", command=stop_df_aggregator)
stop_df_aggregator_button.grid(row=3, column=1, padx=5, pady=5)

launch_dfa_button = tk.Button(
    root, text="DF-Aggregator Interface", command=launch_dfa_interface)
launch_dfa_button.grid(row=3, column=2, padx=5, pady=5)

start_photon_button = tk.Button(
    root, text="Start Photon Map", command=create_photon_thread)
start_photon_button.grid(row=6, column=0, padx=5, pady=5)

stop_photon_button = tk.Button(
    root, text="Stop Photon Map", command=stop_photon)
stop_photon_button.grid(row=6, column=1, padx=5, pady=5)

launch_photon_button = tk.Button(
    root, text="Photon Map Interface", command=launch_photon_interface)
launch_photon_button.grid(row=6, column=2, padx=5, pady=5)

edit_photon_layers_button = tk.Button(
    root, text="Edit Photon Map Layers", command=edit_photon_layers)
edit_photon_layers_button.grid(row=7, column=2, padx=5, pady=5)

edit_dfa_layers_button = tk.Button(
    root, text="Edit DF-Aggregator Layers", command=edit_dfa_layers)
edit_dfa_layers_button.grid(row=4, column=2, padx=5, pady=5)

# run window
if __name__ == "__main__":
    root.mainloop()

