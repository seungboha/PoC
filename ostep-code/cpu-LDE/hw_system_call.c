
#include <fcntl.h>    // open
#include <unistd.h>   // read, write, close

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>

#define ITERATIONS 1000000


static uint64_t now_us(void);
static void back_to_back_measurement(void);
static void measure_system_call(void);




int main(void)
{
    printf("gettimeofday measurement doing nothing\n");
    back_to_back_measurement();
    printf("measure system call\n");
    measure_system_call();
    return 0;
}

static uint64_t now_us(void)
{
    struct timeval tv;

    if (gettimeofday(&tv, NULL) == -1) {
        perror("gettimeofday");
        exit(1);
    }

    return (uint64_t)tv.tv_sec * 1000000ULL + tv.tv_usec;
}



static void back_to_back_measurement(void)
{
    for (int i = 0; i < 5; i++) 
    {
        uint64_t start = now_us();
        uint64_t end = now_us();

        printf("Difference: %llu microseconds\n",
               (unsigned long long)(end - start));
    }
}


static void measure_system_call(void)
{
    int fd = open("/dev/null", O_RDONLY);
    if (fd == -1) {
        perror("open");
        exit(1);
    }

    uint64_t start = now_us();

    for (int i = 0; i < ITERATIONS; i++) {
        if (read(fd, NULL, 0) == -1) {
            perror("read");
            exit(1);
        }
    }
    
    uint64_t end = now_us();
    close(fd);

    uint64_t elapsed_us = end - start;
    double average_ns = elapsed_us * 1000.0 / ITERATIONS;

    printf("Total: %llu microseconds\n",
        (unsigned long long)elapsed_us);
    printf("Average: %.2f nanoseconds\n", average_ns);
    
}
