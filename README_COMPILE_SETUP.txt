https://www.msys2.org/

Get msys2 and install MinGW 64 bit

___

compile with:
gcc -c -march=native -fopenmp -pipe -Wall  -fPIC -O3 -lm hkl.c
gcc -shared -Wall -march=native -fopenmp -pipe -O3  -lm hkl.o -o libhkl.dll


___

Use conda to install python 3.6 into environment "chess" and activate with:
conda activate chess

___

Now the compiled .dll should work and multithreading should work
