#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
	if (argc != 3) {
		printf("ERROR! Provide two numbers!\n");
		return 1;
	}
	// addition of two bits
	int a = atoi(argv[1]);
	int b = atoi(argv[2]);
	int c = a + b;
	printf("%d\n", c);
	return 0;
}