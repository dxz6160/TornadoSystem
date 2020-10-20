import os
import shutil
import time
import json
import random
import string
import numpy as np
import cv2
from tornado.gen import coroutine
from tornado.web import RequestHandler
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

class PicHandler(RequestHandler):
    executor = ThreadPoolExecutor(100)

    def write_error(self, status_code, **kwargs):
        if status_code == 500:
            self.set_status(500)
            self.write({'code': 500, 'msg': '服务器内部错误，请联系开发者', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        elif status_code == 555:
            self.set_status(555)
            self.write({'code': 555, 'msg': '上传文件为空', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})

    @coroutine
    def post(self):
        res = yield self.Time_consuming_operation()

        result = res[0]
        pic_id = res[1]
        confidence = res[2]

        result_dic = {
            'code': 200,
            'Pic_id': pic_id,
            'Classification': result.strip(),
            'Confidence': confidence.strip(),
            'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        self.write(result_dic)

    @run_on_executor
    def Time_consuming_operation(self):
        upload_path = './static/picture'
        size = getFileSize(upload_path)
        # print(size)
        if size >= 10737418240:
            shutil.rmtree(upload_path)
            os.mkdir(upload_path)
        meta = self.request.files.get('file', [])[0]  # 获取文件对象
        if meta == []:
            self.send_error(555)
        file_name = meta.get('filename')
        pic_id = 'pic_' + time.strftime("%Y%m%d", time.localtime()) + ''.join(random.sample(string.ascii_letters + string.digits, 4))
        pic_name = pic_id + '.' + file_name.split('.')[1]
        file_path = os.path.join(upload_path, pic_name)
        with open(file_path, 'wb') as f:
            f.write(meta.get('body'))

        project_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))

        try:
            method = self.request.arguments.get('method', [])[0]
            method = method.decode('UTF-8')
        except:
            method = 'method1'

        if method == 'method1':
            cmd = 'cd {}/jcai_project/image_classification/method1 && python predict.py {}/static/picture/'.format(project_path, project_path) + pic_name
            val = os.popen(cmd).read()
           # print(val)
            result = val.split('预测结果')[1].strip('\n')
            confidence = val.split(':')[1].split('\n')[0]
        elif method == 'method2':
            cmd = 'cd {}/jcai_project/image_classification/method2/build && ./classifier ../resnet152-300.pt ../label.txt {}/static/picture/'.format(project_path, project_path) + pic_name
            val = os.popen(cmd).read()
            # print(val)
            result = val.split(':')[1].split('\n')[0]
            confidence = val.split(':')[2].strip('\n')
        return result, pic_id, confidence


class VideoHandler(RequestHandler):
    executor = ThreadPoolExecutor(10)

    def write_error(self, status_code, **kwargs):
        if status_code == 500:
            self.set_status(500)
            self.write(
                {'code': 500, 'msg': '服务器内部错误，请联系开发者', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        elif status_code == 555:
            self.set_status(555)
            self.write({'code': 555, 'msg': '上传文件为空', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})

    @coroutine
    def post(self):
        res = yield self.post_video()

        video_id  = res[0]
        result = res[1]

        result_dic = {
            'code': 200,
            'Video_id': video_id,
            'Content': result,
            'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        self.write(result_dic)

    @run_on_executor
    def post_video(self):
        upload_path = './static/video'
        size = getFileSize(upload_path)
        print(size)
        if size >= 107374182400:
            shutil.rmtree(upload_path)
            os.mkdir(upload_path)
        meta = self.request.files.get('file', [])[0]  # 获取文件对象
        if meta == []:
            self.send_error(555)
        file_name = meta.get('filename')
        video_id = 'video_' + time.strftime("%Y%m%d", time.localtime()) + ''.join(random.sample(string.ascii_letters + string.digits, 4))
        video_name = video_id + '.' + file_name.split('.')[1]
        file_path = os.path.join(upload_path, video_name)
        with open(file_path, 'wb') as f:
            f.write(meta.get('body'))

        project_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))

        out_picture_path = '{}/static/out_picture/'.format(project_path)

        size = getFileSize(out_picture_path)
        # print(size)
        if size >= 107374182400:
            shutil.rmtree(out_picture_path)
            os.mkdir(out_picture_path)

        ffmpeg(video_name)

        try:
            method = self.request.arguments.get('method', [])[0]
            method = method.decode('UTF-8')
        except:
            method = 'method1'

        if method == 'method1':
            cmd = 'cd {}/jcai_project/object_detection/method1 && python predict.py {}'.format(project_path, out_picture_path) + video_name.split('.')[0] + '/'
            print(cmd)
            val = os.popen(cmd).read()
            result = content1(val, tag = 0)
            # print(result)
        elif method == 'method2':
            cmd = 'cd {}/jcai_project/object_detection/method2/build && ./example-app ../resNetFpn-model-50.pt {}'.format(project_path, out_picture_path) + video_name.split('.')[0] + '/'
            # print(cmd)
            val = os.popen(cmd).read()
            result = content2(val, tag = 0)
        elif method == 'method3':
            cmd = 'cd {}/jcai_project/object_detection/method3 && python detect.py --source {}'.format(project_path, out_picture_path) + video_name.split('.')[0] + '/'
            print(cmd)
            val = os.popen(cmd).read()
            result = content3(val, tag = 0)
        elif method == 'method4':
            cmd = 'cd {}/jcai_project/object_detection/method4/build && ./libtorchtest ../best.torchscript.pt {}'.format(project_path, out_picture_path) + video_name.split('.')[0] + '/'
            # print(cmd)
            val = os.popen(cmd).read()
            result = content4(val, tag = 0)
        with open('{}/static/out/{}.txt'.format(project_path, video_id + '----'),'w') as f:
            f.write(str(val))
        with open('{}/static/out/{}.txt'.format(project_path, video_id),'w') as f:
            f.write(str(result))
        #tag_picture(video_name, result)
        #get_video(video_name)
        return video_id, result

class FileHandler(RequestHandler):
    executor = ThreadPoolExecutor(10)

    def write_error(self, status_code, **kwargs):
        if status_code == 500:
            self.set_status(500)
            self.write(
                {'code': 500, 'msg': '服务器内部错误，请联系开发者', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        elif status_code == 555:
            self.set_status(555)
            self.write({'code': 555, 'msg': '上传文件为空', 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})

    @coroutine
    def post(self):
        res = yield self.get_file()

        video_id  = res[0]
        result = res[1]

        result_dic = {
            'code': 200,
            'Video_id': video_id,
            'Content': result,
            'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        self.write(result_dic)

    @run_on_executor
    def get_file(self):
        meta = self.request.arguments.get('file', [])[0]  # 获取文件对象
        meta = bytes.decode(meta)
        if meta == []:
            self.send_error(555)
        video_id = 'video_' + time.strftime("%Y%m%d", time.localtime()) + ''.join(
            random.sample(string.ascii_letters + string.digits, 4))
        file_path = meta

        project_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))

        try:
            method = self.request.arguments.get('method', [])[0]
            method = method.decode('UTF-8')
        except:
            method = 'method1'

        if method == 'method1':
            cmd = 'cd {}/jcai_project/object_detection/method1 && python predict.py {}'.format(project_path, file_path)
            # print(cmd)
            val = os.popen(cmd).read()
            result = content1(val, tag = 1)
            # print(result)
        elif method == 'method2':
            cmd = 'cd {}/jcai_project/object_detection/method2/build && ./example-app ../resNetFpn-model-gpu.pt {}'.format(project_path, file_path)
            # print(cmd)
            val = os.popen(cmd).read()
            result = content2(val, tag = 1)
        elif method == 'method3':
            cmd = 'cd {}/jcai_project/object_detection/method3 && python detect.py --source {}'.format(project_path, file_path)
            # print(cmd)
            val = os.popen(cmd).read()
            result = content3(val, tag = 1)
        elif method == 'method4':
            cmd = 'cd {}/jcai_project/object_detection/method4/build && ./libtorchtest ../best.torchscript.pt {}'.format(project_path, out_picture_path) + video_name.split('.')[0] + '/'
            # print(cmd)
            val = os.popen(cmd).read()
            result = content4(val, tag = 1)

        # with open('{}/static/out/{}.txt'.format(project_path, video_id + '----'),'w') as f:
        #     f.write(str(val))
        #
        # with open('{}/static/out/{}.txt'.format(project_path, file_path),'w') as f:
        #     f.write(str(result))
        # tag_picture(video_name, result)
        # get_video(video_name)
        return video_id, result

def ffmpeg(filename):
    video_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/video", filename)
    outPutDirName = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/out_picture/", filename.split('.')[0]) + '/'
    os.mkdir(outPutDirName)
    cmd = "ffmpeg -i {} -f image2 {}%d.jpg".format(video_path, outPutDirName)
    #cmd = "ffmpeg -i {} -vf scale=iw/4:-1 {}%d.jpg".format(video_path, outPutDirName)
    # print(cmd)
    os.system(cmd)

def content1(content, tag):
    content = content.replace('\n', '').replace(' ', '').replace(",device='cuda:0'", '')
    content = content.replace("'boxes'", '')
    content = content.replace("'labels'", '')
    content = content.replace("'scores'", '')
    content = content.replace(",size=(0,4)", '')
    content = content.replace(",dtype=torch.int64", '')
    content = content.replace(":tensor", '')

    content1 = content.split('}')

    dic = {}

    for content2 in content1[:-1]:
        id = content2.split('{')[0]
        id = id.split('/')[-1]
        id = id.split('.')[0]
        if tag == 0:
            id = int(id)
        content3 = content2.split('{')[1].strip('(').split(')')
        boxes = content3[0].strip('[').strip(']').split('],[')
        lables = content3[1].strip(',(').strip('[').strip(']').split(',')
        labless = []
        for i in lables:
            if i == "1":
                i = '结焦'
            elif i == "2":
                i = '燃烧器'
            elif i == "3":
                i = '吹灰口'
            elif i == "4":
                i = '弯曲'
            labless.append(i)
        scores = content3[2].strip(',(').strip('[').strip(']').split(',')
        result = zip(boxes, labless, scores)
        result = list(result)
        result = str(result).replace("('', '', '')", "")

        dic[id] = eval(result)

    final = sorted(dic.items(), key=lambda obj: obj[0])
    return final

def content2(content, tag):
    dic = {}
    content = content.replace('labels is ', '|')
    content = content.replace('\nscore is', '')
    content = content.replace('\nbox is ', ' ')
    content = content.replace('---', ',')
    content = content.replace('\n', '')
    content = content.split('#')
    for content1 in content[:-1]:
        content1 = content1.split('|')
        pic_id = content1[0].split('/')[-1].split('.')[0]
        if tag == 0:
            pic_id = int(pic_id)
        list = []
        for content2 in content1[1:]:
            content2 = content2.split(' ')
            box = content2[2]
            score = content2[1]
            lable = content2[0]
            if lable == "1":
                lable = '结焦'
            elif lable == "2":
                lable = '燃烧器'
            elif lable == "3":
                lable = '吹灰口'
            elif lable == "4":
                lable = '弯曲'
            result = (box, lable, score)
            list.append(result)
        dic[pic_id] = list

    final = sorted(dic.items(), key=lambda obj: obj[0])
    return final

def content3(content, tag):
    dic = {}

    content = content.replace("]], device='cuda:0')", '')
    content = content.replace("tensor([[", '')
    content = content.replace(' ', '')
    content = content.replace('\n', '')
    content = content.replace('.00000', '.0')
    content = content.replace('png', 'jpg')
    for content1 in content.split('image')[1:]:
        content2 = content1.split('.jpg:')
        pic_id = content2[0].split('/')[-1]
        if tag == 0:
            pic_id = int(pic_id)
        list = []
        if content2[1] == '':
            pass
        else:
            for boxs in content2[1].split('],['):
                box = boxs.split(',')[0] + ',' + boxs.split(',')[1] + ',' + boxs.split(',')[2] + ',' + boxs.split(',')[3]
                score = boxs.split(',')[-2]
                lable = boxs.split(',')[-1]
                if lable == "0.0":
                    lable = '结焦'
                elif lable == "1.0":
                    lable = '燃烧器'
                elif lable == "2.0":
                    lable = '吹灰口'
                elif lable == "3.0":
                    lable = '弯曲'
                result = (box, lable, score)
                # print(result)
                list.append(result)
        dic[pic_id] = list
    final = sorted(dic.items(), key=lambda obj: obj[0])
    return final

def content4(content, tag):
    dic = {}

    content = content.replace('\n', '')
    content = content.replace('---', ',')

    content = content.replace('DJI_0547_', '')
    # print(content)
    for content1 in content.split('%')[:-1]:
        content1 = content1.strip()
        content2 = content1.split('.jpg')
        pic_id = content2[0].split('/')[-1]
        if tag == 0:
            pic_id = int(pic_id)
        list = []
        if content2[1] == '[]':
            pass
        else:
            for boxs in content2[1].split('#')[:-1]:
                # print(boxs)
                box = boxs.split('|')[0]
                score = boxs.split('|')[1].split(' ')[1]
                lable = boxs.split('|')[1].split(' ')[0]
                if lable == "coking":
                    lable = '结焦'
                elif lable == "burner":
                    lable = '燃烧器'
                elif lable == "soot":
                    lable = '吹灰口'
                elif lable == "curve":
                    lable == "弯曲"
                result = (box, lable, score)
                # print(result)
                list.append(result)
        dic[pic_id] = list
    final = sorted(dic.items(), key=lambda obj: obj[0])
    return final

def tag_picture(filename, result):
    sourceFileName = filename.split('.')[0]
    outPutDirName = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/tag_picture/", sourceFileName) + "/"
    if not os.path.exists(outPutDirName):
        os.makedirs(outPutDirName)
    times = 1
    picture_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/out_picture/", sourceFileName) + "/"
    path_list = os.listdir(picture_path)
    path_list.sort(key=lambda x: int(x.split('.')[0]))
    for file in path_list:
        file_path = os.path.join(picture_path, file)
        local = result[times - 1][1]
        img = cv2.imread(file_path)
        for tag in local:
            try:
                x1 = int(tag[0].split(',')[0].split('.')[0])
                y1 = int(tag[0].split(',')[1].split('.')[0])
                x2 = int(tag[0].split(',')[2].split('.')[0])
                y2 = int(tag[0].split(',')[3].split('.')[0])
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
    project_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))
    filename = filename.split('.')[0]
    cmd = "ffmpeg -i {}/static/tag_picture/{}/image%d.jpg {}/static/tag_video/tag_{}.mp4".format(project_path, filename, project_path, filename)
    os.system(cmd)

def getFileSize(filePath, size=0):
    for root, dirs, files in os.walk(filePath):
        for f in files:
            size += os.path.getsize(os.path.join(root, f))
    return size
