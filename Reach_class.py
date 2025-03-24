'''
Author: smasky
Date: 2021-06-16 21:43:52
LastEditTime: 2025-03-22 13:08:13
LastEditors: smasky
Description: python versions for 1d_rivers 
FilePath: \Rivers_1d-main\Reach_class.py
You will never know unless you try
'''
import numpy as np
import math

from numpy.ma.core import default_fill_value
class reach():
    def __init__(self,ID,reach_ID,info_sec,DT,sita,roughness):
        num_sec=info_sec['num_sec']
        self.reach_ID=reach_ID
        self.num_sec=info_sec['num_sec']
        self.DT=DT
        self.sita0=sita 
        self.ID=ID
        self.info_sec=info_sec
        self.roughness=roughness
        self.x=info_sec['x']
        self.y=info_sec['y']
        self.order_mileages=info_sec['order_mileages']
        self.Q=info_sec['Q']
        self.Z=info_sec['Z']

        self.C=np.zeros(num_sec)
        self.D=np.zeros(num_sec)
        self.E=np.zeros(num_sec)
        self.F=np.zeros(num_sec)
        self.G=np.zeros(num_sec)
        self.fai=np.zeros(num_sec)

        self.Y1=np.zeros(num_sec)
        self.Y2=np.zeros(num_sec)
        self.Y3=np.zeros(num_sec)
        self.Y4=np.zeros(num_sec)
    def _cal_basic(self,x,y,z,Q):
        '''
        cal B R S X ALF U
        '''
        S=0
        B=0
        X=0

        for i in range(len(x)-1):
            x1=x[i]
            y1=y[i]
            x2=x[i+1]
            y2=y[i+1]
            if z<=min(y1,y2):
                continue
            deta1=z-y1
            deta2=z-y2
            deta_x=x2-x1
            if deta1<0:
                deta1=0
                deta_x=deta2/(y1-y2)*deta_x
            elif deta2<0:
                deta2=0
                deta_x=deta1/(y2-y1)*deta_x
            S=S+0.5*(deta1+deta2)*deta_x
            X=X+math.sqrt((deta1-deta2)**2+deta_x**2)
            B=B+deta_x
        if X==0:
            R=0.1
        else:
            R=S/X
        if R<0.1:
            R=0.1
        ALF=1.0
        U=Q/S
        return B,R,S,X,ALF,U

    def update_basic(self):
        '''
        C D E F G
        '''
        DT=self.DT
        sita0=self.sita0
        Z1=self.Z[0]
        Q1=self.Q[0]
        order_mileages=self.order_mileages
        roughness=self.roughness
        x=self.x
        y=self.y
        B1,R1,S1,X1,ALF1,U1=self._cal_basic(x[0],y[0],Z1,Q1)
        for i in range(1,self.num_sec):
            Z2=self.Z[i]
            Q2=self.Q[i]

            B2,R2,S2,X2,ALF2,U2=self._cal_basic(x[i],y[i],Z2,Q2)

            DX=order_mileages[i]-order_mileages[i-1]
            SA=abs(U1)*9.81*roughness**2*DX/(R1*2*sita0)
            SB=abs(U2)*9.81*roughness**2*DX/(R2*2*sita0)
            BC=(B1+B2)/2
            C1=BC*DX/(2*DT*sita0)
            D1=C1*(Z1+Z2)-(1-sita0)/sita0*(Q2-Q1)
            E1=DX/(2*sita0*DT)-(ALF1*U1)+SA
            G1=DX/(2*sita0*DT)+(ALF2*U2)+SB
            F1=9.81*(S1+S2)/2
            fai=DX/(2*sita0*DT)*(Q1+Q2)-(1-sita0)/sita0*((ALF2*U2*Q2)-(ALF1*U1*Q1))-(1-sita0)/sita0*F1*(Z2-Z1)
            self.C[i-1]=C1
            self.D[i-1]=D1
            self.E[i-1]=E1
            self.F[i-1]=F1
            self.G[i-1]=G1
            self.fai[i-1]=fai
            B1=B2;Z1=Z2;Q1=Q2;U1=U2;S1=S2;R1=R2;ALF2=ALF1
class out_reach(reach):
    def __init__(self,ID,reach_ID,resverse,type_node,info_sec,nodes,time_series,DT,sita,roughness):
        '''
        ID 河道ID号 type_node 节点类型 info_sec 断面信息 nodes: 节点编号 time_series: 外节点时间序列
        '''
        super().__init__(ID,reach_ID,info_sec,DT,sita,roughness)
        num_sec=info_sec['num_sec']
        self.resverse=resverse
        self.ID=ID
        self.Sec_ID=info_sec['section_id']
        self.begin=nodes[0]
        self.end=nodes[1]
        self.type_node=type_node
        self.time_series=np.array(time_series)
        self.P=np.zeros(num_sec)
        self.V=np.zeros(num_sec)
        self.S=np.zeros(num_sec)
        self.T=np.zeros(num_sec)
    def update_coe(self,t):
        '''
        更新迭代系数
        '''
        
        # if not self.resverse:
        #     if self.type_node==0:
        #         self.Q[0] = self.time_series[t, 1]
        #     else:
        #         self.Z[0] = self.time_series[t, 1]
        # else:
        #     if self.type_node==0:
        #         self.Q[-1] = self.time_series[t, 1]
        #     else:
        #         self.Z[-1] = self.time_series[t, 1]
                
        self.update_basic()
        P=self.P;V=self.V;S=self.S;T=self.T;C=self.C;D=self.D;E=self.E;F=self.F;G=self.G;fai=self.fai

        P[0]=self.time_series[t,1]
        V[0]=0
        P1=P[0]
        V1=V[0]
        for i in range(1,self.num_sec):
            C1=C[i-1]
            D1=D[i-1]
            E1=E[i-1]
            F1=F[i-1]
            G1=G[i-1]
            fai1=fai[i-1]
            if self.type_node==1: #水位边界
                Y1=D1-C1*P1
                Y2=fai1+F1*P1
                Y3=1+C1*V1
                Y4=E1+F1*V1

                S1=(C1*Y2-F1*Y1)/(F1*Y3+C1*Y4)
                T1=(G1*C1-F1)/(F1*Y3+C1*Y4)
                P1=(Y1+Y3*S1)/C1
                V1=(Y3*T1+1)/C1

                S[i]=S1
                T[i]=T1
                P[i]=P1
                V[i]=V1
            else:
                Y1=C1+V1
                Y2=F1+E1*V1
                Y3=D1+P1
                Y4=fai1-E1*P1

                S1=(G1*Y3-Y4)/(Y1*G1+Y2)
                T1=(G1*C1-F1)/(Y1*G1+Y2)
                P1=(Y3-Y1*S1)
                V1=(C1-Y1*T1)

                S[i]=S1
                T[i]=T1
                P[i]=P1
                V[i]=V1
        self.T=T;self.S=S;self.P=P;self.V=V
    def node_coe(self):
        '''
        给内节点传递系数 sign_node,coe_z,const_z
        '''
        if self.type_node==1:#水位 流入节点
            coe_z=-1/self.V[-1]
            const_z=-self.P[-1]/self.V[-1]
        else:
            coe_z=-self.V[-1]
            const_z=-self.P[-1]
        return self.end,coe_z,const_z
    def steady(self,t,all_Z):
        deta_Q=100
        i=0

        while i<100:
            Q1=self.Q.copy()
            Z1=self.Z.copy()
            self.update_coe(t)
            self.compute_Q_Z(t,all_Z)

            deta_Q=np.sum(abs(Q1-self.Q))
            deta_Z=np.sum(abs(Z1-self.Z))
            i+=1
            #print(i)
            #print(self.Q)
            #print(self.Z)
    def compute_Q_Z(self,t,all_Z):
        end=self.end
        Zb=all_Z[end]
        Z=self.Z
        Q=self.Q;P=self.P;T=self.T;S=self.S;V=self.V
        Z[self.num_sec-1]=Zb
        sign=self.type_node
        if self.type_node==1: #水位
            Z[0]=self.time_series[t,1]
            Q1=P[self.num_sec-1]/V[self.num_sec-1]-(1/V[self.num_sec-1])*Zb
            Q[self.num_sec-1]=Q1
        else:
            Q[0]=self.time_series[t,1]
            Z1=Zb
            Q[self.num_sec-1]=P[self.num_sec-1]-V[self.num_sec-1]*Z1
        for i in range(self.num_sec-2,-1,-1):
            if sign:
                Q1=S[i+1]-T[i+1]*Q1
                Z1=P[i]-V[i]*Q1
            else:
                Z1=S[i+1]-T[i+1]*Z1
                Q1=P[i]-V[i]*Z1
            Q[i]=Q1
            Z[i]=Z1

        self.Q=Q;self.Z=Z
        if self.resverse:
            Q=-Q
        #print("aaaaaaa:",-Q[0]+self.C[0]*Z[0]+Q[1]+self.C[0]*Z[1]-self.D[0])
        #print("bbbbb:",self.E[0]*Q[0]-self.F[0]*Z[0]+self.G[0]*self.Q[1]+self.F[0]*Z[1]-self.fai[0])
        return self.ID,self.reach_ID,self.Sec_ID,Q,Z







class inner_reach(reach):
    def __init__(self,ID,reach_ID,info_sec,nodes,DT,sita,roughness):
        super().__init__(ID,reach_ID,info_sec,DT,sita,roughness)
        self.ID=ID
        self.Sec_ID=info_sec['section_id']
        num_sec=info_sec['num_sec']
        self.begin=nodes[0]
        self.end=nodes[1]
        self.num_sec=num_sec
        self.alpha=np.zeros(num_sec)
        self.beta=np.zeros(num_sec)
        self.zeta=np.zeros(num_sec)
        self.sita=np.zeros(num_sec)
        self.eta=np.zeros(num_sec)
        self.gama=np.zeros(num_sec)
    def update_coe(self):
        '''
        更新追赶系数
        '''
        num_sec=self.num_sec
        self.update_basic()
        C=self.C;D=self.D;E=self.E;F=self.F;G=self.G;fai=self.fai
        alpha=self.alpha;beta=self.beta;zeta=self.zeta;sita=self.sita;gama=self.gama;eta=self.eta

        be_end=num_sec-2

        fai1=fai[be_end];C1=C[be_end];D1=D[be_end];E1=E[be_end];F1=F[be_end];G1=G[be_end]

        alpha1=(fai1-G1*D1)/(G1+E1);beta1=(C1*G1+F1)/(G1+E1);zeta1=(C1*G1-F1)/(G1+E1)
        alpha[be_end]=alpha1;beta[be_end]=beta1;zeta[be_end]=zeta1

        for i in range(be_end-1,-1,-1):
            C1=C[i];D1=D[i];E1=E[i];F1=F[i];G1=G[i];fai1=fai[i]

            Y1=C1+beta1#i+1
            Y2=G1*beta1+F1

            alpha1=(Y1*(fai1-alpha1*G1)-Y2*(D1-alpha1))/(E1*Y1+Y2)
            beta1=(Y2*C1+Y1*F1)/(Y1*E1+Y2)
            zeta1=zeta1*(Y2-Y1*G1)/(Y1*E1+Y2)

            alpha[i]=alpha1;beta[i]=beta1;zeta[i]=zeta1
#######################################################################################
        fai1=fai[0];C1=C[0];D1=D[0];E1=E[0];F1=F[0];G1=G[0]

        sita1=(E1*D1+fai1)/(E1+G1);eta1=-(C1*E1+F1)/(E1+G1);gama1=(F1-C1*E1)/(E1+G1)
        sita[1]=sita1;eta[1]=eta1;gama[1]=gama1
        for i in range(2,num_sec):
            C1=C[i-1];D1=D[i-1];E1=E[i-1];F1=F[i-1];G1=G[i-1];fai1=fai[i-1]

            Y1=C1-eta1;Y2=E1*eta1-F1

            sita1=(Y2*(D1+sita1)-Y1*(fai1-E1*sita1))/(Y2-G1*Y1)
            eta1=(F1*Y1-C1*Y2)/(Y2-G1*Y1)
            gama1=gama1*(Y2+E1*Y1)/(Y2-G1*Y1)

            sita[i]=sita1;eta[i]=eta1;gama[i]=gama1
        self.alpha=alpha;self.beta=beta;self.zeta=zeta;self.sita=sita;self.eta=eta;self.gama=gama

    def begin_coe(self):
        '''
        返回首节点的系数  begin,end,alpha,beta,zeta
        '''
        begin=self.begin
        end=self.end
        beta=-self.beta[0]
        alpha=self.alpha[0]
        zeta=-self.zeta[0]

        return begin,end,alpha,beta,zeta
    def end_coe(self):
        '''
        返回末节点的系数 end,begin,sita,eta,gama
        '''
        begin=self.begin
        end=self.end
        sita=-self.sita[-1]
        eta=self.eta[-1]
        gama=self.gama[-1]

        return end,begin,sita,eta,gama
    def compute_Q_Z(self,all_Z):
        '''
        计算河段内的水位和流量
        '''
        begin=self.begin;end=self.end
        Za=all_Z[begin];Zb=all_Z[end]
        Z=self.Z
        Q=self.Q

        alpha=self.alpha
        beta=self.beta
        zeta=self.zeta

        sita=self.sita
        eta=self.eta
        gama=self.gama
        for i in range(1,self.num_sec-1):
            Z1=(sita[i]-alpha[i]+gama[i]*Za-zeta[i]*Zb)/(beta[i]-eta[i])
            Q1=alpha[i]+beta[i]*Z1+zeta[i]*Zb
            Q1=sita[i]+eta[i]*Z1+gama[i]*Za
            Z[i]=Z1
            Q[i]=Q1

        Q1=alpha[0]+beta[0]*Za+zeta[0]*Zb
        Q2=sita[self.num_sec-1]+eta[self.num_sec-1]*Zb+gama[self.num_sec-1]*Za

        Z[0]=Za;Z[self.num_sec-1]=Zb;Q[0]=Q1;Q[self.num_sec-1]=Q2
        self.Z=Z;self.Q=Q

        tmp=0
        #print("aaaaaaa:",-Q[tmp]+self.C[tmp]*Z[tmp]+Q[tmp+1]+self.C[tmp]*Z[tmp+1]-self.D[tmp])
        #print("bbbbb:",self.E[tmp]*Q[tmp]-self.F[tmp]*Z[tmp]+self.G[tmp]*self.Q[tmp+1]+self.F[tmp]*Z[tmp+1]-self.fai[tmp])
        return self.ID,self.reach_ID,self.Sec_ID,Q,Z
