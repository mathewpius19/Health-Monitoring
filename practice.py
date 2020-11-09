import psutil

virtual_memory = psutil.virtual_memory()
freePercent = (virtual_memory.free/virtual_memory.total)*100
print(freePercent)

disk_usage=psutil.disk_usage('/')
free_Percnt=(disk_usage.free/disk_usage.total)*100
print(free_Percnt)

ctime = psutil.cpu_times()
cpuTotal = (ctime.user + ctime.system)
print(cpuTotal)

percent = psutil.cpu_times_percent()
print(percent)

bytesRead = psutil.disk_io_counters() 
print(bytesRead.read_bytes)