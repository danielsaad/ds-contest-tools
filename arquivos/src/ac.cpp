#include <iostream>
#include <vector>
#include <algorithm>
#include <queue>
using namespace std;



void solve_aux(vector<pair<int,int>>& v, deque<pair<int,int>>& sequence, int i, deque<pair<int,int>>& best_sequence,
vector<bool>& processed){
    if(i==v.size()){
        if(sequence.size() > best_sequence.size()){
            best_sequence = sequence;
        }
    }
    else{
        if(sequence.size()==0){
            for(int j=0;j<v.size();j++){
                sequence.push_back(v[j]);
                processed[j] = true;
                solve_aux(v,sequence,i+1,best_sequence,processed);
                sequence.pop_back();
                processed[j] = false;
                solve_aux(v,sequence,i+1,best_sequence,processed);
            }
        }
        else{
            for(int j=0;j<v.size();j++){
                if(!processed[j]){
                    processed[j] = true;
                    if(v[j].second == sequence.front().first || v[j].first == sequence.front().first){
                        if(v[j].second == sequence.front().first){
                            sequence.push_front(v[j]);
                        }
                        else{
                            sequence.push_front(make_pair(v[j].second,v[j].first));
                        }
                        solve_aux(v,sequence,i+1,best_sequence,processed);
                        sequence.pop_front();
                    }
                    // Put the piece in the right end;
                    if(v[j].first == sequence.back().second || v[j].second == sequence.back().second){
                        if(v[j].first == sequence.back().second){
                            sequence.push_back(v[j]);
                        }
                        else{
                            sequence.push_back(make_pair(v[j].second,v[j].first));
                        }
                        solve_aux(v,sequence,i+1,best_sequence,processed);
                        sequence.pop_back();
                    }
                    // Triest to solve without putting the piece
                    processed[j] = false;
                    solve_aux(v,sequence,i+1,best_sequence,processed);
                }
            }
        }
    }
}



void solve(vector<pair<int,int>>& v){
    deque<pair<int,int>> sequence;
    deque<pair<int,int>> best_sequence;
    vector<bool> processed(v.size());
    solve_aux(v,sequence,0,best_sequence,processed);
    cout << best_sequence.size() << "\n";
    for(int i=0;i<best_sequence.size();i++){
        cout << best_sequence[i].first << '|' << best_sequence[i].second;
        i<best_sequence.size()-1 ? cout << ' ' : cout << '\n';
    }
}

int main(){
    int n;
    cin >> n;
    vector<pair<int,int>> v;
    for(int i=0;i<n;i++){
        pair<int,int> p;
        cin >> p.first;
        cin.ignore(1);
        cin >> p.second;
        v.push_back(p);
    }
    solve(v);
}