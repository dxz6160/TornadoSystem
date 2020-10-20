'''
@author: trise
@studioe: JCAI
@software: pycharm
@time: 2020/10/7 15:22
'''
import os
import time
import json
import shutil
import random
import string
import numpy as np
import cv2
import requests
from PIL import Image
from tornado.gen import coroutine
from tornado.web import RequestHandler
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

class IndexHandler(RequestHandler):
    def get(self):
        self.render('index.html')

class PicHandler(RequestHandler):
    executor = ThreadPoolExecutor(100)

    def write_error(self, status_code, **kwargs):
        if status_code == 500:
            self.set_status(500)
            self.write({'code': 500, 'msg': '服务器内部错误，请联系开发者', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        elif status_code == 404:
            self.set_status(404)
            self.write({'code': 404, 'msg': '资源不存在', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        elif status_code == 555:
            self.set_status(555)
            self.write({'code': 555, 'msg': '上传文件为空', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})

    def get(self):
        # global method
        #
        # try:
        #     method = self.request.arguments.get('method', [])[0]
        #     method = method.decode('UTF-8')
        # except:
        #     pass
        self.render('post_pic.html', filename = 'None.png', result = '')

    @coroutine
    def post(self):
        # global method

        res, filename = yield self.Time_consuming_operation()

        type = res['Classification']



        self.render('post_pic.html', filename = filename, result = type)

    @run_on_executor
    def Time_consuming_operation(self):
        upload_path = './static/picture'
        size = getFileSize(upload_path)
        # print(size)
        if size >= 380000:
            shutil.rmtree(upload_path)
            os.mkdir(upload_path)
        meta = self.request.files.get('file', [])[0]
        if meta == []:
            self.send_error(555)
        file_name = meta.get('filename')
        file_path = os.path.join(upload_path, file_name)
        with open(file_path, 'wb') as f:
            f.write(meta.get('body'))
        image_type = file_name.split('.')[-1]
        # 缩略图
        im = Image.open(file_path)  # 打开图片
        im.thumbnail((400, 400))  # 设置图片大小
        if image_type == 'jpg':
            aa = 'jpeg'
        elif image_type == 'png':
            aa = 'png'
        im.save(file_path, aa)

        method = 'method1'

        files = {'file': open(file_path, 'rb')}
        data = {"method": method}
        res = requests.post('http://192.168.1.12:8000/post_pic', files = files, data=data)

        res = json.loads(res.text)

        return res, file_name





class VideoHandler(RequestHandler):
    executor = ThreadPoolExecutor(10)

    def write_error(self, status_code, **kwargs):
        if status_code == 500:
            self.set_status(500)
            self.write({'code': 500, 'msg': '服务器内部错误，请联系开发者', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        elif status_code == 404:
            self.set_status(404)
            self.write({'code': 404, 'msg': '资源不存在', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        elif status_code == 555:
            self.set_status(555)
            self.write({'code': 555, 'msg': '上传文件为空', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})

    def get(self):
    #     global method
    #
    #     try:
    #         method = self.request.arguments.get('method', [])[0]
    #         method = method.decode('UTF-8')
    #     except:
    #         pass
        self.render('post_video.html')

    @coroutine
    def post(self):

        res = yield self.Time_consuming_operation()

        filename = res

        video_name = 'tag_{}.mp4'.format(filename.split('.')[0])

        # video_id = res[0]
        # result = res[1]
        # videoname = res[2].split('.')[0]
        # filename = 'tag_' + videoname + '.mp4'
        #
        # result_dic = {
        #     'Statu_code': 200,
        #     'Video_id': video_id,
        #     'Content': result,
        #     'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # }
        # result_dic = json.dumps(result_dic, ensure_ascii=False)
        # # self.write(result_dic)
        self.render('video.html', filename=video_name)
        # self.write("success")

    @run_on_executor
    def Time_consuming_operation(self):
        upload_path = './static/video'
        meta = self.request.files.get('file', [])[0]  # 获取文件对象
        if meta == []:
            self.send_error(555)
        file_name = meta.get('filename')
        file_path = os.path.join(upload_path, file_name)  # 拼接路径
        with open(file_path, 'wb') as f:
            f.write(meta.get('body'))

        method = 'method2'

        files = {'file': (file_name, open(file_path, 'rb'))}
        data = {"method": method}
        res = requests.post('http://192.168.1.12:8000/post_video', files=files, data=data)

        # print("发送成功")

        res = json.loads(res.text)

        result = res['Content']

        print(result)

        # print(res)

        ffmpeg(file_name)

        tag_picture(file_name,result)

        get_video(file_name)





        return file_name

def ffmpeg(filename):
    video_path = os.path.join(os.path.dirname(__file__), "static/video", filename)
    print(video_path)
    outPutDirName = os.path.join(os.path.dirname(__file__), "static/out_picture/", filename.split('.')[0]) + '/'
    if not os.path.exists(outPutDirName):
        os.makedirs(outPutDirName)
    cmd = "ffmpeg -i {} -f image2 {}%d.jpg".format(video_path, outPutDirName)
    #cmd = "ffmpeg -i {} -vf scale=iw/4:-1 {}%d.jpg".format(video_path, outPutDirName)
    # print(cmd)
    os.system(cmd)


class VideoHandler(RequestHandler):
    executor = ThreadPoolExecutor(10)

    def write_error(self, status_code, **kwargs):
        if status_code == 500:
            self.set_status(500)
            self.write({'code': 500, 'msg': '服务器内部错误，请联系开发者', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        elif status_code == 404:
            self.set_status(404)
            self.write({'code': 404, 'msg': '资源不存在', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        elif status_code == 555:
            self.set_status(555)
            self.write({'code': 555, 'msg': '上传文件为空', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})

    def get(self):
    #     global method
    #
    #     try:
    #         method = self.request.arguments.get('method', [])[0]
    #         method = method.decode('UTF-8')
    #     except:
    #         pass
        self.render('post_video.html')

    @coroutine
    def post(self):

        res = yield self.Time_consuming_operation()

        filename = res

        video_name = 'tag_{}.mp4'.format(filename.split('.')[0])

        # video_id = res[0]
        # result = res[1]
        # videoname = res[2].split('.')[0]
        # filename = 'tag_' + videoname + '.mp4'
        #
        # result_dic = {
        #     'Statu_code': 200,
        #     'Video_id': video_id,
        #     'Content': result,
        #     'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # }
        # result_dic = json.dumps(result_dic, ensure_ascii=False)
        # # self.write(result_dic)
        self.render('video.html', filename=video_name)
        # self.write("success")

    @run_on_executor
    def Time_consuming_operation(self):
        upload_path = './static/video'
        meta = self.request.files.get('file', [])[0]  # 获取文件对象
        if meta == []:
            self.send_error(555)
        file_name = meta.get('filename')
        file_path = os.path.join(upload_path, file_name)  # 拼接路径
        with open(file_path, 'wb') as f:
            f.write(meta.get('body'))

        method = 'method2'

        files = {'file': (file_name, open(file_path, 'rb'))}
        data = {"method": method}
        res = requests.post('http://192.168.1.12:8000/post_video', files=files, data=data)

        # print("发送成功")

        res = json.loads(res.text)

        result = res['Content']

        print(result)

        # print(res)

        ffmpeg(file_name)

        tag_picture(file_name,result)

        get_video(file_name)

        return file_name

class FileHandler(RequestHandler):
    executor = ThreadPoolExecutor(10)

    def write_error(self, status_code, **kwargs):
        if status_code == 500:
            self.set_status(500)
            self.write({'code': 500, 'msg': '服务器内部错误，请联系开发者', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        elif status_code == 404:
            self.set_status(404)
            self.write({'code': 404, 'msg': '资源不存在', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        elif status_code == 555:
            self.set_status(555)
            self.write({'code': 555, 'msg': '上传文件为空', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})

    def get(self):
    #     global method
    #
    #     try:
    #         method = self.request.arguments.get('method', [])[0]
    #         method = method.decode('UTF-8')
    #     except:
    #         pass
        self.render('post_file.html')

    @coroutine
    def post(self):

        res = yield self.Time_consuming_operation()

        # print(res)
        #
        filename = res
        #
        video_name = 'tag_{}.mp4'.format(filename.split('.')[0])

        # video_id = res[0]
        # result = res[1]
        # videoname = res[2].split('.')[0]
        # filename = 'tag_' + videoname + '.mp4'
        #
        # result_dic = {
        #     'Statu_code': 200,
        #     'Video_id': video_id,
        #     'Content': result,
        #     'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # }
        # result_dic = json.dumps(result_dic, ensure_ascii=False)
        # # self.write(result_dic)
        self.render('video.html', filename=video_name)
        # self.write("success")

    @run_on_executor
    def Time_consuming_operation(self):
        upload_path = './static/video'
        meta = self.request.arguments.get('file', [])[0]  # 获取文件对象
        if meta == []:
            self.send_error(555)
        file_path = str(meta, encoding='utf-8')

        method = 'method3'

        file_name = file_path.split('\\')[-1]

        # print(file_path)
        #
        # print(file_name)


        files = {'file': (file_name, open(file_path, 'rb'))}
        data = {"method": method}
        res = requests.post('http://192.168.1.12:8000/post_video', files=files, data=data)

        # print("发送成功")

        res = json.loads(res.text)

        result = res['Content']

        # print(result)

        # print(res)

        ffmpeg2(file_path)
        #
        tag_picture(file_name,result)
        #
        get_video(file_name)

        return file_name


def ffmpeg(filename):
    video_path = os.path.join(os.path.dirname(__file__), "static/video", filename)
    print(video_path)
    outPutDirName = os.path.join(os.path.dirname(__file__), "static/out_picture/", filename.split('.')[0]) + '/'
    if not os.path.exists(outPutDirName):
        os.makedirs(outPutDirName)
    cmd = "ffmpeg -i {} -f image2 {}%d.jpg".format(video_path, outPutDirName)
    #cmd = "ffmpeg -i {} -vf scale=iw/4:-1 {}%d.jpg".format(video_path, outPutDirName)
    # print(cmd)
    os.system(cmd)

def ffmpeg2(filename):
    video_path = filename
    # print(video_path)
    outPutDirName = os.path.join(os.path.dirname(__file__), "static/out_picture/", filename.split('.')[0]) + '/'
    if not os.path.exists(outPutDirName):
        os.makedirs(outPutDirName)
    cmd = "ffmpeg -i {} -f image2 {}%d.jpg".format(video_path, outPutDirName)
    #cmd = "ffmpeg -i {} -vf scale=iw/4:-1 {}%d.jpg".format(video_path, outPutDirName)
    # print(cmd)
    os.system(cmd)

def tag_picture(filename, result):
    sourceFileName = filename.split('.')[0]
    outPutDirName = os.path.join(os.path.dirname(__file__), "static/tag_picture/", sourceFileName) + "/"
    print(outPutDirName)
    if not os.path.exists(outPutDirName):
        os.makedirs(outPutDirName)
    times = 1
    picture_path = os.path.join(os.path.dirname(__file__), "static/out_picture/", sourceFileName) + "/"
    path_list = os.listdir(picture_path)
    path_list.sort(key=lambda x: int(x.split('.')[0]))
    for file in path_list:
        file_path = os.path.join(picture_path, file)
        local = result[times - 1][1]
        img = cv2.imread(file_path)
        for tag in local:
            try:
                x1 = int(tag[0].split(',')[0].split('.')[0]) / 4
                y1 = int(tag[0].split(',')[1].split('.')[0]) / 4
                x2 = int(tag[0].split(',')[2].split('.')[0]) / 4
                y2 = int(tag[0].split(',')[3].split('.')[0]) / 4
            except:
                x1 = x2 = y1 = y2 = 0
            try:
                type = tag[1]
                #print(type)
                confident = tag[2]
            except:
                type = ''
                confident = ''
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 4)
            font = cv2.FONT_HERSHEY_COMPLEX_SMALL
            text = 'type:{} confident:{}'.format(type, confident)
            cv2.putText(img, text, (x1, y1 + 100), font, 2, (0, 0, 255), 2)
        cv2.imwrite(outPutDirName + 'image' + str(times) + '.jpg', img)
        times += 1


def get_video(filename):
    project_path = os.path.join(os.path.dirname(__file__))
    filename = filename.split('.')[0]
    cmd = "ffmpeg -y -i {}/static/tag_picture/{}/image%d.jpg {}/static/tag_video/tag_{}.mp4".format(project_path, filename, project_path, filename)
    print(cmd)
    os.system(cmd)

def getFileSize(filePath, size=0):
    for root, dirs, files in os.walk(filePath):
        for f in files:
            size += os.path.getsize(os.path.join(root, f))
    return size

if __name__ == '__main__':
    # get_video('DJI_0547_out.MP4')
    pass