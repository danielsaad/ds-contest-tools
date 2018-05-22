#include "testlib.h"
#include <bits/stdc++.h>

const int number_of_manual_tests = 3;
const int number_of_tests = 60;

void manual_tests(){
    startTest(1);
    // Print manual test 1
    startTest(2);
    // Print manual test 2
    startTest(3);
    // Print manual test 3
}

void generate_test(int i){
    startTest(i);
}


int main(int argc, char* argv[]){
    //The first 3 tests are manually generated
    manual_tests();
    registerGen(argc, argv, 1);
    for(uint64_t i=number_of_manual_test+1;i<=number_of_tests;i++){
        generate_test(i);
    }    
}