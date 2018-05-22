#include "../testlib.h"
#include <iostream>
#include <set>
#include <algorithm>
#include <cstdint>
#include <cassert>
using namespace std;


const int number_of_tests = 30;
const int number_of_pieces = 28; //number of dominó pieces
const int max_number_of_pieces = 8; //maximum number of dominó pieces
const int number_of_manual_tests = 3;

void generate_test(int i){
    startTest(i);
    uint64_t n;
    vector<pair<int,int>> v;
    for(int i =0 ; i < 7;i++){
        for(int j=i;j<7;j++){
            v.push_back(make_pair(i,j));
        }
    }
    assert(v.size() == number_of_pieces);   
    n = rnd.next(1,max_number_of_pieces);
    cout << n << "\n";
    shuffle(v.begin(),v.end());
    for(int i=0;i<n;i++){
        cout << v[i].first << '|' << v[i].second;
        if(i<n-1){
            cout << ' ';
        }
        else{ 
            cout << '\n';
        }
    }
}

int main(int argc, char* argv[]){
    //The first 3 tests are manually generated
    registerGen(argc, argv, 1);
    for(uint64_t i=number_of_manual_tests;i<number_of_tests;i++){
        generate_test(i);
    }    
}