import psutil
import requests
import time
import sys

PORT = 4400

flask_URL = f'http://localhost:{PORT}/report'

try:
    SERVER_NAME=sys.argv[1]
    USER_NAME=sys.argv[2]
    print(SERVER_NAME,USER_NAME)
except:
    print("Invalid Entry")
    sys.exit()
       

def get_health(): 
    
    print('generating health report')

    cpu_percent = psutil.cpu_percent(interval=2.0)
    
    disk_usage = psutil.disk_usage("/")
    freePercnt=((disk_usage.free/disk_usage.total)*100)
    ctime = psutil.cpu_times()
    epochTime = time.time()
    cpuTotal = (ctime.user + ctime.system)
    virtualMemory = psutil.virtual_memory() 
    memoryFree = (virtualMemory.free /virtualMemory.total)*100
    bytesRead = psutil.disk_io_counters()   

    # The keys in this dict should match the db cols
    report = dict (
        USER_NAME=USER_NAME,
        SERVER_NAME=SERVER_NAME,
        epoch_time = round(epochTime,2),
        cpupercent = cpu_percent,
        cpu_total = round(cpuTotal,2),
        free_Percnt = round(freePercnt,2),
        memory_Free = round(memoryFree,2),
        bytes_read = bytesRead.read_bytes
        )

    return report
if __name__=='__main__':
    print("Reporting program is running and communicating with app.py at {PORT}...")

    while True:
        report = get_health()
        print("Done generating report. Sending report to flask emitting server.")
        r1 = requests.post(flask_URL, json=report)
        time.sleep(10)
        # print(report)
