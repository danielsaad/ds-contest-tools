#include "testlib.h"
#include <bits/stdc++.h>

using namespace std;

const int MIN_N = 0;
const int MAX_N = 100;

const int rnd_test_n = 100;

template <typename T> void append(vector<T> &dest, const vector<T> &orig) {
	dest.insert(dest.end(), orig.begin(), orig.end());
}

string output_tc(int x, int y) {
	ostringstream oss;
    oss << x << " " << y << endl;
	return oss.str();
}

vector<string> generate_sample_tests() {
	vector<string> tests;
    tests.push_back(output_tc(1, 1));
    tests.push_back(output_tc(2, 2));
    tests.push_back(output_tc(0, 0));
	return tests;
}

vector<string> generate_manual_tests() {
	vector<string> tests;
	tests.push_back(output_tc(100, 0));
	tests.push_back(output_tc(0, 100));
	return tests;
}

string rnd_test(int i){
    int min_n = MIN_N;
    int max_n = MAX_N;
    
    if(i<rnd_test_n / 3){
        max_n = 5;
    }
    else if(i<rnd_test_n / 2){
        max_n = 20;
    }

    int x = rnd.next(min_n, max_n);
    int y = rnd.next(min_n, max_n);
    return(output_tc(x, y));
}

vector<string> generate_random_tests() { 
    vector<string> tests;
    for (int i = 0; i < rnd_test_n; i++){
        tests.push_back(rnd_test(i));
    } 
    return tests;
}

string extreme_test_1(){
    return(output_tc(100, 100));
}

vector<string> generate_extreme_tests(){
    vector<string> tests;   
    tests.push_back(extreme_test_1());
    return tests;
}

int main(int argc, char *argv[]) {
	registerGen(argc, argv, 1);
	vector<string> tests;
	size_t test = 0;
	append(tests, generate_sample_tests());
	append(tests, generate_manual_tests());
	append(tests, generate_random_tests());
	append(tests, generate_extreme_tests());
	for (const auto &t : tests) {
		startTest(++test);
		cout << t;
	}
	return 0;
}