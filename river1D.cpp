// #include "section.h"
#include "reach.h"
#include <memory>
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

namespace py = pybind11;

std::shared_ptr<Section> createSection(size_t SEC_ID, size_t RCH_ID, size_t RV_ID, double MIL, double roughness,
                            // size_t nPoint, py::array_t<double> xSec_array, py::array_t<double> ySec_array, py::array_t<double> rSec_array,
                            size_t nY, py::array_t<double> areaList_array, py::array_t<double> wpList_array, py::array_t<double> bsList_array, py::array_t<double> yList_array,
                            size_t nT, py::array_t<double> Q_array, py::array_t<double> Z_array){

    py::buffer_info areaList_buf = areaList_array.request(true); 
    py::buffer_info wpList_buf = wpList_array.request(true);
    py::buffer_info bsList_buf = bsList_array.request(true);
    py::buffer_info yList_buf = yList_array.request(true);
    py::buffer_info Q_buf = Q_array.request(true);
    py::buffer_info Z_buf = Z_array.request(true);
    
    double *areaList = static_cast<double*>(areaList_buf.ptr);
    double *wpList = static_cast<double*>(wpList_buf.ptr);
    double *bsList = static_cast<double*>(bsList_buf.ptr);
    double *yList = static_cast<double*>(yList_buf.ptr);
    double *Q = static_cast<double*>(Q_buf.ptr);
    double *Z = static_cast<double*>(Z_buf.ptr);

    auto section = std::make_shared<Section>(SEC_ID, RCH_ID, RV_ID, MIL, roughness, nY, areaList, wpList, bsList, yList, nT, Q, Z);
    
    return section;
}

std::shared_ptr<OuterReach> createOuterReach(size_t RV_ID, size_t RCH_ID, size_t nSec, size_t fdNodeID, size_t bdNodeID, 
                     std::vector<std::shared_ptr<Section>> sections_ptr, py::array_t<double> TimeSer_array,
                        double dev_sita, double dt, size_t t, size_t reverse, size_t nodeType){
    
    py::buffer_info TimeSer_buf = TimeSer_array.request(true);
    double *TimeSer = static_cast<double*>(TimeSer_buf .ptr);
    
    return std::make_shared<OuterReach>(RV_ID, RCH_ID, nSec, fdNodeID, bdNodeID, sections_ptr, TimeSer, dev_sita, dt, t, reverse, nodeType);
}

std::shared_ptr<InnerReach> createInnerReach(size_t RV_ID, size_t RCH_ID, size_t nSec, size_t fdNodeID, size_t bdNodeID, 
                    std::vector<std::shared_ptr<Section>> sections_ptr, 
                        double dev_sita, double dt, size_t t){
    return std::make_shared<InnerReach>(RV_ID, RCH_ID, nSec, fdNodeID, bdNodeID, sections_ptr, dev_sita, dt, t);
}

PYBIND11_MODULE(river1D, m) {
     py::class_<Section, std::shared_ptr<Section>>(m, "Section")
        .def_static("createSection", &createSection, "Create a new Section object",
                   py::return_value_policy::take_ownership)
        .def_property("MIL", 
            [](const Section& self) { return self.MIL; },  // getter
            [](Section& self, double value) { self.MIL = value; })
        // .def_property("nPoint", 
        //     [](const Section& self) { return self.nPoint; },  // getter
        //     [](Section& self, size_t value) { self.nPoint = value; })
        .def_property("b", 
            [](const Section& self) { return self.b; },  // getter
            [](Section& self, double value) { self.b = value; })
        .def_property("r", 
            [](const Section& self) { return self.r; },  // getter
            [](Section& self, double value) { self.r = value; })
        .def_property("s", 
            [](const Section& self) { return self.s; },  // getter
            [](Section& self, double value) { self.s = value; })
        .def_property("x", 
            [](const Section& self) { return self.x; },  // getter
            [](Section& self, double value) { self.x = value; })
        .def_property("alf", 
            [](const Section& self) { return self.alf; },  // getter
            [](Section& self, double value) { self.alf = value; })
        .def_property("u", 
            [](const Section& self) { return self.u; },  // getter
            [](Section& self, double value) { self.u = value; })
        .def_property("QQ", 
            [](const Section& self) { return self.QQ; },  // getter
            [](Section& self, double value) { self.QQ = value; })
        .def_property("ZZ", 
            [](const Section& self) { return self.ZZ; },  // getter
            [](Section& self, double value) { self.ZZ = value; })
        // .def("print_info", &Section::print_info)
        .def("compute_hydraulic_basic", &Section::compute_hydraulic_basic);
    
    py::class_<OuterReach, std::shared_ptr<OuterReach>>(m, "OuterReach")
        .def_static("createOuterReach", &createOuterReach, "Create a new OuterReach object",
                   py::return_value_policy::take_ownership)
        .def("compute_outer_coefficients", &OuterReach::compute_outer_coefficients)
        .def("compute_basic_coefficients", &OuterReach::compute_basic_coefficients)
        .def("recompute_QZ", &OuterReach::recompute_QZ)
        .def("get_node_coe", &OuterReach::get_node_coe)
        .def("update_t", &OuterReach::update_t)
        .def_property("fdNodeID", 
            [](const OuterReach& self) { return self.fdNodeID; },  // getter
            [](OuterReach& self, size_t value) { self.fdNodeID = value; })
        .def_property("bdNodeID", 
            [](const OuterReach& self) { return self.bdNodeID; },  // getter
            [](OuterReach& self, size_t value) { self.bdNodeID = value; })
        .def_property_readonly("C", [](const OuterReach& self) {
            return py::array_t<double>(self.nSec, self.C);
        })
        .def_property_readonly("D", [](const OuterReach& self) {
            return py::array_t<double>(self.nSec, self.D);
        })
        .def_property_readonly("E", [](const OuterReach& self) {
            return py::array_t<double>(self.nSec, self.E);
        })
        .def_property_readonly("F", [](const OuterReach& self) {
            return py::array_t<double>(self.nSec, self.F);
        })
        .def_property_readonly("G", [](const OuterReach& self) {
            return py::array_t<double>(self.nSec, self.G);
        })
        .def_property_readonly("fai", [](const OuterReach& self) {
            return py::array_t<double>(self.nSec, self.fai);
        })
        .def_property_readonly("P", [](const OuterReach& self) {
            return py::array_t<double>(self.nSec, self.P);
        })
        .def_property_readonly("V", [](const OuterReach& self) {
            return py::array_t<double>(self.nSec, self.V);
        })
        .def_property_readonly("S", [](const OuterReach& self) {
            return py::array_t<double>(self.nSec, self.S);
        })
        .def_property_readonly("T", [](const OuterReach& self) {
            return py::array_t<double>(self.nSec, self.T);
        })
        .def_property_readonly("TimeSer", [](const OuterReach& self) {
            return py::array_t<double>(2000, self.TimeSer);
        })
        .def_property_readonly("reverse", [](const OuterReach& self) {
            return self.reverse;
        })
        .def_property_readonly("nodeType", [](const OuterReach& self) {
            return self.nodeType;
        })
        .def_property_readonly("innerNodeID", [](const OuterReach& self) {
            return self.innerNodeID;
        });

    py::class_<InnerReach, std::shared_ptr<InnerReach>>(m, "InnerReach")
        .def_static("createInnerReach", &createInnerReach, "Create a new InnerReach object",
                   py::return_value_policy::take_ownership)
        .def("compute_inner_coefficients", &InnerReach::compute_inner_coefficients)
        .def("get_fd_coe", &InnerReach::get_fd_coe)
        .def("get_bd_coe", &InnerReach::get_bd_coe)
        .def("recompute_QZ", &InnerReach::recompute_QZ)
        .def("update_t", &InnerReach::update_t)
        .def_property_readonly("Alpha   ", [](const InnerReach& self) {
            return py::array_t<double>(self.nSec, self.Alpha);
        })
        .def_property_readonly("Beta", [](const InnerReach& self) {
            return py::array_t<double>(self.nSec, self.Beta);
        })
        .def_property_readonly("Zeta", [](const InnerReach& self) {
            return py::array_t<double>(self.nSec, self.Zeta);
        })
        .def_property_readonly("Sita", [](const InnerReach& self) {
            return py::array_t<double>(self.nSec, self.Sita);
        })
        .def_property_readonly("Eta", [](const InnerReach& self) {
            return py::array_t<double>(self.nSec, self.Eta);
        })
        .def_property_readonly("Gama", [](const InnerReach& self) {
            return py::array_t<double>(self.nSec, self.Gama);
        })
        .def_property_readonly("fdNodeID", [](const InnerReach& self) {
            return self.fdNodeID;
        })
        .def_property_readonly("bdNodeID", [](const InnerReach& self) {
            return self.bdNodeID;
        });
}





