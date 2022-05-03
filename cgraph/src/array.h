/**
 * @file array.c
 * @author Lucas Mailllet (https://github.com/LoucasMaillet)
 * @brief Create dynamicly avanced array.
 * @version 0.1
 * @date 2021-12-21
 *
 * @copyright Copyright (c) 2021
 */

#ifndef ARRAY_HEADER
#define ARRAY_HEADER

/**
 * @brief Maximum and minimum of array
 */
typedef struct
{
    int max;
    int min;
} Extrem;

/**
 * @brief Array with length
 */
typedef struct
{
    int *content;
    size_t length;
    Extrem ex;
} Array;

/**
 * @brief 2D array with length
 */
typedef struct
{
    Array *content;
    size_t length;
} Array2D;

/**
 * @brief XY array with extremum and length
 */
typedef struct
{
    int *x;
    int *y;
    size_t length;
    Extrem x_ext;
    Extrem y_ext;
} ArrayXY;

/**
 * @brief Get the maximum and the minimum of an array
 *
 * @param array Pointer to the array
 * @param length pointer in the length of the array
 * 
 * @return Extrem
 */
Extrem extremum(int *(*array), size_t *length);

/**
 * @brief Create an array, just like in python
 *
 * @param first First value
 * @param last Last value
 * @param gap Value between each value
 * 
 * @return Array
 */
Array range(int first, int last, int gap);

/**
 * @brief Append an item (Array or int) to an Array
 *
 * @param array Array or Array2D
 * @param item Array or int
 */
void append(void *array, void *item);

/**
 * @brief Create an Array2D based on content of a CSV file
 *
 * @param filepath File's path
 * 
 * @return Array2D
 */
Array2D fromCSV(char *filepath);

/**
 * @brief Create an ArraXY based on Array2D
 *
 * @param data Array2D content
 * 
 * @return ArrayXY
 */
ArrayXY from2D(Array2D *data);

/**
 * @brief Create an ArrayXY based on Array and function
 *
 * @param x X-axis values
 * @param fn Function dealing with x values
 * 
 * @return ArrayXY
 */
ArrayXY fromFn(Array *x, int (*fn)(int));

#endif