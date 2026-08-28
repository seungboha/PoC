#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/wait.h>

int main(int argc, char *argv[])
{
    printf("hello world (pid:%d)\n", (int) getpid());
    int rc = fork();

    if (rc < 0) {
        // fork failed; exit
        fprintf(stderr, "fork failed\n");
        exit(1);
    } else if (rc == 0) {
        // child (new process)
        printf("Child - (pid:%d)\n", (int) getpid());

    } else {
        // parent goes down this path (original process)
        // int wait_status = wait(NULL);
        int status;
        int wait_status = waitpid(rc, &status, 0);
        if (WIFEXITED(status)) {
            printf("Child exited with %d\n", WEXITSTATUS(status));
        }

        printf("wait_status: %d\n", wait_status);
        printf("Parent - (pid:%d)\n", (int) getpid());
    }
    return 0;
}


