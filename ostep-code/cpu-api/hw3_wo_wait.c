#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>

volatile sig_atomic_t child_finished = 0;

void handle_signal(int signal)
{
    child_finished = 1;
}

int main(int argc, char *argv[])
{
    signal(SIGUSR1, handle_signal);

    // printf("hello world (pid:%d)\n", (int) getpid());
    int rc = fork();
    if (rc < 0) {
        // fork failed; exit
        fprintf(stderr, "fork failed\n");
        exit(1);
    } else if (rc == 0) {
        // child (new process)
        printf("Hello\n");
        kill(getppid(), SIGUSR1); // Send a signal to the parent process

    } else {
        // parent goes down this path (original process)
        while (!child_finished) {
            // Wait for the child to finish
            pause();
        }
        printf("Goodbye\n");
    }
    return 0;
}


