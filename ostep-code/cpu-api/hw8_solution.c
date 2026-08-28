#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

int
main(void)
{
    int pipefd[2];

    if (pipe(pipefd) == -1) {
        perror("pipe");
        exit(1);
    }

    pid_t child1 = fork();

    if (child1 == -1) {
        perror("fork child1");
        exit(1);
    }

    if (child1 == 0) {
        // Connect child 1's stdout to the pipe's write end.
        if (dup2(pipefd[1], STDOUT_FILENO) == -1) {
            perror("dup2 child1");
            _exit(1);
        }

        close(pipefd[0]);
        close(pipefd[1]);

        const char message[] = "Hello from child 1\n";

        if (write(STDOUT_FILENO, message, sizeof(message) - 1) == -1) {
            perror("write child1");
            _exit(1);
        }

        _exit(0);
    }

    // Only the original parent reaches this fork.
    pid_t child2 = fork();

    if (child2 == -1) {
        perror("fork child2");
        close(pipefd[0]);
        close(pipefd[1]);
        waitpid(child1, NULL, 0);
        exit(1);
    }

    if (child2 == 0) {
        // Connect child 2's stdin to the pipe's read end.
        if (dup2(pipefd[0], STDIN_FILENO) == -1) {
            perror("dup2 child2");
            _exit(1);
        }

        close(pipefd[0]);
        close(pipefd[1]);

        char buffer[100];
        ssize_t bytes_read = read(STDIN_FILENO, buffer, sizeof(buffer));

        if (bytes_read == -1) {
            perror("read child2");
            _exit(1);
        }

        const char prefix[] = "Child 2 received: ";
        write(STDOUT_FILENO, prefix, sizeof(prefix) - 1);
        write(STDOUT_FILENO, buffer, (size_t) bytes_read);

        _exit(0);
    }

    // The parent does not use either end of the pipe.
    close(pipefd[0]);
    close(pipefd[1]);

    waitpid(child1, NULL, 0);
    waitpid(child2, NULL, 0);

    return 0;
}
