import paramiko
import datetime
import time
import re
from config import switcher_ssh_config as s_s_c
from flask import render_template
#导入蓝图
from . import network_api

#创建蓝图对象


def replace_escape(str):

    return str.replace("---- More ----",'').replace("\x1b[42D",'').replace("  ",'')
        
def multi_cmd(ssh_object,cmds):
    res = []
    for x in cmds:
        ssh_object.send(x)
        time.sleep(0.5)
        res.append(replace_escape(ssh_object.recv(99999).decode()))
    return res

@network_api.route("/get_all_acl")
def get_all_acl():

    #创建ssh对象
    # ssh = paramiko.SSHClient()
    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    import ftplib
    import zipfile

    hostname = s_s_c.hostname
    username = s_s_c.username
    password = s_s_c.password

    # ssh.connect(hostname=hostname,port=22,username=username,password=password,allow_agent=False,look_for_keys=False)

    # chan = ssh.invoke_shell()

    # chan.send("sys\n")
    # chan.send("dis acl all\n               ")
    # time.sleep(1)
    # all_info = chan.recv(99999).decode()
    # all_info = replace_escape(all_info)
    # acl_list = re.findall("Advanced[\s\S]*?\r\n\r\n",all_info)
    # ACL_classification = []

    #使用ftp快速获取当前所有课室的网络情况


    f = ftplib.FTP(hostname) #实例化
    f.login(username,password)

    #获取当前路径
    bufsize = 1024
    fp = open("vrpcfg.zip",'wb')
    f.retrbinary("RETR vrpcfg.zip",fp.write,bufsize)
    fp.close()

    zip_file_target = zipfile.ZipFile("vrpcfg.zip")
    for x in zip_file_target.namelist():
        zip_file_target.extract(x,"vrcfg.txt")
    zip_file_target.close()

    #打开文件
    with open("vrcfg.txt/vrpcfg.cfg") as file1:
        switcher_cfg = file1.readlines()
    
    #然后是正则提取ACL规则

    switcher_cfg = "".join(switcher_cfg)
    

    acl_list = re.findall("acl number [\s\S]*?#",switcher_cfg)

    ACL_classification = []
    print(repr(acl_list))
    #按分类,保存好规则数据
    for x in acl_list:
        ACL_dict = {}
        ACL_dict['name'] = re.findall("(?<=acl number )\d+",x)
        ACL_dict['rule'] = re.findall("rule.+(?=\n)",x)
        ACL_classification.append(ACL_dict)

    ## 尝试循环分类
    for x1 in ACL_classification:
        print("当前规则名称是:%s"%x1['name'])
        print("当前有以下ACL规则↓↓↓↓↓↓")
        for x2 in x1['rule']:
            print("    "+x2)
    # ssh.close()



    return render_template('network/show_acl.html')




# @network_api.route("/test")
# def test_hello():

#     return "if you can echo me,that the import is right!",200

