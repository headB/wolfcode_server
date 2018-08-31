from flask import Flask,request,make_response
import hashlib
import time
import xmltodict
import requests
import json

appid = "wx72e3704260c67375"
secret = "a746f4c11170781b89378b657537f55b"


##调用全局对象,保存对象
from flask import g
#但是也可以考虑redis数据库保存数据

#导入配置
from config import Config,redis_store,decode_state_code

#第一步设置flask实例

app = Flask(__name__)
app.config.from_object(Config)
#配置一下redis先

#添加路由

@app.route("/test")
def index():
    return "welcome"

@app.route("/",methods=["GET","POST"])
def wechat():

    if request.method=='GET':
        token = 'weiphp'
        #获取参数
        data = request.args
        #上面这个我知道，是获取url地址的参数
        signature = data.get("signature")
        timestamp = data.get("timestamp")
        nonce = data.get("nonce")
        echostr = data.get("echostr")
        #对参数进行字典排序，拼接字符串
        temp = [timestamp,nonce,token]
        print(temp)
        #OK！派not all出场
        if not all(temp):
            return "缺少参数",404
        temp.sort()
        temp = ''.join(temp)
        #上面这个过程还是看得懂，就是偷懒，把所有想拼接的字符串收集到一个列表里面，然后用join快速讲列表里面的值进行拼接
        #加密
        x1 = hashlib.sha1(temp.encode()).hexdigest()
        if (x1 == signature):
            return make_response(echostr)
        #上面这个勉强看得明白，但是呢，不是直接return就可以了吗？我准备尝试一下先。
        else:
            return 'error',403
            #这个真的看懂了，flask就是这么直接的
    
    if request.method=="POST":
        xml = request.data
        req = xmltodict.parse(xml)['xml']
        if 'text' == req.get('MsgType'):
            resp = {
                'ToUserName':req.get('FromUserName'),
                'FromUserName':req.get('ToUserName'),
                'CreateTime':int(time.time()),
                'MsgType':'text',
                'Content':req.get('Content')
            }
            xml = xmltodict.unparse({'xml': resp})
            
            print(xml)
            return xml
        else:
            resp = {
                'ToUserName': req.get('FromUserName', ''),
                'FromUserName': req.get('ToUserName', ''),
                'CreateTime': int(time.time()),
                'MsgType': 'text',
                'Content': 'I LOVE ITCAST,https://520su.cn'
            }
            xml = xmltodict.unparse({'xml':resp})
            
            return xml

# @app.route("/.well-known/pki-validation/fileauth.txt")
# def static_1():
#     return "201808300150424hp5fbf0mb90bfjb84lbbbmgh1k9shz988f2sfa7ljdx4kx0r5"

#第一步
#获取code
@app.route("/get_code")
def get_code():
    #res = requests.get(url="")
    if request.method == "GET":

        code = request.args.get('code')
        if code:
            
            #保存code代码，准备用于交换access_token
            redis_store.setex("code",7200,code)

            return "成功获取code"
        else:
            return "获取code失败！",403
    

    
    

#第二步
#获取token
@app.route("/get_token")
def get_token():
    code = redis_store.get("code").decode()
    if not code:
        return "冇token数据",404
    res = requests.get(url="https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&state&grant_type=authorization_code"%(appid,secret,code))

    content = json.loads(res.content.decode())
    #如果成功获取access token的话，就保存到reids中,顺便把用户在这个唯一的公众号的openID也保存到redis中
    access_token = content.get("access_token")
    if access_token:
        redis_store.setex("access_token",7200,access_token)
        redis_store.setex("openid",7200,content.get("openid"))
    else:
        return "无法保存token,%s"%content,404
    
    return content,200

#第四步
#获取用户信息
@app.route("/get_user_info")
def get_user_info():
    
    try:
        access_token = redis_store.get("access_token").decode()
        openid = redis_store.get("openid").decode()
    except Exception as e:
        return "获取通用token，id失败",404


    res = requests.get(url="https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN"%(access_token,openid))

    content = res.content.decode()

    return content,202

#第三步
#重新刷新token的数值
@app.route("/refresh_token")
def refresh_token():



    res = requests.get(url="https://api.weixin.qq.com/sns/oauth2/refresh_token?appid=wx72e3704260c67375&grant_type=refresh_token&refresh_token=13_5KcYd9PXfMc2c5HorDLbLo9ewJb5APGB0wmROWPVoOWpo2Dw4GusYNmr4XUyrSPr2Uo_wvoQZw8aOHD8fIUFlzVY6zvMBx0huMQVcWAkP7s")

    print(res.content.decode())

    return 'xxx'

@app.route("/all_in_one")
def all_in_one():
    #get_code()
    mesg = get_token()
    if not decode_state_code(mesg[1]):
        return mesg[0]

    mesg = get_user_info()
    if not decode_state_code(mesg[1]):
        return mesg[0]

    print(mesg[1])
    
    return "it's well"

if __name__ == "__main__":

    #app.run(host="0.0.0.0",port=8080,debug=True,ssl_context='adhoc')
    app.run(host="0.0.0.0",port=8080,debug=True,ssl_context=('cert.pem','key.pem'))
