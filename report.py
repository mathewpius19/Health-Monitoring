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

    
    epochTime = time.time()
    bytesFromDisk = psutil.disk_io_counters()  
    bytesFromNet = psutil.net_io_counters() 

    # The keys in this dict should match the db cols
    report = dict (
        USER_NAME=USER_NAME,
        SERVER_NAME=SERVER_NAME,
        epoch_time = round(epochTime,2),
        bytes_read = bytesFromDisk.read_bytes,
        bytes_write = bytesFromDisk.write_bytes,
        bytes_sent = bytesFromNet.bytes_sent,
        bytes_recv = bytesFromNet.bytes_recv,
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