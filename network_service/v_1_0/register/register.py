from flask import render_template,request
import datetime
import time
from . import register_api
import re
import xmltodict
import datetime
from config import Config
import hashlib
from manage import mail,db,logging
from flask_mail import Message
from network_service.v_1_0.register.models import User,ClassRoom
import requests
from sqlalchemy import or_
import json
from hashlib import sha1
from manage import cache

#本微信公众号的号码
host_weixin_openid = 'gh_8e01c367f25d'

#验证码,现在要出动itsdangous了
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


#设置一个函数,去获取access_token,利用的是appid+secret
def get_access_token(Config):

    try:
        req_url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s"%(Config.app_id,Config.app_secret)
        token_response = requests.get(req_url,timeout=4).content.decode()
        token_dict = json.loads(token_response)
        return token_dict['access_token']
    except Exception as e:
        logging.error(e)
        logging.error("获取access_token失败!")

#设计一个获取2个小时有效的jsapi-ticket,主要用于微信的jssdk接口临时使用的.!
@cache.cached(timeout=7000,key_prefix='random_ticket')
def get_js_api_ticket(Config):

    access_token = get_access_token(Config)
    url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi"%access_token
    try:
        response = json.loads(requests.get(url,timeout=4).content.decode())
        return response['ticket']
    except Exception as e:
        logging.error("获取临时ticket失败!")
        return None



#设置一个消息封装

def decode_msg(xml_object):

    content = xmltodict.parse(xml_object)['xml']
    timestamp = time.time()
    return_content = {}
    try:
        return_content['ToUserName'] = content['FromUserName']
        return_content['FromUserName'] = content['ToUserName']
        return_content['CreateTime'] = int(timestamp)
        return_content['MsgType'] = 'text'
        return_content['Content'] = content['Content']
    except Exception as e:
        return False

    return return_content





@register_api.route("/",methods=["GET","POST"])
def index():
    db.session.close()
    if request.method == "POST":
        
        content_xml = request.data
    
        # timestamp = time.mktime(datetime.datetime.now().timetuple())
        timestamp = time.time()
        ##捕捉一些野生openid

        return_content = decode_msg(content_xml)
        req_con = return_content['Content']

        weixin_openid = return_content['ToUserName']
        

        if re.findall("(评分系统|评分|评价|系统)",req_con):

            #获取通讯码
            # code = weixin_checkin_token()
            openid = return_content['ToUserName']

            token = token_create({'open_id':openid},21600)

            return_content['Content'] = "免账号密码登录\n可以点击这里登陆\n6个小时候需重新获取\n\n<a href=\"https://weixin.520langma.com/estimate/login/weixin_checkin/?code=%s\">点我点我</a>"%token
        
        elif re.findall("课室\d+(断|开网)",req_con):
            number = re.findall("课室\d+(?=断|开网)",req_con)

            operate_online = re.findall("开网",req_con)

            if not operate_online:
                operate = "deny"
            else:
                operate = "permit"

            #晕，还是需要去数据库获取课室的地址，不过，巧妙一点。用get的方式。
            try:
                exist_class = ClassRoom.query.filter(ClassRoom.class_number==number[0],ClassRoom.block_number.in_((2,3,4,5))).first()
            # exist_class = ClassRoom.query.filter(ClassRoom.class_number==number).first()
            
                if not exist_class:
                    return_content['Content'] = "稳唔到课室（找不到课室）"
                
            except Exception as e:

                return_content['Content'] = "数据库连接出现异常！"
                db.session.rollback()
            
            else:
                try:
                #获取具体课室的id
                    class_id = exist_class.id
                    #然后调动url了
                    set_network_url = "http://192.168.113.1/estimate/index/set_network/?cls=%s&operate=%s&acl=520su1314"%(class_id,operate)

                    #然后尝试去请求了
                    res = redirect_after_weixin_checkin(weixin_openid,set_network_url)
                    if res['success']:
                        
                        content = re.findall("(?<=<h2>).+?,",res['msg'].content.decode())

                        return_content['Content'] = content[0]
                        
                    else:
                        return_content['Content'] = res['msg']
                    
                except Exception as e:
                    return_content['Content'] = "唔好意思（不好意思），设置失败：错误02"

            #然后就可以调用开网断网的url地址了，这里应该是调用函数了。
            #关键就是，拿到最新的cookie里面的sessionid数值就可以了
            #然后有各式各样的调用，就设置一个公共方法去登陆吧。
            #请求的url地址+weixin_openid就已经足够了，然后就是
        
        elif re.findall("邮箱|绑定",req_con):

            return_content['Content'] = "邮箱绑定,请你按一定要求输入你的邮箱地址\n输入的格式带有前缀 'email#'然后加上'xxxx@wolfcode.cn'，两部分信息\n，示例:\n\nemail#xxxxx@wolfcode.cn\n\n或者是:\n\nemail#xxx@520it.com\n\n发送过程稍慢，请不要重复提交命令"

        elif re.findall("验证|认证",req_con):

            from datetime import datetime as dates
            import random

            now = dates.now().strftime("%m-%d %H:%M")
            verify_code = "".join([ str(random.randint(0,9)) for x in range(4)])
            verify_code_detail = now+" "+verify_code

            is_exist1 = User.query.filter(User.weixin_openid==weixin_openid).first()
            is_exist2 = User.query.filter(User.username==weixin_openid).first()

            if is_exist1 or is_exist2:
                return_content['Content'] = "出錯!你認證過嘅數據存在系數據庫當中,唔使重複申請認證!"
            else:
                # return_content['Content'] = "出錯!數據庫异常!!"
            
            #要么成功插入待认证数据,要么就是已经存在认证数据,又或者数据库异常
                try:
                    admin = User(
                        username = weixin_openid,
                        weixin_openid_tmp = weixin_openid,
                        password = "6666",
                        department = 20,
                        email = "xxx@wolfcode.cn",
                        quick_verify = verify_code_detail,
                        realname = "wolfcode_employee"

                    )
                    # admin = User()
                    # admin.username = weixin_openid
                    # admin.password = "6666"
                    # admin.department = 20
                    # admin.email = "xx@wolfcode.cn"
                    # admin.quick_verify = verify_code_detail
                    # admin.realname = "wolfcode_employee"

                    
                    db.session.add(admin)
                    db.session.commit()

                except Exception as e:
                    logging.error(e)
                    logging.error(admin.__dict__)
                    db.session.rollback()
                    return_content['Content'] = "出錯!數據庫异常!!"

                else:

                    return_content['Content'] = "申請認證成功,呢個系你嘅隨機驗證:%s,請keep好"%verify_code

        #复用验证流程,添加多一个关键字
        elif re.findall("list",req_con):

            #先检查权限
            check_auth = User.query.filter(User.weixin_openid==weixin_openid).first()
            
            if check_auth and (check_auth.id == 5):
                
                
                #查询所有待验证的微信id
                wait_for_verify = User.query.filter(or_(User.weixin_openid_tmp != None,User.xcx_openid_tmp!=None)).all()

                if wait_for_verify:
                    
                    content = ''
                    for x in wait_for_verify:
                        
                        if x.weixin_openid_tmp:
                            types = "公众号认证"
                        else:
                            types = "小程序认证"

                        content += "%s id:%s verify_code:%s\n"%(types,x.id,x.quick_verify)
                    
                    
                    
                    return_content['Content'] = content
                    return_content['Content'] += "\n\n提示:输入confirm#[需要通过的id]#[汉语名字],如果是是认证小程序,请添加#x"


                else:

                    return_content['Content'] = "没有需要等待认证"

            else: 
                return_content['Content'] = "你没有权限！"
             
        elif re.findall("^confirm#(\d+)#(.+)",req_con):
            info = re.findall("^confirm#(\d+)#(.+)",req_con)

            ##复用验证功能.添加认证小程序,或者,
            ##可以给已经认证公众号的同事,添加快速添加小程序认证功能,这个再说吧.现在不急.

            set_xcx_verify = re.findall("^confirm#\d+#(.+)#x",req_con)
            

            if info:
                id = int(info[0][0])
                realname = set_xcx_verify[0]

                #尝试修改认证数据

                #ok,想将公众号刚提交的用户,关联到那些,可能已经登陆的用户信息
                #所以,现在用户名就是关键了.realname就是关键了.
                #所以需要修改规则了

                try:
                    verify = User.query.get(id)
                    if  set_xcx_verify:
                        verify.xcx_openid = verify.xcx_openid_tmp
                        verify.xcx_openid_tmp = None
                    else:
                        verify.weixin_openid = verify.weixin_openid_tmp
                        verify.weixin_openid_tmp = None
                    
                    verify.realname = realname
                    
                    db.session.add(verify)
                    db.session.commit()
                    # verify.realname = realname

                    #查询以realname为条件,是否存在数据
                    is_exist = User.query.filter(User.realname==realname).first()

                    if is_exist and (is_exist.id != verify.id):
                        
                        if  set_xcx_verify:
                            is_exist.xcx_openid = verify.xcx_openid
                            is_exist.xcx_openid_tmp = None
                        else:
                            is_exist.weixin_openid = verify.weixin_openid
                            is_exist.weixin_openid_tmp = None

                        db.session.add(is_exist)
                        db.session.delete(verify)
                        db.session.commit()
                        
                
                except Exception as e:
                    logging.error(e)
                    db.session.rollback()
                    return_content['Content'] = "通过失败!"
                else:                
                    return_content['Content'] = "通过!"

            else:

                return_content['Content'] = "通过失败!"


        elif re.findall("(?<=email#)([a-z]+[0-9]*@(wolfcode\.cn|520it\.com))",req_con):
            x1 = re.findall("(?<=email#)([a-z]+[0-9]*@(wolfcode\.cn|520it\.com))",req_con)

            #邮箱正确,然后就马上发送邮件,根据两端相同的密钥

            
            if send_verify_code(return_content['ToUserName'],x1[0][0]):

                return_content['Content'] = "已经成功发送咗(了)激活码到你的邮箱，请点击邮箱里面的激活码进行实名绑定！"
            else:
                return_content['Content'] = "发送唔成功（不成功）"
 
        elif re.findall("(控制|教室|课室|网络|断网|开网|关闭|打开)",req_con):
    
            return_content['Content'] = "关于如何用语句控制网络的提示↓↓↓↓\n\n开启课室网络，请回复的指定内容，回复内容的格式是(例子):\n课室1开网\n\n关闭课室网络，回复内容的格式:\n课室15断网"
            return_content['Content'] += "\n\n\n备注：目前仅支持广州远程操作，上海和北京暂时只能使用电脑网页端的<评价系统>里面的<网络管理>来控制网络"

        
        elif re.findall("([wW][iI][fF][iI]|无线|密码)",req_con):
            
            user_info = is_user_binding(weixin_openid)

            #可以先尝试组织wifi密码的表达方式

            wifi_info_str = ""

            for name,pwd in Config.WIFI_PWD.items():

                wifi_info_str += "wifi名字:%s\n密码:%s \n\n"%(name,pwd)

            if user_info:
                return_content['Content'] = wifi_info_str
            else:
                return_content['Content'] = "你尚未进行实名公司邮箱认证"

                

        else:

            return_content['Content'] = "操作无效，目前支持的关键字是：教室|课室|网络|断网|开网|关闭|打开|评分系统|wifi"
            

        x1 = xmltodict.unparse({'xml':return_content})
        db.session.close()
        return x1

    else:

        #这里添加一个get请求,这里get请求就捆绑一个数据库请求,大概就是这样子
        if request.args.get("beetle"):
            if request.args.get("beetle") == "diaonimienijiangmiea":
                user_info = User.query.filter().first()
                

        db.session.close()
        return render_template('index.html')
        

@register_api.route("/estimate/login/send_weixin_mail/")
def decode_verify_code():
     
    token = request.args.get('token')

    if not token:
        return "错误，invalid的token"

    #进行解码延签
    try:
    #首先生成一个序列化的对象
        token_info = token_decode(token,300)
        weixin_openid = token_info['weixin_openid']
        email = token_info['email']
    except Exception as e:
        
        return "<h1>通过安检的时候，失败了！请联系管理员</h1>"


    admin = User.query.filter(User.email==email).first()

    
    
    if admin and admin.weixin_openid:
        return "<h1>你已经注册过了,如果需要解绑的话,请联系管理员</h1>"

    #然后呢,就可以操作数据库了.
    elif not admin:
        user_add = User()

        user_add.username = weixin_openid
        user_add.password = "6666"
        user_add.email = email
        user_add.department = 20
        user_add.realname = 'wolfcode_employee'
        user_add.weixin_openid = weixin_openid

        #然后就尝试保存数据
        #但是这个是针对没有绑定过的用户的.
        try:
            db.session.add(user_add)

            #保存的时候,都是用commit,然后呢,假如这里有多个类似`user_add`这样的对象的话,使用db.session.add_all([user_add,])
            db.session.commit()
        except Exception as e:
            
            db.session.rollback()
            return "<h1>保存数据错误,db错误01</h1>"

    else:

        try:
            admin.weixin_openid = weixin_openid
            db.session.add(admin)
            db.session.commit()
        except Exception as e:
            
            db.session.rollback()
            return "<h1>保存数据错误,db错误02<h1>"
        

    db.session.close()
    #没有异常,就证明成功了.!

    return "<h1>实名认证成功!</h1>"

    #然后，现在就进行数据库操作了。！没有错，就是跨数据库工作，虽然也是estimate数据库。


#2019-1-8添加新功能
@register_api.route("/test")
def test():

    jsapi_ticket = get_js_api_ticket(Config)
    print(jsapi_ticket)
    app_id=Config.app_id
    timestamp='1546956170'
    nonce_str='kumanxuan'
    url="http://192.168.113.1%s"%request.path
    signature_values="jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s"%(jsapi_ticket,nonce_str,timestamp,url)
    signature = sha1(signature_values.encode()).hexdigest()

    return render_template('test.html',signature=signature,app_id=app_id,timestamp=timestamp,nonce_str=nonce_str)


def send_verify_code(weixin_opnid,email):

    # 尝试获取open_id
    
    # 初始化一个对象先

    # 把微信的id,添加到加密的token当中.

    

    token_info = {'weixin_openid':weixin_opnid,'email':email}

    token = token_create(token_info,300)
    
    msg = Message("叩丁狼-微信办公-实名登记", sender='lizhixuan@wolfcode.cn', recipients=[email, ])

    msg.body = "hello world!"

    # 编辑好一个用于激活邮箱地址的加密token

    activate_link = "<a href='https://kumanxuan1.f3322.net/estimate/login/send_weixin_mail/?token=%s'>点我实名认证</a>"%token

    msg.html = "hello,点击这个链接完成最后的实名认证:%s"%activate_link

    mail.send(msg)

    return True

def token_create(dict_object,expired):

    serializer = Serializer(Config.SECRET_KEY,expired)
    token_info = serializer.dumps(dict_object)
    return token_info.decode()

def token_decode(token,expired):
    serializer = Serializer(Config.SECRET_KEY,expired)
    token_info = serializer.loads(token)
    return token_info


@register_api.route("/send_message")
def test_independent_send_msg(target_weixin='oDet_1s8FnM_52XTGnikyeSiD0Nk',feedback='你的请求已经完成'):

    timestamp = time.time()
    #最重要是获取对象的open_id
    return_content = {}
    return_content['ToUserName'] = target_weixin
    return_content['FromUserName'] = host_weixin_openid
    return_content['CreateTime'] = int(timestamp)
    return_content['MsgType'] = 'text'
    return_content['Content'] = feedback
    
    content = xmltodict.unparse({'xml':return_content})

    return content

#设置一个专门用于获取访问评分系统的token
def try_get_estimate_token(weixin_openid):

    token = token_create({'open_id':weixin_openid},21600)

    checkin_url = "http://192.168.113.1/estimate/login/weixin_checkin/?code=%s"%token
    res1 = requests.get(checkin_url,verify=False,timeout=5)
    content = res1.content.decode()
    #然后根据内容，查看是否成功登陆
    #随便找一个特征，去认定是否登陆成功
    
    valid_value = re.findall("当前站点",content)
    if valid_value:
        #如果为真的话，就返回token值
        return res1.request.headers.get("cookie")
    else:
        False
    

#尝试获取查看是否具有权限
def is_user_binding(weixin_openid):

    user_info = User.query.filter(User.weixin_openid==weixin_openid).first()
    

    if user_info:
        return True
    else:
        return False

    db.session.close()

#这里设计一个，接收微信公众号匹配的url跳转，但是，这里加了一层认证，根据weixin_openid来做认证

def redirect_after_weixin_checkin(weixin_openid,request_url):

    #调用这个函数的话，每次都得补充当前的weixin_openid+token去访问看看是否能成功获取access_token
    #可以的话，继续下一步。
    
    access_token = try_get_estimate_token(weixin_openid)

    if not access_token:

        # return "获取授权失败，你是否已经绑定邮箱？"
        return {"success":False,'msg':"获取授权失败，你绑定邮箱未？请输入关键字：邮箱，来获取更多信息"}

    headers = {'cookie':access_token}

    try:
        res1 = requests.get(request_url,headers=headers,verify=False)

    except Exception as e:
        pass

    return {"success":True,'msg':res1}



#设置菜单
menu_info = """
{
"button":
        [
            {
                "type": "view",
                "name": "开发指引",
                "url":"http://192.168.113.1/estimate"
            },
            {
                "name": "公众平台",
                "sub_button":
                [
                    {
                        "type": "view",
                        "name": "更新公告",
                        "url": "http://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1418702138&token=&lang=zh_CN"
                    },
                    {
                        "type": "view",
                        "name": "接口权限说明",
                        "url": "http://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1418702138&token=&lang=zh_CN"
                    },
                    {
                        "type": "view",
                        "name": "返回码说明",
                        "url": "http://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1433747234&token=&lang=zh_CN"
                    }
                ]
            }
          ]
}
"""

#创建菜单
def create_menu(accessToken,menu_info):
    post_url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s" %accessToken

    #删除菜单用下面这条
    # post_url = "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token=%s" %accessToken

    # post_data = json.dumps(menu_info)
    try:
        res = requests.post(post_url,menu_info.encode(),timeout=5).content.decode()

        #删除菜单用这条
        # res = requests.get(post_url).content.decode()
        print(res)
    except Exception as e:
        logging.error(e)
        logging.error("创建菜单失败")
        print(e)


#一旦程序运行起来,就直接创建菜单
# token = get_access_token(Config)
# create_menu(token,menu_info)

#尝试获取临时ticket

# @cache.cached(timeout=7200,key_prefix='random_number')
# js_ticket = get_js_api_ticket(Config)

# print(js_ticket)

js_ticket = "HoagFKDcsGMVCIY2vOjf9qYjGFsZIFamI2zJz7boHiwuTzhnS62wv3PqgbbrXhwvX2EFfNS_rq-x9XdrvSYO0w"

# jsapi_ticket=HoagFKDcsGMVCIY2vOjf9qYjGFsZIFamI2zJz7boHiwuTzhnS62wv3PqgbbrXhwvX2EFfNS_rq-x9XdrvSYO0w&noncestr=kumanxuan&timestamp=1546956170&url=https://weixin.520langma.com/test

# jsapi_ticket=HoagFKDcsGMVCIY2vOjf9qYjGFsZIFamI2zJz7boHiwuTzhnS62wv3PqgbbrXhwvX2EFfNS_rq-x9XdrvSYO0w&noncestr=kumanxuan&timestamp=1546956170&url=https://weixin.520langma.com/test



