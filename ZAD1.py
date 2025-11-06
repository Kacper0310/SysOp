import os
import pwd
import glob

def ps_eo_user_pid_comm():
    "odczytuje i wyswietla listę procesow nasladując 'ps -eo user,pid,comm'."
    print(f"{'USER':<8} {'PID':>6} COMM")
    
    for entry in os.listdir('/proc'):
        if entry.isdigit():
            pid = entry
            proc_dir = os.path.join('/proc', pid)
            
            try:
                stat_info = os.stat(proc_dir)
                uid = stat_info.st_uid
                user_info = pwd.getpwuid(uid)
                user_name = user_info.pw_name
            except (FileNotFoundError, KeyError):
                continue
            
            try:
                with open(os.path.join(proc_dir, 'comm'), 'r') as f:
                    comm = f.read().strip()
            except FileNotFoundError:
                continue
            
            print(f"{user_name:<8} {pid:>6} {comm}")

if __name__ == "__main__":
    try:
        ps_eo_user_pid_comm()
    except PermissionError:
        print("blad - wymagane uprawnienia do odczytu niektórych danych w /proc")
    except Exception as e:
        print(f" wyjatek: {e}")