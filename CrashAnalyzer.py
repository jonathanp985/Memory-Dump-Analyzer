import os
import file_write 
import subprocess
from os import system
from subprocess import *

explanation = file_write.make_file()

def run_windbg(dump_file):
    windbg_file = "WindbgX.exe"

    commands = [windbg_file, '-z', dump_file, '-c', '.logopen my_logfile.txt; !analyze -v; .time; ||; !sysinfo cpuinfo; .exr -1; !vm; .logclose; qqd']
    try:
        ans = subprocess.run(commands)
    except:
        return 0
    
def create_logfile():
    try: 
        memdump_path = input("Enter in the path of the MEMORY.dmp file: ")
        if os.path.exists(memdump_path) and memdump_path.endswith(".dmp"):
            run_windbg(memdump_path)
        else:
            raise Exception()
    except: 
        print(f"File does not exist or Incorrect file extension")
        exit(0)

def get_synopsis(log_file):
    with open(log_file, 'r') as file:
        lines = file.readlines() 
    res = []
    ind = 0
    for line in lines:
        if "Arguments:" in line:
            break
        if line == '\n':
            ind = 1
        if ind == 1:
            res.append(line)
    return res

def get_bugcheck(log_file):
    checks = {}
    with open(log_file, 'r') as file:
        lines = file.readlines()
    
    for line in lines:
        if "MODULE_NAME:" in line:
            checks["mod_name"] = line.split()[1]

        if "PROCESS_NAME:" in line:
            checks["process_name"] = line.split()[1]

        if "SYMBOL_NAME:" in line:
            checks["symbol_name"] = line.split()[1]

        if "IMAGE_NAME:" in line:
            checks["image_name"] = line.split()[1]

        if "System Uptime:" in line:
            checks["system_uptime"] = line.split()[2:]
            checks["system_uptime"] = " ".join(checks["system_uptime"])
        
        if line[0] == '.':
            checks["file_type"] = line.split()[1:]
            checks['file_type'] = " ".join(checks['file_type'])
        

    return checks

def get_exception(log_file):
    with open(log_file, 'r') as file:
        lines = file.readlines() 
    checks = {}

    for line in lines:
        if "FAILURE_BUCKET_ID:" in line:
            checks["fail_id"] = line.split()[1]

        if "FAILURE_ID_HASH:" in line:
            checks["id_hash"] = line.split()[1]

        if "ExceptionAddress: " in line:
            checks["exception_address"] = line.split()[1]

        if "ExceptionCode: " in line:
            checks["exception_code"] = line.split()[1]
        
        if "ExceptionFlags: " in line:
            checks["exception_flags"] = line.split()[1]

        if "NumberParameters:" in line:
            checks["number_parameters"] = line.split()[1]

    return checks

def get_state(log_file):
    system_state = []

    with open(log_file, 'r') as file:
        lines = file.readlines() 

    # Page file info
    ind = 0
    system_state.append([])
    for line in lines:
        if "Page File: " in line:
          ind = 1
          system_state[0].append(line)
        elif ind == 1 and  'Free System PTEs:' not in line:
            system_state[0].append(line)  
        elif ind == 1 and 'Free System PTEs:' in line:
            system_state[0].append(line)
            break
        else:
            continue
    
    # Memory commit info
    system_state.append([])

    for line in lines:
        if 'Commit: ' in line or 'Committed pages: ' in line or 'Commit limit: ' in line:
            system_state[1].append(line)    
    return system_state


def get_stack_trace(log_file):
    thread = []

    with open(log_file, 'r') as file:
        lines = file.readlines() 
    ind = 0
    for line in lines:
        if "STACK_TEXT: " in line:
          ind = 1
        elif ind == 1 and line != '\n':
            thread.append(line)  
        elif ind == 1 and line == '\n':
            return thread
        else:
            continue
    return thread

def get_running_processes(log_file):
    processes = []

    with open(log_file, 'r') as file:
        lines = file.readlines() 

    ind = 0
    for line in lines:       
        if "Pid ImageName" in line:
            ind = 1
            processes.append(line)
        elif ind == 1 and 'Closing' not in line:
            processes.append(line)
        else:
            continue

    return processes


def get_processor(log_file):
    with open(log_file, 'r') as file:
        lines = file.readlines()
    res = []
    ind = 0
    for line in lines:   
        if "OSPLATFORM_TYPE:" in line:
            res.append(line)
        if "[CPU Information]" in line:
          ind = 1
          res.append(line)
        elif ind == 1 and  'MSR8B' not in line:
            res.append(line)  
        elif ind == 1 and 'MSR8B' in line:
            res.append(line)
            break
        else:
            continue
    return res


def make_info_file():
    file = open("crash_info.txt", 'w')
    
    synopsis = get_synopsis('my_logfile.txt')
    info_hash = get_bugcheck("my_logfile.txt")
    system_state = get_state('my_logfile.txt')
    processor_arr = get_processor('my_logfile.txt')
    exception_hash = get_exception('my_logfile.txt')
    crash_thread = get_stack_trace('my_logfile.txt')
    processes = get_running_processes('my_logfile.txt')

    # Synopsis
    file.writelines(explanation.get_synposis())
    for line in synopsis:
        file.write(line)

    file.write("\n")
    for module in info_hash:
        file.write(f'{module}: {info_hash[module]}\n\n')
    
    # Exception 
    file.writelines(explanation.get_exception())
    for exception in exception_hash:
        file.write(f'{exception}: {exception_hash[exception]}\n\n')
    
    # System State
    file.write(explanation.get_state())
    for state in system_state[0]:
        file.write(state)

    for commit in system_state[1]:
        file.write(commit)
        
    # Modules and Processes
    file.writelines(f'{explanation.get_module()}')
    file.write("")
    for process in processes:
        file.write(process)
    
    # Processor
    file.writelines(explanation.get_processor())
    for line in processor_arr:
        file.write(line)
    
    # Thread 
    file.writelines(explanation.get_thread())
    file.write("")
    for item in crash_thread:
        file.write(item)
    




create_logfile()
print("LOADED MODULES: ",  get_bugcheck("my_logfile.txt"))
make_info_file()
print("REACHED")

