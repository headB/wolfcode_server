from . import micro_app_api

@micro_app_api.route("/")
def index():

    return "你好,这是用于微信小程序的!"