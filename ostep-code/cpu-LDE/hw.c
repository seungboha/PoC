
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
    for (int i = 0; i < 10; i++) 
    {
        uint64_t start = now_us();
        uint64_t end = now_us();

        printf("Difference: %llu microseconds\n",
               (unsigned long long)(end - start));
    }
}


static void measure_system_call(void)
{
    uint64_t start = now_us();
    int fd = open("/dev/null", O_RDONLY);

    
    for (int i = 0; i < ITERATIONS; i++) {
        if (read(fd, NULL, 0) == -1) {
            perror("read");
            exit(1);
        }
    }
    close(fd);
    uint64_t end = now_us();
    
    printf("Difference: %llu microseconds\n",
           (unsigned long long)(end - start));
    
}