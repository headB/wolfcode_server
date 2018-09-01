import paramiko

#创建ssh对象
ssh = paramiko.SSHClient()



#把主机添加到konwn_host
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#连接到服务器
ssh.connect(hostname=hostname,port=22,username=username,password=password,allow_agent=False,look_for_keys=False)

cmd = 'sys'

stdin, stdout,stderr = ssh.exec_command(cmd)

res = stdout.read()

if not res:
    res = stderr.read()

ssh.close()

print(res)