#include <stdio.h>
#include <stdlib.h>

#include "cli.h"

char *ask(void)
{
    char *str;
    int null, c, i = 0;
    scanf("%i", &null);
    while ((c = getchar()) != '\n' && c != EOF)
    {
        str = realloc(str, (i + 1) * sizeof(char));
        str[i++] = c;
    }
    return str;
}