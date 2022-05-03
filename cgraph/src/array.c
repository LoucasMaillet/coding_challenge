#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "array.h"
#include "cli.h"

static const size_t MAX_BUFFER_SIZE = 1024 / sizeof(char);

#define append(array, item)          \
    _Generic(array, Array *          \
             : append_int, Array2D * \
             : append_array)(array, item)

void append_int(Array *array, int item)
{
    array->content = realloc(array->content, (array->length + 1) * sizeof(int));
    array->content[array->length++] = item;
}

void append_array(Array2D *array, Array *item)
{
    array->content = realloc(array->content, (array->length + 1) * sizeof(Array));
    array->content[array->length++] = *item;
}

Array range(int first, int last, int gap)
{
    check(gap == 0, ERROR_ARRAY_GAP);
    unsigned int s_gap = gap > 0;
    check(first < last && !s_gap || first > last && s_gap, ERROR_ARRAY_ILLOGICAL); // If it's need to increase or decrease but the gap won't work.
    Array res = {.length = (last - first) / gap};
    check(res.length == 0, ERROR_ARRAY_EMPTY);
    res.content = malloc(sizeof(int) * res.length);
    for (size_t i = 0; i < res.length; i++)
    {
        res.content[i] = first;
        first += gap;
    }
    return res;
}

Extrem extremum(int *(*array), size_t *length)
{
    Extrem res = {
        .max = 0,
        .min = (*array)[0]};
    for (size_t i = 0; i < *length; i++)
    {
        if ((*array)[i] > res.max)
            res.max = (*array)[i];
        else if ((*array)[i] < res.min)
            res.min = (*array)[i];
    }
    return res;
}

Array2D fromCSV(char *filepath)
{
    FILE *file = fopen(filepath, "r");
    check(file == NULL, ERROR_FILE);
    Array2D array = {};
    char line[MAX_BUFFER_SIZE];
    while (fgets(line, MAX_BUFFER_SIZE, file) != NULL)
    {
        Array child = {};
        char *item = strtok(line, ";");
        while (item != NULL)
        {
            append(&child, atoi(item));
            item = strtok(NULL, ";");
        }
        append(&array, &child);
    }
    fclose(file);
    check(array.length == 0, ERROR_ARRAY_EMPTY);
    return array;
}

ArrayXY fromFn(Array *x, int (*fn)(int))
{
    check(x->length == 0, ERROR_ARRAY_EMPTY);
    ArrayXY res = {
        .x = x->content,
        .y = malloc(sizeof(int) * x->length),
        .length = x->length,
        .x_ext = extremum(&x->content, &x->length)};
    for (size_t i = 0; i < res.length; i++)
    {
        res.y[i] = fn(res.x[i]);
    }
    res.y_ext = extremum(&res.y, &res.length);
    return res;
}

ArrayXY from2D(Array2D *array)
{
    ArrayXY res = {
        .x = malloc(sizeof(int) * array->length),
        .y = malloc(sizeof(int) * array->length),
        .length = array->length,
    };
    for (size_t i = 0; i < res.length; i++)
    {
        res.x[i] = array->content[i].content[0];
        res.y[i] = array->content[i].content[1];
    }
    res.x_ext = extremum(&res.x, &res.length);
    res.y_ext = extremum(&res.y, &res.length);
    return res;
}