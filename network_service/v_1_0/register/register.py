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
            return_content['Content'] = "请输入你想输入的内容,<a href='https://kumanxuan1.f3322.net'>点我点我</a>"
            return_content['FromUserName'] = content['ToUserName']
            return_content['CreateTime'] = int(timestamp)
            return_content['MsgType'] = 'text'
        except Exception as e:
            return "处理参数出错"

        #现在问题就是，如何接收一坨的xml标签的内容呢？
        print(request.data)
        
        x1 = xmltodict.unparse({'xml':return_content})
        
        return x1


    else:
        
        return render_template('index.html')

@register_api.route("/index")
def index2():
    print("xxyQQ")
    #调用首页显示
    return render_template('index.html')

