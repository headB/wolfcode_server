from flask import Flask,request,make_response
import hashlib
import time
import xmltodict
import requests

##调用全局对象,保存对象
from flask import g
#但是也可以考虑redis数据库保存数据


#第一步设置flask实例

app = Flask(__name__)

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

@app.route("/.well-known/pki-validation/fileauth.txt")
def static_1():
    return "201808300150424hp5fbf0mb90bfjb84lbbbmgh1k9shz988f2sfa7ljdx4kx0r5"

#获取token
@app.route("/get_token")
def get_token():
    res = requests.get(url="https://api.weixin.qq.com/sns/oauth2/access_token?appid=wx72e3704260c67375&secret=a746f4c11170781b89378b657537f55b&code=081bG7Sb120gcu0JIhTb1dujSb1bG7Su&state&grant_type=authorization_code")

    content = res.content.decode()
    print(content)
    return "OK",200

#获取用户信息
@app.route("/get_user_info")
def get_user_info():
    
    res = requests.get(url="https://api.weixin.qq.com/sns/userinfo?access_token=13_3KS_bd4SBlDtRwqANxnNQ9acOtvQL3GwPYMUQQsiaWQH0904lN3yF_9-0Y8q28KVCeP6KnpLgmsRP5xEYXEHl5nvWwwyTtlqT0nXQ54FLq4&openid=oDet_1s8FnM_52XTGnikyeSiD0Nk&lang=zh_CN")

    print(res.content.decode())

    return 'xx'

#重新刷新token的数值
@app.route("/refresh_token")
def refresh_token():

    res = requests.get(url="https://api.weixin.qq.com/sns/oauth2/refresh_token?appid=wx72e3704260c67375&grant_type=refresh_token&refresh_token=13_5KcYd9PXfMc2c5HorDLbLo9ewJb5APGB0wmROWPVoOWpo2Dw4GusYNmr4XUyrSPr2Uo_wvoQZw8aOHD8fIUFlzVY6zvMBx0huMQVcWAkP7s")

    print(res.content.decode())

    return 'xxx'

if __name__ == "__main__":

    #app.run(host="0.0.0.0",port=8080,debug=True,ssl_context='adhoc')
    app.run(host="0.0.0.0",port=8080,debug=True,ssl_context=('cert.pem','key.pem'))
