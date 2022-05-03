/**
 * @brief This is my first real C program I write, so might have some things useless
 * and that isn't conforming with the normes but anyways this is nothing
 * really usefull. As you have probably noticed, I use Doxygen to document my code.
 *
 * @author Lucas Maillet
 */

#include <stdio.h>
#include <stdlib.h>
#include <sys/ioctl.h>

#include "graph.h"
#include "cli.h"

/**
 * @brief Just a sample function used to fill an array
 * 
 * @param x The x-axis value
 * @return int 
 */
int fn(int x)
{
    return -x * x;
}

int main()
{
    struct winsize size;
    ioctl(0, TIOCGWINSZ, &size);

    Theme theme = {
        .background = '-',
        .marker = '=',
        .beforeMarker = "\033[33m",
        .afterMarker = "\033[0m",
        .stroke_size = 1,
        .n_cols = size.ws_col,
        .n_rows = size.ws_row - 1};

    // Get parameters
    size_t start, end, gap;
    printf("Enter size_t <start> <end> <gap> to create a range (must be over 10 values): ");
    scanf("%lu %lu %lu", &start, &end, &gap);

    // Create an array based on range
    Array data_x = range(start, end, gap);

    // Create an array with data_x as X values and fn(X) as Y values
    ArrayXY data = fromFn(&data_x, fn);
    graph(&data, &theme);

    // Get parameters
    printf("Enter a char* <filepath> to a .csv file: ");
    char *filepath = ask();

    // Create an array of array based on items for each lines of .csv file
    Array2D data_csv = fromCSV(filepath);
    free(filepath);

    // Create an array based on data_csv
    data = from2D(&data_csv);
    graph(&data, &theme);

    return 0;
}
