import redis
from urllib import parse

class Config:
    ##配置redis链接信息

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    #flask-session配置
    #SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER = True #对cookie中的session_id进行隐藏.!
    PERMANENT_SESSION_LIFETIME = 86400 #session数据的有效期,单位秒


    SECRET_KEY = "q1z9=_0k)j_p4n3n^&e-w!r0wv25h7465q_rlb262!lizhixua"

    #这里开始的是关于数据库
    db_pwd = parse.quote_plus("beetleLove@XiaoSu123")
    SQLALCHEMY_DATABASE_URI = "mysql://register:%s@192.168.113.2:3306/estimate?charset=utf8"%db_pwd
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_POOL_RECYCLE= 590
    


    MAIL_SERVER = 'smtp.ym.163.com'  # 电子邮件服务器的主机名或IP地址
    MAIL_PORT = 25  # 电子邮件服务器的端口
    MAIL_USE_TLS = True  # 启用传输层安全
    # 注意这里启用的是TLS协议(transport layer security)，而不是SSL协议所以用的是25号端口
    MAIL_USERNAME = 'lizhixuan@wolfcode.cn'  # 你的邮件账户用户名
    MAIL_PASSWORD = 'lizhixuan123'

    #这里设置一个字典，用于储存公司的wifi账号，密码

    WIFI_PWD = {
        'XMG_2.4':'GM025ITM',
        'XMG_5.3':'GM025ITM',
        'XMG_535':"GM025ITM",
        'wolfcode_wifi':'lizhixuan123',
        'wolfcodewifi':'lizhixuan123',
        'wolfcode_wifi3':'GM025ITM',
        '市场&网络营销部':'GM025ITM',
    }

    #这个是专门用于测试用的app_id
    app_id = 'wx2f6212c8f8f7172e'
    app_secret = 'e7e73777f0b044961cc47a720853b226'   

    #下面这个是真实的app_id
    # app_id = 'wx72e3704260c67375'
    # app_secret = 'a746f4c11170781b89378b657537f55b'


#获取Config的类属性
redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

def decode_state_code(code):
    code = str(code)
    if code.startswith('2'):
        return True
    else:
        return False

class switcher_ssh_config:

    hostname = '192.168.113.254'
    username = 'xmg'
    password = 'xmg175207'
