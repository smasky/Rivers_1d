#include "reaches.h"
#include <iostream>
// 1d rivers network programe
// smasky 20210607
Reach::Reach(int river_id, int reach_id,int num_sec,int dt,double dev_sita,double roughness,int *section_id,
		double *sec_x,double *sec_y,int length_sec_xy,int *points_sec, double *mileage, double *Q, double *Z):m_river_id(river_id),
		m_reach_id(reach_id),m_num_sec(num_sec),m_dt(dt),m_dev_sita(dev_sita),m_roughness(roughness){
		//////////////////////////////////////////////////
			m_Q= new double[m_num_sec];
			memcpy(m_Q,Q,m_num_sec*sizeof(double));
			m_Z= new double[m_num_sec];
			memcpy(m_Z,Z,m_num_sec*sizeof(double));
			m_mileage= new double[m_num_sec];
			memcpy(m_mileage,mileage,m_num_sec*sizeof(double));
			m_section_id=new int[m_num_sec];
			memcpy(m_section_id,section_id,m_num_sec*sizeof(int));
			m_points_sec=new int[m_num_sec];
			memcpy(m_points_sec,points_sec,m_num_sec*sizeof(int));
			//for (int i=0;i<m_num_sec;i++){
				//m_points_sec[i]=points_sec[i];
				//m_section_id[i]=section_id[i];
			//}
		////////////////////////////////////////////////
			m_C=new double[m_num_sec];
			m_D=new double[m_num_sec];
			m_E=new double[m_num_sec];
			m_F=new double[m_num_sec];
			m_G=new double[m_num_sec];
			m_fai=new double[m_num_sec];
			/////////////////////////////////////////////
			/////////////////////////////////////////////
			m_sec_x=new double[length_sec_xy];
			m_sec_y=new double[length_sec_xy];
			/////////////////////////////////////////////////
			m_begin_sec_x=new double*[m_num_sec];
			m_begin_sec_y=new double*[m_num_sec];

			for (int i=0;i<length_sec_xy;i++){
				m_sec_x[i]=sec_x[i];
				m_sec_y[i]=sec_y[i];
			}

			double *tmp_pr_x=m_sec_x, *tmp_pr_y=m_sec_y;

			for (int i=0;i<m_num_sec;i++){
				m_begin_sec_x[i]=tmp_pr_x;
				m_begin_sec_y[i]=m_sec_y;
				tmp_pr_x=tmp_pr_x+points_sec[i];
				tmp_pr_y=tmp_pr_y+points_sec[i];
			}
		}
Reach::~Reach(){
	delete []m_points_sec;
	delete []m_section_id;
	delete []m_C;delete []m_D; delete []m_E; delete []m_F; delete []m_G;delete []m_fai;
	delete []m_sec_x; delete []m_sec_y;
	delete []m_begin_sec_x; delete []m_begin_sec_y;



	delete []m_Q;delete []m_Z;delete []m_mileage;
}
void Reach::compute_basic_cofficients(){
	double b1=0,b2=0,s1=0,s2=0,x1=0,x2=0,alf1=0,alf2=0,u1=0,u2=0,r1=0,r2=0;
	double dx=0,sa=0,sb=0;
	double z1=0,z2=0,q1=0,q2=0,bc=0;
	double c1=0,d1=0,e1=0,g1=0,f1=0,fai1=0,tmp=0;

	z1=m_Z[0];
	q1=m_Q[0];
	_compute_basic(m_begin_sec_x[0],m_begin_sec_y[0],m_points_sec[0],m_Q[0],m_Z[0],&b1,&r1,&s1,&x1,&alf1,&u1);

	for (int i=1;i<m_num_sec;i++){
		z2=m_Z[i];
		q2=m_Q[i];

		_compute_basic(m_begin_sec_x[i],m_begin_sec_y[i],m_points_sec[i],q2,z2,&b2,&r2,&s2,&x2,&alf2,&u2);

		dx=m_mileage[i]-m_mileage[i-1];

		sa=fabs(u1)*9.81*pow(m_roughness,2)*dx/(pow(r1,1.33)*2*m_dev_sita);
		sb=fabs(u2)*9.81*pow(m_roughness,2)*dx/(pow(r2,1.33)*2*m_dev_sita);

		bc=(b1+b2)/2;

		c1=bc*dx/(2*m_dt*m_dev_sita);
		d1=c1*(z1+z2)-(1-m_dev_sita)*(q2-q1)/m_dev_sita;
		e1=dx/(2*m_dev_sita*m_dt)-(alf1*u1)+sa;
		g1=dx/(2*m_dev_sita*m_dt)+(alf2*u2)+sb;
		f1=9.81*(s1+s2)/2;
		tmp=alf2*u2*q2-alf1*u1*q1;
		fai1=dx/(2*m_dev_sita*m_dt)*(q1+q2)-(1-m_dev_sita)*(tmp)/m_dev_sita-(1-m_dev_sita)*f1*(z2-z1)/m_dev_sita;

		m_C[i-1]=c1;
		m_D[i-1]=d1;
		m_E[i-1]=e1;
		m_F[i-1]=f1;
		m_G[i-1]=g1;
		m_fai[i-1]=fai1;

		b1=b2;z1=z2;q1=q2;u1=u2;s1=s2;r1=r2;alf2=alf1;
	}

	z1=0;



}

void Reach::_compute_basic(double *begin_x,double *begin_y,int points_num, double q, double z, double *b,double *r,double *s,double *x, double *alf, double *u){
	double x1,x2,y1,y2,deta1,deta2,deta_x;
	*b=0;*r=0;*s=0;*x=0;*alf=0;*u=0;
	for (int i=0;i<points_num-1;i++){
		x1=begin_x[i];
		x2=begin_x[i+1];
		y1=begin_y[i];
		y2=begin_y[i+1];

		if(z<=std::min(y1,y2)){
			continue;
		}

		deta1=z-y1;deta2=z-y2;deta_x=x2-x1;
		if(deta1<0){
			deta1=0;
			deta_x=deta2/(y1-y2)*deta_x;
		}else if (deta2<0){
			deta2=0;
			deta_x=deta1/(y2-y1)*deta_x;
		}

		*s=*s+0.5*(deta1+deta2)*deta_x;
		*x=*x+sqrt(pow((deta1-deta2),2)+pow(deta_x,2));
		*b=*b+deta_x;
	if(*x<1e-10){
			*r=0.1;
	}else{
			*r=*s/(*x);
	}
	*alf=1.0;
	*u=q/(*s);
	}
}

OuterReach::OuterReach(int river_id,int reach_id,int num_sec, int dt, int begin_node, int end_node, int t_1d_end_end,int type_node,
		int is_resverse, double dev_sita, double roughness,int t,int total_times,int *section_id, double *time_series,
		double *sec_x,double *sec_y,int length_sec_xy,int *points_sec, double *mileage, double *Q, double *Z):Reach(river_id,
		reach_id,num_sec,dt,dev_sita,roughness,section_id, sec_x,sec_y,length_sec_xy,points_sec,mileage,Q,Z),
		m_begin_node(begin_node),m_end_node(end_node),m_is_resverse(is_resverse),m_type_node(type_node),m_t(t),m_1d_end_end(t_1d_end_end){
			/////////////////////////////////////
			m_time_series=new double[total_times];
			memcpy(m_time_series,time_series,total_times*sizeof(double));
			//////////////////////////////////////
			m_P=new double[m_num_sec];
			m_V=new double[m_num_sec];
			m_S=new double[m_num_sec];
			m_T=new double[m_num_sec];

			m_result_Q=new double*[total_times];
			for (int i=0;i<total_times;i++){
				m_result_Q[i]=new double[m_num_sec];
			}

			m_result_Z=new double*[total_times];
			for (int i=0;i<total_times;i++){
				m_result_Z[i]=new double[m_num_sec];
			}

		}
OuterReach::~OuterReach(){
	delete []m_P;delete []m_V;delete []m_S;delete []m_T;
	for (int i=0;i<m_num_sec;i++){
		delete []m_result_Q[i];
		delete []m_result_Z[i];
	}
	delete []m_result_Q;
	delete []m_time_series;
	delete []m_result_Z;

}

void OuterReach::compute_outer_cofficients(){
	double c1,d1,e1,f1,g1,fai1;
	double y1,y2,y3,y4;
	double s1,t1,p1,v1;
	compute_basic_cofficients();
	m_P[0]=m_time_series[m_t];
	m_V[0]=0;
	p1=m_P[0];
	v1=m_V[0];

	for (int i=1;i<m_num_sec;i++){
		c1=m_C[i-1];d1=m_D[i-1];e1=m_E[i-1];f1=m_F[i-1];g1=m_G[i-1];fai1=m_fai[i-1];
		if(m_type_node==1){
			// water level node
			y1=d1-c1*p1;
			y2=fai1+f1*p1;
			y3=1+c1*v1;
			y4=e1+f1*v1;

			s1=(c1*y2-f1*y1)/(f1*y3+c1*y4);
			t1=(g1*c1-f1)/(f1*y3+c1*y4);
			p1=(y1+y3*s1)/c1;
			v1=(y3*t1+1)/c1;

		}else{
		    // discharge node
			y1=c1+v1;
			y2=f1+e1*v1;
			y3=d1+p1;
			y4=fai1-e1*p1;

			s1=(g1*y3-y4)/(y1*g1+y2);
			t1=(g1*c1-f1)/(y1*g1+y2);
			p1=(y3-y1*s1);
			v1=(c1-y1*t1);
		}

		m_S[i]=s1;
		m_T[i]=t1;
		m_P[i]=p1;
		m_V[i]=v1;
		//std::cout<<s1<<" "<<t1<<" "<<p1<<" "<<std::endl;
	}


}

void OuterReach::return_node_coes(int *end_node, double *coe_item, double *const_item){
	*end_node=m_1d_end_end;
	if(m_type_node==1){
		*coe_item=-1/m_V[m_num_sec-1];
		*const_item=-m_P[m_num_sec-1]/(m_V[m_num_sec-1]);
	}else{
		*coe_item=-m_V[m_num_sec-1];
		*const_item=-m_P[m_num_sec-1];
	}
}

void OuterReach::recompute_Q_Z(double *all_Z){
	double Zb;
	double q1,z1;
	Zb=all_Z[m_end_node];
	m_Z[m_num_sec-1]=Zb;
	if(m_type_node==1){
		// water level node
		m_Z[0]=m_time_series[m_t];
		q1=m_P[m_num_sec-1]/m_V[m_num_sec-1]-(1/m_V[m_num_sec-1])*Zb;
		m_Q[m_num_sec-1]=q1;
	}else{
		// discharge level node
		m_Q[0]=m_time_series[m_t];
		z1=Zb;
		m_Q[m_num_sec-1]=m_P[m_num_sec-1]-m_V[m_num_sec-1]*z1;
	}

	for(int i=m_num_sec-2;i>-1;i--){
		if(m_type_node==1){
			q1=m_S[i+1]-m_T[i+1]*q1;
			z1=m_P[i]-m_V[i]*q1;
		}else{
			z1=m_S[i+1]-m_T[i+1]*z1;
			q1=m_P[i]-m_V[i]*z1;
		}

		m_Q[i]=q1;
		m_Z[i]=z1;
	}
	//TODO  result new double*[total_times];
	if(m_is_resverse==1){
		for (int i=0;i<m_num_sec;i++){
		m_result_Q[m_t][m_num_sec-1-i]=-m_Q[i];
		m_result_Z[m_t][m_num_sec-1-i]=m_Z[i];
		}
	}else{
		for (int i=0;i<m_num_sec;i++){
		m_result_Q[m_t][i]=m_Q[i];
		m_result_Z[m_t][i]=m_Z[i];
		}
	}
	// TMEP: update m_t
	m_t+=1;

}

InnerReach::InnerReach(int river_id,int reach_id,int num_sec, int dt, int begin_node, int end_node,
		int t_1d_begin_begin,int t_1d_begin_end,int t_1d_end_end,int t_1d_end_begin,double dev_sita,
		double roughness,int t,int total_times, int *section_id,double *sec_x,double *sec_y,
		int length_sec_xy,int *points_sec,double *mileage, double *Q,
		double *Z):Reach(river_id,reach_id,num_sec,dt,dev_sita,roughness,section_id,
		sec_x,sec_y,length_sec_xy,points_sec,mileage,Q,Z),m_begin_node(begin_node),m_end_node(end_node),
		m_1d_begin_begin(t_1d_begin_begin),m_1d_begin_end(t_1d_begin_end),m_1d_end_end(t_1d_end_end),
		m_1d_end_begin(t_1d_end_begin),m_t(t),m_total_times(total_times){
			m_alpha= new double[m_num_sec];
			m_beta=new double[m_num_sec];
			m_zeta=new double[m_num_sec];

			m_sita=new double[m_num_sec];
			m_eta=new double[m_num_sec];
			m_gama=new double[m_num_sec];

			m_result_Q=new double*[total_times];
			for (int i=0;i<total_times;i++){
				m_result_Q[i]=new double[m_num_sec];
			}

			m_result_Z=new double*[total_times];
			for (int i=0;i<total_times;i++){
				m_result_Z[i]=new double[m_num_sec];
			}
		}
InnerReach::~InnerReach(){
	delete []m_alpha;delete []m_zeta;delete []m_beta;delete []m_sita;delete []m_eta;delete []m_gama;

	for (int i=0;i<m_total_times;i++){
		delete []m_result_Q[i];
		delete []m_result_Z[i];
	}
	delete []m_result_Q;
	delete []m_result_Z;
}
void InnerReach::compute_inner_cofficients(){
	double alpha1,beta1,zeta1,sita1,eta1,gama1;
	double c1,d1,e1,f1,g1,fai1;
	double y1,y2;
	int be_end;

	be_end=m_num_sec-2;
	compute_basic_cofficients();

	fai1=m_fai[be_end];c1=m_C[be_end];d1=m_D[be_end];g1=m_G[be_end];e1=m_E[be_end];f1=m_F[be_end];
	//
	alpha1=(fai1-g1*d1)/(g1+e1);beta1=(c1*g1+f1)/(g1+e1);zeta1=(c1*g1-f1)/(g1+e1);
	m_alpha[be_end]=alpha1;m_beta[be_end]=beta1;m_zeta[be_end]=zeta1;
	for (int i=be_end-1;i>-1;i--){
		c1=m_C[i];d1=m_D[i];e1=m_E[i];f1=m_F[i];g1=m_G[i];fai1=m_fai[i];

		y1=c1+beta1;
		y2=g1*beta1+f1;

		alpha1=(y1*(fai1-alpha1*g1)-y2*(d1-alpha1))/(e1*y1+y2);
		beta1=(y2*c1+y1*f1)/(y1*e1+y2);
		zeta1=zeta1*(y2-y1*g1)/(y1*e1+y2);

		m_alpha[i]=alpha1;m_beta[i]=beta1;m_zeta[i]=zeta1;
	}
	//
	fai1=m_fai[0];c1=m_C[0];d1=m_D[0];g1=m_G[0];e1=m_E[0];f1=m_F[0];

	sita1=(e1*d1+fai1)/(e1+g1);eta1=-(c1*e1+f1)/(e1+g1);gama1=(f1-c1*e1)/(e1+g1);

	m_sita[1]=sita1;m_eta[1]=eta1;m_gama[1]=gama1;
	for (int i=2;i<m_num_sec;i++){
		c1=m_C[i-1];d1=m_D[i-1];e1=m_E[i-1];f1=m_F[i-1];g1=m_G[i-1];fai1=m_fai[i-1];

		y1=c1-eta1;y2=e1*eta1-f1;

		sita1=(y2*(d1+sita1)-y1*(fai1-e1*sita1))/(y2-g1*y1);
		eta1=(f1*y1-c1*y2)/(y2-g1*y1);
		gama1=gama1*(y2+e1*y1)/(y2-g1*y1);
		//std::cout<<c1<<" "<<d1<<" "<<e1<<" "<<f1<<" "<<g1<<" "<<fai1<<std::endl;
		//std::cout<<sita1<<" "<<eta1<<" "<<gama1<<" "<<std::endl;
		m_sita[i]=sita1;m_eta[i]=eta1;m_gama[i]=gama1;
	}
	//std::cout<<m_river_id<<m_sita[m_num_sec]<<m_eta[3]<<m_gama[2]<<m_beta[2]<<std::endl;
}

void InnerReach::begin_coe(int *node1, int *node2, double *alpha, double *beta, double *zeta){
	(*node1)=m_1d_begin_begin;(*node2)=m_1d_begin_end;
	(*beta)=-m_beta[0];(*alpha)=m_alpha[0];(*zeta)=-m_zeta[0];
}

void InnerReach::end_coe(int *node1, int *node2, double *sita, double *eta, double *gama){
	(*node1)=m_1d_end_end;(*node2)=m_1d_end_begin;

	(*sita)=-m_sita[m_num_sec-1];(*eta)=m_eta[m_num_sec-1];(*gama)=m_gama[m_num_sec-1];
}

void InnerReach::recompute_Q_Z(double *all_Z){
	double Za,Zb,Z1,Q1,Q2;

	Za=all_Z[m_begin_node];Zb=all_Z[m_end_node];

	for (int i=1;i<m_num_sec-1;i++){
		Z1=(m_sita[i]-m_alpha[i]+m_gama[i]*Za-m_zeta[i]*Zb)/(m_beta[i]-m_eta[i]);
		Q1=m_alpha[i]+m_beta[i]*Z1+m_zeta[i]*Zb;

		m_Z[i]=Z1;
		m_Q[i]=Q1;
	}

	Q1=m_alpha[0]+m_beta[0]*Za+m_zeta[0]*Zb;
	Q2=m_sita[m_num_sec-1]+m_eta[m_num_sec-1]*Zb+m_gama[m_num_sec-1]*Za;

	m_Z[0]=Za;m_Z[m_num_sec-1]=Zb;;m_Q[0]=Q1;m_Q[m_num_sec-1]=Q2;

	for (int i=0;i<m_num_sec;i++){
		m_result_Q[m_t][i]=m_Q[i];
		m_result_Z[m_t][i]=m_Z[i];
	}
 }
