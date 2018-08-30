from flask import Flask,request,make_response
import hashlib
import time
import xmltodict


#第一步设置flask实例

app = Flask(__name__)

#添加路由

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
            print(req.get('Content'))
            return xml
        else:
            resp = {
                'ToUserName': req.get('FromUserName', ''),
                'FromUserName': req.get('ToUserName', ''),
                'CreateTime': int(time.time()),
                'MsgType': 'text',
                'Content': 'I LOVE ITCAST'
            }
            xml = xmltodict.unparse({'xml':resp})
            return xml
        

if __name__ == "__main__":

    #app.run(host="0.0.0.0",port=8080,debug=True,ssl_context='adhoc')
    app.run(host="0.0.0.0",port=8080,debug=True,ssl_context=('cert.pem','key.pem'))
