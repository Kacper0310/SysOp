import sys
import csv
from collections import deque

class Process:
    def __init__(self, name, length, start):
        self.name = name
        self.remaining_time = int(length)
        self.start_time = int(start)
        self.initial_length = int(length)

    def __repr__(self):
        return f"{self.name}(len={self.initial_length}, start={self.start_time})"

class RoundRobinScheduler:
    def __init__(self, processes, quantum):
        self.waiting_to_arrive = deque(processes)
        self.ready_queue = deque()
        self.quantum = quantum
        self.current_time = 0

    def run(self):
        while self.waiting_to_arrive or self.ready_queue:
            new_arrivals = False
            while self.waiting_to_arrive and self.waiting_to_arrive[0].start_time <= self.current_time:
                p = self.waiting_to_arrive.popleft()
                self.ready_queue.append(p)
                print(f"T={self.current_time}: New process {p.name} is waiting for execution (length={p.initial_length})")
                new_arrivals = True

            if not self.ready_queue:
                if self.waiting_to_arrive:
                    print(f"T={self.current_time}: No processes currently available")
                    self.current_time = self.waiting_to_arrive[0].start_time
                    continue
                else:
                    break

            current_process = self.ready_queue.popleft()
            
            run_duration = min(self.quantum, current_process.remaining_time)
            
            print(f"T={self.current_time}: {current_process.name} will be running for {run_duration} time units. "
                  f"Time left: {current_process.remaining_time - run_duration}")

            for _ in range(run_duration):
                self.current_time += 1
                while self.waiting_to_arrive and self.waiting_to_arrive[0].start_time <= self.current_time:
                    p = self.waiting_to_arrive.popleft()
                    self.ready_queue.append(p)
                    print(f"T={self.current_time}: New process {p.name} is waiting for execution (length={p.initial_length})")

            current_process.remaining_time -= run_duration

            if current_process.remaining_time > 0:
                self.ready_queue.append(current_process)
            else:
                print(f"T={self.current_time}: Process {current_process.name} has been finished")

        print(f"T={self.current_time}: No more processes in queues")

def main():
    if len(sys.argv) < 3:
        print("Użycie: python rr.py <plik.csv> <kwant_czasu>")
        return

    file_path = sys.argv[1]
    try:
        quantum = int(sys.argv[2])
    except ValueError:
        print("Kwant czasu musi być liczbą całkowitą.")
        return

    processes = []
    try:
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    processes.append(Process(row[0], row[1], row[2]))
    except FileNotFoundError:
        print(f"Nie znaleziono pliku: {file_path}")
        return

    scheduler = RoundRobinScheduler(processes, quantum)
    scheduler.run()

if __name__ == "__main__":
    main()