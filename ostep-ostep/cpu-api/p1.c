// Question1
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int
main(int argc, char *argv[])
{
    int x = 100;
    printf("x : %d\n", x);
    printf("hello world (pid:%d)\n", (int) getpid());
    int rc = fork();
    printf("rc right after fork: %d\n", rc);
    if (rc < 0) {
        // fork failed; exit
        fprintf(stderr, "fork failed\n");
        exit(1);
    } else if (rc == 0) {
        // child (new process)
        printf("==== hello, I am child (pid:%d) ====\n", (int) getpid());
        printf("rc: %d\n", rc);
        printf("child x : %d\n", x);
        
        x = 200;
        printf("** change child x **\n");
        printf("child x : %d\n", x);
    } else {
        // parent goes down this path (original process)
        printf("==== hello, I am parent (pid:%d) ====\n", (int) getpid());
        printf("rc: %d\n", rc);
        printf("parent x : %d\n", x);        
        x = 300;
        printf("** change parent x ** \n");
        printf("parent x : %d\n", x);
    }
    return 0;
}
