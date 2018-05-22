#include <bits/stdc++.h>
#include "../testlib.h"

using namespace std;

const int max_number_of_pieces = 8; //maximum number of dominó pieces


// This function receives stream as an argument, reads an answer from it,
// checks its correctness
// with _wa outcome if stream = ouf (contestant) or with _fail outcome if stream = ans (jury).
int check_ans(InStream& stream,set<pair<int,int>> s) {
    // reading participant answer
    int n = stream.readInt(0,max_number_of_pieces);
    stream.readEoln();
    if(n < s.size()){
        stream.quitf(_wa,"WA: wront answer, less pieces than optimal solution");
    }
    pair<int,int> last_pair;
    for(int i=0;i<n;i++){
        int a,b;
        string str = stream.readToken();
        
        if(!isdigit(str[0]) || !isdigit(str[2]) || str[1]!='|'){
            stream.quitf(_wa,"WA: not a valid domino piece");
        }
        a = str[0]-'0';
        b = str[2]-'0';

        pair<int,int> p,pswp;
        p = make_pair(a,b);
        pswp = make_pair(b,a);
        if(s.find(p)==s.end() && s.find(pswp)==s.end()){
            stream.quitf(_wa,"WA: invalid solution, piece not available");
        }
        else{
            // Remove piece
            auto f = s.find(p);
            if(f!=s.end())
                s.erase(f);
            f = s.find(pswp);
            if(f!=s.end())
                s.erase(f);
        }
        if(i>0){
            if(p.first != last_pair.second){
                stream.quitf(_wa,"WA: invalid solution, not a domino chain");
            }
        }
        last_pair = p;
    }
    stream.readEoln();
    stream.readEof();
    return n;
}

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    int max_n = inf.readInt(0,max_number_of_pieces);
    inf.readEoln();
    set<pair<int,int>> s;
    for(int i=0;i<max_n;i++){
        string str = inf.readToken();
        ensuref(isdigit(str[0]) && isdigit(str[2]), "devem ser números");
        int a,b;
        a = str[0]-'0';
        b = str[2]-'0';

        pair<int,int> p,pswp;
        p = make_pair(a,b);
        s.insert(p);
    }
    int jans = check_ans(ans,s);
    int pans = check_ans(ouf,s);
    if (jans > pans){
        quitf(_wa, "WA: jury has the better answer: jans = %d, pans = %d\n", jans, pans);
    }
    else if (jans == pans){
        quitf(_ok, "AC: answer = %d\n", pans);
    }
    else{ // (jans < pans)
        quitf(_fail, "ERROR:  participant has the better answer: jans = %d, pans = %d\n", jans, pans);
    }
    return 0;
}