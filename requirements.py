import sys
import os
password=sys.argv[1]
username=sys.argv[2]
servername=sys.argv[3]
os.system(f"echo {password}|sudo -S apt install python3-pip")
os.system("pip3 install psutil")
os.system("pip3 install pandas")
os.system("pip3 install sklearn")
os.system("pip3 install keras")
os.system("pip3 install https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow_cpu-2.3.0-cp38-cp38-manylinux2010_x86_64.whl")
os.system("pip3 install requests")
os.system(f"echo {password}|sudo -S python3 app.py &")





