#include "section.h"
#include <iostream>

Section::Section(size_t SEC_ID, size_t RCH_ID, size_t RV_ID, double MIL,
                    size_t nPoint, double *xSec, double *ySec, double *rSec,
                        size_t nT, double *Q, double *Z): 
                        SEC_ID(SEC_ID), 
                        RCH_ID(RCH_ID), 
                        RV_ID(RV_ID), 
                        MIL(MIL), 
                        nPoint(nPoint),
                        xSec(xSec), 
                        ySec(ySec), 
                        rSec(rSec),
                        nT(nT), 
                        Q(Q), 
                        Z(Z) {
    QQ = Q[0];
    ZZ = Z[0];
}

void Section::compute_hydraulic_basic(){
    double x1, x2, y1, y2, delta1, delta2, delta_x;
    this->s = 0.0; this->x = 0.0; this->r = 0.0; this->alf = 0.0; this->u = 0.0;this->b = 0.0;
    for (int i = 0; i < this->nPoint - 1; i++) {
        x1 = this->xSec[i];
        x2 = this->xSec[i + 1];
        y1 = this->ySec[i];
        y2 = this->ySec[i + 1];

        if (this->ZZ <= std::min(y1, y2)) {
            continue;
        }

        delta1 = this->ZZ - y1;
        delta2 = this->ZZ - y2;
        delta_x = x2 - x1;

        if(delta1 < 0){
            delta1 = 0;
            delta_x = delta2 / (y1 -y2) * delta_x;
        }else if(delta2 < 0){
            delta2 = 0;
            delta_x = -delta1 / (y1 -y2) * delta_x;

        }

        this->s = this->s + 0.5*(delta1 + delta2)*delta_x;
        this->x = this->x + sqrt(pow(delta1 - delta2, 2) + pow(delta_x, 2));
        this->b = this->b + delta_x;

        if(this->x < 1e-10){
            this->r = 0.1;
        }else{
            this->r = this->s / this->x;
        }

        this->alf = 1.0; //TODO check right or not
        this->u = this->QQ / this->s;

        // std::cout<<this->QQ<<" "<<this->ZZ<<" "<<this->s<<" "<<this->x<<" "<<this->r<<" "<<this->alf<<" "<<this->u<<std::endl;
    }
}

void Section::print_info(){
    std::cout << "Section ID: " << SEC_ID << " MIL: " << MIL << std::endl;

    for(int i = 0; i < this->nPoint; i++){
        std::cout<<"x:"<<this->xSec[i]<<" y:"<<this->ySec[i]<<" r:"<<this->rSec[i]<<std::endl;
    }
}

Section::~Section(){
}

