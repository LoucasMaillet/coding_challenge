/**
 * @file cli.c
 * @author Lucas Mailllet (https://github.com/LoucasMaillet)
 * @brief Handle errors.
 * @version 0.1
 * @date 2021-12-21
 *
 * @copyright Copyright (c) 2021
 */

#ifndef ERROR_HEADER
#define ERROR_HEADER

// Errors tag

#define ERROR_FILE "FileError: 404 File not found"
#define ERROR_ARRAY_EMPTY "ArrayError: Attempt to create an empty array"
#define ERROR_ARRAY_GAP "ArrayError: Gap between each values must not be zero"
#define ERROR_ARRAY_ILLOGICAL "ArrayError: Attempt to create an array with an illogical range"
#define ERROR_GRAPH "GraphError: Extremums are not high enough to see a difference"

/**
 * @brief Check a condition to throw an error
 *
 * @param condition Condition to throw the error
 * @param error_tag Tag to show before exit
 */
#define check(condition, error_tag) (                                                                                                        \
    {                                                                                                                                        \
        if (condition)                                                                                                                       \
        {                                                                                                                                    \
            fprintf(stderr, "\rTraceback (before exit):\n    File \"%s\", line %i, in %s()\n%s\n", __FILE__, __LINE__, __func__, error_tag); \
            exit(-1);                                                                                                                        \
        };                                                                                                                                   \
    })

/**
 * @brief Get full stdin in a string
 *
 * @return char*
 */
char *ask(void);

#endif