from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_script import Manager
import config
#导入创建实例化数据库用的SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_cache import Cache

#还是需要导入那个什么脚本助手了,导入Manager


app = Flask(__name__)

app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280

cache = Cache(app,config={'CACHE_TYPE': 'simple'})
cache.init_app(app)


bootstrap = Bootstrap(app)
# app.register_blueprint
app.config.from_object(config.Config)
mail = Mail(app)

#实例化数据库
# db = SQLAlchemy(session_options = {'autocommit':True})
db = SQLAlchemy()

db.init_app(app)


#导入蓝图
from network_service.v_1_0 import register_api
from network_service.v_1_0 import micro_app_api

app.register_blueprint(register_api,url_prefix="/")
app.register_blueprint(micro_app_api,url_prefix="/xcx")

#使用外部工具

manager = Manager(app)


#设置日志
# logging.basicConfig(level=logging.ERROR,filename="log_debug.log",format=' - %(funcName)s -  %(lineno)d - %(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logging.basicConfig(level=logging.DEBUG,format=' - %(funcName)s -  %(lineno)d - %(asctime)s - %(name)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    
    #app.run('0.0.0.0', debug=True,port=8080,ssl_context=('cert.pem', 'key.pem')) 
    
    manager.run()
    

    

    


