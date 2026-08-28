#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <assert.h>
#include <sys/wait.h>
#include <sys/stat.h>

int
main(int argc, char *argv[])
{
    printf("hello world (pid:%d)\n", (int) getpid());

    // int rc = fork(); --> overwrites the file descriptor table of the child process, so we need to open the file before forking
    int fd = open("./hw2.txt", O_CREAT | O_WRONLY | O_TRUNC, S_IRWXU);
    if (fd < 0) {
        perror("open");
        exit(1);
    }

    int rc = fork();

    if (rc < 0) {
        // fork failed; exit
        fprintf(stderr, "fork failed\n");
        exit(1);
    } else if (rc == 0) {
        // child (new process)
        printf("hello, I am child (pid:%d)\n", (int) getpid());
        const char *message = "Hello from child.c\n";
        write(fd, message, strlen(message));
    } else {
        // parent goes down this path (original process)
        printf("hello, I am parent of %d (pid:%d)\n",
	       rc, (int) getpid());
        const char *message = "Hello from parent.c\n";
        write(fd, message, strlen(message));
    }
    return 0;
}