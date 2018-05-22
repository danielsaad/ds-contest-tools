#include <bits/stdc++.h>
#include "../testlib.h"

using namespace std;

const int max_number_of_pieces = 8; //maximum number of dominó pieces


int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    int n;
    n = inf.readInt(1, max_number_of_pieces, "n");
    inf.readEoln();
    for(int i=0;i<n;i++){
        string str = inf.readToken();
        set<pair<int,int>> s;
        ensuref(isdigit(str[0]) && isdigit(str[2]) && str[1]=='|',"Formato de dominó inválido.");
        int a,b;
        a = str[0] - '0';
        b = str[2] - '0';
        ensuref(a>=0 && a<=6 && b>=0 && b<=6,"dominós com valores inválidos");
        pair<int,int> p = make_pair(a,b);
        pair<int,int> pswp = make_pair(b,a);
        ensuref( s.find(p)==s.end() && s.find(pswp)==s.end(), "peça repetida na entrada");
        s.insert(p);
        if(i==n-1){
            inf.readEoln();
        }
        else{
            inf.readSpace();
        }
    }
    inf.readEof();
    return 0;
}