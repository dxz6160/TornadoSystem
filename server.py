'''
@author: trise
@studioe: JCAI
@software: pycharm
@time: 2020/10/7 15:15
'''
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import features
import os
from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers = [
            (r"/Index", features.IndexHandler),
            (r"/PicturePlatform", features.PicHandler),
            (r"/VideoPlatform", features.VideoHandler),
            (r"/FilePlatform", features.FileHandler),
        ],
        static_path = os.path.join(os.path.dirname(__file__), "static"),
        template_path = os.path.join(os.path.dirname(__file__), "templates")
    )
    http_server = tornado.httpserver.HTTPServer(app, max_buffer_size=5048576000, max_body_size=5048576000)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()