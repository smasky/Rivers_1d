#include "utils.h"
#include <iostream>
void solve_SOR(double *A, double *b, int *Dr, int *Ri, double *all_Z,const int length_A, const int length_Ri){
	double w=0.8;
	double temp_Ze=0.0,temp_aii=0.0,sum_error=0.0;
	int k=0;
	while(k<100){
		for(int j=0;j<length_Ri;j++){
			temp_Ze=temp_Ze+b[j];
			///////////////
			for(int i=Ri[j];i<Ri[j+1];i++){
				if(Dr[j]==i) temp_aii=A[i];
				temp_Ze=temp_Ze-A[i]*all_Z[Dr[i]];
			}
			//////////////
			temp_Ze=w*temp_Ze/temp_aii;
			all_Z[j]=all_Z[j]+temp_Ze;
			sum_error+=temp_Ze;
			temp_Ze=0;
		}
		if((sum_error<1e-10) & (sum_error>-1e-10)) break;
		k+=1;
		sum_error=0;
	};
}
