#define WEIGHTED 1
#include "ligra.h"

struct BFS_F {
  uintE* Parents;
  intE* A;
  uintE* IA;
  uintE* JA;
  BFS_F(uintE* _Parents, intE* _A, uintE* _IA, uintE* _JA) : Parents(_Parents), A(_A), IA(_IA), JA(_JA) {
  }

  inline bool update(uintE s, uintE d, intE edgeLen) { // Update
    intE currentFlow = INT_E_MIN;
    for (long i = IA[s]; i < IA[s + 1]; i++) {
      if (d == JA[i]) {
        currentFlow = A[i];
        break;
      }
    }

    if (currentFlow < edgeLen && Parents[d] == UINT_E_MAX) { 
      Parents[d] = s; 
      return 1; 
    }
    return 0;
  }

  inline bool updateAtomic(uintE s, uintE d, intE edgeLen) { // atomic version of Update
    intE currentFlow = INT_E_MIN;
    for (long i = IA[s]; i < IA[s + 1]; i++) {
      if (d == JA[i]) {
        currentFlow = A[i];
        break;
      }
    }
    
    if (currentFlow < edgeLen) {
      return (CAS(&Parents[d],UINT_E_MAX,s));
    }
    return false;
  }
  
  // cond function checks if vertex has been visited yet
  inline bool cond(uintE d) { 
    return (Parents[d] == UINT_E_MAX); 
  } 
};

template <class vertex>
void Compute(graph<vertex>& GA, commandLine P) {
  long start = P.getOptionLongValue("-r", 0);
  long destination = P.getOptionLongValue("-d", 127);
  long n = GA.n;
  long m = GA.m;

  long maxFlow = 0;

  // BFS parent array
  uintE* Parents = newA(uintE, n); // stores augmenting path

  // Create CSR arrays for flows
  intE* A = newA(intE, m);
  uintE* IA = newA(uintE, n + 1);
  uintE* JA = newA(uintE, m);
  IA[0] = 0;
  parallel_for(long i = 0; i < m; i++) A[i] = 0; // Initialize flows to 0
  for (long i = 1; i < n + 1; i++) { // Initialize IA, don't parallelize
    IA[i] = IA[i - 1] + GA.V[i - 1].getOutDegree();
  }
  uintE runningOffset = 0;
  for (long i = 0; i < n; i++) { // Initialize JA, don't parallelize
    intE* outNeighbors = (intE*) GA.V[i].getOutNeighbors();
    for (long j = 0; j < 2 * GA.V[i].getOutDegree(); j += 2) {
      JA[runningOffset++] = outNeighbors[j];
    }
  }

  while (Parents[destination] != UINT_E_MAX) {
    // initialize Parents array
    parallel_for(long i = 0; i < n; i++) Parents[i] = UINT_E_MAX;
    Parents[start] = start;

    vertexSubset Frontier(n, start); // creates initial frontier
    while (!Frontier.isEmpty()) { // loop until frontier is empty
      vertexSubset output = edgeMap(GA, Frontier, BFS_F(Parents, A, IA, JA));    
      Frontier.del();
      Frontier = output; //set new frontier
    } 
    Frontier.del();

    // If sink is unreachable, break
    if (Parents[destination] == UINT_E_MAX) {
      break;
    }

    // Else update flow adjacency matrix
    // First determine the flow delta
    uintE current = destination;
    intE delta = INT_E_MAX;
    while (current != start) {
      // Search for the capacity
      intE* outNeighbors = (intE*) GA.V[Parents[current]].getOutNeighbors();
      intE capacity = INT_E_MAX;
      for (long i = 0; i < 2 * GA.V[Parents[current]].getOutDegree(); i += 2) {
        if (current == outNeighbors[i]) {
          capacity = outNeighbors[i + 1];
          break;
        }
      }

      // Search for the flow
      for (long i = IA[Parents[current]]; i < IA[Parents[current] + 1]; i++) {
        if (JA[i] == current) {
          intE aug = capacity - A[i];
          if (aug < delta) {
            delta = aug;
          }
          break;
        }
      }
      current = Parents[current];
    }

    // Second update all flows
    current = destination;
    while (current != start) {
      for (long i = IA[Parents[current]]; i < IA[Parents[current] + 1]; i++) {
        if (JA[i] == current) {
          A[i] += delta;
          break;
        }
      }

      for (long i = IA[current]; i < IA[current + 1]; i++) {
        if (JA[i] == Parents[current]) {
          A[i] -= delta;
          break;
        }
      }
      current = Parents[current];
    }
    maxFlow += delta;
  }

  free(Parents);
  free(A);
  free(IA);
  free(JA);
}