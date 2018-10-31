#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef enum
{
    GEOHASH_NORTH = 0,
    GEOHASH_EAST,
    GEOHASH_WEST,
    GEOHASH_SOUTH,
    GEOHASH_SOUTH_WEST,
    GEOHASH_SOUTH_EAST,
    GEOHASH_NORT_WEST,
    GEOHASH_NORT_EAST
} GeoDirection;

typedef struct
{
        uint64_t bits;
        uint8_t step;
} GeoHashBits;

typedef struct
{
        double max;
        double min;
} GeoHashRange;

typedef struct
{
        GeoHashBits hash;
        GeoHashRange latitude;
        GeoHashRange longitude;
} GeoHashArea;

typedef struct
{
        GeoHashBits north;
        GeoHashBits east;
        GeoHashBits west;
        GeoHashBits south;
        GeoHashBits north_east;
        GeoHashBits south_east;
        GeoHashBits north_west;
        GeoHashBits south_west;
} GeoHashNeighbors;

int geohash_encode(double latitude, double longitude, uint8_t step, GeoHashBits* hash)
 {
    if (NULL == hash || step > 32 || step == 0)
    {
        return -1;
    }
    GeoHashRange lat_range, lon_range;
    lat_range.max = 90.0;
    lat_range.min = -90.0;
    lon_range.max = 180.0;
    lon_range.min = -180.0;
    hash->bits = 0;
    hash->step = step;
    uint8_t i = 0;
    if (latitude < lat_range.min || latitude > lat_range.max || longitude < lon_range.min || longitude > lon_range.max)
    {
        return -1;
    }
    for (; i < step; i++)
    {
        uint8_t lat_bit, lon_bit;
        if (lat_range.max - latitude >= latitude - lat_range.min)
        {
            lat_bit = 0;
            lat_range.max = (lat_range.max + lat_range.min) / 2;
        }
        else
        {
            lat_bit = 1;
            lat_range.min = (lat_range.max + lat_range.min) / 2;
        }
        if (lon_range.max - longitude >= longitude - lon_range.min)
        {
            lon_bit = 0;
            lon_range.max = (lon_range.max + lon_range.min) / 2;
        }
        else
        {
            lon_bit = 1;
            lon_range.min = (lon_range.max + lon_range.min) / 2;
        }
        hash->bits <<= 1;
        hash->bits += lon_bit;
        hash->bits <<= 1;
        hash->bits += lat_bit;
    }
    return 0;
}

static inline uint8_t get_bit(uint64_t bits, uint8_t pos)
{
    return (bits >> pos) & 0x01;
}

int geohash_decode(const GeoHashBits* hash, GeoHashArea* area)
{
    if (NULL == hash || NULL == area)
    {
        return -1;
    }
    area->hash = *hash;
    uint8_t i = 0;
    area->latitude.min = -90.0;
    area->latitude.max = 90.0;
    area->longitude.min = -180.0;
    area->longitude.max = 180.0;
    for (; i < hash->step; i++)
    {
        uint8_t lat_bit, lon_bit;
        lon_bit = get_bit(hash->bits, (hash->step - i) * 2 - 1);
        lat_bit = get_bit(hash->bits, (hash->step - i) * 2 - 2);
        if (lat_bit == 0)
        {
            area->latitude.max = (area->latitude.max + area->latitude.min) / 2;
        }
        else
        {
            area->latitude.min = (area->latitude.max + area->latitude.min) / 2;
        }
        if (lon_bit == 0)
        {
            area->longitude.max = (area->longitude.max + area->longitude.min) / 2;
        }
        else
        {
            area->longitude.min = (area->longitude.max + area->longitude.min) / 2;
        }
    }
    return 0;
}

static int geohash_move_x(GeoHashBits* hash, int8_t d)
{
    if (d == 0)
        return 0;
    uint64_t x = hash->bits & 0xaaaaaaaaaaaaaaaaLL;
    uint64_t y = hash->bits & 0x5555555555555555LL;

    uint64_t zz = 0x5555555555555555LL >> (64 - hash->step * 2);
    if (d > 0)
    {
        x = x + (zz + 1);
    }
    else
    {
        x = x | zz;
        x = x - (zz + 1);
    }
    x &= (0xaaaaaaaaaaaaaaaaLL >> (64 - hash->step * 2));
    hash->bits = (x | y);
    return 0;
}

static int geohash_move_y(GeoHashBits* hash, int8_t d)
{
    if (d == 0)
        return 0;
    uint64_t x = hash->bits & 0xaaaaaaaaaaaaaaaaLL;
    uint64_t y = hash->bits & 0x5555555555555555LL;

    uint64_t zz = 0xaaaaaaaaaaaaaaaaLL >> (64 - hash->step * 2);
    if (d > 0)
    {
        y = y + (zz + 1);
    }
    else
    {
        y = y | zz;
        y = y - (zz + 1);
    }
    y &= (0x5555555555555555LL >> (64 - hash->step * 2));
    hash->bits = (x | y);
    return 0;
}

int geohash_get_neighbors(const GeoHashBits* hash, GeoHashNeighbors* neighbors)
{
    neighbors->east = *hash;
    neighbors->west = *hash;
    neighbors->north = *hash;
    neighbors->south = *hash;
    neighbors->south_east = *hash;
    neighbors->south_west = *hash;
    neighbors->north_east = *hash;
    neighbors->north_west = *hash;
    geohash_move_x(&neighbors->east, 1);
    geohash_move_y(&neighbors->east, 0);
    geohash_move_x(&neighbors->west, -1);
    geohash_move_y(&neighbors->west, 0);
    geohash_move_x(&neighbors->south, 0);
    geohash_move_y(&neighbors->south, -1);
    geohash_move_x(&neighbors->north, 0);
    geohash_move_y(&neighbors->north, 1);
    geohash_move_x(&neighbors->north_west, -1);
    geohash_move_y(&neighbors->north_west, 1);
    geohash_move_x(&neighbors->north_east, 1);
    geohash_move_y(&neighbors->north_east, 1);
    geohash_move_x(&neighbors->south_east, 1);
    geohash_move_y(&neighbors->south_east, -1);
    geohash_move_x(&neighbors->south_west, -1);
    geohash_move_y(&neighbors->south_west, -1);
    return 0;
}
