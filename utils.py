import datetime
import logging
import os
import psutil
import textwrap
import time
import torch
import wandb

def check_device(gpu):
    if gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = gpu

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    return device

def log_setup(logger_file, 
              log_level='DEBUG', 
              console_level='INFO', 
              format='%(name)s - %(levelname)s - %(message)s'):
    
    logging.basicConfig(filename=logger_file, filemode='w', format=format)
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))

    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, console_level))
    logger.addHandler(console_handler)

    return logger 

def time_counter(func):
    def wrapper():
        t1 = time.perf_counter()
        func()
        total = time.perf_counter() - t1

        print(f'{func.__name__}, {total:.4f} sec')

def wandb_setup(opt):

    t = TimeUtils()
    wandb.init(
        project=t.get_curr_time_attr(),
        
        # track hyperparameters and run metadata
        config={
        "learning_rate": opt.lr,
        "architecture": opt.model.upper(),
        "dataset": "VAC-MRT",
        "epochs": opt.epochs,
        }
    )
    
class MemoryUtils:
    def __init__(self):
        self.init_mem: float = None
        self.self_pid = os.getpid()

        self.sys_total_ram = psutil.virtual_memory().total

    def convert_unit(self, x, unit1='b', unit2='mb'):
        factors = {'b': 0, 'kb': 1, 'mb': 2, 'gb': 3, 'tb': 4}
        f1 = factors.get(unit1.lower(), 0)
        f2 = factors.get(unit2.lower(), 2)
        return x / (1024 ** (f2 - f1))

    def get_memory_usage(self, checkpoint: str) -> float:
        # get the current process ID
        pid = psutil.Process()

        # get the memory usage in bytes
        memory_bytes = pid.memory_info().rss

        # convert to megabytes
        memory_mb = self.convert_unit(memory_bytes)

        if self.init_mem is None:
            self.init_mem = memory_mb
            print(f"Checkpoint {checkpoint} Initial memory usage: {memory_mb:.2f} MB")
        else:
            memory_mb -= self.init_mem
            print(f"Checkpoint {checkpoint} Current memory usage (-init): {memory_mb:.2f} MB")

        return memory_mb

    # def set_ram_limit(self, percentage=None, custom_limit=None):
    #     if percentage and custom_limit:
    #         raise AttributeError('Percentage and custom limit conflict')
        
    #     elif percentage:
    #         max_ram = self.sys_total_ram * percentage / 100

    #     elif custom_limit: 
    #         value = custom_limit[0]
    #         unit = custom_limit[1]
    #         max_ram = self.convert_unit(value, unit1=unit, unit2='b')

    #     else:
    #         raise AttributeError('No values provided')

    #     max_ram = int(max_ram)
    #     soft, hard = resource.getrlimit(resource.RLIMIT_DATA)
    #     resource.setrlimit(resource.RLIMIT_DATA, (max_ram, hard))
    #     print(f'Set max RAM to {self.convert_unit(max_ram) :.1f} MB')


    def get_processes(self, top=10):
        # Get a list of all running processes and their memory usage
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            processes.append([proc.info['pid'], 
                            proc.info['name'], 
                            self.convert_unit(proc.info['memory_info'].rss)])

        # Sort the list of processes by memory usage (descending order)
        processes.sort(key=lambda x: x[2], reverse=True)
        rrm = psutil.virtual_memory().available

        if top:
            print(f"Top {top} process usage:")
            for pid, name, mem_usage in processes[:top]:
                print(f"PID: {pid:<8} | Name: {name:<20} | Memory Usage: {mem_usage:>8.1f} MB")

            print(f'Memory available: {self.convert_unit(rrm):.1f} MB')
        return processes

class TimeUtils:
    def __init__(self):
        self.days = ["Monday", "Tuesday", "Wednesday", 
                     "Thursday", "Friday", 
                     "Saturday", "Sunday"]
        self.time_attributes = ['year', 'month', 'day', 
                                'hour', 'minute', 'second']

    def get_current_time_attributes(self, num_attrs=6):
        now = datetime.datetime.now()
        timestamp = []
        for i, attr in enumerate(self.time_attributes):
            if i >= num_attrs:
                break
            value = getattr(now, attr)
            timestamp.append(f"{value:02d}")
        return '-'.join(timestamp)

    def get_day_of_week(self, timestamp=None):
        if timestamp is None: 
            timestamp = datetime.datetime.now()

        day_of_week = timestamp.weekday()
        return self.days[day_of_week]

def timer(func):
    def wrapper(*args, **kwargs):

        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()

        print(f"Execution time: {end_time - start_time:.6f} seconds")
        return result
    return wrapper
