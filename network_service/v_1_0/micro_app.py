from . import micro_app_api
import requests

@micro_app_api.route("/")
def index():

    #尝试一下获取利用后台反馈用户的openid
    #这里就得配置开发者开发的app_secret

    return "你好,这是用于微信小程序的!"


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
