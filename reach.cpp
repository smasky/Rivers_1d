#include "reach.h"
#include <iostream>

Reach::Reach(size_t RV_ID, size_t RCH_ID, size_t nSec, 
                size_t fdNodeID, size_t bdNodeID, 
                std::vector<std::shared_ptr<Section>> &sections_ptr, double dev_sita, double dt, size_t t)
    : RV_ID(RV_ID), RCH_ID(RCH_ID), nSec(nSec), sections_ptr(sections_ptr),fdNodeID(fdNodeID), bdNodeID(bdNodeID), dev_sita(dev_sita), dt(dt), t(t) {

        C = new double[nSec];
        D = new double[nSec];
        E = new double[nSec];
        F = new double[nSec];
        G = new double[nSec];
        fai = new double[nSec];
    }

void Reach::compute_basic_coefficients() {
    double dx, tmp;
    double sa, sb, bc;
    double c, d, e, g, f, fai;

    std::shared_ptr<Section> fdSec = this->sections_ptr[0];

    fdSec->compute_hydraulic_basic();

    for(size_t i = 1; i < this->nSec; i++){

        std::shared_ptr<Section> bdSec = this->sections_ptr[i]; 
        bdSec->compute_hydraulic_basic();

        dx = fabs(bdSec->MIL - fdSec->MIL);

        sa = fabs(fdSec->u) * 9.81 * pow(fdSec->rSec[0], 2) * dx / (pow(fdSec->r, 4.0/3) * 2 * this->dev_sita);//TODO using sec roughness
        sb = fabs(bdSec->u) * 9.81 * pow(bdSec->rSec[0], 2) * dx / (pow(bdSec->r, 4.0/3) * 2 * this->dev_sita);

        bc = (fdSec->b + bdSec->b) / 2;
        c = bc * dx / ( 2 * this->dt * this->dev_sita );
        d = c * (fdSec->ZZ + bdSec->ZZ) - ( 1 - this->dev_sita ) * (bdSec->QQ - fdSec->QQ)/this->dev_sita;
        e = dx / (2 * this->dev_sita * this->dt) - (fdSec->alf * fdSec->u) + sa;
        g = dx / (2 * this->dev_sita * this->dt) + (bdSec->alf * bdSec->u) + sb;
        f = 9.81 * (fdSec->s + bdSec->s) / 2;
        tmp = bdSec->alf * bdSec->u * bdSec->QQ - fdSec->alf * fdSec->u * fdSec->QQ;
        fai = dx / (2 * this->dev_sita * this->dt ) * (bdSec->QQ + fdSec->QQ) - (1 - this->dev_sita) * tmp / this->dev_sita - (1 - this->dev_sita) * f * (bdSec->ZZ - fdSec->ZZ) / this->dev_sita;

        this->C[i-1] = c;
        this->D[i-1] = d;
        this->E[i-1] = e;
        this->F[i-1] = f;
        this->G[i-1] = g;
        this->fai[i-1] = fai;

        fdSec = bdSec;
    }
    
}

void Reach::update_t() {
    this->t++;
}

Reach::~Reach() {}

OuterReach::OuterReach(size_t RV_ID, size_t RCH_ID, size_t nSec, size_t fdNodeID, size_t bdNodeID, 
                    std::vector<std::shared_ptr<Section>> &sections_ptr, double *TimeSer,
                        double dev_sita, double dt, size_t t, size_t reverse, size_t nodeType)
    : Reach(RV_ID, RCH_ID, nSec, fdNodeID, bdNodeID, sections_ptr, dev_sita, dt, t), TimeSer(TimeSer), reverse(reverse), nodeType(nodeType) {

    this->P = new double[nSec];
    this->V = new double[nSec];
    this->S = new double[nSec];
    this->T = new double[nSec];

    if(this->reverse == 0){
        this->innerNodeID = this->bdNodeID;
    }else{
        this->innerNodeID = this->fdNodeID;
    }

}

std::tuple<size_t, double, double> OuterReach::get_node_coe(){
    double coe_z, const_z;
    size_t nodeID;

    if (this->nodeType == 1){
        coe_z = -1/this->V[this->nSec-1];
        const_z = -this->P[this->nSec-1]/this->V[this->nSec-1];
    }else{
        coe_z = -this->V[this->nSec-1];
        const_z = -this->P[this->nSec-1];
    }

    if (this->reverse == 1){
        nodeID = this->fdNodeID;
    }else{
        nodeID = this->bdNodeID;
    }
   
    return std::make_tuple(nodeID, coe_z, const_z);
}

OuterReach::~OuterReach() {}

void OuterReach::compute_outer_coefficients() {
    double c, d, e, f, g, fai;
    double y1, y2, y3, y4;
    double s, t_, p, v;

    this->compute_basic_coefficients();

    if (this->nodeType == 1) {
        this->P[0] = this->TimeSer[this->t];
    }else{
        this->P[0] = this->TimeSer[this->t];
    }
    
    this->V[0] = 0;

    p = this->P[0];
    v = this->V[0];
    
    for(size_t i = 1; i < this->nSec; i++){
        c = this->C[i-1];
        d = this->D[i-1];
        e = this->E[i-1];
        f = this->F[i-1];
        g = this->G[i-1];
        fai = this->fai[i-1];

        if (this->nodeType == 1) {
            y1 = d - c * p;
            y2 = fai + f * p;
            y3 = 1 + c * v;
            y4 = e + f * v;
            
            s = (c * y2 - f * y1) / (f * y3 + c * y4);
            t_ = (g * c - f) / (f * y3 + c * y4);
            p = (y1 + y3 * s) / c;
            v = (y3 * t_ + 1) / c;
        }else{
            y1 = c + v;
            y2 = f + e * v;
            y3 = d + p;
            y4 = fai - e * p;

            s = (g * y3 - y4)/(y1 * g + y2);
            t_ = (g * c -f)/(y1 * g + y2);
            p = (y3 - y1 * s);
            v = (c - y1 * t_);
        }

        this->S[i] = s;
        this->T[i] = t_;
        this->P[i] = p;
        this->V[i] = v;
    }

}

void OuterReach::recompute_QZ(double z_compute) {
    double q, z;

    // if(this->reverse == 0){
    //     this->sections_ptr[this->nSec-1]->ZZ = z_compute;
    // }else{
    //     this->sections_ptr[0]->ZZ = z_compute;
    // }
    
    this->sections_ptr[this->nSec-1]->ZZ = z_compute;

    if(this->nodeType == 1){
        //Water level node
        q = this->P[this->nSec-1] / this->V[this->nSec-1] - this->sections_ptr[this->nSec-1]->ZZ / this->V[this->nSec-1];
        this->sections_ptr[this->nSec-1]->QQ = q;
    }else{
        //Discharge node
        z = this->sections_ptr[this->nSec-1]->ZZ;
        this->sections_ptr[this->nSec-1]->QQ = this->P[this->nSec-1] - z * this->V[this->nSec-1];
    }

    for(int i = this->nSec - 2; i > -1; i--){

        if(this->nodeType == 1){
            q = this->S[i+1] - this->T[i+1] * q;
            z = this->P[i] - this->V[i] * q;
        }else{
            z = this->S[i+1] - this->T[i+1] * z;
            q = this->P[i] - this->V[i] * z;
        }

        this->sections_ptr[i]->QQ = q;
        this->sections_ptr[i]->ZZ = z;

    }

    if(this->reverse == 1){
        //TODO:check right
        for(size_t i = 0; i < this->nSec; i++){
            this->sections_ptr[i]->Q[this->t] = this->sections_ptr[i]->QQ * -1;
            this->sections_ptr[i]->Z[this->t] = this->sections_ptr[i]->ZZ;
        }
    }else{
        for(size_t i = 0; i < this->nSec; i++){
            this->sections_ptr[i]->Q[this->t] = this->sections_ptr[i]->QQ;
            this->sections_ptr[i]->Z[this->t] = this->sections_ptr[i]->ZZ;
        }
    }
    
}

InnerReach::InnerReach(size_t RV_ID, size_t RCH_ID, size_t nSec, size_t fdNodeID, size_t bdNodeID, 
                    std::vector<std::shared_ptr<Section>> &sections_ptr, 
                        double dev_sita, double dt, size_t t)
    : Reach(RV_ID, RCH_ID, nSec, fdNodeID, bdNodeID, sections_ptr, dev_sita, dt, t) {

    this->Alpha = new double[nSec];
    this->Beta = new double[nSec];
    this->Zeta = new double[nSec];

    this->Sita = new double[nSec];
    this->Eta = new double[nSec];
    this->Gama = new double[nSec];
}

void InnerReach::compute_inner_coefficients() {
    double alpha, beta, zeta, sita, eta, gama;
    double c, d, e, f, g, fai;
    double y1, y2;

    this->compute_basic_coefficients();

    fai = this->fai[this->nSec-2]; c = this->C[this->nSec-2]; d = this->D[this->nSec-2]; e = this->E[this->nSec-2]; f = this->F[this->nSec-2]; g = this->G[this->nSec-2];

    alpha = (fai - g * d) / (g + e);
    beta = (c * g + f) / (g + e);
    zeta = (c * g - f) / (g + e);

    this->Alpha[this->nSec-2] = alpha;
    this->Beta[this->nSec-2] = beta;
    this->Zeta[this->nSec-2] = zeta;

    for(int i = this->nSec-3; i > -1; i--){
        
        c = this->C[i]; d = this->D[i]; e = this->E[i]; f = this->F[i]; g = this->G[i]; fai = this->fai[i];

        y1 = c + beta;
        y2 = g * beta + f;

        alpha = (y1 * (fai - alpha * g) - y2 * (d - alpha)) / (e * y1 + y2);
        beta = (y2 * c + y1 * f) / (y1 * e + y2);
        zeta = zeta * (y2 - y1 * g) / (y1 * e + y2);

        this->Alpha[i] = alpha; this->Beta[i] = beta; this->Zeta[i] = zeta;
    }
    //

    fai = this->fai[0]; c = this->C[0]; d = this->D[0]; e = this->E[0]; f = this->F[0]; g = this->G[0];

    sita = (e * d + fai) / (e + g); eta = - (c * e + f) / (e + g); gama = (f - c * e) / (e + g);

    this->Sita[1] = sita; this->Eta[1] = eta; this->Gama[1] = gama;

    for (int i = 2; i < this->nSec; i++){
        
        c = this->C[i-1]; d = this->D[i-1]; e = this->E[i-1]; f = this->F[i-1]; g = this->G[i-1]; fai = this->fai[i-1];

        y1 = c - eta;
        y2 = e * eta - f;

        sita = (y2 * (d + sita) - y1 * (fai - e * sita)) / (y2 - g * y1);
        eta =  (f * y1 - c * y2) / (y2 - g * y1);
        gama = gama * (y2 + e * y1) / (y2 - g * y1);
        
        this->Sita[i] = sita; this->Eta[i] = eta; this->Gama[i] = gama;
    }

    this->alpha = this->Alpha[0];
    this->beta = -1 * this->Beta[0];
    this->zeta = -1 * this->Zeta[0];

    this->sita = -1 * this->Sita[this->nSec-1];
    this->eta = this->Eta[this->nSec-1];
    this->gama = this->Gama[this->nSec-1];
}

void InnerReach::recompute_QZ(double fd_z_compute, double bd_z_compute) {
    double q, z, za, zb;

    this->sections_ptr[0]->ZZ = fd_z_compute;
    this->sections_ptr[this->nSec-1]->ZZ = bd_z_compute;
    
    za = this->sections_ptr[0]->ZZ;
    zb = this->sections_ptr[this->nSec-1]->ZZ;

    for (int i = 1; i < this->nSec - 1; i++){
        z = (this->Sita[i] - this->Alpha[i] + this->Gama[i] * za - this->Zeta[i] * zb) / (this->Beta[i] - this->Eta[i]);
        q = this->Alpha[i] + this->Beta[i] * z + this->Zeta[i] * zb;

        this->sections_ptr[i]->QQ = q;
        this->sections_ptr[i]->ZZ = z;
        // std::cout<<this->sections_ptr[i]->SEC_ID<<" "<<this->sections_ptr[i]->QQ<<" "<<this->sections_ptr[i]->ZZ<<std::endl;
    }

    this->sections_ptr[0]->QQ = this->Alpha[0] + this->Beta[0] * za + this->Zeta[0] * zb;
    this->sections_ptr[this->nSec-1]->QQ = this->Sita[this->nSec-1] + this->Eta[this->nSec-1]*zb + this->Gama[this->nSec-1]*za;

    // for(size_t i = 0; i < this->nSec; i++){
    //     std::cout<<this->sections_ptr[i]->SEC_ID<<" "<<this->sections_ptr[i]->QQ<<" "<<this->sections_ptr[i]->ZZ<<std::endl;
    // }

    for(int i = 0; i< this->nSec; i++){
        this->sections_ptr[i]->Q[this->t] = this->sections_ptr[i]->QQ;
        this->sections_ptr[i]->Z[this->t] = this->sections_ptr[i]->ZZ;
    }

}

std::tuple<size_t, size_t, double, double, double> InnerReach::get_fd_coe(){
    return std::make_tuple(this->fdNodeID, this->bdNodeID, this->alpha, this->beta, this->zeta);
}

std::tuple<size_t, size_t, double, double, double> InnerReach::get_bd_coe(){
    return std::make_tuple(this->bdNodeID, this->fdNodeID, this->sita, this->eta, this->gama);
}

InnerReach::~InnerReach() {}