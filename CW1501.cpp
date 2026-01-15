#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>
#include <pthread.h>
#include <thread>

struct SharedData {
    unsigned int counts[26];
    double ascii_sum;
    pthread_mutex_t mutex;
};

int main(int argc, char* argv[]) {
    if (argc < 2) return 1;

    const char* filepath = argv[1];
    int num_processes = (argc > 2) ? std::stoi(argv[2]) : std::thread::hardware_concurrency();
    if (num_processes < 1) num_processes = 1;

    int fd = open(filepath, O_RDONLY);
    if (fd == -1) return 1;

    struct stat sb;
    fstat(fd, &sb);
    size_t filesize = sb.st_size;

    char* file_mem = (char*)mmap(NULL, filesize, PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd);

    SharedData* shared = (SharedData*)mmap(NULL, sizeof(SharedData), 
                                           PROT_READ | PROT_WRITE, 
                                           MAP_SHARED | MAP_ANONYMOUS, -1, 0);

    for(int i = 0; i < 26; ++i) shared->counts[i] = 0;
    shared->ascii_sum = 0.0;

    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
    pthread_mutex_init(&shared->mutex, &attr);

    size_t chunk_size = filesize / num_processes;

    for (int i = 0; i < num_processes; ++i) {
        pid_t pid = fork();
        if (pid == 0) {
            size_t start = i * chunk_size;
            size_t end = (i == num_processes - 1) ? filesize : (i + 1) * chunk_size;

            unsigned int local_counts[26] = {0};
            double local_sum = 0.0;

            for (size_t j = start; j < end; ++j) {
                unsigned char c = file_mem[j];
                local_sum += std::sqrt((double)c);

                if (c >= 'A' && c <= 'Z') local_counts[c - 'A']++;
                else if (c >= 'a' && c <= 'z') local_counts[c - 'a']++;
            }
            pthread_mutex_lock(&shared->mutex);
            for (int k = 0; k < 26; ++k) shared->counts[k] += local_counts[k];
            shared->ascii_sum += local_sum;
            pthread_mutex_unlock(&shared->mutex);

            munmap(file_mem, filesize);
            exit(0);
        }
    }

    for (int i = 0; i < num_processes; ++i) wait(NULL);

    for (int i = 0; i < 26; ++i) {
        std::cout << (char)('a' + i) << ": " << shared->counts[i] << " ";
        if ((i + 1) % 13 == 0) std::cout << std::endl;
    }
    std::cout << "\nSuma: " << shared->ascii_sum << std::endl;

    pthread_mutex_destroy(&shared->mutex);
    pthread_mutexattr_destroy(&attr);
    munmap(shared, sizeof(SharedData));
    munmap(file_mem, filesize);

    return 0;
}