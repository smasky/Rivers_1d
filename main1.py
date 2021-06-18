'''
Author: smasky
Date: 2021-06-13 00:19:23
LastEditTime: 2021-06-17 22:14:11
LastEditors: smasky
Description: Use cython to 1d_rivers computation
FilePath: \Rivers_1d\main1.py
You will never know unless you try
'''
from Database_Tools import *
import rivers_1d
import time
# #############Setting##################

# ###################连接数据库
a = time.time()
path = 'test6.db'
conn = rivers_1d.link_database(path)
rivers_1d.begin_project(conn)
b = time.time()
print(b-a)
# conn=create_project(path,'setting.txt','rivers.txt','nodes.txt','sections.txt','boundary.tx
