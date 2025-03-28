#include "section.h"
#include <iostream>
#include <vector>
#include <algorithm>

Section::Section(size_t SEC_ID, size_t RCH_ID, size_t RV_ID, double MIL, double roughness,
                    size_t nPoint, double *xSec, double *ySec, double *rSec,
                    // size_t nY, double *areaList, double *wpList, double *bsList, double *yList,
                    size_t nT, double *Q, double *Z): 
                        SEC_ID(SEC_ID), 
                        RCH_ID(RCH_ID), 
                        RV_ID(RV_ID), 
                        MIL(MIL), 
                        roughness(roughness),
                        nPoint(nPoint),
                        xSec(xSec), 
                        ySec(ySec), 
                        rSec(rSec),
                        nT(nT), 
                        Q(Q), 
                        Z(Z) {
    QQ = Q[0];
    ZZ = Z[0];

    this->compute_hydraulic_list();

}

void Section::compute_hydraulic_list(){

    size_t minI = 0; size_t leftHI = 0; size_t rightHI = 0;
    double minY = this->ySec[0];

    for(size_t i = 1; i < this->nPoint; i++){
        if(this->ySec[i] < minY){
            minY = this->ySec[i];
            minI = i;
        }
    }

    double leftHY = this->ySec[0];
    for(size_t i = 1; i < minI; i++){
        if(this->ySec[i] > leftHY){
            leftHY = this->ySec[i];
            leftHI = i;
        }
    }

    double rightHY = this->ySec[minI];
    rightHI = minI;
    for(size_t i = minI+1; i < this->nPoint; i++){
        if(this->ySec[i] > rightHY){
            rightHY = this->ySec[i];
            rightHI = i;
        }
    }

    this->minY = minY;
    this->maxY = std::max(leftHY, rightHY);

    std::vector<double> uniqueY;
    size_t i = leftHI;
    while (i <= rightHI){
        double y = this->ySec[i];
        size_t j = i;
        while (j+1 < rightHI && this->ySec[j+1] == y){
            j++;
        }
        uniqueY.push_back(y);
        if (j > i){
            uniqueY.push_back(y + 1e-6);
        }
        i = j+1;
    }

    std::sort(uniqueY.begin(), uniqueY.end());
    auto last = std::unique(uniqueY.begin(), uniqueY.end());
    uniqueY.erase(last, uniqueY.end());

    this->nY = uniqueY.size();
    this->yList = new double[this->nY];
    std::copy(uniqueY.begin(), uniqueY.end(), this->yList);

    this->areaList = new double[this->nY];
    this->wpList = new double[this->nY];
    this->bsList = new double[this->nY];

    for(size_t i = 0; i < this->nY; i++){
        double y = this->yList[i];
        double area = 0;
        double wp = 0;
        double bs = 0;

        for(size_t j = leftHI; j < rightHI; j++){
            double x1 = this->xSec[j];
            double x2 = this->xSec[j+1];
            double y1 = this->ySec[j];
            double y2 = this->ySec[j+1];

            if(y <= std::min(y1, y2)){
                continue;
            }

            double delta1 = y - y1;
            double delta2 = y - y2;
            double delta_x = x2 - x1;

            if(delta1 < 0){
                delta1 = 0;
                delta_x = delta2 / (y1 - y2) * delta_x;
            }else if(delta2 < 0){
                delta2 = 0;
                delta_x = -delta1 / (y1 - y2) * delta_x;
            }

            area += 0.5 * (delta1 + delta2) * delta_x;
            bs += delta_x;
            wp += sqrt(pow(delta1 - delta2, 2) + pow(delta_x, 2));

            this->areaList[i] = area;
            this->wpList[i] = wp;
            this->bsList[i] = bs;
        }
    }
}
void Section::compute_hydraulic_basic(){
    // std::cout << "ZZ: " << this->ZZ << " minY: " << this->minY << " maxY: " << this->maxY << std::endl;
    if (this->ZZ < this->minY || this->ZZ > this->maxY){
        this->compute_hydraulic_direct();
        // std::cout << "compute_hydraulic_direct" << std::endl;
        return;
    }

    for(size_t i = 0; i < this->nY-1; i++){
        double y1 = this->yList[i];
        double y2 = this->yList[i+1];
        // std::cout<< "ZZ: " << this->ZZ << " y1: " << y1 << " y2: " << y2 << std::endl;
        if(this->ZZ < std::min(y1, y2) || this->ZZ > std::max(y1, y2)){
            continue;
        }

        double area1 = this->areaList[i];
        double area2 = this->areaList[i+1];

        double wp1 = this->wpList[i];
        double wp2 = this->wpList[i+1];

        double bs1 = this->bsList[i];
        double bs2 = this->bsList[i+1];

        this->s = area1 + (this->ZZ - y1)*(area2 - area1);

        this->x = wp1 + (this->ZZ - y1)*(wp2 - wp1);

        this->b = bs1 + (this->ZZ - y1)*(bs2 - bs1);

        this->r = this->s / this->x;

        this->alf = 1.0; //TODO check right or not

        this->u = this->QQ / this->s;   
        
        break;
    }
    // std::cout << "s: " << this->s << " x: " << this->x << " r: " << this->r << " alf: " << this->alf << " u: " << this->u << std::endl;
}

void Section::compute_hydraulic_direct(){
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

    }
    if(this->x < 1e-10){
        this->r = 0.1;
    }else{
        this->r = this->s / this->x;
    }

    this->alf = 1.0; //TODO check right or not
    if(this->s > 0){
        this->u = this->QQ / this->s;
    }else{
        this->u = 0.0;
    }
}

Section::~Section(){
}

