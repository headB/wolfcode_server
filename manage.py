from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_script import Manager
import config
#还是需要导入那个什么脚本助手了,导入Manager


app = Flask(__name__)
bootstrap = Bootstrap(app)
app.register_blueprint
app.config.from_object(config.Config)
mail = Mail(app)

#导入蓝图
from network_service.v_1_0 import register_api

app.register_blueprint(register_api,url_prefix="/")

#使用外部工具
manager = Manager(app)

if __name__ == "__main__":
    
    #app.run('0.0.0.0', debug=True,port=8080,ssl_context=('cert.pem', 'key.pem')) 
    manager.run()


#想想具体的流程

#因为这个基本上都是属于响应了,等等,普通的CMS也是这样啊,用户负责提交请求啊,然后服务端就负责响应.

#然后在微信当中,假如我现在挂靠在公司,就只有一个入口了,然后就是展示当前的所有功能了.

#所以设置一个首页响应把.首先得这样吧.