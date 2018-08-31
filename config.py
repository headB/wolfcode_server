import redis

class Config:
    ##配置redis链接信息
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    #flask-session配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER = True #对cookie中的session_id进行隐藏.!
    PERMANENT_SESSION_LIFETIME = 86400 #session数据的有效期,单位秒


#获取Config的类属性
redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

def decode_state_code(code):
    code = str(code)
    if code.startswith('2'):
        return True
    else:
        return False