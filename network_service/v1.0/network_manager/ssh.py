import paramiko
import datetime
import time
import re
from config import switcher_ssh_config as s_s_c

#导入蓝图
from . import ssh_api

#创建蓝图对象


def replace_escape(str):

    return str.replace("---- More ----",'').replace("\x1b[42D",'').replace("  ",'')
        
def multi_cmd(ssh_object,cmds):
    for x in cmds:
        ssh_object.send(x)
        time.sleep(0.5)
        res = replace_escape(ssh_object.recv(99999).decode())
        return res

@ssh_api.route("/get_all_acl")
def get_all_acl():

    #创建ssh对象
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    hostname = s_s_c.hostname
    username = s_s_c.username
    password = s_s_c.password

    ssh.connect(hostname=hostname,port=22,username=username,password=password,allow_agent=False,look_for_keys=False)

    chan = ssh.invoke_shell()
    cmds = ['sys\n']
    multi_cmd(chan,cmds)

    time.sleep(3)
    all_info = chan.recv(99999).decode()
    all_info = replace_escape(all_info)
    acl_list = re.findall("Advanced[\s\S]*?\r\n\r\n",all_info)
    ACL_classification = []

    #按分类,保存好规则数据
    for x in acl_list:
        ACL_dict = {}
        ACL_dict['name'] = re.findall("ACL \d+",x)[0]
        ACL_dict['rule'] = re.findall("rule .+(?=\()",x)
        ACL_classification.append(ACL_dict)

    ## 尝试循环分类
    for x1 in ACL_classification:
        print("当前规则名称是:%s"%x1['name'])
        print("当前有以下ACL规则↓↓↓↓↓↓")
        for x2 in x1['rule']:
            print("    "+x2)
    return all_info,200


