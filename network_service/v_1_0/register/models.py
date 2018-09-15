#OK！准备开始写models了。
#现在前面配置的时候，创建一个 SQLAlchemy的实例

from datetime import datetime
from manage import db

#编写用户模型类
class User(db.Model):

    """
    用户模型类
    """
    __tablename__ = "login_admin"

    id = db.Column(db.Integer,primary_key=True) #用户id
    username = db.Column(db.String(20),unique=True,nullable=False)#用户名
    password = db.Column(db.String(100),nullable=False)#密码
    department = db.Column(db.Integer,nullable=False)#部门
    email = db.Column(db.String(60),unique=True,nullable=False)#密码
    realname = db.Column(db.String(30),nullable=False)#密码
    password = db.Column(db.String(100),nullable=False)#密码
    weixin_openid = db.Column(db.String(100),unique=True,nullable=False)#密码

    #这样就OK了？？？就是少了点提示

#编写课室模型类
class ClassRoom(db.Model):
    """
    课室的数据库模型类
    """

    __tablename__ = "login_classroom"

    id = db.Column(db.Integer,primary_key=True)
    class_number = db.Column(db.String(10),nullable=False)
    block_number = db.Column(db.Integer)
    ip_addr = db.Column(db.String(80),nullable=False)
    ACL = db.Column(db.String(20),nullable=False)

    
