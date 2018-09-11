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
        content = xmltodict.parse(content_xml)['xml']

        return_content = {}
        
        # timestamp = time.mktime(datetime.datetime.now().timetuple())
        timestamp = time.time()
        ##捕捉一些野生openid
        try:
            return_content['ToUserName'] = content['FromUserName']
            #return_content['Content'] = "请输入你想输入的内容,<a href='https://kumanxuan1.f3322.net/estimate'>点我点我</a>"
            return_content['FromUserName'] = content['ToUserName']
            return_content['CreateTime'] = int(timestamp)
            return_content['MsgType'] = 'text'
            req_con = content['Content']
        except Exception as e:
            return "处理参数出错"

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
            return_content['Content'] = "暂时还没有支持一键免账号密码登陆，但是支持手动登陆，可以点击这里登陆\n\n<a href='https://kumanxuan1.f3322.net/estimate'>点我点我</a>"

        

        elif re.findall("(控制|教室|课室|网络|断网|开网|关闭|打开)",req_con):
            
            return_content['Content'] = "关于如何用语句控制网络的提示↓↓↓↓\n\n开启课室网络的语句格式:\n课室1开网\n\n关闭课室网络的语句格式:\n课室15断网"
            return_content['Content'] += "\n\n\n备注：目前仅支持广州远程操作，上海和北京暂时只能使用<评价系统>里面的<网络管理>来控制网络"
        else:

            return_content['Content'] = "操作无效，目前支持的关键字是：教室|课室|网络|断网|开网|关闭|打开|评分系统"
            

        x1 = xmltodict.unparse({'xml':return_content})
        
        return x1

    else:
        
        return render_template('index.html')

@register_api.route("/index")
def index2():
    
    #调用首页显示
    return render_template('index.html')

