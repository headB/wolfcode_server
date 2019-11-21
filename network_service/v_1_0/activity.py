##这个模块就负责处理关于活动室的问题了.!


from . import micro_app_api
import requests
from flask import request, jsonify, session
import json
import datetime
from manage import logging, db, mail
from flask_mail import Message
from .register.models import Activity, ActivityHistory, AuthUser
import datetime
import uuid


# 认证过的微信用户可以提交 申请 活动室 申请
@micro_app_api.route("/activity", methods=["GET", "POST"])
def set_activity():
    if request.method == "GET":

        return "NOT SUPPORT GET METHOD!"

    elif request.method == "POST":

        print(session)
        message = {}
        json_data = json.loads(request.get_data())
        message['statusCode'] = '201'
        message['status'] = "activity设置失败!"
        error_message = jsonify(message)

        if not check_user_login_status():
            return jsonify(message)

        setting_info = {}
        setting_info['topic'] = json_data.get('topic')
        setting_info['name'] = json_data.get('name')
        setting_info['startDate'] = json_data.get('startDate')
        setting_info['endDate'] = json_data.get('endDate')

        # 然后这里必须是获取了登陆!.
        # 其实简单查看一下是否存在username应该就差不多的了.!

        print(setting_info)

        if session.get("username") and all(
                [setting_info['topic'], setting_info['name'], setting_info['startDate'], setting_info['endDate']]):

            # 进行权限设置
            try:

                setting_info['startDate'] = datetime.datetime.strptime(json_data.get('startDate'), "%Y-%m-%d %H:%M")
                setting_info['endDate'] = datetime.datetime.strptime(json_data.get('endDate'), "%Y-%m-%d %H:%M")


            except Exception as e:

                if isinstance(setting_info['startDate'], datetime.datetime):

                    setting_info['endDate'] = setting_info['startDate']

                else:
                    logging.error(e)
                    message['status'] = "发生参数验证错误!或者没有设置日期"
                    return jsonify(message)

            if setting_info['endDate'] < setting_info['startDate']:
                message['status'] = "时间格式错误!"
                return jsonify(message)

            # 然后进入正式的时间设置流程了.!

            # 这个地方还没有设置好数据库的啦!.
            # message['status'] = True

            # 然后就是需要设计数据表了.!

            try:
                pass
                # 这里有两个地方需要设置,第一呢,就是,

                # 把过期的申请取消掉先.!
                # 获取当前时间
                now_time = datetime.datetime.now()

                update_activity()

                # 然后需要查询是否和当前的活动冲突!

            except Exception as e:

                logging.error(e)
                db.session.rollback()
                db.session.close()
                pass
            # topic
            # name
            # date

            # 需要检测当前那些已经申请通过的活动

            try:
                # 然后整理数据,准备插入.

                topic = Activity()
                topic_history = ActivityHistory()

                uuid1 = str(uuid.uuid1())[:8]
                topic_history.uuid, topic.uuid = uuid1, uuid1
                topic_history.topic, topic.topic = setting_info['topic'], setting_info['topic']
                topic_history.apply_name, topic.apply_name = setting_info['name'], setting_info['name']
                topic_history.crm_username, topic.crm_username = session.get('username'), session.get('username')
                topic_history.start_date, topic.start_date = setting_info['startDate'], setting_info['startDate']
                topic_history.end_date, topic.end_date = setting_info['endDate'], setting_info['endDate']

                class object1:

                    pass

                o1 = object1()

                o1.start_date = setting_info['startDate']
                o1.end_date = setting_info['endDate']

                print(o1.start_date)
                print(o1.end_date)

                mes1 = check_activity_passed(o1)

                if mes1['code'] == 500:
                    return jsonify(mes1)

                db.session.add(topic)
                db.session.add(topic_history)
                db.session.commit()

                message['status'] = True

            except Exception as e:

                logging.error(e)
                logging.error("数据库保存错误!")
                db.session.rollback()
                message['status'] = "数据保存失败!请联系beetle Lai"

            db.session.close()

            # 终于搞掂空参数问题了.!

            # 搞掂之后,需要给名胜和beetle发送一份邮件测试一下
            msg = Message("你有一个活动室申请需要审核,请打开wolfcodeOAservice小程序查看", sender='lizhixuan@wolfcode.cn', recipients=["limingsheng@wolfcode.cn", "lizhixuan@wolfcode.cn" ])

            msg.body = "你有一个活动室申请需要审核,请打开wolfcodeOAservice小程序查看!"

            # 编辑好一个用于激活邮箱地址的加密token

            msg.html = "你有一个活动室申请需要审核,请打开wolfcodeOAservice小程序查看"

            mail.send(msg)

            return jsonify(message)

    else:
        pass

    message['status'] = "缺少参数"
    return jsonify(message)


#  管理员审核所有提交的活动
@micro_app_api.route("/activity_review", methods=["GET", "POST", "PUT", "DELETE"])
def review():
    db.session.close()
    message = {}
    message['status'] = ''
    message['code'] = 201
    message['content'] = ''

    message_json = jsonify(message)

    if (not check_user_login_status()):
        return jsonify(message)

    if (request.method == "GET"):

        # 获取权限组
        auth_users = AuthUser.query.filter(AuthUser.id == 1).first()

        userids = []

        if (auth_users):
            userids = auth_users.member.split(",")

        if (not session.get('username') or not str(session.get('uid')) in userids):
            return jsonify({'status': '没有权限操作!'})

        ##返回joson格式,让小程序可以直接接受

        # 查询有多少个符合的待审核结果
        now_time = datetime.datetime.now()
        activity_review = Activity.query.filter(Activity.end_date >= now_time, Activity.passed == 0).all()

        if (activity_review):

            ##然后就去整理结果了,!最后输出json格式.!

            # 我要组织成为一个数组?
            content = []
            for x in activity_review:
                content1 = {}
                content1['name'] = x.apply_name
                content1['topic'] = x.topic
                content1['start_date'] = x.start_date.strftime("%Y-%m-%d %H:%M")
                content1['end_date'] = x.end_date.strftime("%Y-%m-%d %H:%M")
                content1['uuid'] = x.uuid
                content.append(content1)

            message['content'] = content

        else:
            pass
            print("不好意思,这个位置是没有结果的!")

        return jsonify(message)

    elif (request.method == "PUT" or request.method == "DELETE"):

        # 这里就是更新操作了,就是通过和不通过的操作了.!
        ##这里就是当作是审核通过的意思了.!
        try:

            pass
            # 尝试接收数值
            json_data = json.loads(request.get_data())
            uuid = json_data.get('id')
            ##拿到uuid数值,然后就是需要进一步操作了.!

            # 查询对应的记录.两条记录
            act_now = Activity.query.filter(Activity.uuid == uuid).first()
            act_history = ActivityHistory.query.filter(ActivityHistory.uuid == uuid).first()

            # 审核的时候,判断是否和已经审核通过的条目对比
            try:
                if (request.method == "PUT"):
                    mess1 = check_activity_passed(act_now)

                    if (mess1['code'] == 500):
                        return jsonify(mess1)




            except Exception as e:

                logging.error(e)
                logging.error("更新出现问题")

            # 然后进行更新.
            if (request.method == "PUT"):
                act_now.passed = 1
                act_history.passed = 1
            else:

                act_now.passed = -1
                act_history.passed = -1

            db.session.add(act_now)
            db.session.add(act_history)

            db.session.commit()
            db.session.close()


        except Exception as e:

            logging.error(e)
            logging.error("审核流程出错!")
            db.session.rollback()
            db.session.close()
            message['status'] = "出错!"
            pass

        return jsonify(message)



    else:

        return jsonify(message)


@micro_app_api.route("/activitys", methods=["GET"])
def set_activitys():
    message = {}

    # 尽量开头和结束都设置一下db.session.close
    db.session.close()

    message['statusCode'] = 201
    message['status'] = "activitys获取失败"
    message['content'] = ''

    if (not check_user_login_status()):
        return jsonify(message)

    now_time = datetime.datetime.now()
    id = request.args.get('id')

    if (id == 1 or id == "1"):

        activity_review = Activity.query.filter(Activity.crm_username == session.get("username"),
                                                Activity.end_date >= now_time, Activity.passed == 1).all()
    else:

        activity_review = Activity.query.filter(Activity.end_date >= now_time, Activity.passed == 1).all()

    content = []

    if (activity_review):
        for x in activity_review:
            content1 = {}
            content1['name'] = x.apply_name
            content1['topic'] = x.topic
            content1['start_date'] = x.start_date.strftime("%Y-%m-%d %H:%M")
            content1['end_date'] = x.end_date.strftime("%Y-%m-%d %H:%M")
            content1['uuid'] = x.uuid
            content.append(content1)

    message['content'] = content

    return jsonify(message)


def update_activity():
    now_time = datetime.datetime.now()
    print(now_time)
    all_act_rec = Activity.query.filter(Activity.end_date < now_time).all()
    print(all_act_rec)
    for x in all_act_rec:

        if (now_time > x.end_date):
            # 将x插到到历史当中.!
            # 不了,还是直接删除吧.!

            db.session.delete(x)

            print("超期啦!要强制转移的啦!")

    db.session.commit()


def check_activity_passed(act_now):
    update_activity()

    act_passed = Activity.query.filter(Activity.passed == 1).all()

    message = {}
    message['code'] = 400

    for x in act_passed:

        if (act_now.end_date <= x.start_date or act_now.start_date >= x.end_date):

            pass
        else:

            message['content'] = ''
            message['status'] = "有活动时间冲突"
            message['code'] = 500

            break

    return message


def check_user_login_status():
    if (session.get("username")):

        return True
    else:
        return False
