# -*- coding: utf-8 -*-
"""
统一使用run.py作为主程序入口，命令行只需要传入如下参数：

配置redis库的ip,port,dbid：所有配置信息都存在这个统一库中

服务ID：每个freetime服务进程都分配一个唯一编号：
格式为：服务类型+具体编号, 例如CO01
参见demo/conf/server.json的具体内容
"""

def main():
    pass
if (__name__ == '__main__'):
    main()