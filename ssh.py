import paramiko
import datetime
import time

#创建ssh对象
ssh = paramiko.SSHClient()

hostname = ''
username = ''
password = ''




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
        time.sleep(1)
        res = ssh_object.recv(999)
        print(res)
        
    # ssh_object.close()

    

# ssh.exec_command("sys")
# ssh.exec_command(cmd)

# stdin, stdout,stderr = ssh.exec_command("dis acl 3307")
# stdin, stdout,stderr = ssh.exec_command("sys")

cmds = ['sys\n','dis acl 3307\n']

multi_cmd(chan,cmds)


print(datetime.datetime.now())