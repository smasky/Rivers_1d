#include "control.h"
#include "utils.h"
Control::Control(){
	has_begin=0;
	//cout<<"Linker created successfully"<<endl;
}

Control::~Control(){
	for (vector<OuterReach*>::const_iterator iter =m_outer.cbegin();iter !=m_outer.cend(); iter++){
		(*iter)->~OuterReach();
	}

	for (vector<InnerReach*>::const_iterator iter =m_inner.cbegin();iter !=m_inner.cend(); iter++){
		(*iter)->~InnerReach();
	}
}
void Control::add_Outer_Reach(int river_id,int reach_id,int num_sec, int dt, int begin_node, int end_node, int t_1d_end_node,int type_node,
		int is_resverse, double dev_sita, double roughness,int t,int total_times, int *section_id, double *time_series,
		double *sec_x,double *sec_y,int length_sec_xy,int *points_sec,double *mileage, double *Q, double *Z){
			OuterReach *temp_r=new OuterReach(river_id,reach_id,num_sec,dt,begin_node,end_node,t_1d_end_node,type_node,is_resverse,dev_sita,
			roughness,t,total_times,section_id,time_series,sec_x,sec_y,length_sec_xy,points_sec,mileage,Q,Z);
			m_outer.push_back(temp_r);
			//cout<<"add outer reach sucessfully"<<endl;
		}
void Control::add_Inner_Reach(int river_id,int reach_id,int num_sec, int dt, int begin_node, int end_node,
		int t_1d_begin_begin,int t_1d_begin_end,int t_1d_end_end,int t_1d_end_begin,double dev_sita, double roughness,int t,int total_times,
		int *section_id,double *sec_x,double *sec_y,int length_sec_xy,int *points_sec,double *mileage,double *Q, double *Z){
			InnerReach *temp_r=new InnerReach(river_id,reach_id,num_sec,dt,begin_node,end_node,t_1d_begin_begin,t_1d_begin_end,
			t_1d_end_end,t_1d_end_begin,dev_sita,roughness,t,total_times,section_id,
			sec_x,sec_y,length_sec_xy,points_sec,mileage,Q,Z);
			m_inner.push_back(temp_r);
			//cout<<"add inner reach sucessfully"<<endl;
			
		}

void Control::set_time_setting(int t,int total_times){
		m_t=t;
		m_total_times=total_times;
}
void Control::set_nodes_setting(double *A,double *b,int *Ri,int *Dr,int *sign_nodes, int length_A,int length_b){
	m_A=new double[length_A];
	memcpy(m_A,A,length_A*sizeof(double));

	m_b=new double[length_b];
	memcpy(m_b,b,length_b*sizeof(double));

	m_Ri=new int[length_b+1];
	memcpy(m_Ri,Ri,(length_b+1)*sizeof(int));

	m_Dr=new int[length_A];
	memcpy(m_Dr,Dr,(length_A)*sizeof(int));

	m_sign_nodes=new int[length_A];
	memcpy(m_sign_nodes,sign_nodes,length_A*sizeof(int));

	m_length_A=length_A;
	m_length_b=length_b;
}
void Control::begin(){
	size_t num_outer=m_outer.size();
	int num_inner=m_length_b;
	int num_all=num_outer;
	int sign_node=-1;
	int temp_node,temp_node1,temp_node2;
	double temp_coe,temp_const,temp_alpha,temp_beta,temp_zeta;
	double *all_Z=new double[num_inner];
	
	has_begin=1;
	m_size_outer=m_outer.size();
	m_size_inner=m_inner.size();

	memset(all_Z,0,num_inner*sizeof(double));
	//cout<<m_t<<" "<<m_total_times <<endl;
	for(int t=m_t;t<m_total_times;t++){

		//compute_basic_cofficients+return node_cofficients
		memset(m_A,0,m_length_A*sizeof(double));
		memset(m_b,0,num_inner*sizeof(double));
		for (vector<OuterReach*>::const_iterator iter =m_outer.cbegin();iter !=m_outer.cend(); iter++){
			(*iter)->compute_outer_cofficients();
			(*iter)->return_node_coes(&temp_node,&temp_coe,&temp_const);

			sign_node=m_sign_nodes[temp_node];

			m_b[sign_node]+=temp_const;
			m_A[temp_node]+=temp_coe;
			//cout<<(*iter)->m_river_id<<" "<<(*iter)->m_reach_id<<" "<<temp_const<<" "<<temp_coe<<endl;
		}

		for (vector<InnerReach*>::const_iterator iter =m_inner.cbegin();iter !=m_inner.cend(); iter++){
			(*iter)->compute_inner_cofficients();
			(*iter)->begin_coe(&temp_node1,&temp_node2,&temp_alpha,&temp_beta,&temp_zeta);
			sign_node=m_sign_nodes[temp_node1];
			m_b[sign_node]+=temp_alpha;
			m_A[temp_node1]+=temp_beta;
			m_A[temp_node2]+=temp_zeta;
			(*iter)->end_coe(&temp_node1,&temp_node2,&temp_alpha,&temp_beta,&temp_zeta);
			sign_node=m_sign_nodes[temp_node1];
			m_b[sign_node]+=temp_alpha;
			m_A[temp_node1]+=temp_beta;
			m_A[temp_node2]+=temp_zeta;
		}
		solve_SOR(m_A, m_b, m_Dr, m_Ri,all_Z,m_length_A,num_inner);
		std::cout<<t<<" ";
		for(int num=0;num<num_inner;num++){
			std::cout<<all_Z[num]<<" ";
		}
		std::cout<<std::endl;
		// compute Q_Z
		for (vector<OuterReach*>::const_iterator iter =m_outer.cbegin();iter !=m_outer.cend(); iter++){
			(*iter)->recompute_Q_Z(all_Z);
		}

		for (vector<InnerReach*>::const_iterator iter =m_inner.cbegin();iter !=m_inner.cend(); iter++){
			(*iter)->recompute_Q_Z(all_Z);
		}

	}
}

int Control::get_size_inner(){
	if(has_begin){
		return m_size_inner;
	}

	return -1;

}

int Control::get_size_outer(){
	if(has_begin){
		return m_size_outer;
	}

	return -1;
}

int Control::get_result_outer_n(int n,int *river_id,int *reach_id,int *section_id,double **result_Q, double **result_Z){
	if(has_begin==0){
		return -1;
	}

	if(n>=m_size_outer){
		return -2;
	}

	OuterReach *tmp=m_outer[n];
	*river_id=tmp->m_river_id;
	*reach_id=tmp->m_reach_id;

	section_id=tmp->m_section_id;

	result_Q=tmp->m_result_Q;
	result_Z=tmp->m_result_Z;

	return 1;
}
