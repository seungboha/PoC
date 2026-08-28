#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/wait.h>

int main(int argc, char *argv[])
{   
    int pipefd[2];

    if (pipe(pipefd) == -1) {
        perror("pipe");
        exit(1);
    }

    int rc1 = fork();

    if (rc1 < 0) {
        // fork failed; exit
        fprintf(stderr, "fork failed\n");
        exit(1);
    } else if (rc1 == 0) {
        fprintf(stderr, "Child1 - (pid:%d)\n", (int) getpid());
        dup2(pipefd[1], STDOUT_FILENO); // Redirect standard output to the write end of the pipe
        fprintf(stdout, "Hello from child1\n");
        fflush(stdout);
        _exit(0);

    } else {
        // parent goes down this path (original process)
        waitpid(rc1, NULL, 0);
        close(pipefd[1]); // Close the write end of the pipe in the parent
        fprintf(stderr, "Parent - (pid:%d)\n", (int) getpid());
    }

    int rc2 = fork();

    if (rc2 < 0) 
    {
        // fork failed; exit
        fprintf(stderr, "fork failed\n");
        exit(1);
    } 
    else if (rc2 == 0) 
    {
        fprintf(stderr, "Child2 - (pid:%d)\n", (int) getpid());
        dup2(pipefd[0], STDIN_FILENO);

        close(pipefd[0]);

        char buffer[100];
        ssize_t bytes_read = read(STDIN_FILENO, buffer, sizeof(buffer) - 1);

        if (bytes_read > 0) {
            buffer[bytes_read] = '\0';
            fprintf(stderr, "Child2 received: %s", buffer);
        }

        _exit(0);
    }
    else {
        // parent goes down this path (original process)
        waitpid(rc2, NULL, 0);
        fprintf(stderr, "Parent - (pid:%d)\n", (int) getpid());
    }

    return 0;
}


