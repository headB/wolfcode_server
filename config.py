import redis
from urllib import parse

class Config:
    ##配置redis链接信息

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    #flask-session配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER = True #对cookie中的session_id进行隐藏.!
    PERMANENT_SESSION_LIFETIME = 86400 #session数据的有效期,单位秒

    SECRET_KEY = ""

    #这里开始的是关于数据库
    db_pwd = parse.quote_plus("")
    SQLALCHEMY_DATABASE_URI = "mysql://register:%s@192.168.113.2:3306/estimate?charset=utf8&autocommit=true"%db_pwd
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_POOL_RECYCLE= 590

    MAIL_SERVER = 'smtp.ym.163.com'  # 电子邮件服务器的主机名或IP地址
    MAIL_PORT = 25  # 电子邮件服务器的端口
    MAIL_USE_TLS = True  # 启用传输层安全
    # 注意这里启用的是TLS协议(transport layer security)，而不是SSL协议所以用的是25号端口
    MAIL_USERNAME = ''  # 你的邮件账户用户名
    MAIL_PASSWORD = ''

    #这里设置一个字典，用于储存公司的wifi账号，密码

    WIFI_PWD = {
     
    }

#获取Config的类属性
redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

def decode_state_code(code):
    code = str(code)
    if code.startswith('2'):
        return True
    else:
        return False

class switcher_ssh_config:

    hostname = ''
    username = ''
    password = ''
