'''
Author: smasky
Date: 2021-06-02 16:34:36
LastEditTime: 2025-03-20 09:34:34
LastEditors: smasky
Description: python version for 1d-rivers computaion
FilePath: \River1d\main.py
You will never know unless you try
'''
from pandas.core.arrays.sparse import dtype
from Database_Tools import *
from Reach_class import *
from scipy.linalg import lu, solve
import time
from scipy import interpolate
# setting
aaa = time.time()
In_Q = 0
In_Z = 3.2
path = 'test6.db'
# reload_database(path)
conn=link_database(path)
#conn=create_project(path,"setting.txt","rivers.txt","nodes.txt","sections.txt","boundary.txt")
DT=100
Time=DT*1000

assert type(Time%DT==0)
NT=int(Time/DT)
Inner_reaches=[]
Outer_reaches=[]
N_I,N_O=load_nodes_num(conn)

#####################
Time_index=np.arange(1,Time+DT+1,DT,dtype=float)


Basic_info=load_rivers(conn)
Nodes_info=load_nodes(conn)
Sections_info=load_sections(conn)
Nodes_info=Nodes_info.sort_values(['NAME_ID','Mileage'])
Nodes_num=len(Nodes_info)

group_Sec=Sections_info.groupby('NAME_ID')
temp=Nodes_info.groupby('NAME_ID')
Boundary=pd.read_sql_query('SELECT * FROM BOUNDARY',conn)#NODE_ID,TimeSer,TYPE
Boundary.index=Boundary['NODE_ID']

for ID,group in Nodes_info.groupby('NAME_ID'):#ID相同
    group.sort_values(by="Mileage",inplace=True)
    g_Sec=group_Sec.get_group(ID)
    i=0
    r_i=0
    while i<len(group):
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

        select_Sec=g_Sec[(g_Sec['Mileage']>=mi1)&(g_Sec['Mileage']<=mi2)]
        #####initial Q Z#############
        temp_num=len(select_Sec)
        Initital_Z=np.ones(temp_num)*In_Z
        Initital_Q=np.ones(temp_num)*In_Q
        ################################
        order_mileages=np.array(select_Sec['Mileage'])
        section_id=np.array(select_Sec['Section_ID'])
        X=[];Y=[]
        for j in range(len(select_Sec)):
            temp_json=select_Sec.iloc[j,5]
            temp=eval(temp_json)
            X.append(np.array(temp['x'],dtype=float));Y.append(np.array(temp['y'],dtype=float))
        X=np.array(X,dtype=object)
        Y=np.array(Y,dtype=object)
        
        info={}
        info['Q']=Initital_Q

        info['order_mileages']=order_mileages
        info['x']=X
        info['y']=Y
        YY=np.array(Y,dtype=float)
        y_min=YY.min(axis=1)
        info['Z']=Initital_Z+y_min
        info['num_sec']=len(select_Sec)
        info['section_id']=section_id
        nodes=[node1,node2]
        r=g_Sec['Roughness'].iloc[0]
        if raw1.at[ind1,'If_out'] or raw2.at[ind2,'If_out']:
            if raw1.at[ind1,'If_out']:
                out_node=raw1.at[ind1,'NODE_ID']
                inner_node=raw2.at[ind2,'NODE_ID']
                reserve=0
            else:
                out_node=raw2.at[ind2,'NODE_ID']
                inner_node=raw1.at[ind1,'NODE_ID']
                order_mileages=order_mileages[::-1]
                info['order_mileages']=order_mileages.max()-order_mileages
                X=X[::-1].copy()
                Y=Y[::-1].copy()
                Z=info['Z']
                info['Z']=Z[::-1]
                section_id=section_id[::-1]
                info['x']=X
                info['y']=Y
                info['section_id']=section_id
                reserve=1
            nodes=[out_node,inner_node]
            TimeSer=np.array(eval(Boundary.at[out_node,'TimeSer']),dtype=float)
            a=TimeSer[:,0];b=TimeSer[:,1]
            Time_values=interpolate.interp1d(TimeSer[:,0],TimeSer[:,1],kind='linear')(Time_index)
            TimeSer=np.array([Time_index,Time_values]).T
            Type=Boundary.at[out_node,'TYPE']
            Outer_reaches.append(out_reach(ID,r_i,reserve,Type,info,nodes,TimeSer,DT,0.75,r))
            r_i+=1
        else:
            Inner_reaches.append(inner_reach(ID,r_i,info,nodes,DT,0.75,r))
            r_i+=1
'''
for t in range(100):
    out1=Outer_reaches[0]
    out1.begin=2;out1.end=0
    out2=Outer_reaches[1]
    out2.begin=3;out2.end=1
    out3=Inner_reaches[0]
    out3.begin=0;out3.end=1
    Nodes_matrix=np.zeros((2,2),dtype=float)
    B=np.zeros((2,1))
    out1.update_coe(t)
    out2.update_coe(t)
    out3.update_coe()
    node,coe_z,const_z=out1.node_coe()
    Nodes_matrix[node,node]+=coe_z
    B[node]+=const_z
    node,coe_z,const_z=out2.node_coe()
    Nodes_matrix[node,node]+=coe_z
    B[node]+=const_z

    #print(B)
    node1,node2,alpha,beta,zeta=out3.begin_coe()
    B[node1]+=alpha;Nodes_matrix[node1,node1]+=beta;Nodes_matrix[node1,node2]+=zeta
    node1,node2,sita,eta,gama=out3.end_coe()
    B[node1]+=sita;Nodes_matrix[node1,node1]+=eta;Nodes_matrix[node1,node2]+=gama
    #print(Nodes_matrix)
    #print(B)
    p,l,u =  lu(Nodes_matrix)
    y = solve(p.dot(l), B)
    all_Z = solve(u, y)
    print(all_Z)
    result=pd.DataFrame(columns=['Name_ID','Sec_ID','Q','Z'])
    if(t==99):
        a=1
    ID,Reach_ID,Sec_ID,Q,Z=out1.compute_Q_Z(t,all_Z)
    result=pd.concat([result,pd.DataFrame({'Name_ID':[ID]*len(Sec_ID),'Sec_ID':Sec_ID,'Reach_ID':[Reach_ID]*len(Sec_ID),'Q':Q,'Sec_ID2':Sec_ID,'Z':Z})])#拆
    ID,Reach_ID,Sec_ID,Q,Z=out2.compute_Q_Z(t,all_Z)
    result=pd.concat([result,pd.DataFrame({'Name_ID':[ID]*len(Sec_ID),'Sec_ID':Sec_ID,'Reach_ID':[Reach_ID]*len(Sec_ID),'Q':Q,'Sec_ID2':Sec_ID,'Z':Z})])#拆
    ID,Reach_ID,Sec_ID,Q,Z=out3.compute_Q_Z(all_Z)
    result=pd.concat([result,pd.DataFrame({'Name_ID':[ID]*len(Sec_ID),'Sec_ID':Sec_ID,'Reach_ID':[Reach_ID]*len(Sec_ID),'Q':Q,'Sec_ID2':Sec_ID,'Z':Z})])#拆
    result.sort_values(['Name_ID','Reach_ID','Sec_ID'],inplace=True)
    result.to_csv('temp.csv')
'''

for t in range(300):
    Nodes_matrix=np.zeros((N_I,N_I),dtype=float)
    B=np.zeros((N_I,1))


    for out in Outer_reaches:
        #update_coe()
        out.update_coe(t)
        #out.steady(t,[0.5]*30)
        node,coe_z,const_z=out.node_coe()
        Nodes_matrix[node,node]+=coe_z
        B[node]+=const_z

    for inner in Inner_reaches:
        inner.update_coe()
        node1,node2,alpha,beta,zeta=inner.begin_coe()
        B[node1]+=alpha;Nodes_matrix[node1,node1]+=beta;Nodes_matrix[node1,node2]+=zeta
        node1,node2,sita,eta,gama=inner.end_coe()
        B[node1]+=sita;Nodes_matrix[node1,node1]+=eta;Nodes_matrix[node1,node2]+=gama

    #time_b=time.time()
    ###SOR求解器

    p,l,u =  lu(Nodes_matrix)
    y = solve(p.dot(l), B)
    all_Z = solve(u, y)
    print(t,all_Z)
    ##################################
    #time_c=time.time()
    #result=pd.DataFrame(columns=['Name_ID','Sec_ID','Q','Z'])
    #if(t==int(Time/DT)-1):
      #  aaa=1
    for out in Outer_reaches:
        ID,Reach_ID,Sec_ID,Q,Z=out.compute_Q_Z(t,all_Z)
        #if(t==int(Time/DT)-1):
           # result=pd.concat([result,pd.DataFrame({'Name_ID':[ID]*len(Sec_ID),'Reach_ID':[Reach_ID]*len(Sec_ID),'Sec_ID':Sec_ID,'Q':Q,'Sec_ID2':Sec_ID,'Z':Z})])#拆
    for inner in Inner_reaches:
        ID,Reach_ID,Sec_ID,Q,Z=inner.compute_Q_Z(all_Z)
        #if(t==int(Time/DT)-1):
            #result=pd.concat([result,pd.DataFrame({'Name_ID':[ID]*len(Sec_ID),'Sec_ID':Sec_ID,'Reach_ID':[Reach_ID]*len(Sec_ID),'Q':Q,'Sec_ID2':Sec_ID,'Z':Z})])#拆
    #time_d=time.time()
    #if(t==int(Time/DT)-1):
       # result.sort_values(['Name_ID','Reach_ID','Sec_ID'],inplace=True)
    #记录结果
    #print('t:{},update_coes:{},solve:{},compute:{}'.format(t,time_b-time_a,time_c-time_b,time_d-time_c))
b=time.time()
#result.to_csv('temp1.csv')
print(b-aaa)
print(all_Z)
