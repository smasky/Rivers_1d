/*
 * @Author: smasky
 * @Date: 2021-06-16 21:43:52
 * @LastEditTime: 2021-06-18 14:49:49
 * @LastEditors: smasky
 * @Description: reaches class(Reach,OuterReach,InnerReach)
 * @FilePath: \cytest\reaches.h
 * You will never know unless you try
 */

#include<cmath>
#include <algorithm>
#include <math.h>
#include <iostream>
#include <cstring>
class Reach
{
	// base class for outer_Reach or inner_Reach
	protected:
		
		int m_dt;// computaion time step
		double m_dev_sita,m_roughness; //difference coefficient
		// section id in current reach
		double **m_begin_sec_x,**m_begin_sec_y;
		double *m_sec_x,*m_sec_y;
		int *m_points_sec;
		double *m_mileage; //section mileages array
		double *m_Q,*m_Z; //Q:Discharge array;Z:Water array
		double *m_C,*m_D,*m_E,*m_F,*m_G,*m_fai; //used coefficients array
	public: //result interface for python
		int m_river_id,m_reach_id,m_num_sec;// basic information
		int *m_section_id;
		
		Reach(int river_id,int reach_id,int num_sec, int dt, double dev_sita, double roughness,int *section_id, 
		double *sec_x,double *sec_y,int length_sec_xy,int *points_sec, double *mileage, double *Q, double *Z);
		~Reach(); 
		
		void compute_basic_cofficients();
	private:
		void _compute_basic(double *begin_x,double *begin_y,int points_num, double q, double z, double *b,double *r,double *s,double *x, double *alf, double *u);
};

class OuterReach:public Reach
{
	// dervide from Reach class
	private:
		int m_begin_node,m_end_node,m_type_node;
		int m_1d_end_end; 
		int m_is_resverse;
		
		double *m_time_series;
		double *m_P,*m_V,*m_S,*m_T;
		

	public:
		int m_t,m_total_times;
		double *m_result_Q,*m_result_Z;
		OuterReach(int river_id,int reach_id,int num_sec, int dt, int begin_node, int end_node,int t_1d_end_end,int type_node,
		int is_resverse, double dev_sita, double roughness,int t,int total_times, int *section_id, double *time_series,
		double *sec_x,double *sec_y,int length_sec_xy,int *points_sec,double *mileage, double *Q, double *Z);
		void compute_outer_cofficients(); 
		void return_node_coes(int *m_end_node, double *coe_item, double *const_item);
		void recompute_Q_Z(double *all_Z); 
		~OuterReach();
		

		
		
		

};

class InnerReach:public Reach
{
	private:
		int m_begin_node,m_end_node;
		int m_1d_begin_begin,m_1d_begin_end,m_1d_end_begin,m_1d_end_end; 
		
		double *m_alpha,*m_beta,*m_zeta;
		double *m_sita,*m_eta,*m_gama;
		
		
	public:
		int m_t,m_total_times;
		double *m_result_Q,*m_result_Z;
		InnerReach(int river_id,int reach_id,int num_sec, int dt, int begin_node, int end_node,
		int t_1d_begin_begin,int t_1d_begin_end,int t_1d_end_end,int t_1d_end_begin,double dev_sita, 
		double roughness,int t,int total_times, int *section_id,double *sec_x,double *sec_y,
		int length_sec_xy,int *points_sec,double *mileage, double *Q, double *Z);
		void compute_inner_cofficients();
		void begin_coe(int *node1, int *node2, double *alpha, double *beta, double *zeta);
		void end_coe(int *node1, int *node2, double *sita, double *eta, double *gama);
		void recompute_Q_Z(double *all_Z); 
		~InnerReach();
		
		
};

