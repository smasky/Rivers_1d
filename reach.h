#include "section.h"
#include <vector>
#include <memory>

class Reach{
    
    public:
        size_t RV_ID;
        size_t RCH_ID;
        size_t nSec;
        size_t fdNodeID;
        size_t bdNodeID;
        size_t t;

        double dev_sita;
        double dt;

        std::vector<std::shared_ptr<Section>>  sections_ptr;

        double *C, *D, *E, *F, *G, *fai;  // coefficients for each section

        Reach(size_t RV_ID, size_t RCH_ID, size_t nSec, size_t fdNodeID, size_t bdNodeID, 
                    std::vector<std::shared_ptr<Section>> &sections_ptr, 
                        double dev_sita, double dt, size_t t);

        void compute_basic_coefficients();

        ~Reach();
};


class OuterReach: public Reach{

    public:
        size_t fdNodeID;
        size_t bdNodeID;
        size_t reverse;
        size_t nodeType;
        size_t t;
        

        double *P, *V, *S, *T;

        OuterReach(size_t RV_ID, size_t RCH_ID, size_t nSec, size_t fdNodeID, size_t bdNodeID, 
                    std::vector<std::shared_ptr<Section>> &sections_ptr, 
                        double dev_sita, double dt, size_t t, size_t reverse, size_t nodeType);

        void compute_outer_coefficients();

        void recompute_QZ();

        ~OuterReach();
};


class InnerReach: public Reach{

    public:
        double *Alpha, *Beta, *Zeta;
        double *Sita, *Eta, *Gama;
        double alpha, beta, zeta;
        double sita, eta, gama;
        
        InnerReach(size_t RV_ID, size_t RCH_ID, size_t nSec, size_t fdNodeID, size_t bdNodeID, 
                    std::vector<std::shared_ptr<Section>> &sections_ptr, 
                        double dev_sita, double dt, size_t t);

        void compute_inner_coefficients();

        void recompute_QZ();

        ~InnerReach();
};
