# distutils: language = c++
import numpy as np
import Database_Tools as DT
import scipy
import datetime
from libc.stdlib cimport malloc, free
from rivers_1d cimport Control

cdef Control c=Control()

cpdef link_database(path):
    conn=DT.link_database(path)
    return conn
cpdef create_project(path,setting,rivers,nodes,sections,boundary):
    conn=DT.create_project(path,setting,rivers,nodes,sections,boundary)
    return conn
cpdef begin_project(conn):

    Inner_reaches=[]
    Outer_reaches=[]
    Basic_info=DT.load_rivers(conn)
    Nodes_info=DT.load_nodes(conn)
    Sections_info=DT.load_sections(conn)
    Boundary=DT.load_boundary(conn)
    Setting=DT.load_setting(conn)
    N_I,N_O=DT.load_nodes_num(conn)
    #########################setting################################
    In_Z=Setting.at[0,'In_Z']
    In_Q=Setting.at[0,'In_Q']
    Begin_time=datetime.datetime.strptime(Setting.at[0,'Begin_time'], "%Y-%m-%d-%H:%M")
    End_time=datetime.datetime.strptime(Setting.at[0,'End_time'],"%Y-%m-%d-%H:%M")
    deta_time=(End_time-Begin_time).seconds
    Step=Setting.at[0,'Step']
    Time_index=np.linspace(1,deta_time,np.int(Step))
    dt=Time_index[1]-Time_index[0]
    dev_sita=Setting.at[0,'Dev_sita']
    ##########################################################
    sign_matrix=np.zeros((N_I,N_I))
    #########################################################
    Nodes_info=Nodes_info.sort_values(['NAME_ID','Mileage'])
    Nodes_num=len(Nodes_info)
    #######################################################河网构建
    group_Sec=Sections_info.groupby('NAME_ID')
    temp=Nodes_info.groupby('NAME_ID')
    Boundary.index=Boundary['NODE_ID']
    for ID,group in Nodes_info.groupby('NAME_ID'):#ID相同
        group.sort_values(by="Mileage",inplace=True)
        g_Sec=group_Sec.get_group(ID)
        i=0
        r_i=0
        while i<len(group):
            info={}
            raw1=group.iloc[[i]];i+=1
            ind1=raw1.index.to_list()[0]
            if i>=len(group):
                break
            raw2=group.iloc[[i]]
            ind2=raw2.index.to_list()[0]
            mi1=raw1.loc[ind1,'Mileage']
            mi2=raw2.loc[ind2,'Mileage']
            node1=raw1.loc[ind1,'NODE_ID']
            node2=raw2.loc[ind2,'NODE_ID']
            ##########################################
            select_Sec=g_Sec[(g_Sec['Mileage']>=mi1)&(g_Sec['Mileage']<=mi2)]
            info['begin_node']=node1;info['end_node']=node2
            #####################is_resverse
            if raw1.at[ind1,'If_out'] or raw2.at[ind2,'If_out']:
                if raw1.at[ind1,'If_out']:
                    begin_node=raw1.at[ind1,'NODE_ID']
                    end_node=raw2.at[ind2,'NODE_ID']
                    reserve=0
                else:
                    begin_node=raw2.at[ind2,'NODE_ID']
                    end_node=raw1.at[ind1,'NODE_ID']
                    reserve=1
            ########################mileage section_id
            order_mileages=np.array(select_Sec['Mileage'],dtype=np.float)
            section_id=np.array(select_Sec['Section_ID'],dtype=np.int)
            if (reserve):
                order_mileages=order_mileages.max()-order_mileages
                order_mileages=np.array(order_mileages[::-1],dtype=np.float,order='c')
                section_id=np.array(section_id[::-1],dtype=np.int,order='c')
            info['mileage']=order_mileages
            info['dt']=dt
            info['total_times']=deta_time
            info['t']=0
            info['river_id']=ID
            info['reach_id']=r_i
            ####################################sec_x,sec_y,points_sec
            if reserve:
                lists=range(len(select_Sec)-2,-1,-1)
                first=len(select_Sec)-1
            else:
                lists=range(1,len(select_Sec))
                first=0
            temp_x=eval(select_Sec.iloc[first,5])['x'];temp_y=eval(select_Sec.iloc[first,5])['y']
            points_sec=[]
            each_sec_ymin=[]
            sec_x=np.array(temp_x,dtype=float)
            sec_y=np.array(temp_y,dtype=float)
            points_sec.append(len(temp_x))
            each_sec_ymin.append(np.min(temp_y))
            for j in lists:
                temp_json=select_Sec.iloc[j,5]
                temp=eval(temp_json)
                temp_x=np.array(temp['x'],dtype=np.float);temp_y=np.array(temp['y'],dtype=np.float)
                sec_x=np.concatenate((sec_x,temp_x))
                sec_y=np.concatenate((sec_y,temp_y))
                points_sec.append(len(temp_x))
                each_sec_ymin.append(np.min(temp_y))
            points_sec=np.array(points_sec,dtype=np.int)
            each_sec_ymin=np.array(each_sec_ymin,dtype=np.float)
            info['sec_x']=sec_x
            info['sec_y']=sec_y
            info['points_sec']=points_sec
            info['length_sec_xy']=sec_x.shape[0]
            ############################Q,Z,num_sec,section_id,roughness
            temp_num=len(select_Sec)
            Z=np.ones(temp_num,dtype=np.float)*In_Z
            Q=np.ones(temp_num,dtype=np.float)*In_Q
            info['Q']=Q
            info['Z']=Z+each_sec_ymin
            info['num_sec']=len(select_Sec)
            info['section_id']=section_id
            info['roughness']=g_Sec['Roughness'].iloc[0]
            info['dev_sita']=dev_sita
            #############################
            if raw1.at[ind1,'If_out'] or raw2.at[ind2,'If_out']:
                if(sign_matrix[end_node,end_node]==0):
                    sign_matrix[end_node,end_node]=1
                info['begin_node']=begin_node;info['end_node']=end_node
                info['is_reserve']=reserve
                TimeSer=np.array(eval(Boundary.at[begin_node,'TimeSer']),dtype=float)
                Time_values=np.interp(Time_index,TimeSer[:,0],TimeSer[:,1])
                TimeSer=np.array([Time_index,Time_values],dtype=np.float).T
                type_node=Boundary.at[begin_node,'TYPE']
                info['time_series']=TimeSer[:,1]
                info['type_node']=int(type_node)
                Outer_reaches.append(info)
                r_i+=1
            else:
                sign_matrix[node1,node1]=1
                sign_matrix[node1,node2]=1
                sign_matrix[node2,node2]=1
                sign_matrix[node2,node1]=1
                Inner_reaches.append(info)
                r_i+=1
    Ri=[0] #数量
    Dr=[] #列
    cor={}
    sign=[]
    index=0
    for i in range(N_I):
        ri=Ri[i]
        for j in range(N_I):
            if(sign_matrix[i,j]==1):
                cor[(i,j)]=index;index+=1
                sign.append(i)
                Dr.append(j)
                ri+=1
        Ri.append(ri)
    Ri=np.array(Ri,dtype=np.int)
    Dr=np.array(Dr,dtype=np.int)
    sign=np.array(sign,dtype=np.int)
    length_A=index
    #################t_1d_XXXX
    for info in Outer_reaches:
        begin_node=info['begin_node']
        end_node=info['end_node']
        t_1d_end_end=cor[(end_node,end_node)]
        info['t_1d_end_end']=t_1d_end_end
    for info in Inner_reaches:
        begin_node=info['begin_node']
        end_node=info['end_node']
        t_1d_begin_begin=cor[(begin_node,begin_node)]
        t_1d_begin_end=cor[(begin_node,end_node)]
        t_1d_end_end=cor[(end_node,end_node)]
        t_1d_end_begin=cor[(end_node,begin_node)]
        info['t_1d_begin_begin']=t_1d_begin_begin
        info['t_1d_begin_end']=t_1d_begin_end
        info['t_1d_end_end']=t_1d_end_end
        info['t_1d_end_begin']=t_1d_end_begin
    all_reaches=Outer_reaches+Inner_reaches
    p_add_Reach(all_reaches)
    p_set_time_setting(0,Step)
    p_set_nodes_setting(np.zeros(length_A,dtype=np.float),np.zeros(N_I,dtype=np.float),
    Ri,Dr,sign,length_A,N_I)
    p_begin()
    ##############################################


cpdef p_add_Reach(infos):
    for info in infos:
        if('time_series' in info):
            _add_Outer_Reach(info['river_id'],info['reach_id'],info['num_sec'],info['dt'],
            info['begin_node'],info['end_node'],info['t_1d_end_end'],info['type_node'],
            info['is_reserve'],info['dev_sita'],info['roughness'],info['t'],
            info['total_times'],info['section_id'],info['time_series'],info['sec_x'],
            info['sec_y'],info['length_sec_xy'],info['points_sec'],info['mileage'],
            info['Q'],info['Z'])
        else:
            _add_Inner_Reach(info['river_id'],info['reach_id'],info['num_sec'],info['dt'],
            info['begin_node'],info['end_node'],info['t_1d_begin_begin'],
            info['t_1d_begin_end'],info['t_1d_end_end'],info['t_1d_end_begin'],
            info['dev_sita'],info['roughness'],info['t'],info['total_times'],
            info['section_id'],info['sec_x'],info['sec_y'],info['length_sec_xy'],
            info['points_sec'],info['mileage'],info['Q'],info['Z'])
cdef _add_Outer_Reach(int river_id,int reach_id,int num_sec, int dt,
    int begin_node, int end_node, int t_1d_end_end,int type_node,int is_resverse,
    double dev_sita, double roughness,int t,int total_times, int[:] section_id,
	double[:] time_series,double[:] sec_x,double[:] sec_y,int length_sec_xy,int[:] points_sec,double[:] mileage,double[:] Q,double[:] Z):
    '''
    input:int river_id,int reach_id,int num_sec,int dt,int begin_node,int end_node,int t_1d_end_node,int type_node,int is_resverse,double dev_sita,double roughness,int t,
    int total_times, int *section_id,double *time_series,double *sec_x,double *sec_y,int length_sec_xy,int *points_sec,double *mileage, double *Q, double *Z
    '''
    c.add_Outer_Reach(river_id,reach_id,num_sec,dt,begin_node,end_node,t_1d_end_end,
    type_node,is_resverse,dev_sita,roughness,t,total_times,&section_id[0],&time_series[0],
    &sec_x[0],&sec_y[0],length_sec_xy,&points_sec[0],&mileage[0],&Q[0],&Z[0])
cpdef _add_Inner_Reach(int river_id,int reach_id,int num_sec, int dt, int begin_node,
    int end_node,int t_1d_begin_begin,int t_1d_begin_end,int t_1d_end_end,int t_1d_end_begin, double dev_sita, double roughness,int t,int total_times, int[:] section_id,double[:] sec_x,double[:] sec_y,int length_sec_xy,int[:] points_sec,double[:] mileage, double[:] Q, double [:] Z):
    '''
    input:int river_id,int reach_id,int num_sec, int dt, int begin_node, int end_node,
    int t_1d_begin_begin,int t_1d_begin_end,int t_1d_end_end,int t_1d_end_begin,
    double dev_sita, double roughness,int t,int total_times, int *section_id,double *sec_x,
    double *sec_y,int length_sec_xy,int *points_sec,double *mileage, double *Q, double *Z
    '''
    c.add_Inner_Reach(river_id,reach_id,num_sec,dt,begin_node,end_node,t_1d_begin_begin,
    t_1d_begin_end,t_1d_end_end,t_1d_end_begin,dev_sita,roughness,t,total_times,&section_id[0],&sec_x[0],&sec_y[0],length_sec_xy,&points_sec[0],&mileage[0],&Q[0],&Z[0])

cpdef p_begin():
    c.begin()
cpdef p_set_time_setting(int t,int total_times):
    c.set_time_setting(t,total_times)
cpdef p_set_nodes_setting(double[:] A,double[:] b,int[:] Ri, int[:] Dr, int[:] sign_nodes,
        int length_A,int length_b):
    c.set_nodes_setting(&A[0],&b[0],&Ri[0],&Dr[0],&sign_nodes[0],length_A,length_b)
