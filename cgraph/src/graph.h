/**
 * @file graph.c
 * @author Lucas Mailllet (https://github.com/LoucasMaillet)
 * @brief Print graphic from array.
 * @version 0.1
 * @date 2021-12-21
 *
 * @copyright Copyright (c) 2021
 */

#ifndef GRAPH_HEADER
#define GRAPH_HEADER

#include "array.h"

/**
 * @brief Theme settings for graph
 */
typedef struct
{
    char background;
    char marker;
    char *beforeMarker;
    char *afterMarker;
    float stroke_size;
    int n_cols;
    int n_rows;
} Theme;

/**
 * @brief Count the digits of a number
 *
 * @param number The number counted
 *
 * @return size_t
 */
size_t digit(int number);

/**
 * @brief Get the maximum number of digit based on Extremum
 *
 * @param ext Extremum of an Array
 *
 * @return size_t
 */
size_t digit_ext(Extrem *ext);

/**
 * @brief Multiply a character in a string
 *
 * @param src The character to duplicate
 * @param occurence The number of multiplication
 *
 * @return char*
 */
char *charmult(char src, int occurence);

/**
 * @brief  Create a graphic representation of function data
 *
 * @param array Data to show
 * @param theme Theme used
 */
void graph(ArrayXY *array, Theme *theme);

#endif