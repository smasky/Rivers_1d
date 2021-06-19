import sqlite3
import os
import pandas as pd
import numpy as np
import json
import datetime
def reload_database(path):
    if os.path.isfile(path):
        os.remove(path)
    link_database(path)
def create_project(project_name,setting_file,basic_river_file,nodes_file,sections_file,boundary_file):
    conn = sqlite3.connect(project_name)
    create_Table(conn)
    read_setting(setting_file,conn)
    read_basic_rivers(basic_river_file,conn)
    read_nodes(nodes_file,conn)
    read_sections(sections_file,conn)
    read_boundary(boundary_file,conn)

    return conn
def link_database(path):
    if os.path.isfile(path):
        conn = sqlite3.connect(path) #
    return conn

def create_Table(conn):
    '''
    初始化数据库创建需要的表 河道表  节点表
    '''
    conn.execute('''CREATE TABLE SECTIONS
       (ID INTEGER PRIMARY KEY  AUTOINCREMENT   NOT NULL,
       NAME_ID        INT    NOT NULL,
       X           FLOAT     ,
       Y           FLOAT     ,
       Section_ID  INTEGER       NOT NULL,
       Section_Info JSON NOT NULL,
       Mileage     FLOAT     NOT NULL,
       Roughness   FLOAT     NOT NULL
       );'''
       )  #河网表 NAME河名称 X,Y 平面位置 Section(可省略) Section_ID 断面id Mileage 断面里程 Roughness 断面的roughness   Section_Info {x:[],y:[]}

    conn.execute(''' CREATE TABLE SETTING
    (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    Step       FLOAT NOT NULL,
    Begin_time  FLOAT NOT NULL,
    End_time    FLOAT NOT NULL,
    Dev_sita FLOAT NOT NULL,
    In_Z     FLOAT NOT NULL,
    In_Q     FLOAT NOT NULL
    );
    ''')

    conn.execute(''' CREATE TABLE NODES
    ( ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      NODE_ID       INTEGER NOT NULL,
      NAME_ID      INTEGER  NOT NULL,
      Mileage      FLOAT NOT NULL,
      If_out       INTEGER  NOT NULL
    );
    ''') #节点表 ID 节点ID NAME 节点所属的河道名称 Mileage 节点的里程 If_out 是否为外节点

    conn.execute(''' CREATE TABLE BASIC_INFO
    (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
     NAME TEXT NOT NULL,
     Mileages FLOAT NOT NULL
    );
    ''') #河道基本信息表 河道名称  N_Sec 断面数量  Mileages 总里程

    conn.execute(''' CREATE TABLE BOUNDARY
    (
        ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        NODE_ID INTEGER NOT NULL,
        TimeSer JSON NOT NULL,
        TYPE INTEGER NOT NULL
    );
    ''')
    conn.commit()
def load_nodes_num(conn):
    '''
    返回内节点的数量
    return: inner_num,outer_num;type: int,int
    '''

    nodes=pd.read_sql_query('SELECT * FROM NODES',conn)
    groups=nodes.groupby('If_out')
    N_I=groups.get_group(0)['NODE_ID'].max()+1
    N_O=groups.get_group(1)['NODE_ID'].max()-N_I+1

    return N_I,N_O
def load_rivers(conn):
    '''
    返回基础河道信息表的信息
    return Basic_rivers;type: pd.DataFrame
    '''

    script="SELECT * FROM BASIC_INFO"
    Basic_rivers=pd.read_sql_query(script,conn) #NAME_ID,ID,NAME,N_sec,Mileage

    return Basic_rivers
def load_nodes(conn):
    '''
    返回节点表的信息
    return Nodes;type: pd.DataFrame
    '''
    script="SELECT * FROM NODES"
    Nodes=pd.read_sql_query(script,conn)

    return Nodes
def load_sections(conn):
    '''
    返回断面信息
    return Sections;type: pd.DataFrame
    '''
    script="SELECT * FROM SECTIONS"
    Sections=pd.read_sql_query(script,conn)

    return Sections

def read_basic_rivers(path,conn):
    '''
    读取河道基本信息存入数据库
    '''
    with open(path,'r') as f:
        lines=f.readlines()
    for line in lines:
        line=line.rstrip('\n').split()
        script="INSERT INTO BASIC_INFO (NAME,Mileages) VALUES(?,?)"
        conn.execute(script,(line[0],line[1]))
    conn.commit()


def read_nodes(path,conn):
    '''
    读取节点信息存入数据库
    '''

    script="Select * FROM BASIC_INFO"
    rivers_info=pd.read_sql_query(script,conn)
    Name_ID=rivers_info['ID'];Mileages=rivers_info['Mileages']
    Nodes={};N=1
    for key,value in rivers_info.iterrows():
        Nodes[N]={'ID': N,'Na':value[1],'Mi':0,'Out':1};N+=1
        Nodes[N]={'ID':N,'Na':value[1],'Mi':value[2],'Out':1};N+=1
    outer_Nodes=pd.DataFrame(Nodes).T
    outer_Nodes=outer_Nodes.convert_dtypes()
    outer_Nodes['Mi']=outer_Nodes['Mi'].astype(float)
    outer_Nodes['ID']=outer_Nodes['ID'].astype(int)
    #inner_Nodes=pd.DataFrame(columns=['Na1','Mi1','Na2','Mi2'])
    with open(path,'r') as f:
        lines=f.readlines()
    inner={}
    for line in lines:
        line=line.rstrip('\n').split()
        inner[N]={'ID':N,'Na1':line[0],'Mi1':line[1],'Na2':line[2],'Mi2':line[3]};N+=1
       # script="INSERT INTO NODES () VALUE({},{},{},{})".format(line[0],line[1],line[2])
        #conn.execute(script)
    inner_Nodes=pd.DataFrame(inner,dtype=str).T
    inner_Nodes=inner_Nodes.convert_dtypes()
    inner_Nodes[['Mi1','Mi2']]=inner_Nodes[['Mi1','Mi2']].astype(float)
    inner_Nodes['ID']=inner_Nodes['ID'].astype(int)
    temp_inner1=inner_Nodes[['ID','Na1','Mi1']].copy().rename(columns={'Na1':'Na','Mi1':'Mi'})
    temp_inner2=inner_Nodes[['ID','Na2','Mi2']].copy().rename(columns={'Na2':'Na','Mi2':'Mi'})
    temp_inner=temp_inner1.append(temp_inner2,ignore_index=True)
    doublication=temp_inner[temp_inner.duplicated(subset=['Na','Mi'], keep=False)]

    for (_,_),group in doublication.groupby(['Na','Mi']):
        id=group['ID'];i_min=id.min()
        ind=temp_inner[temp_inner['ID'].isin(id)].index
        temp_inner.loc[ind,'ID']=i_min
    temp_inner['Out']=np.zeros(len(temp_inner))

    i=0
    a=temp_inner.groupby('ID')
    for _,group in temp_inner.groupby('ID'):
        id=group['ID']
        ind=temp_inner[temp_inner['ID'].isin(id)].index
        temp_inner.loc[ind,'ID']=i;i+=1

    t_max=temp_inner['ID'].max()

    outer_Nodes.loc[:,'ID']+=t_max
    temp_inner=temp_inner.drop_duplicates()
    nodes=temp_inner.append(outer_Nodes,ignore_index=True)
    num_inner=len(temp_inner)
    new_nodes=pd.merge(nodes,rivers_info,left_on='Na',right_on='NAME',suffixes=('_node','_river'),how='left')
    new_nodes[['ID_node','Out','ID_river']].astype(int)
    new_nodes.drop_duplicates(subset = ['Na','Mi'],keep='first',inplace=True)
    new_nodes.loc[new_nodes['Out']==1,"ID_node"]=np.arange(1,len(new_nodes)-num_inner+1)+t_max
    for raw in new_nodes.itertuples():
        script="INSERT INTO NODES (NODE_ID,NAME_ID,Mileage,If_out) VALUES(?,?,?,?)"
        conn.execute(script,(raw[1],raw[5],raw[3],raw[4]))
        conn.commit()
def read_sections(path,conn):
    with open(path,'r') as f:
        lines=f.readlines()
    i=0
    sections={}
    while i<len(lines):
        line=lines[i]
        temp_str=line.rstrip('\n').split()
        if temp_str[0]=='NAME':
            river_name=temp_str[1];i+=1
            line=lines[i];temp_str=line.rstrip('\n').split()
            mileages=temp_str[1];i+=1
            line=lines[i];temp_str=line.rstrip('\n').split()
            roughness=float(temp_str[1]);i+=1
            line=lines[i];temp_str=line.rstrip('\n').split()
            profile=int(temp_str[1]);i+=1


            x_y=np.array([line.rstrip('\n').split() for line in lines[i:i+profile]],dtype=np.float)
            x=x_y[:,0].tolist();y=x_y[:,1].tolist()
            sec_js=json.dumps({'x':x,'y':y})
            sections[i]={"Na":river_name,"Mi":mileages,"Sec_js":sec_js,"Roughness":roughness}
            i=i+profile
        else:
            i+=1
    sec_pd=pd.DataFrame(sections).T
    new_sec=pd.DataFrame(columns=['Na','Mi','Sec_js','Sec_ID'])
    for _,group in sec_pd.groupby('Na'):
        group.sort_values(by='Mi')
        group['Sec_ID']=np.arange(1,len(group)+1)
        group=group.copy()
        new_sec=pd.concat([new_sec,group],ignore_index=True)

    script="INSERT INTO SECTIONS (Section_ID,NAME_ID,Section_INfo,Mileage,Roughness) VALUES(?,?,?,?,?)"
    river_info=pd.read_sql_query('SELECT NAME,ID FROM BASIC_INFO',conn)
    new_sec[['Sec_ID']].astype(int);new_sec['Mi'].astype(float);new_sec['Sec_js'].astype(str)
    new_sec=pd.merge(new_sec,river_info,how="left",left_on='Na',right_on='NAME')
    for row in new_sec.itertuples():
        conn.execute(script,(row[4],row[7],json.dumps(eval(row[3])),row[2],row[5]))
    conn.commit()
def read_boundary(path,conn):
    '''
    读取边界条件文件
    '''
    with open(path,'r') as f:
        lines=f.readlines()
    i=0;bo={}
    while i<len(lines):
        line=lines[i]

        if 'NAME' in line:
            temp_list=line.rstrip('\n').split()
            name=temp_list[1];i+=1;line=lines[i]
            temp_list=line.rstrip('\n').split()
            mi=temp_list[1];i+=1;line=lines[i]
            temp_list=line.rstrip('\n').split()
            num=int(temp_list[1]);i+=1;line=lines[i]
            temp_list=line.rstrip('\n').split()
            type_node=temp_list[1];i+=1
            values=json.dumps([[temp.rstrip('\n').split()[0],temp.rstrip('\n').split()[1]] for temp in lines[i:i+num]]);i=i+num
            bo[i]={'Na':name,'Mi':mi,'Type':type_node,'Values':values}
        else:
            i=i+1
    bound=pd.DataFrame(bo).T
    script='SELECT * FROM BASIC_INFO'
    basic_info=pd.read_sql_query(script,conn)
    script='SELECT * FROM NODES WHERE If_out==1'
    nodes=pd.read_sql_query(script,conn)

    new_bo=pd.merge(bound,basic_info,how='left',left_on='Na',right_on='NAME',suffixes=('_left','_right'))
    new_bo['ID']=new_bo['ID'].astype(int)
    new_bo['Mi']=new_bo['Mi'].astype(float)
    nodes['NAME_ID']=nodes['NAME_ID'].astype(int)
    nodes['Mileage']=nodes['Mileage'].astype(float)

    boundary=pd.merge(new_bo,nodes,how='left',left_on=['ID','Mi'],right_on=['NAME_ID','Mileage'])
    script="INSERT INTO BOUNDARY (NODE_ID,TimeSer,TYPE) VALUES (?,?,?)"

    for raw in boundary.itertuples():
        conn.execute(script,(int(raw[9]),raw[4],int(raw[3])))
    conn.commit()
def load_boundary(conn):
    Boundary=pd.read_sql_query('SELECT * FROM BOUNDARY',conn)#NODE_ID,TimeSer,TYPE
    return Boundary
def read_setting(path,conn):
    with open(path,'r') as f:
        lines=f.readlines()
    i=0
    set={}
    while i<len(lines):
        tmp_str=lines[i].upper()
        if "#" in tmp_str:
            i+=1
            continue
        tmp_str_list=tmp_str.strip('\n').split()

        if "IN_Z" in tmp_str:
            set['IN_Z']=float(tmp_str_list[1])
            i+=1
            continue
        if "IN_Q" in tmp_str:
            set['IN_Q']=float(tmp_str_list[1])
            i+=1
            continue
        if "STEP" in tmp_str:
            set['STEP']=int(tmp_str_list[1])
            i+=1
            continue
        if "BEGIN" in tmp_str:
            set['BEGIN']=tmp_str_list[1]
            i+=1
            continue
        if "END" in tmp_str:
            set['END']=tmp_str_list[1]
            i+=1
            continue
        if "DEV_SITA" in tmp_str:
            set['DEV_SITA']=tmp_str_list[1]
            i+=1
            continue
    script="INSERT INTO SETTING (Step,Begin_time,End_time,Dev_sita,In_Z,In_Q) VALUES (?,?,?,?,?,?)"

    conn.execute(script,(set['STEP'],set['BEGIN'],set['END'],set['DEV_SITA'],
    set['IN_Z'],set['IN_Q']))
    conn.commit()

    return conn
def load_setting(conn):
    Setting=pd.read_sql_query('SELECT * FROM SETTING', conn)
    return Setting

