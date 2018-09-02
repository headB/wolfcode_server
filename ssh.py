import paramiko
import datetime
import time
import re

#创建ssh对象
ssh = paramiko.SSHClient()

hostname = ''
username = ''
password = ''


hostname = '192.168.113.254'
username = 'admin'
password = 'kumanxuan@gzit'

#把主机添加到konwn_host
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

time1 = datetime.datetime.now()
print(time1)
#连接到服务器
ssh.connect(hostname=hostname,port=22,username=username,password=password,allow_agent=False,look_for_keys=False)

chan = ssh.invoke_shell()

def multi_cmd(ssh_object,cmds):
    for x in cmds:
        ssh_object.send(x)
        time.sleep(0.5)
        res = replace_escape(ssh_object.recv(99999).decode())
        print((res))

def replace_escape(str):

    return str.replace("---- More ----",'').replace("\x1b[42D",'').replace("  ",'')
        

cmds = ['sys\n','dis acl 3307\n']

multi_cmd(chan,cmds)

chan.send("dis acl all\n               ")
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

print(datetime.datetime.now())