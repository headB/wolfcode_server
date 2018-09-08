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

from flask import render_template

from . import register_api

@register_api.route("/index")
def index():

    #调用首页显示
    return render_template('index.html')

@register_api.route("/")
def index2():

    #调用首页显示
    return render_template('index.html')

