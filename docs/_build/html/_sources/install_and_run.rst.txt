.. MyServer install and run

安装
====

从源码安装
---------

下载源码后直接运行python setup tools 即可完成安装。使用-h查看帮助和使用方法。

.. code-block:: shell

   $ git clone https://github.com/dispensable/myserver.git
   $ python3 setup.py install
   $ myserver -h
   $ myserver <you wsgi app module> <your wsgi app>

从github安装
-----------

*从Github下载源码*

.. code-block:: shell

   $ git clone https://github.com/dispensable/myserver.git
   $ sudo chmod +x <MyServer repository>/main.py
   $ ./main.py <your wsgi app module> <your wsgi app>

.. note:: 确保你的应用在app相同目录下

运行
====

MyServer可以通过以下两种方式运行：

CLI方式运行
----------

.. code-block:: shell

   $ cd <your wsgi app dir>
   $ myserver --worker 2 <your app module> <your app name>

从源码运行
---------

.. code-block:: shell

   $ cd <MyServer repository>/app
   $ ./main.py <your wsgi app module> <your wsgi app>

.. note:: 确保你的应用在app相同目录下

自定义wsgiapp
-------------

你也可以自定义自己的wsgi app直接插入到server运行，下面是一个示例：

.. code-block:: python

   from myserver.app.baseapp import App

   def my_wsgi_app(environ, start_response):
       status = '200 OK'
       headers = [('Content-Type', 'text/plain')]
       start_response(status, headers)

       return ['hello ', 'world']

   class MyApp(App):
       def load(self):
           return my_wsgi_app

   if __name__ == '__main__':
       myapp = MyApp()
       myapp.run()
