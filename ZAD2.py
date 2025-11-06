import sys
import time
import os

def zad2(file_path):
    "Tworzy lub czyści plik a następnie co sekundę dopisuje numerowaną linię."

    try:

        with open(file_path, 'w') as f:
            f.write("Start logowania.\n")
    except IOError as e:
        print(f"Bląd dostępu do pliku {file_path}: {e}")
        sys.exit(1)

    print(f"rozpoczęto logowanie do pliku {file_path}")
    
    line_number = 0
    while True:
        try:

            with open(file_path, 'a') as f:
                log_line = f"Linia numer: {line_number}\n"
                f.write(log_line)
                print(f"Dopisano: {log_line.strip()}")
                line_number += 1
            time.sleep(1)
        except IOError as e:
            print(f"\n wystąpił bląd zapisu plik usuniety: {e}")
            time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Użycie: {sys.argv[0]} <nazwa_pliku>")
        sys.exit(1)
        
    file_to_log = sys.argv[1]
    zad2(file_to_log)