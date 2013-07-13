// reading a text file
#include <iostream>
#include <fstream>
#include <stdint.h>
#include <string>
using namespace std;

unsigned long long int count(int numbers[], int length);
unsigned long long int countSplitInversions(int arr[], int length);

int main () {
    int numbers[100000];
    
    string line;
    ifstream myfile ("/Users/tjordan/Desktop/Algo/hw1/algoHW1/algoHW1/IntegerArray.txt");
    if (myfile.is_open()) {
        int position = 0;
        while ( myfile.good() ) {
            getline (myfile,line);
            numbers[position] = atoi(line.c_str());
            position++;
        }
        myfile.close();
    }
    
    else cout << "Unable to open file";
    
    int arr[] =  {1,3,5,7,9,11,2,4,6,8,10};
    printf(" Number of inversions are  %llu \n", count(numbers, 100000));
    getchar();
    
    return 0;
}

unsigned long long int count (int *numbers , int length ) {
    static unsigned long long int invCount = 0;
    if (length == 1)
        return 0;
    else {
        unsigned int i,j,k, size;
        int *tmp;
        size = length / 2;
        
        
        count(numbers, size);
        count(&numbers[size], length - size);
        invCount += countSplitInversions(numbers, length);
        
        return invCount;
    }
}

unsigned long long int countSplitInversions(int arr[] , int length) {
    unsigned int i,j,k;
    unsigned long long int invCounter = 0;
    int *tmp;
    
    tmp = (int *)malloc(length*sizeof(int));
    
    // copy elements over from arr into temp
    for(i = 0; i < length / 2; i++)
        tmp[i] = arr[i];
    
    //reverses the order
    for(j = length - 1; i < length; i++, j--)
        tmp[j] = arr[i];
    
    
    for(k = 0, i = 0, j = length - 1; k < length; k++) {
        if(tmp[i] <= tmp[j])
            arr[k] = tmp[i++];
        else {
            invCounter += length/2 - i;
            arr[k] = tmp[j--];
        }
    }
    free(tmp);
    
    return invCounter;
}