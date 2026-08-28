#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/wait.h>

int main(int argc, char *argv[])
{
    printf("before fork");
    // fflush(stdout);

    int rc = fork();

    if (rc < 0) {
        // fork failed; exit
        fprintf(stderr, "fork failed\n");
        exit(1);
    } else if (rc == 0) {
        // child (new process)
        printf("Child - (pid:%d)\n", (int) getpid());
        printf("Before closing standard output\n");
        close(STDOUT_FILENO); // Close standard output
      
        int printf_result = printf("hello from child\n");
        int flush_result = fflush(stdout);

        fprintf(stderr, "printf returned: %d\n", printf_result);

        if (flush_result == EOF) {
            perror("fflush");
        }



    } else {
        // parent goes down this path (original process)
        // int wait_status = wait(NULL);
        int status;
        int waited_pid = waitpid(rc, &status, 0);
        if (waited_pid == -1) {
            perror("waitpid");
            exit(1);
        }
        if (WIFEXITED(status)) {
            printf("Child exited with %d\n", WEXITSTATUS(status));
        }

        printf("Parent - (pid:%d)\n", (int) getpid());
    }
    return 0;
}


