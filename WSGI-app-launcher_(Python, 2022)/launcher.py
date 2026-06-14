#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import re
import subprocess
import webbrowser
import tarfile
import time
import socket
try:
    if sys.version_info[0] == 2:
        import Tkinter as tk
        from Tkinter import RIGHT, LEFT, BOTH, X, Y, END
        import tkMessageBox as MessageBox
        import tkFileDialog as filedialog
    elif sys.version_info[0] == 3:
        import tkinter as tk
        from tkinter import RIGHT, LEFT, BOTH, X, Y, END
        import tkinter.messagebox as MessageBox
        import tkinter.filedialog as filedialog
    else:
        print ("Warning. Your Python version unsupported.")
except ImportError:
    print("Tkinter not founded. Setup Tkinter module before:")
    print("Linux Ubuntu/Debian: apt-get install python-tk")
    print("Linux CentOS/RHEL: yum -y install tkinter")
    sys.exit(1)
try:
    if sys.version_info[0] == 2:
        import ConfigParser as configparser
    elif sys.version_info[0] == 3:
        import configparser
except ImportError:
    print ("Config parser not ready for use. Install Config Parser module.")
try:
    if sys.version_info[0] == 2:
        from urllib2 import urlopen
    elif sys.version_info[0] == 3:
        from urllib.request import urlopen
except ImportError:
    print ("Urllib2 or urllib.request not found. Install Urllib module.")

# Encoding fix
if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf8')

__version__ = '0.1 [15-May-2018]'
__about__ = """
A simple wsgi app launcher for python microframeworks, allows you to manage the project on a local server. 
This application was not developed for industrial applications, only for localhost and test servers
Uses standard modules and Tkinter GUI."""
__license__ = "TBSD-2-Clause License. Copyright (c) 2018 <ins1x>"
asciiartlogo = """
                         _                        _                
     /\                 | |                      | |               
    /  \   _ __  _ __   | | __ _ _   _ _ __   ___| |__   ___ _ __  
   / /\ \ | '_ \| '_ \  | |/ _` | | | | '_ \ / __| '_ \ / _ \ '__| 
  / ____ \| |_) | |_) | | | (_| | |_| | | | | (__| | | |  __/ |    
 /_/    \_\ .__/| .__/  |_|\__,_|\__,_|_| |_|\___|_| |_|\___|_|    
          | |   | |                                                
          |_|   |_|                                                                                                         
"""
# Show CLI startup message
STARTUP_MESSAGE = "\n".join([str(asciiartlogo), str(__about__), (__license__), "\n"])
print (STARTUP_MESSAGE)
#print (asciiartlogo)
# CAUTION: Do not change the variable here.
# Automatically generated depending on the environment or from the config.
APP_TITLE = "Simple launcher for python web applications"
# Contains a header with the launcher version, platform, python version
LAUNCHER_RUN_ENV = "".join(["Launcher build: ", str(__version__), " Python: ", str(sys.version_info[0]), ".x ", str(sys.platform)])
# Logfile size in bytes. Default 1048576 bytes = 1 MB
MAX_LOG_SIZE = 1048576
# Scan by default 30 lines
MAX_PARSING_LINES = 30
# Settings file path. Default script run directory file settings.cfg
configfile = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "settings.cfg")
# Do not change host here!
LOCALHOST = "127.0.0.1"
# Main Tkinter window size
MAIN_WINDOW_SIZE = "720x480"
# Launcher run time
START_TIME = time.time()

def framework_parsing(appdir):
    """
    Determines which framework is used.
    Return array [framework as str, filepath as path]
    """
    patterns = {"Flask": "Flask",
    "Django": "Django",
    "CherryPy": "cherrypy",
    "KissPy": "kiss",
    "Tornado": "tornado",
    "Falcon": "falcon",
    "Bottle": "bottle",
    "Itty-Bitty": "itty"}
    # The parser does not process the files in this list
    excludelist = [str(sys.argv[0]), "__init__.py", "setup.py", "__version__.py", "__about__.py"]
    # If there are more than one app in the folder, the application from the root folder will be launched first. 
    # If there are several applications in the root folder, then automatically the first one will be selected according to the alphabetical order.
    def pywalker(path):
        """ Recursivelly search files at directory.
        Return Array of *.py files without current script. """
        os.chdir(path)
        fileslist = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.lower().endswith(".py"):
                    file = os.path.join(root, name)
                    file = os.path.normpath(file)
                    for ex_file in excludelist:
                        if file != ex_file:
                            fileslist.append(file)
        return fileslist

    def sub_search(file, value):
        """ Search modules in files by pattern."""
        importing = ["import ", "from "]
        try:
            os.chdir(appdir)
            line_numb = 1
            with open(file, "r") as f:
                for line in f.readlines():
                    line_numb += 1
                    for mask in importing:
                        pattern = "".join([mask, value])
                        patterncmp = re.compile(pattern)
                        match = patterncmp.search(line)
                        if match:
                            # debug print(" ".join([str(line_numb),str(line)]))
                            return True
                        if line_numb > MAX_PARSING_LINES:
                            break
        except OSError:
            print("OS Error. Can not access to files")
    # Alternately processes the files from the list and searches for modules
    fileslist = pywalker(appdir)
    for file in fileslist:
        for key, value in patterns.items():
            data = sub_search(file, value)
            if data:
                return key, file

def init_config(configfile):
    """
    Import data from configfile. If there is no config file, it uses the default values.
    Values are determined automatically based on the environment.
    """
    global appdir, appname, windowsize, appfullpath, devserverport, framework, backuppath, logfilepath
    global runned, use_configfile
    runned = False  # The status of the application
    try:
        config = configparser.ConfigParser()
        if os.path.isfile(configfile):
            use_configfile = True
            config.read(configfile)
            devserverport = config.get("app", "port")
            devserverport = int(devserverport)
            # 65535 - the max number of ports within the TCP / IP protocol stack.
            if devserverport > 65535:
                print("Port in the config is incorrectly specified. Max value 65535")
                print("by default set port 8080")
                devserverport = 8080
            appdir = config.get("app", "appdir")
            if not os.path.isdir(appdir):
                print("The < appdir > folder in the config is incorrectly specified")
                print("by default set the current startup folder will be installed.")
                appdir = os.path.abspath(os.path.dirname(sys.argv[0]))
            backuppath = config.get("app", "backuppath")
            if not os.path.isdir(backuppath):
                print("The < backuppath > folder in the config is incorrectly specified")
                print("by default set the current startup folder will be installed.")
                backuppath = os.path.join(appdir, "backup")
            logfilepath = config.get("app", "logfilepath")
            if not os.path.isdir(logfilepath):
                check_in_appdir = os.path.join(appdir, logfilepath)
                if not os.path.isfile(check_in_appdir):
                    print("The < logfilepath > folder in the config is incorrectly specified")
                    print("by default set the current startup folder - applauncher.log.")
                    logfilepath = "applauncher.log"
            windowsize = config.get("launcher", "windowsize")
            size = windowsize.split('x')
            for i in size:
                if type(i) != int:
                    windowsize = MAIN_WINDOW_SIZE
            framework = config.get("app", "framework")
            appname = config.get("app", "appname")
            appfullpath = os.path.join(appdir, appname)
            if not os.path.isfile(appfullpath):
                print("The < appfullpath > in the config is incorrectly specified")
                print("Many functions will not be available with this configuration")
            # end import config from config file
        else:
            # The code is executed only if it does not find the config
            use_configfile = False
            appdir = os.path.abspath(os.path.dirname(sys.argv[0]))
            parsing_result = framework_parsing(appdir)
            if parsing_result:
                framework = parsing_result[0]
                appfullpath = parsing_result[1]
            else:
                framework = "Unknown microframework"
                appfullpath = os.path.abspath(os.path.dirname(sys.argv[0]))
                print("Unknown microframework or directory is empty.")
            appname = os.path.basename(appfullpath)
            if framework == "Flask":
                devserverport = 5000
            elif framework == "CherryPy" or framework == "KissPy" or framework == "Bottle":
                devserverport = 8080
            elif framework == "Falcon" or framework == "Itty-Bitty" or framework == "Django":
                devserverport = 8000
            elif framework == "Torando":
                devserverport = 8888
            else:
                print("No app found. Select the app manually: App > Choose app")
                appname = None
                devserverport = 8000
                framework = "Unknown microframework"
            # Default window size
            windowsize = MAIN_WINDOW_SIZE
            # Log file destination
            logfilepath = os.path.join(appdir, "applauncher.log")
            # Output path for backups
            backuppath = os.path.join(appdir, "backup")
    except IOError:
        print ("IO Error. Can not access to config file.")
    except ValueError:
        print ("Broken configfile is incorrectly specified.Launcher started using standard values.")
        init_config("No configfile")
    except configparser.Error: 
        print ("Broken configfile. Launcher started using standard values.")
        init_config("Broken")
# Checking and importing data from the config
init_config(configfile)

def os_version():
    """ Return current OS version. Support linux/windows python 2-3. """
    # https://en.wikipedia.org/wiki/List_of_Microsoft_Windows_versions
    if sys.platform.startswith('win'):
        version = sys.getwindowsversion()
        if version[0] <= 4:
            os_distrver = "Windows ME-98 or older build"
        elif version[0] == 5 and version[1] == 0:
            os_distrver = "Windows NT build"
        elif version[0] == 5 and version[1] == 1:
            os_distrver = "Windows XP build"
        elif version[0] == 5 and version[1] == 2:
            os_distrver = "Windows XP x64 build"
        elif version[0] == 6 and version[1] == 0:
            os_distrver = "Windows Vista build"
        elif version[0] == 6 and version[1] == 1:
            os_distrver = "Windows 7 build"
        elif version[0] == 6 and version[1] == 2:
            os_distrver = "Windows 8 build"
        elif version[0] == 6 and version[1] == 3:
            os_distrver = "Windows 8.1 build"
        elif version[0] == 10:
            os_distrver = "Windows 10 build"
        else:
            os_distrver = "Windows build"
        # Return Windows version, build, service pack
        distr = " ".join([os_distrver, str(version[2]), str(version[4])])
        return distr
    if sys.platform.startswith('lin'):
        # check /etc/issue if can't open use uname function
        try:
            with open("/etc/issue", "r") as issue:
                text = issue.readline()
                spl = text.split(" ")
                distr = " ".join([spl[0], spl[1], spl[2]])
                return distr
        except IOError:
            uname = list(os.uname())
            uname.pop(3)
            return (" ".join(uname))

# -------------------------- utils --------------------------------------
def edit_file(filepath):
    """ Open file in text editor. """
    try: 
        if sys.platform.startswith('win'):
            shellwin = subprocess.Popen(["notepad.exe", filepath])
        elif sys.platform.startswith('linux'):
            if os.path.isfile("/usr/bin/gedit"):
                gedit_proc = subprocess.Popen(["gedit", filepath])
            elif os.path.isfile("/usr/bin/kate"):
                kate_proc = subprocess.Popen(["kate", filepath])
            elif os.path.isfile("/usr/bin/kwriter"):
                kwriter_proc = subprocess.Popen(["kwriter", filepath])
            elif os.path.isfile("/usr/bin/leafpad"):
                leafpad_proc = subprocess.Popen(["leafpad", filepath])
            elif os.path.isfile("/usr/bin/mousepad"):
                mousepad_proc = subprocess.Popen(["mousepad", filepath])
            else:
                nano_proc = subprocess.Popen(["nano", filepath])
    except OSError:
        log("".join(["OS Error: Can not access to - ", filepath]))

def check_is_writeable(path):
    try:
        f = open(path, 'a')
    except IOError as e:
        raise RuntimeError("Error: '%s' isn't writable [%r]" % (path, e))
    f.close()

def as_root():
    """ Checking script has root-like privileges"""
    if sys.platform.startswith('linux'):
        user = os.getenv("SUDO_USER")
        if user is None:
            # print("This program need 'sudo'")
            return False
        else:
            return True

def walker(path):
    """Recursivelly search files at directory. Return Array of files"""
    os.chdir(path)
    fileslist = []
    for rootdir, dirs, files in os.walk(path):
        for name in files:
            fileslist.append(os.path.join(rootdir, name))
        for name in dirs:
            fileslist.append(os.path.join(rootdir, name))
    return fileslist

# -------------------------- LOG --------------------------------------
# The data container's log file
LOGCONTENT = []

def log(*args):
    global LOGCONTENT
    """ Writes line to the log GUI text field. """
    data = []
    for i in args: 
        data.append(str(i))
    data.insert(0, time.strftime("[%X-%x]"))
    data.append("\n")
    line = (" ".join(data))
    LOGCONTENT.append(line)
    logarea.insert('end', line)

def clear_log():
    logarea.delete("1.0", 'end')

def copy_log():
    logarea.event_generate("<<Copy>>")

def save_log():
    global LOGCONTENT
    try:
        output = str(logfilepath)
        with open(output, "a") as logfile:
            for line in LOGCONTENT:
                logfile.write(line)
            log('Log was saved: ', str(output))
    except IOError:
        log('IO Error. no access', str(output))

def save_as_log(event=None):
    global LOGCONTENT
    try:
        root.filename = filedialog.askdirectory(initialdir = os.getcwd(),
            title = "Save log as.")
        if root.filename:
            path = os.path.normpath(root.filename)
            output = os.path.join(path, "applauncher.log")
            with open(output, "a") as logfile:
                for line in LOGCONTENT:
                    logfile.write(line)
                log('Log was saved: ', str(output))
    except IOError:
        log('IO Error. no access', str(output))

def load_log():
    try:
        edit_file(str(logfilepath))
    except IOError:
        log('IO Error. no access', str(logfilepath))

def remove_log():
    try:
        if os.path.isfile(logfilepath):
            os.remove(logfilepath)
            log("The log was deleted successfully")
    except OSError:
        log("OS Error. Can not access to file")

def check_log_overflow():
    global logsize
    try:
        if os.path.isfile(logfilepath):
            logsize = os.path.getsize(logfilepath)
            if logsize > MAX_LOG_SIZE:
                os.remove(logfilepath)
                log("The size of the logs has reached the maximum value, the logs are cleared")
    except OSError:
        log("OS Error. Can not access to log file")

def show_log():
    if logarea.winfo_viewable():
        global windowsize
        logarea.grid_remove()
        root.geometry("500x280")
    else:
        logarea.grid()
        root.geometry(windowsize)

def clear_shell_screen():
    if sys.platform.startswith('win'):
        subprocess.call('cls', shell=True)
    if sys.platform.startswith('lin'):
        subprocess.call('clear', shell=True)

# -------------------------- APP --------------------------------------
def start_app():
    """ Simple app runner. Launches the application if it is not running. """
    global runned
    os.chdir(appdir)
    if not os.path.isfile(appfullpath):
        log("Application is not found. Check configfile or choose app file. (App > Choose app)")
    try:
        if not runned:
            procapp = subprocess.Popen(["python", appfullpath])
            host = "".join(["http://127.0.0.1:", str(devserverport)])
            log("Try to run the application on", host, "using", framework)
            log("The current application status will be displayed in the console.")
            runned = True
            if sys.platform.startswith('win'):
                # check incorrect start on windows (check port if closed app run incorrectly)
                time.sleep(1)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((LOCALHOST, devserverport))
                s.close()
                log("Application started successfully.")
    except socket.error:
        s.close()
        log("Socket error. Can't run application. Check application configuration in", appname)
    except OSError:
        print("OSError. Something wrong. Can't run application")
        log("OSError. Something wrong. Can't run application")

def stop_app(port=devserverport):
    """ 
    Stop app. Kill app procs by pid. 
    Searches through netstat for the listening port
    """
    global runned
    if sys.platform.startswith('win'):
        command = "".join(['netstat -ano | findstr ', str(port)])
    if sys.platform.startswith('lin'):
        command = "".join(["lsof -i:", str(port), " -t"])
    launcher_pid = os.getpid()
    stdout = os.popen(command).read().split("\n")
    del stdout[-1] 
    if stdout:
        if sys.platform.startswith('lin'):
            for pid in stdout:
                kill = subprocess.Popen(["kill", "-9", pid])
                log("Stop app proc by PID ", str(pid))
        if sys.platform.startswith('win'):
            for line in stdout:
                listening = re.compile("LISTENING")
                match = listening.search(line)
                if match:
                    symb = list(line)
                    pid = "".join([symb[-4], symb[-3], symb[-2], symb[-1]]).replace(" ", "")
                    if pid:
                        prockill = subprocess.Popen(["taskkill", "/PID", pid, "/F"])
                        log("Stop app proc by PID ", str(pid))
        runned = False

def restart_app():
    """ Simple restart """
    if runned:
        stop_app()
        start_app()
    else:
        start_app()

def status_app():
    if runned:
        MessageBox.showinfo("App status", " ".join([appname,
            "runned. Use port", str(devserverport),
            "Project location:", str(appdir)]))
    else:
        MessageBox.showinfo("App status", "App not runned.")

def choose_app(silentmode=False):
    """
    Choose main app file. Used to manually configure the project.
    silentmode is bool. Specifies whether to output information to the log and show messages
    """
    global appfullpath, appdir, appname
    root.filename = filedialog.askopenfilename(initialdir = os.getcwd(),
        title = "Select the primary app file",
        filetypes = (("all files", "*.*"),("python files", "*.py")))
    if root.filename:
        appfullpath = str(root.filename)
        # etracts appdir and appname from appfullpath
        path = os.path.split(appfullpath)
        data = []
        for i in path:
             data.append(i)
        appname = data.pop()
        appdir = ''.join(map(str, data))
        appdir = os.path.normpath(appdir)
        if not silentmode:
            message = "\n".join(["You selected as the primary app file.",
                appfullpath,
                "To save config, update the configuration with the button. App > Export config."])
            log(message)
            MessageBox.showinfo("app", message)
        return os.path.normpath(appfullpath)

# -------------------------- END APP -----------------------------------

def install_from_pip():
    """ Setup python modules containing in requirements file
    "Requirements file" are file containing a list of items to be installed using pip install.
    Similar to a command in a shell: pip install -r /path/to/requirements.txt
    Details on the format of the files are here: 
        https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format
    """
    requirements = os.path.join(os.getcwd(), "requirements.txt")
    try:
        if sys.platform.startswith('linux'):
            if os.path.isfile(requirements):
                # check the availability of the utility in the system
                pip = os.popen('command -v pip').read()
                if pip:
                    pipproc = subprocess.Popen(["pip", "install", "-r", requirements])
                    log("Requirements installed successfully")
                else:
                    log("pip is not installed. Get more: Help > Pip online installation")
            else:
                log("requirements file not found.")
        if sys.platform.startswith('win'):
            pip_path = os.path.join(sys.executable[:-10], "Scripts")
            os.path.normpath(pip_path)
            if os.path.isdir(pip_path):
                pip = os.path.join(pip_path, "pip.exe")
                if os.path.isfile(pip):
                    # Log("pip path: ", pip_path)
                    os.chdir(pip_path)
                    pipproc = subprocess.Popen(["pip.exe", "install", "-r", requirements])
                    log("Requirements installed successfully")
                else:
                    log("pip is not installed. Get more: Help > Pip online installation")
            else:
                log("OS Error. Cant find python Scripts directory")
    except OSError:
        print ("OS Error. Can not access to files")

def pip_list():
    """ List installed packages, including editables."""
    try:
        if sys.platform.startswith('linux'):
            pip = os.popen('command -v pip').read()
            if pip:
                pipproc = os.system("pip list --format=legacy > tmp")
                with open("tmp", "r") as f:
                    modules = f.readlines()
                    f.close()
                    os.remove("tmp")
                MessageBox.showinfo("Modules", modules)
            else:
                log("pip is not installed. Get more: Help > Pip online installation")
        if sys.platform.startswith('win'):
            pip_path = os.path.join(sys.executable[:-10], "Scripts")
            os.path.normpath(pip_path)
            if os.path.isdir(pip_path):
                pip = os.path.join(pip_path, "pip.exe")
                if os.path.isfile(pip):
                    os.chdir(pip_path)
                    pipproc = os.system("pip.exe list --format=legacy > tmp")
                    with open("tmp", "r") as f:
                        modules = f.readlines()
                        f.close()
                        os.remove("tmp")
                    MessageBox.showinfo("Modules", modules)
                else:
                    log("pip is not installed. Get more: Help > Pip online installation")
            else:
                log("OS Error. Cant find python Scripts directory")
    except OSError:
        print ("OS Error. Can not access to files")

def edit_apt_sourceslist():
    if sys.platform.startswith('linux'): 
        edit_file("/etc/apt/sources.list")

def edit_sshd_config():
    if sys.platform.startswith('linux'): 
        edit_file("/etc/ssh/sshd_config")

def open_hosts():
    """ Open default hosts file. (Need root permissions) """
    if sys.platform.startswith('win'):
        hostsfile = "C:\Windows\System32\drivers\etc\hosts"
        edit_file(hostsfile)
    if sys.platform.startswith('linux'):
        hostsfile = "/etc/hosts"
        edit_file(hostsfile)

def get_publick_ip():
    """ Check your publick ip, use ip.42.pl . Return publick IP IPv4"""
    pub_ip = urlopen('http://ip.42.pl/raw').read()
    return pub_ip

def get_local_ip():
    """ Return your local host IP IPv4 (work on all platforms) """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 0))
    return str(s.getsockname()[0])

def start_ipconfig():
    """ List out ifaces configuration """
    if sys.platform.startswith('win'):
        os.system("ipconfig /all")
    if sys.platform.startswith('linux'):
        # check the availability of the utility in the system
        ipconfig = os.popen('command -v ipconfig').read()
        if ipconfig:
            os.system("ifconfig")
        else:
            os.system("ip addr")

def show_ip():
    """ Show messagebox with the local and global IP. """
    ip_info = "".join(["IP statistics: \n",
        "publick IP: ", str(get_publick_ip()), "\n",
        "local IP: ", str(get_local_ip()), "\n",
        ])
    MessageBox.showinfo("IP info", ip_info)

def reverse_dns(host):
    """ Return IP for host. Accepts DNS names as input. """
    try:
        ips = socket.gethostbyname_ex(host)
    except socket.gaierror:
        ips = []
    return ips

def check_port(address, port):
    """" Check port is open, return True ro False"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # AF_INET - Socket Family (here Address Family version 4 or IPv4)
    # SOCK_STREAM - Socket type TCP connections
    # SOCK_DGRAM - Socket type UDP connections
    try:
        port = int(port)
        s.connect((address, port))
        s.close()
        return True
    except socket.error:
        s.close()
        return False

def check_app_port():
    port_opened = check_port(LOCALHOST, devserverport)
    if port_opened:
        log("Application port", str(devserverport), "opened")
    else:
        log("Application port", str(devserverport), "closed")

def check_localserv_ports():
    portslist = {8000: "Django",
        4000: "Werkzeug - Gunicorn",
        5000: "Flask",
        6543: "Pyramid",
        8080: "TurboGears-Bottle"}
    log("Check the ports of the popular Python frameworks. Do not close the window process may take a minute.")
    for key, value in portslist.items():
        port_opened = check_port(LOCALHOST, key)
        if port_opened:
            log("".join([str(value), " port ", str(key), " - is open"]))
        else:
            log("".join([str(value), " port ", str(key), " - is closed"]))

def check_database_ports():
    portslist = {1433: "Microsoft SQL Server",
        3306: "Mysql",
        5432: "Postgres",
        11211: "Memcache",
        27017: "MongoDB"}
    log("Check the ports of the database services. Do not close the window process may take a minute.")
    for key, value in portslist.items():
        port_opened = check_port(LOCALHOST, key)
        if port_opened:
            log("".join([str(value), " port ", str(key), " - is open"]))
        else:
            log("".join([str(value), " port ", str(key), " - is closed"]))

def check_pop_ports():
    portslist ={20: "FTP", 21: "FTP",
        23: "SSH-TELNET",
        25: "SMTP",
        53: "DNS",
        80: "HTTP", 8080: "HTTP",
        110: "POP3",
        139: "NetBIOS",
        443: "HTTPS",
        1080: "SOCKS",
        3128: "SQUID",
        3389: "RDP",
        5900: "VNC"}
    log("Checking the popular ports. Do not close the window process may take a minute.")
    for key, value in portslist.items():
        port_opened = check_port(LOCALHOST, key)
        if port_opened:
            log("".join([str(value), " port ", str(key), " - is open"]))
        else:
            log("".join([str(value), " port ", str(key), " - is closed"]))

def show_arp_table():
    """ Show the kernel's IPv4 network neighbour cache. """
    if sys.platform.startswith('win'):
        os.system("arp -a")
    if sys.platform.startswith('linux'):
        arp = os.popen('command -v arp').read()
        if arp:
            os.system("arp -a")
        else:
            os.system("ip neigh")

def show_runned_pyprocs():
    """ Show runned python processes. """
    if sys.platform.startswith('win'):
        os.system('tasklist | find "python"')
    if sys.platform.startswith('linux'):
        os.system('ps | grep "python"')

def show_routes_table():
    """ Show the kernel routing table. """
    if sys.platform.startswith('win'):
        os.system("route print")
    if sys.platform.startswith('linux'):
        route = os.popen('command -v route').read()
        if route:
            os.system("route -n")
        else:
            os.system("ip route list")

def netstat(port=False):
    """ List out tcp-udp connections by port.
    In Linux use netstat or ss tool depending on the platform
    """
    if not port:
        if sys.platform.startswith('win'):
            os.system("netstat -an")
        if sys.platform.startswith('linux'):
            netstat = os.popen('command -v netstat').read()
            if netstat:
                os.system('netstat -ant')
            else:
              os.system('ss -ant')
    else:
        port = int(port)
        # 65535 - the max number of ports within the TCP / IP protocol stack.
        if devserverport > 65535:
            log("Port in the config is incorrectly specified. Max value 65535")
        if runned:
            if sys.platform.startswith('win'):
                command = "".join(["netstat -ano | findstr ", str(port)])
                stdout = os.popen(command).read().replace("\n", "")
                if stdout:
                    log("Show Netstat statistics", port, "port\n", stdout)
            if sys.platform.startswith('linux'):
                netstat = os.popen('command -v netstat').read()
                if netstat:
                  command = "".join(["netstat -ant | grep ", str(port)])
                else:
                  command = "".join(["ss -a | grep ", str(port)])
                stdout = os.popen(command).read().replace("\n", "")
                if stdout:
                    log("Show Netstat statistics", port, "port\n", stdout)
        else:
            log("The application was not started.")

# add to tkmenu netstat func
def show_netstat_all():
    netstat()
def show_app_netstat():
    netstat(devserverport)

def open_iface_conf():
    """ Open netwok config in default editor """
    if sys.platform.startswith('lin'):
        if os.path.isfile("/etc/network/interfaces"):
            edit_file("/etc/network/interfaces")
        else:
            # /etc/sysconfig/network
            rhelconf = os.popen('command -v system-config-network').read()
            if rhelconf:
                os.system("system-config-network")

def show_svchosts_proc():
    """ Show list of running svchost instances """
    if sys.platform.startswith('win'):
        svproc = subprocess.Popen("wmic process where description='svchost.exe' list brief", stdout=subprocess.PIPE)
        svchost = svproc.stdout.read()
        MessageBox.showwarning("Show list of running svchost instances", svchost)
    else:
        MessageBox.showerror("Error", "Sorry this function only for Windows")

def exit():
    """ Safely completes processes and exit"""
    stop_app()
    log("Exit", time.strftime("%d.%m.%Y"),"\n")
    save_log()
    clear_shell_screen()
    root.destroy
    sys.exit(0)

def export_config():
    """ Export configuration into .cfg file. """
    os.chdir(appdir)
    config = configparser.RawConfigParser()
    try:
        def rewrite_config():
            with open(configfile, 'w') as exported_configfile:
                config.add_section('app')
                config.set('app', 'appdir', appdir)
                config.set('app', 'port', devserverport)
                config.set('app', 'backuppath', backuppath)
                config.set('app', 'logfilepath', logfilepath)
                config.set('app', 'framework', framework)
                if appname:
                    config.set('app', 'appname', appname)
                else:
                    print("First you need to specify the application. App > Choose app. After you can export the settings.")
                    choose_app()
                    config.set('app', 'appname', appname)
                config.add_section('launcher')
                config.set('launcher', 'windowsize', windowsize)
                config.write(exported_configfile)
        # MsgBox Ask Rewrite config or no
        if os.path.isfile(configfile):
            overwriteconfig = MessageBox.askquestion("Warning", "The config file already exists, you want to overwrite?")
            if overwriteconfig == "yes":
                rewrite_config()
                log("The config file was rewritten.")
            elif overwriteconfig == "no":
                log("The config file closed without changes.")
        else:
            rewrite_config()
    except IOError:
        print ("IO Error. Can not access to config file")

def open_configfile():
    """ Open app in default editor """
    edit_file(configfile)

def create_backup():
    """ 
    Create project backup, creates an archive tar.gz in backup path. 
    backuppath - declared in init_config()
    At the output, the name of the archive will be: backup_Friday_10.11.2017.tar
    """
    global backuppath
    # specify below the folders you want to exclude from the backup
    excludelist = ["backup"]
    if os.path.dirname(backuppath) == os.path.dirname(appfullpath):
        log("Backup is saved in the root directory of the project.",
        "It is unsafe in case of damage of the project will be lost backup.")
    try:
        dt_time = time.strftime("%A_%d.%m.%Y")
        outname = "".join(['Backup_', dt_time, '.tar.gz'])
        outfile = os.path.join(backuppath, outname)
        # create backup folder if not found
        if not os.path.exists(backuppath):
            os.mkdir(backuppath)
        if os.path.exists(appdir) and os.path.exists(backuppath):
            tar = tarfile.open(outfile, "w:gz")
            log("Create a backup with the name -", outname)
            log("Saved in the folder -", backuppath)
            os.chdir(appdir)
            fileslist = os.listdir('.')
            for folder in excludelist:
                fileslist.remove(folder)
            for file in fileslist:
                tar.add(file)
            # list of compressed files
            for tarinfo in tar:
                if tarinfo.isreg():
                    text = "".join(["add file - ", tarinfo.name])
                    print(text)
                elif tarinfo.isdir():
                    text = "".join(["add dir - ", tarinfo.name])
                    print(text)
            tar.close()
            # considers the full size
            statinfo = os.stat(outfile)
            k_size = statinfo.st_size / 1000
            log("Backup created successfully. Totally size: ", k_size, " Kbytes")
            print("Backup created successfully. Totally size: ", k_size, " Kbytes")
        return outfile
    except ValueError:
        print("ValueError: Check, input and output backup folders, check exclude fileslist")
    except OSError:
        print ("OS Error. Can not access to files")

def list_backups():
    """
    Show messagebox with backup list statistics. Return backuplist.
    """
    if os.path.isdir(backuppath):
        fileslist = os.listdir(backuppath)
        backupslist = []
        totally = 0
        for file in fileslist:
            if file.lower().endswith(".tar.gz"):
                statinfo = os.stat(os.path.join(backuppath, file))
                kb_size = statinfo.st_size / 1000
                totally += kb_size
                backupslist.append(" ".join([str(file), "=", str(kb_size), "kb"]))
        if backupslist:
            backupslist.append(" ".join(["Totally: ", str(totally), "kb"]))
            backups = "\n".join(backupslist)
            MessageBox.showinfo("Backups", backups)
            return backupslist
        else:
            MessageBox.showwarning("Backups", "No backups founded. Create before or configure launcher.")
    else:
        MessageBox.showwarning("Backups", "No backups folder founded. Configure launcher type <backuppath>.")

def remove_pyc():
    """Recursivelly remove *.pyc and *.pyo files"""
    os.chdir(appdir)
    try:
        fileslist = walker(appdir)
        for file in fileslist:
            if file.lower().endswith(".pyc") or file.lower().endswith(".pyo"):
                os.remove(file)
                log("".join([file, " - was deleted"]))
    except OSError:
        print("OS Error. Can not access to files")

# -------------------------- HELP ----------------------------------
def open_pythondoc_url():
    webbrowser.open("https://docs.python.org")
def open_getpippy_url():
    webbrowser.open("https://pip.pypa.io/en/stable/installing/")
def open_pep8online_url():
    webbrowser.open("http://pep8online.com/upload")
def open_virustotal_url():
    webbrowser.open("https://www.virustotal.com/#/home/upload")
def open_webframeworks_url():
    webbrowser.open("https://wiki.python.org/moin/WebFrameworks")
def open_online_python_ide_url():
    webbrowser.open("http://www.tutorialspoint.com/online_python_ide.php")
def open_wikiports_url():
    webbrowser.open("https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers")
def open_homepage_url():
    webbrowser.open("https://yadi.sk/d/CRtKax-k3QoGb7")
def open_license_url():
    webbrowser.open("https://opensource.org/licenses/BSD-2-Clause")

def show_readme():
    """ Show README file. """
    os.chdir(appdir)
    helpfile = os.path.join(os.getcwd(), "README.txt")
    if os.path.isfile(helpfile):
        edit_file(helpfile)
    else:
        open_homepage_url()
        log("README file is missed. Open project homepage.")

def open_dev_url():
    """ Open index page in default webbrowser """
    if runned:
        devserverurl = "".join(["http://127.0.0.1:", str(devserverport)])
        webbrowser.open(devserverurl)
    else:
        MessageBox.showinfo("App status", "App not runned.")

def open_adm_url():
    """ Open adminboard page in default webbrowser """
    if runned:
        devserverurl = "".join(["http://127.0.0.1:", str(devserverport), "/admin"])
        webbrowser.open(devserverurl)
    else:
        MessageBox.showinfo("App status", "App not runned.")

def show_statistics(logging=False):
    try:
        statistics = "".join(["Statistics for: ", str(socket.gethostname()), "\n",
            "App name: ", str(appname), "\n",
            "Location: ", appdir, "\n",
            "Framework: ", str(framework), "\n",
            "Logfile size: ", str(os.path.getsize(logfilepath)/1000), " Kb", "\n",
            "App last changed: ", time.ctime(os.path.getmtime(appfullpath)), "\n",
            # "Launcher uptime: ", str(time.time() - START_TIME), " Sec", "\n",
            ])
        if logging:
            log(statistics)
        else:
            MessageBox.showinfo("Statistics", statistics)
    except OSError:
        print("First you need to specify the application.")

def show_statistics_intolog():
    show_statistics(True)

def about(event=None):
    aboutinfo = "\n".join([str(__about__),
    "Support Windows/Linux Python 2.6.x+/Python 3.2.x+",
    str(__license__),
    "Contact: https://github.com/ins1x"])
    MessageBox.showinfo("About", aboutinfo)

# -------------------------- GUI --------------------------------------
root = tk.Tk()
# Main window size init
if root.winfo_screenwidth() > 1000 and root.winfo_screenheight() > 1000:
    windowsize = MAIN_WINDOW_SIZE
    root.geometry(windowsize)
else:
    windowsize = "820x480"
    root.geometry(windowsize)

def ui_startproject():
    """ GUI for stratproject menu. """
    # The basic structure of the project folders
    base_folders = ['static', 'static/css', 'static/js', 'static/img', 'static/templates', 'log', 'media', 'env']
    # The basic structure of the project files
    base_files = ['manage.py', 'wsgi.py', 'urls.py', 'settings.py', '__init__.py']
    # Using for output to GUI basic structure of the project files
    appstruct = """App sample struct
    ./appname
    ├── app
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── manage.py"""
    # These data will be recorded for each new py file in the project
    pyfile_content = """#!/usr/bin/env python\n# -*- coding: utf-8 -*-"""
    # Using for output to GUI basic structure of the project folders
    project_folders = "\n".join(base_folders)
    # Variables for checkboxes
    genfiles = tk.IntVar()
    backup_before_creating = tk.IntVar()

    def sub_makedirs(newapp_dir, newapp_name):
        """Make dirs and files structure."""
        try:
            os.chdir(newapp_dir)
            os.mkdir(os.path.normpath(newapp_name))
            newapp_path = os.path.join(newapp_dir, newapp_name)
            for i in base_folders:
                path = os.path.normpath(os.path.join(newapp_dir, i))
                if not os.path.exists(path):
                    os.makedirs(path)
            if genfiles.get() == 1:
                for file in base_files:
                    path = os.path.normpath(os.path.join(newapp_path, file))
                    with open(path, "w") as f:
                        f.write(pyfile_content)
                        f.close()
        except OSError:
            print("OSError. Can not access to files")

    def sub_load():
        """ TODO. Load dir list from txt file. """
        projwindow.destroy()

    def sub_create():
        """ Generator """
        projwindow.grab_set()
        appname_entry.focus()
        newapp_name = appname_entry.get()
        newapp_dir = srcdir_entry.get()
        if newapp_name and os.path.isdir(newapp_dir):
            sub_makedirs(newapp_dir, newapp_name)
            MessageBox.showinfo("Done", "Base directory struct created")
            projwindow.destroy()
        else:
            MessageBox.showinfo("Error", "Wrong appname or directory")
            projwindow.destroy()

    # window init
    projwindow = tk.Toplevel(root)
    projwindow.geometry("650x400")
    projwindow.title("Manage")
    # Grid elements
    appstruct_label = tk.Label(projwindow, text=appstruct, justify=LEFT)
    appstruct_label.grid(row=1, column=1, padx=5, pady=5)
    dirs_label = tk.Label(projwindow, text=project_folders, justify=LEFT)
    dirs_label.grid(row=1, column=2, padx=5, pady=5)
    appname_label = tk.Label(projwindow, text="Input new app name.")
    appname_label.grid(row=2, column=1, padx=5, pady=5)
    appname_entry = tk.Entry(projwindow, width="60", bd=3)
    appname_entry.grid(row=3, column=1, padx=5, pady=5)

    srcdir_label = tk.Label(projwindow, text="Working directory", justify=LEFT)
    srcdir_label.grid(row=4, column=1, padx=5, pady=5)
    srcdir_entry = tk.Entry(projwindow, width="60", bd=3)
    srcdir_entry.grid(row=5, column=1, padx=5, pady=5)
    srcdir_entry.insert(0, os.getcwd())

    dirset_label = tk.Label(projwindow, text="Add more dirs", justify=LEFT)
    dirset_label.grid(row=6, column=1, padx=5, pady=5)
    dirs_name_entry = tk.Entry(projwindow, width="60", bd=3)
    dirs_name_entry.grid(row=7, column=1, padx=5, pady=5)
    # buttons
    but_create = tk.Button(projwindow, width="15", text="Create", command=sub_create)
    but_create.grid(row=9, column=1, padx=5, pady=5)
    # NEW
    # but_load = tk.Button(projwindow, width="15", text="Load", command=sub_load)
    # but_load.grid(row=8, column=1, padx=5, pady=5)
    # checkbox
    genfiles_checkbutton = tk.Checkbutton(projwindow, onvalue = 1, offvalue = 0, text="Make wsgi, urls, settings, manage py files", variable=genfiles)
    genfiles_checkbutton.grid(row=2, column=2, padx=5, pady=5)
    # NEW
    # backup_checkbutton = tk.Checkbutton(projwindow, text="Make backup", variable=backup_before_creating)
    # backup_checkbutton.grid(row=3, column=2, padx=5, pady=5)

def reverse_dns_ui():
    """ GUI for reverse DNS func. """
    def reverse_host_dns():
        """ Sub call reverse_dns() and show returned IPs. """
        host = dns_entry.get()
        ips = reverse_dns(host)
        twindow.grab_set()
        dns_entry.focus()
        MessageBox.showinfo("Returned ip list", ips)
        twindow.destroy()
    
    # window init
    twindow = tk.Toplevel(root)
    twindow.geometry("450x100")
    twindow.title("Reverse DNS")
    # Grid elements
    infolabel = tk.Label(twindow, text="Enter hostname bellow. Example (google.com).")
    infolabel.grid(row=1, column=1, padx=5, pady=5)
    dns_entry = tk.Entry(twindow, width="50", bd=3)
    dns_entry.grid(row=2, column=1, padx=5, pady=5)
    but_getip = tk.Button(twindow, width="15", text="Get ip", command=reverse_host_dns)
    but_getip.grid(row=2, column=2, padx=5, pady=5)

def ui_config():
    """ GUI for the settings app and launcher. """

    def sub_cnf():
        """Get all items from configmenu and export to configfile."""
        global devserverport, appfullpath, backuppath, logfilepath
        dport = port_entry.get()
        dport = int(dport)
        devserverport = dport
        appfullpath = app_entry.get()
        backuppath = backup_entry.get()
        logfilepath = log_entry.get()
        export_config()

    def sub_close():
        window.destroy()

    def sub_path_getter():
        window.pathname = filedialog.askdirectory(initialdir = os.getcwd(),
        title = "Select path")
        if window.pathname:
            path = os.path.normpath(window.pathname)
            return path

    def set_app_path():
        path = choose_app(True)
        app_entry.delete("0", 'end')
        app_entry.insert(0, path)
        window.grab_set()
        app_entry.focus()

    def set_backup_path():
        path = sub_path_getter()
        backup_entry.delete("0", 'end')
        backup_entry.insert(0, path)
        window.grab_set()
        backup_entry.focus()

    def set_log_path():
        path = sub_path_getter()
        log_entry.delete("0", 'end')
        log_entry.insert(0, path)
        window.grab_set()
        log_entry.focus()

    # window init
    window = tk.Toplevel(root)
    window.geometry("550x280")
    window.title("Configuration")
    # config menu form
    app_entry = tk.Entry(window, width="60", bd=3)
    app_entry.grid(row=2, column=1, padx=5, pady=5)
    app_entry.insert(0, appfullpath)
    but_setapp = tk.Button(window, width="15", text="Select app", command=set_app_path)
    but_setapp.grid(row=2, column=2, padx=5, pady=5)

    backup_entry = tk.Entry(window, width="60", bd=3)
    backup_entry.grid(row=3, column=1, padx=5, pady=5)
    backup_entry.insert(0, backuppath)
    but_setbackup = tk.Button(window, width="15", text="Backup output", command=set_backup_path)
    but_setbackup.grid(row=3, column=2, padx=5, pady=5)

    log_entry = tk.Entry(window, width="60", bd=3)
    log_entry.grid(row=4, column=1, padx=5, pady=5)
    log_entry.insert(0, logfilepath)
    but_setlog = tk.Button(window, width="15", text="Log output", command=set_log_path)
    but_setlog.grid(row=4, column=2, padx=5, pady=5)

    olabel = tk.Label(window, text="Other options: ")
    olabel.grid(row=5, column=1, padx=5, pady=5)
    tlabel = tk.Label(window, text="Server port")
    tlabel.grid(row=6, column=2, padx=5, pady=5)
    port_entry = tk.Entry(window, width="15", bd=3)
    port_entry.grid(row=6, column=1, padx=5, pady=5)
    port_entry.insert(0, devserverport)

    olabel = tk.Label(window, text="Be careful, button <Save changes> overwrite the current config!!")
    olabel.grid(row=7, column=1, padx=5, pady=5)
    but_setcnf = tk.Button(window, text="Save changes", command=sub_cnf)
    but_setcnf.grid(row=8, column=1, padx=5, pady=5)
    but_expcnf = tk.Button(window, text="Open configfile in editor", command=open_configfile)
    but_expcnf.grid(row=8, column=2, padx=5, pady=5)
    but_close = tk.Button(window, text="Close", command=sub_close)
    but_close.grid(row=9, column=2, padx=5, pady=5)

root.title(APP_TITLE)
# Declare GUI main window objects
label = tk.Label(text=LAUNCHER_RUN_ENV)
devserverinfo = "".join(["Use ", str(framework), " framework."])
statelabel = tk.Label(width="30", text=devserverinfo)
but_restartapp = tk.Button(command=restart_app, width="20", text="Start/Restart server")
but_stopapp = tk.Button(command=stop_app, width="20", text="Stop server")
but_openindex = tk.Button(command=open_dev_url, width="20", text="Open index")
but_uiconfig = tk.Button(command=ui_config, width="20", text="Configure")
but_exit = tk.Button(command=exit, width="20", text="Exit")
but_about = tk.Button(command=about, width="5", text="About")
logarea = tk.Text(font='Arial 10', width="80", height="20", wrap="word")
logarea.config(bg="#f5f5f5", fg="#000000")
# bind hotkeys
logarea.bind('<KeyPress-F1>', about)
logarea.bind('<Control-S>', save_as_log)
logarea.bind('<Control-s>', save_as_log)
# Grid GUI
# 1 column 
logarea.grid(row=5, column=0, rowspan=2, columnspan=2)
# 2 column
label.grid(row=1, column=1)
statelabel.grid(row=2, column=1)
# 3 column
but_restartapp.grid(row=1, column=2, padx=5, pady=5)
but_stopapp.grid(row=2, column=2, padx=5, pady=5)
but_openindex.grid(row=3, column=2, padx=5, pady=5)
but_uiconfig.grid(row=4, column=2, padx=5, pady=5)
but_exit.grid(row=5, column=2, padx=5, pady=5)
but_about.grid(row=3, column=1)
# Main program menu
m = tk.Menu(root)
root.config(menu=m)
fm = tk.Menu(m)
m.add_cascade(label="App", menu=fm)
fm.add_command(label="Start server", command=start_app)
fm.add_command(label="Stop server", command=stop_app)
fm.add_command(label="Restart server", command=restart_app)
subman = tk.Menu(m)
fm.add_cascade(label="Manage", menu=subman)
subman.add_command(label="Choose app", command=choose_app)
subman.add_command(label="Status app", command=status_app)
subman.add_command(label="Start new project", command=ui_startproject)
subman.add_separator()
subman.add_command(label="Open index in browser", command=open_dev_url)
subman.add_command(label="Open adminboard in browser", command=open_adm_url)
fm.add_separator()
fm.add_command(label="Configure launcher", command=ui_config)
fm.add_command(label="Show statistics", command=show_statistics)
fm.add_command(label="Close only GUI(CLI messages will be displayed)", command=root.destroy)
fm.add_command(label="Exit", command=exit)
fv = tk.Menu(m)
m.add_cascade(label="Log", menu=fv)
fv.add_command(label="Save log", command=save_log)
fv.add_command(label="Save as log", command=save_as_log)
fv.add_command(label="Clear log area", command=clear_log)
fv.add_command(label="Copy selected text to clipboard", command=copy_log)
fv.add_command(label="Show-Hide log area", command=show_log)
fv.add_command(label="Open full log (for all time of use)", command=load_log)
fv.add_command(label="Remove log file (for all time of use)", command=remove_log)
fv.add_command(label="Show statistics into log", command=show_statistics_intolog)
fl = tk.Menu(m)
m.add_cascade(label="Loclahost", menu=fl)
subfp = tk.Menu(m)
fl.add_cascade(label="Port status", menu=subfp)
subfp.add_command(label="Check app port status", command=check_app_port)
subfp.add_command(label="Check popular ports is open", command=check_pop_ports)
subfp.add_command(label="Check the ports of the popular Python frameworks", command=check_localserv_ports)
subfp.add_command(label="Check the ports of the database services", command=check_database_ports)
subfp.add_command(label="List of TCP and UDP port numbers", command=open_wikiports_url)
subfip = tk.Menu(m)
fl.add_cascade(label="Network tools", menu=subfip)
subfip.add_command(label="Show Network interfaces", command=start_ipconfig)
if sys.platform.startswith('lin'):
    subfip.add_command(label="Edit Network interfaces configuration", command=open_iface_conf)
    subfip.add_command(label="Edit SSH daemon configuration", command=edit_sshd_config)
subfip.add_command(label="IP statistics (local and global ip)", command=show_ip)
subfip.add_command(label="Reverse DNS (dns -> ip)", command=reverse_dns_ui)
subfip.add_command(label="ARP table", command=show_arp_table)
subfip.add_command(label="Routes table", command=show_routes_table)
subfip.add_command(label="Show hosts", command=open_hosts)
subfip.add_command(label="Netstat application statistics", command=show_app_netstat)
subfip.add_command(label="Netstat full statistics", command=show_netstat_all)
if sys.platform.startswith('win'):
    subfip.add_command(label="Show list of running svchost instances", command=show_svchosts_proc)
subfm = tk.Menu(m)
fl.add_cascade(label="Modules", menu=subfm)
subfm.add_command(label="Install python modules containing in requirements file(run as root)", command=install_from_pip)
subfm.add_command(label="List pip installed python modules", command=pip_list)
subfm.add_command(label="Pip online installation", command=open_getpippy_url)
if sys.platform.startswith('lin'):
    subfm.add_command(label="Configure apt sources.list", command=edit_apt_sourceslist)
subfbak = tk.Menu(m)
fl.add_cascade(label="Backup", menu=subfbak)
subfbak.add_command(label="Create app backup (tar.gz)", command=create_backup)
subfbak.add_command(label="Show all backups list (tar.gz)", command=list_backups)
subfbak.add_command(label="Remove .pyc and .pyo files in app directory", command=remove_pyc)
fl.add_command(label="Runned python processes", command=show_runned_pyprocs)
fh = tk.Menu(m)
m.add_cascade(label="Help", menu=fh)
fh.add_command(label="Web Frameworks for Python", command=open_webframeworks_url)
fh.add_command(label="Python online documentation", command=open_pythondoc_url)
fh.add_command(label="Check your code for PEP8 requirements online", command=open_pep8online_url)
fh.add_command(label="Check your files and URLs to detect types of malware online", command=open_virustotal_url)
fh.add_command(label="Online Python IDE", command=open_online_python_ide_url)
fh.add_separator()
fh.add_command(label="README ", command=show_readme)
fh.add_command(label="LICENSE", command=open_license_url)
fh.add_command(label="Homepage", command=open_homepage_url)
fh.add_separator()
fh.add_command(label="About", command=about)

# Specifies the message when the application starts
print ("Launcher runned. Do not close this window. The server log is displayed here")
print ("Press <CTRL + C> or <CTRL + BREAK> to exit")
check_log_overflow()
log(LAUNCHER_RUN_ENV)
log(os_version())
if use_configfile:
    log("Receiving data from a settings file successfully")
else:
    log("The launcher is running in the auto mode")
log("Application use", framework, "framework.")
log("WSGI server configured to use port:", devserverport)
root_rights = as_root()
if root_rights:
    log("Running with administrator rights - good")

root.mainloop()

# Disclaimer. This app was written just for fun. Maybe looks ugly but it really works
# Excuse possible errors in translation, because English is not my native language
