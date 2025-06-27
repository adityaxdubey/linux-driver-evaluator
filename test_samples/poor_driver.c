#include <stdio.h>

char buffer[1000];

int main() {
    char input[2000];
    printf("Enter data: ");
    gets(input);
    strcpy(buffer, input);
    return 0;
}