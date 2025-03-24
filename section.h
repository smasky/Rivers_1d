#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>

namespace py = pybind11;

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

        // 保持numpy数组的引用
        std::vector<py::array_t<double>> keep_alive_arrays;

        Section(size_t SEC_ID, size_t RCH_ID, size_t RV_ID, double mil,
                    size_t nPoint, double *xSec, double *ySec, double *rSec,
                        size_t nT, double *Q, double *Z);

        //  // 添加拷贝构造函数
        //  Section(const Section& other);

        void compute_hydraulic_basic();
        void print_info();
        ~Section(); 
};