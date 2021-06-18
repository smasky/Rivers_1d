/*
 * @Author: smasky
 * @Date: 2021-06-16 21:43:52
 * @LastEditTime: 2021-06-17 22:17:31
 * @LastEditors: smasky
 * @Description: Integrate all Reaches into rivers network 
 * @FilePath: \Rivers_1d\control.h
 * You will never know unless you try
 */
#include <vector>
#include <iostream>
#include "reaches.h"
#include <string.h>
using namespace std;

class Control
{
	public:
		vector<OuterReach*> m_outer;
		vector<InnerReach*> m_inner;
		int has_begin;
		size_t m_size_outer,m_size_inner;
		int m_t,m_total_times;
		double *m_A,*m_b;
		int *m_Ri,*m_Dr,m_length_A,m_length_b;
		int *m_sign_nodes;
		Control();
		~Control();
		void add_Outer_Reach(int river_id,int reach_id,int num_sec, int dt, int begin_node, int end_node, int t_1d_end_node,
		int type_node,int is_resverse, double dev_sita, double roughness,int t,int total_times, int *section_id,
		double *time_series,double *sec_x,double *sec_y,int length_sec_xy,int *points_sec,double *mileage, double *Q, double *Z);

		void add_Inner_Reach(int river_id,int reach_id,int num_sec, int dt, int begin_node, int end_node,int t_1d_begin_begin,
		int t_1d_begin_end,int t_1d_end_end,int t_1d_end_begin, double dev_sita, double roughness,int t,int total_times, int *section_id,double *sec_x,
		double *sec_y,int length_sec_xy,int *points_sec,double *mileage, double *Q, double *Z);

		void set_time_setting(int t,int total_times);
		void set_nodes_setting(double *A,double *b,int *Ri, int *Dr, int *sign_nodes,int length_A,int length_b);
		void begin();

		int get_size_outer();
		int get_size_inner();

		int get_result_outer_n(int n,int *river_id,int *reach_id,int *section_id,double **result_Q, double **result_Z);
		int get_result_inner_n(int n,int *river_id,int *reach_id,int *section_id,double **result_Q, double **result_Z);

 };
