#include <stdio.h>
#include <stdlib.h>

#include "cli.h"
#include "graph.h"

size_t digit(int number)
{
    size_t counter = 0;
    if (number <= 0)
        counter++;
    while (number != 0)
    {
        number = number / 10;
        counter++;
    }
    return counter;
}

size_t digit_ext(Extrem *ext)
{
    int d_max = digit(ext->max),
        d_min = digit(ext->min);
    if (d_max > d_min)
        return d_max;
    else
        return d_min;
}

char *charmult(char src, int occurence)
{
    char *str_res = (char *)calloc(occurence, sizeof(char));
    for (int i = 0; i < occurence; i++)
    {
        str_res[i] = src;
    }
    return str_res;
}

void graph(ArrayXY *array, Theme *theme)
{

    size_t unit_size = digit_ext(&array->y_ext) + 1,
           y_ratio = (abs(array->y_ext.max) + abs(array->y_ext.min)) / (theme->n_rows - 2), // -2 to fit without the last lines (x-axis and stdin)
           line_size = y_ratio * theme->stroke_size / 2,
           n_cols = theme->n_cols - unit_size,
           col;

    check(y_ratio == 0, ERROR_GRAPH);

    // printf("Raw statistics:\n\n\
    // width: %i\n\
    // heigth: %i\n\
    // y_ratio: %lu\n\
    // x_ext.max: %i\n\
    // x_ext.min: %i\n\
    // y_ext.max: %i\n\
    // y_ext.min: %i\n\
    // len: %lu\n\n",
    //        theme->n_cols, theme->n_rows, y_ratio, array->x_ext.max, array->x_ext.min, array->y_ext.max, array->y_ext.min, array->length);

    for (int row = array->y_ext.max; row > array->y_ext.min; row -= y_ratio)
    {
        printf("%s%i ", charmult(' ', unit_size - digit(row) - 1), row);
        for (col = 0; col < n_cols; col++)
        {
            int *y = &array->y[col * array->length / n_cols];
            if (abs(row - *y) < line_size)
                printf("%s%c%s", theme->beforeMarker, theme->marker, theme->afterMarker);
            else
                printf("%c", theme->background);
        }
        printf("\n");
    }

    printf("%s", charmult(' ', unit_size)); // Offset with the y-axis to start the x-axis

    unit_size = digit_ext(&array->x_ext) + 1;

    int last = array->x[array->length - 1];

    for (col = 0; col < n_cols - unit_size; col += unit_size)
    {
        int *x = &array->x[col * array->length / n_cols];
        if (last != *x)
        {
            char *str_x = malloc(sizeof(char) * unit_size);
            sprintf(str_x, "%i", *x);
            printf("%s%s", str_x, charmult(' ', unit_size - digit(*x)));
        }
        else
        {
            printf("%s", charmult(' ', unit_size));
        }
        last = *x;
    }

    int *xlast = &array->x[col * array->length / n_cols];

    if (col + digit(*xlast) <= n_cols && last != array->x[array->length - 1])
        printf("%i", *xlast);
    printf("\n");
}