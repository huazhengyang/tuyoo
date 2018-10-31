#include <unistd.h>
#include <errno.h>

ssize_t ftpread(int fd, void *buf, size_t count, off_t offset)
{
    //printf("fd=%d, buf=%p, count=%d, offset=%d\n", fd, buf, count, offset);
    ssize_t ret = pread(fd, buf, count, offset);
    //printf("ret=%d, error=%d\n", ret, errno);
    return ret;
}

ssize_t ftpwrite(int fd, const void *buf, size_t count, off_t offset)
{
    //printf("fd=%d, buf=%p, count=%d, offset=%d\n", fd, buf, count, offset);
    ssize_t ret = pwrite(fd, buf, count, offset);
    //printf("ret=%d, error=%d\n", ret, errno);
    return ret;
}
