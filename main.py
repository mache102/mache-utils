import time 
from utils import timer

def func(s):
    for x in range(s):
        time.sleep(x / 100)

@timer
func(5)
