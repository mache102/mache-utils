#!/bin/bash

# cpu usage warning threshold
cpuThreshold=95
# memory usage warning threshold
memThreshold=95

cpuNotifShown=false
memNotifShown=false

while :
do 
    # Get the current usage of CPU and memory
    cpuUsage=$(top -bn1 | awk '/Cpu/ { print $2}' | cut -d. -f1)
    memUsage=$(free -m | awk '/Mem/{print $3}' | cut -d. -f1)

    if [[ $cpuUsage -gt $cpuThreshold && $cpuNotifShown == false ]]
    then
        notify-send "CPU usage is over $cpuThreshold%. Yeet some processes?"
        # Run your performance monitor command here, but it might not work as intended
        # perfmon
        cpuNotifShown=true
    elif [[ $cpuUsage -le $cpuThreshold && $cpuNotifShown == true ]]
    then
        cpuNotifShown=false
    fi 


    if [[ $memUsage -gt $memThreshold && $memNotifShown == false ]]
    then
        notify-send "Memory usage is over $memThreshold%. Yeet some processes?"
        # Run your performance monitor command here, but it might not work as intended
        # perfmon
        memNotifShown=true
    elif [[ $memUsage -le $memThreshold && $memNotifShown == true ]]
    then
        memNotifShown=false
    fi
    
    sleep 0.1
done
