from . import micro_app_api
import requests
from config import Config
from flask import request
import json
from network_service.v_1_0.register.models import User


@micro_app_api.route("/")
def index():

    #尝试一下获取利用后台反馈用户的openid
    #这里就得配置开发者开发的app_secret
    


    return "你好,这是用于微信小程序的!"

@micro_app_api.route("/verify")
def request_verify():

    if request.method == "GET":

        code = request.args.get("code")


        get_openid_url = "https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code"%(Config.app_id,Config.app_secret,code)

        #去请求,尝试获取用户的openid
        openid = ''
        try:
            res = requests.get(url=get_openid_url,timeout=4)
            print(res.status_code)
            if res.status_code == 200:
                content = res.content.decode()
                print(content)

                #将内容转换成为字典

                info = json.loads(content)
                openid = info['openid']

            else:
                return "bakckend network error"
        
        except Exception:
            return "backend request is bad"

        print(openid)
        if  openid:
            #可以使用数据库查询openid是否存在于数据库当中    
            exist_openid = User.query.filter(User.xcx_openid==openid).first()

            print(exist_openid)
        
        return "OK"

    
    else:
        return "请使用get方法,非post!"




#设计一个直接兼容使用公众号的函数


#模拟用户使用公众号来请求url
def common_xml_content(openid,req_content):
    
    content = """
    <xml><ToUserName><![CDATA[gh_1bd950877b97]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>1541263645</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><MsgId>6619676950211996607</MsgId></xml>
    """%(openid,req_content)

    headers = {
        "header":"text/xml"
    }

    request = requests.post("http://127.0.0.1/",headers=headers,data=content)

    return request
