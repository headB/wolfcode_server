from flask import Flask
<<<<<<< HEAD
from flask_bootstrap import Bootstrap

=======
from network_service.v_1_0 import network_api,register_api,postman_api
>>>>>>> c0d6a09ce9942fe6360b1afc81dec3ebd1e30ce9

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.register_blueprint

app.register_blueprint(network_api,url_prefix="/network")

if __name__ == "__main__":

    app.run(debug=True)


#想想具体的流程

#因为这个基本上都是属于响应了,等等,普通的CMS也是这样啊,用户负责提交请求啊,然后服务端就负责响应.

#然后在微信当中,假如我现在挂靠在公司,就只有一个入口了,然后就是展示当前的所有功能了.

#所以设置一个首页响应把.首先得这样吧.