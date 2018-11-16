from . import micro_app_api
import requests
from config import Config
from flask import request,jsonify,make_response,session
import json
from network_service.v_1_0.register.models import User
from manage import db,logging
from datetime import datetime
from .register.register import redirect_after_weixin_checkin,try_get_estimate_token
from lxml import etree
import re

base_url = "https://weixin.520langma.com"

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
                session['openid'] = exist_openid.xcx_openid

                
                

                try:
                    token = get_access_token_to_estimate(exist_openid.xcx_openid)
                    

                    #尝试整理session值.
                    session['sessionid'] = token.split("=")[1]
                    
                except Exception as e:
                    logging.error(e)
                    #尝试获取estimate的访问token
                    message['status'] = "异常,将无法设置评分系统,但其他正常"
                    return jsonify(message)        
            

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
        session_name1 = session.get('openid')
        
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


#单独设置一个函数用于处理通断网问题
@micro_app_api.route("/query",methods=['GET',"POST"])
def query():

    #重点,  1必须提供openid或者微信小程序的openid
    #       2.必须是登陆过的用户,直接提取session里面的openid来操作.
    # 是啊,一语惊醒梦中人,对啊,可以将token的值保存到临时的session当中的啦.!

    message = {}
    message['statusCode'] = '201'
    message['status'] = "query获取信息失败"
    error_message = jsonify(message)

    header = {"Cookie":"sessionid="+session['sessionid'],'accept':'application/json'}
    
    if session.get("username"):
        if request.method == 'GET':
            req_type = request.args.get("type")

            if req_type == 'network':
            
                req_url = base_url+"/estimate/index/network/"
                try:                  
                    
                    html_1 = requests.get(req_url,headers=header,verify=False)
                except Exception as e:

                    message['status'] = "获取课室网络信息失败"
                    logging.error(e)
                    
                    return jsonify(message)


                message['statusCode'] = '200'
                message['status'] = 'ok'
                message['all_class_info'] = json.loads(html_1.content.decode())
                message['forwardUrl'] = "/estimate/index/set_network/"
                
                return jsonify(message)

            

            elif req_type == 'class_network_account':

                message['statusCode'] = '200'
                message['status'] = "通常是用户名是:你的名字拼音\n通常密码是:你的拼音加@wolfcode\n\n例如:用户名:lizhixuan\n密码:lizhixuan@wolfcode.cn\n\n\n\n如果不行的请使用通用账号\n账号:lizhixuan123\n密码:lizhixuan123"

                return jsonify(message)

            elif req_type == 'estimate_info':

                port = request.args.get('port')

                try:
                    response = requests.get(url=base_url+"/estimate/index/export/?port=%s"%port,headers=header,verify=False)
                    
                    response_content = json.loads(response.content.decode())

                    response_content['status'] = '请求成功'
                    response_content['statusCode'] = '200'

                    return jsonify(response_content)

                except Exception as e:

                    logging.error(e)

                    return error_message

            elif req_type == 'show_detail':

                req_url = request.args.get("url")

                url = base_url+"/estimate/index/export_txt/"+req_url

                response = requests.get(url=url,headers=header)
                
                response_decode = response.content.decode()

                parse_content = etree.HTML(response_decode)

                content = (''.join(parse_content.xpath("/html//div//text()"))).strip().replace("\n",'').replace('/r','')


                message['status'] = "请求成功"
                message['statusCode'] = '200'
                message['content'] = content
                print(content)
                
                return jsonify(message)

            return jsonify(message)

        else:

            return error_message

    else:

        message['status'] = "你尚未登陆"
        return jsonify(message)



#设置一个通用的url跳转功能

@micro_app_api.route("/forward_url/",methods=['GET'])
def forward_url():


    message = {}
    message['statusCode'] = '201'
    message['status'] = "跳转获取信息失败"
    error_message = jsonify(message)


    if request.method == "GET" and session.get("username"):
        headers_info = {'Cookie':'sessionid='+session.get('sessionid')}
        req_url = request.args.get("url")
        
        
        if req_url:   
            
            try:
                set_networks = requests.get(base_url+req_url,headers=headers_info,timeout=10)
                response_content = set_networks.content.decode()
                message['statusCode'] = '200'
                response_parse = etree.HTML(response_content)
                response_content = ''.join(response_parse.xpath("/html//h2//text()"))

                message['status'] = response_content

            except Exception as e:
                return error_message

            return jsonify(message)

        

    return error_message




#设计一个直接兼容使用公众号的函数

#尝试用每个人的openid去estimate获取访问的access_token并且保存到session当中.

def get_access_token_to_estimate(openid):

#尝试利用函数,绕过验证码登陆
    try:
        token = try_get_estimate_token(session.get('openid'))
    
    except Exception as e:
        logging.error(e)


        return False

    return token


#模拟用户使用公众号来请求url
def common_xml_content(openid,req_content):
    
    content = """
    <xml><ToUserName><![CDATA[gh_1bd950877b97]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>1541263645</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><MsgId>6619676950211996607</MsgId></xml>
    """%(openid,req_content)

    headers = {
        "header":"text/xml"
    }

    request = requests.post("https://kumanxuan1.f33322.net/",headers=headers,data=content,verify=False)

    return request
