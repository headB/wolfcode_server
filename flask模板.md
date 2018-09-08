# flask模板

1. 想起来了,就是flask的模板识别,是在运行的具体主文件所有目录寻找templates文件夹
2. 在渲染模板的时候，默认会从项目根路径下的templates目录下查找模板
3. 如果想要指定模板路径的时候，就在初始化APP的时候，这样操作即可
    ```python
    app = Flask(__name__,template_folder='C:/templates') #template_folder可以指定模板位置    
    ```
4. Flask 扩展一般都在创建程序实例时初始化。Bootstrap
    1. 代码
    ```python
    from flask_bootstrap import Bootstrap
    #...
    bootstrap = Bootstrap(app)
    ```
    2. 