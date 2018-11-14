from . import micro_app_api
import requests
from config import Config
from flask import request,jsonify,make_response,session
import json
from network_service.v_1_0.register.models import User
from manage import db,logging
from datetime import datetime


@micro_app_api.route("/")
def index():

    #尝试一下获取利用后台反馈用户的openid
    #这里就得配置开发者开发的app_secret
    


    return "你好,这是用于微信小程序的!"

@micro_app_api.route("/verify",methods=['GET','POST'])
def request_verify():
    message = {}
    message['statusCode'] = '201'
    message['status'] = "初始状态,不带数据"

    if request.method == "GET":

        code = request.args.get("code")

        if not code:
            message['status'] = '缺少关键词code'
            return jsonify(message)


        openid = code2openid(code)
        #去请求,尝试获取用户的openid
        

        print(openid)
        if  openid:
            #可以使用数据库查询openid是否存在于数据库当中    
            exist_openid = User.query.filter(User.xcx_openid==openid).first()
            
            

            if exist_openid:
                message['statusCode'] = '200'
                message['status'] = "用户名:%s"%(exist_openid.realname)

                #就是这里了,应该需要返回另外的关键数据了.

                #然后这里还可以添加其他的关键返回参数,例如是token值
                # response = make_response("set cookie")
                # response.set_cookie("username",exist_openid.realname)
                session['username'] = exist_openid.realname
            else:
                #设置回复信息,
                
                message['statusCode'] = '201'
                message['status'] = '没有用户相关信息'
                

            db.session.close()
        
        return jsonify(message)

    
    else:
        
        register_info = request.get_json()
        print(register_info)

        realname = register_info['realname']
        code = register_info['code']

        if not all([realname,code]):
            message['status'] = "参数不完整"
            return jsonify(message)

        #然后就是调用 解code为openid的函数了.

        #获取的到openid,
        openid = code2openid(code)
        print(openid)
        if not openid:
            message['status'] = "获取openid失败"
            return jsonify(message)

        #然后结合realname查询

        #尝试查询是否存在用户
        try:
            exist_user = User.query.filter(User.realname==realname).first()

            if exist_user:

                #如果存在,使用update更新用户信息
                exist_user.xcx_openid_tmp = openid

            else:

                exist_user = User()
                exist_user.username = openid
                exist_user.password = "6666"
                exist_user.department = 20
                exist_user.email = "xxx@wolfcode.cn"
                exist_user.realname = realname
                exist_user.xcx_openid_tmp = openid
            
            insert_time = datetime.now().strftime("%m-%d %H:%M")
            exist_user.quick_verify = insert_time

            db.session.add(exist_user)
            db.session.commit()
            db.session.close()
        
        except Exception as e:
            logging.error(e)
            message['status'] = "数据库操作异常"
            return jsonify(message)

        message['status'] = "申请成功,请等待管理员审核"
            
        return jsonify(message)

@micro_app_api.route("/request",methods=['GET','POST'])
def request_service():

    message = {}
    message['statusCode'] = '201'
    message['status'] = "rquest获取信息失败"
    error_message = jsonify(message)

    if request.method == "POST":
        session_name = session.get('username')
        print(session_name)
        if  session_name:

            request_service = request.get_json()
            request_type = request_service.get("type")

            if  request_type:

                if request_type == 'wifi':

                    wifi_info_dict = []

                    for x,y in Config.WIFI_PWD.items():

                        wifi_tmp = {}
                        wifi_tmp['wifiName'] = x
                        wifi_tmp['passwd'] = y
                        wifi_info_dict.append(wifi_tmp)




                    message['statusCode'] = '200'
                    message['status'] = wifi_info_dict
                
            
            return jsonify(message)

        else:

            message['status'] = "你尚未登陆"
            return jsonify(message)


    else:

        return error_message



def code2openid(code):

    get_openid_url = "https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code"%(Config.app_id,Config.app_secret,code)
    openid = ''
    try:
        res = requests.get(url=get_openid_url,timeout=4)
        response = res.content.decode()
        if res.status_code == 200:
            content = res.content.decode()

            #将内容转换成为字典
            info = json.loads(content)
            openid = info['openid']
            return openid

        else:
            logging.error(response)
            return False
    
    except Exception:
        logging.error(response)
        return False


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
