import os
import sys
import time
import platform

from http.server import BaseHTTPRequestHandler, HTTPServer
from subprocess import Popen, PIPE
from win32com.client import GetObject


def checkProcess(processName):

    if platform.system().lower == "windows" :
        WMI = GetObject('winmgmts:')
        pList = []
        processes = WMI.instancesOf('Win32_Process')
        for process in processes:
            if processName == process.Properties_('Name').Value:
                return True
        return False
    else:
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        for pid in pids:
            try:
                cmdLine = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read().split(bytes('\0','utf-8'))
                if len(cmdLine) > 1:
                    process = cmdLine[0].split(bytes(' ','utf-8'))[0].split(bytes('/','utf-8'))[-1]
                    if process == bytes(processName, 'utf-8'):
                        FLAG = True
                        return True
                else:  
                    continue

            except IOError: # proc has already terminated
                continue
        return False



class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if checkProcess(process) is True:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(("<html><body><p>%s is alive.</p>" % process), "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(("<html><body><p>%s is not alive.</p>" % process), "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))
            

hostName = ""
hostPort = 80

process = sys.argv[1] 

myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
