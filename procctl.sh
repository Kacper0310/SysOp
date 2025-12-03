#!/bin/bash
# procctl script

proc_list_cpu() {
    ps aux --sort=-%cpu | head -n 6
}

proc_list_mem() {
    ps aux --sort=-%mem | head -n 6
}

proc_tree() {
    pstree -p
}

proc_name_by_pid() {
    read -p "PID: " pid
    ps -p "$pid" -o comm=
}

proc_pid_by_name() {
    read -p "Process name: " name
    pgrep "$name"
}

proc_kill_pid() {
    read -p "PID to kill: " pid
    kill "$pid"
}

proc_kill_name() {
    read -p "Process name to kill: " name
    pkill "$name"
}

while true; do
    echo ""
    echo "Process Control:"
    echo "1) List top 5 processes by CPU usage"
    echo "2) List top 5 processes by memory usage"
    echo "3) Show process tree"
    echo "4) Show process name by PID"
    echo "5) Show process PID(s) by name"
    echo "6) Kill process by PID"
    echo "7) Kill process by name"
    echo "q) Exit"
    read -p "Choice: " choice

    case "$choice" in
        1) proc_list_cpu ;;
        2) proc_list_mem ;;
        3) proc_tree ;;
        4) proc_name_by_pid ;;
        5) proc_pid_by_name ;;
        6) proc_kill_pid ;;
        7) proc_kill_name ;;
        q) exit 0 ;;
        *) echo "Invalid choice" ;;
    esac
done
