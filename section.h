
#include <vector>

class Section{

    public:
        size_t SEC_ID;
        size_t RCH_ID;
        size_t RV_ID;
        double MIL;

        size_t nPoint; 
        double *xSec;
        double *ySec;
        double *rSec;
        
        size_t nT;
        double *Q;
        double *Z;

        double QQ, ZZ;

        double b=0, r=0, s=0, x=0, alf=0, u=0;

        Section(size_t SEC_ID, size_t RCH_ID, size_t RV_ID, double mil,
                    size_t nPoint, double *xSec, double *ySec, double *rSec,
                        size_t nT, double *Q, double *Z);
                        
        void compute_hydraulic_basic();
        void print_info();
        ~Section(); 
};