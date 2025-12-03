print_cpu() {
    echo -n "CPU: "
    grep -m1 "model name" /proc/cpuinfo | cut -d: -f2 | sed 's/^ //'
}

print_ram() {
    read used total <<< $(free -m | awk '/Mem:/ {print $3, $2}')
    perc=$((100 * used / total))
    echo "RAM: ${used} / ${total} MiB (${perc}% used)"
}


print_load() {
    echo -n "Load: "
    uptime | awk -F'load average:' '{print $2}' | sed 's/^ //'
}

print_uptime() {
    up=$(uptime -p | sed 's/up //')
    echo "Uptime: $up"
}

print_kernel() {
    echo "Kernel: $(uname -r)"
}

print_gpu() {
    echo -n "GPU: "
    lspci | grep -i 'vga\|3d\|display' | head -n1 | cut -d':' -f3- | sed 's/^ //'
}

print_user() {
    echo "User: $(whoami)"
}

print_shell() {
    echo "Shell: $(basename "$SHELL")"
}

print_processes() {
    echo "Processes: $(ps -e | wc -l)"
}


print_threads() {
    echo "Threads: $(ps -eLf | wc -l)"
}

print_ip() {
    echo -n "IP: "
    ip -o -4 addr show | awk '{print $4}' | paste -sd ' '
}

print_dns() {
    echo -n "DNS: "
    grep nameserver /etc/resolv.conf | awk '{print $2}' | paste -sd ' '
}

print_internet() {
    if timeout 1 ping -c1 8.8.8.8 >/dev/null 2>&1; then
        echo "Internet: OK"
    else
        echo "Internet: FAIL"
    fi
}

all_functions=(print_cpu print_ram print_load print_uptime print_kernel print_gpu print_user print_shell print_processes print_threads print_ip print_dns print_internet)

if [ $# -eq 0 ]; then
    for fn in "${all_functions[@]}"; do $fn; done
    exit 0
fi

for arg in "$@"; do
    match=false
    for fn in "${all_functions[@]}"; do
        name=${fn#print_}
        if [[ "${name,,}" == "${arg,,}" ]]; then
            $fn
            match=true
        fi
    done
    if ! $match; then
        echo "Invalid argument: $arg" >&2
        exit 1
    fi
done

exit 0
