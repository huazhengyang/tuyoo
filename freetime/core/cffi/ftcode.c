int ftcode(int seed, char *data, int datalen, char *out)
{
    unsigned randint = 0;
    char randchar;
    int i;
    randint = seed;
    for(i=0;i<datalen;i++)
    {
        randint = randint * 1103515245 + 12345;
        randint = (randint / 65536) % 32768;
        randchar = randint % 255;
        out[i]=data[i]^randchar;
    }
    return 0;
}
