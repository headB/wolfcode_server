# 这个就专门将微信的openid绑定到公司邮箱的
# 这个过程都是使用蓝图的

#这里,设计两个地方
#一个负责注册
#另一个负责登录把.反正都是不负责的.

#OK,
#首先需要知道的是,让公司的员工的微信openid绑定公司邮箱,进行实名认证

#1.openid
#2.email
#3.department
#4.login_time

#然后,权限可以另外设置权限表,先不着急,先设置

#然后呢,注册的时候,这里就需要模拟提供信息给<评分系统>,因为<评分系统>是独立的.!

#然后评分系统唯一需要改的地方就是,在登录验证的时候,去除验证码!

from flask import render_template,request
import datetime
import time
from . import register_api
import re
import xmltodict
import datetime
from config import Config
import hashlib
from manage import mail,db
from flask_mail import Message
from network_service.v_1_0.register.models import User,ClassRoom
import requests

#本微信公众号的号码
host_weixin_openid = 'gh_8e01c367f25d'

#验证码,现在要出动itsdangous了
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


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
    #调用首页显示
    #但是根据实际的请求来操作
    #例如消息都是post的方式
    #然后普通pc访问都是get方式
    
    if request.method == "POST":
        
        #接收一些参数
        #1.ToUserName
        #2.FromUserName
        #3.Create
        #4.MsgType
        #5.Content
        #6.MsgId

        content_xml = request.data
    
        # timestamp = time.mktime(datetime.datetime.now().timetuple())
        timestamp = time.time()
        ##捕捉一些野生openid
        return_content = decode_msg(content_xml)
        print(return_content)
        req_con = return_content['Content']

        weixin_openid = return_content['ToUserName']
        
        #现在问题就是，如何接收一坨的xml标签的内容呢？

        #根据请求，返回不同的响应

        #假如

        #匹配到 #课室4#开网

        ##想想#号也是太难输入了，反正参数不多，直接输入整条语句吧。

        #或者类似这样 #讲师/班主任/辅导员评价#名字#课室
        #评价算了吧。。。。需要的信息太多了。！

        #第一步肯定是直接尝试捕捉命令，但是如果失败，就输出提示
        #if re.findall("")


        #然后到了最后就输出所有提示，当前暂时就是涉及到关键字，课室，教室，网络，开网，断网

        if re.findall("(评分系统|评分|评价|系统)",req_con):

            #获取通讯码
            # code = weixin_checkin_token()
            openid = return_content['ToUserName']

            token = token_create({'open_id':openid},21600)

            return_content['Content'] = "免账号密码登录\n可以点击这里登陆\n6个小时候需重新获取\n\n<a href=\"https://weixin.520langma.com/estimate/login/weixin_checkin/?code=%s\">点我点我</a>"%token
            print(return_content['Content'])
        
        elif re.findall("课室\d+(断|开网)",req_con):
            number = re.findall("课室\d+(?=断|开网)",req_con)

            operate_online = re.findall("开网",req_con)

            if not operate_online:
                operate = "deny"
            else:
                operate = "permit"

            #晕，还是需要去数据库获取课室的地址，不过，巧妙一点。用get的方式。

            exist_class = ClassRoom.query.filter(ClassRoom.class_number==number[0],ClassRoom.block_number.in_((2,3,4,5))).first()
            # exist_class = ClassRoom.query.filter(ClassRoom.class_number==number).first()

            if not exist_class:
                return_content['Content'] = "稳唔到课室（找不到课室）"
            else:
                try:
                #获取具体课室的id
                    class_id = exist_class.id
                    #然后调动url了
                    set_network_url = "https://weixin.520langma.com/estimate/index/set_network/?cls=%s&operate=%s&acl=520su1314"%(class_id,operate)

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

            return_content['Content'] = "邮箱绑定的格式:\n\nemail#xxxxx@wolfcode.cn\n\n或者是:\n\nemail#xxx@520it.com\n\n发送过程稍慢，请不要重复提交命令"

        elif re.findall("(?<=email#)([a-z]+[0-9]*@(wolfcode\.cn|520it\.com))",req_con):
            x1 = re.findall("(?<=email#)([a-z]+[0-9]*@(wolfcode\.cn|520it\.com))",req_con)
            #print(x1[0][0])

            #邮箱正确,然后就马上发送邮件,根据两端相同的密钥

            print(return_content['ToUserName'])
            print(x1[0][0])
            
            if send_verify_code(return_content['ToUserName'],x1[0][0]):

                return_content['Content'] = "已经成功发送咗(了)激活码到你的邮箱，请点击邮箱里面的激活码进行实名绑定！"
            else:
                return_content['Content'] = "发送唔成功（不成功）"
 
        elif re.findall("(控制|教室|课室|网络|断网|开网|关闭|打开)",req_con):
    
            return_content['Content'] = "关于如何用语句控制网络的提示↓↓↓↓\n\n开启课室网络的语句格式:\n课室1开网\n\n关闭课室网络的语句格式:\n课室15断网"
            return_content['Content'] += "\n\n\n备注：目前仅支持广州远程操作，上海和北京暂时只能使用<评价系统>里面的<网络管理>来控制网络"

        
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
        
        return x1

    else:
        
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

    #成功了，然后就要尝试去数据库获取这个weixin_openid是否存在重复注册了。
    #不过现在需要写一个model先，因为，得基本有一个数据库管理的models

    #OK！models写好了，现在去看看能不能读取数据线

    #OK！要进行数据查询了。
    print(weixin_openid)
    #这一句是查询所有的数据,没有条件限制的.
    # admin = User.query.all()
    #下面这条语句是会输出查询语句,但是并没有执行,所以得后面加一个all,但是这个是获取数据的,所以呢,没必要吗
    # admin = User.query.filter(User.weixin_openid==weixin_openid).all()

    #所以下面这个语句,只需要一个first()就可以了.
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
            print(e)
            return "<h1>保存数据错误,db错误01</h1>"

    else:

        try:
            admin.weixin_openid = weixin_openid
            db.session.add(admin)
            db.session.commit()
        except Exception as e:
            print(e)
            return "<h1>保存数据错误,db错误02<h1>"
        


    #没有异常,就证明成功了.!

    return "<h1>实名认证成功!</h1>"

    #然后，现在就进行数据库操作了。！没有错，就是跨数据库工作，虽然也是estimate数据库。


def send_verify_code(weixin_opnid,email):

    #尝试获取open_id
    
    #初始化一个对象先

    #把微信的id,添加到加密的token当中.

    

    token_info = {'weixin_openid':weixin_opnid,'email':email}

    token = token_create(token_info,300)
    
    msg = Message("叩丁狼-微信办公-实名登记",sender='lizhixuan@wolfcode.cn',recipients=[email,])

    msg.body = "hello world!"

    #编辑好一个用于激活邮箱地址的加密token

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

    checkin_url = "https://weixin.520langma.com/estimate/login/weixin_checkin/?code=%s"%token
    res1 = requests.get(checkin_url,verify=False)
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


#这里设计一个，接收微信公众号匹配的url跳转，但是，这里加了一层认证，根据weixin_openid来做认证

def redirect_after_weixin_checkin(weixin_openid,request_url):

    #调用这个函数的话，每次都得补充当前的weixin_openid+token去访问看看是否能成功获取access_token
    #可以的话，继续下一步。
    
    access_token = try_get_estimate_token(weixin_openid)

    if not access_token:

        # return "获取授权失败，你是否已经绑定邮箱？"
        return {"success":False,'msg':"获取授权失败，你绑定邮箱未？"}

    headers = {'cookie':access_token}

    try:
        res1 = requests.get(request_url,headers=headers,verify=False)

    except Exception as e:
        print("提交请求失败")

    return {"success":True,'msg':res1}