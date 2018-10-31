#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/types.h>

#define LOG_MAX_SIZE 4096
#define LOG_HEAD_SIZE 256

typedef struct {
    long long start_id;
    long rec_count;
    char res[LOG_HEAD_SIZE-sizeof(long long)-sizeof(long)];
} LOGHEAD;

int
main(int argc, char *argv[]) {
    if (argc != 5) {
        fprintf(stderr, "Usage:mkbi <bi_file_pathname> <start_id> <rec_count> <rec_size>\n");
        return 1;
    }
    int     fd;
    long    i;
    LOGHEAD loghead;
    char    logrec[LOG_MAX_SIZE];
    char *  filepath = argv[1];
    long long   start_id = atoll(argv[2]);
    long    rec_count = atol(argv[3]);
    int     rec_size = atoi(argv[4]);
    if(rec_size > LOG_MAX_SIZE){
        fprintf(stderr, "Error: Input Record Size %d > Log Record Max Size %d\n", rec_size, LOG_MAX_SIZE);
        return 2;
    }

    printf("LOGHEAD SIZE=%lu\n", sizeof(LOGHEAD));
    memset(&loghead, 0, sizeof(LOGHEAD));

    loghead.start_id = start_id;
    loghead.rec_count = rec_count;
    printf("start_id=%llu\n", start_id);
    printf("rec_count=%lu\n", rec_count);
    printf("rec_size=%u\n", rec_size);
    
    memset(logrec, 0, rec_size);
    logrec[0] ='T';
    logrec[1] ='U';
    logrec[rec_size-2]='Y';
    logrec[rec_size-1]='O';
    
    if((fd = open(filepath, O_RDWR | O_CREAT, 0777))<0) {
        fprintf(stderr, "Open file %s error!\n", filepath);
        return 3;
    }
    
    write(fd, &loghead, sizeof(LOGHEAD));
    
    for(i=0;i<rec_count;i++)
        write(fd, logrec, rec_size);
    
    close(fd);
    return 0;
}
