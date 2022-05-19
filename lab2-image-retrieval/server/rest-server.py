#!flask/bin/python
################################################################################################################################
# ------------------------------------------------------------------------------------------------------------------------------
# This file implements the REST layer. It uses flask micro framework for server implementation. Calls from front end reaches 
# here as json and being branched out to each projects. Basic level of validation is also being done in this file. #                                                                                                                                  	       
# -------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################
from flask import Flask, jsonify, request, redirect, render_template, Response
from flask_httpauth import HTTPBasicAuth
from flask_cors import *
from werkzeug.utils import secure_filename
import os
import shutil
import numpy as np
from search import recommend
from tensorflow.python.platform import gfile

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


app = Flask(__name__,
            static_folder='./template',  # 设置静态文件夹目录
            template_folder="./template",
            static_url_path="")
CORS(app, supports_credentials=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
auth = HTTPBasicAuth()


# Loading the extracted feature vectors for image retrieval
extracted_features = np.zeros((2955, 2048), dtype=np.float32)

tag_type = ['animals', 'baby', 'bird', 'car', 'clouds', 'dog', 'female',
            'flower', 'food', 'indoor', 'lake', 'male', 'night', 'people',
            'plant_life', 'portrait', 'river', 'sea', 'structures', 'sunset',
            'transport', 'tree', 'water']


def image_tags():
    typeDict = dict()
    for i in tag_type:
        typeDict[i] = []
        # 读取对应的文件
        with open('database/tags/' + i + '.txt', 'r') as fp:
            li = fp.readlines()
            for j in li:
                typeDict[i].append(j.strip())
    return typeDict


# 预加载图片标签
typeDict = image_tags()

with open('saved_features_recom.txt') as f:
    for i, line in enumerate(f):
        extracted_features[i, :] = line.split()
print("loaded extracted_features")


# 根据id获取图片内容
@app.route('/image', methods=['GET'])
def get_img():
    imageId = request.values.get('id')

    # 将对应图片复制到static文件夹下
    with open('database/dataset/im' + imageId + '.jpg', mode='rb') as f:
        byte_data = f.read()

    return Response(byte_data, mimetype='image/jpeg')


# 获取用户全部收藏
@app.route('/collect/all', methods=['GET'])
def get_all_collect():
    res = []
    with open('database/favorites.txt', mode='r') as f:
        for i in f.readlines():
            res.append(i.strip())
    return jsonify(res)


# 改变图片收藏状态
@app.route('/collect', methods=['GET'])
def change_img_collect():
    imageId = request.values.get('id')

    # 获取collect文件夹内容
    with open('database/favorites.txt', mode='r') as f:
        s = f.readlines()

    p = []
    isCollected = False
    for i in s:
        # 已经收藏过了
        if i.strip() == imageId:
            isCollected = True
        else:
            p.append(i.strip())

    if not isCollected:
        p.append(imageId)

    # 写文件
    n = len(p)
    with open('database/favorites.txt', mode='w') as f:
        for index, item in enumerate(p):
            if index != n - 1:
                f.write(item + '\n')
            else:
                f.write(item)

    return jsonify({
        'status': True,
    })


@app.route("/tags", methods=['GET'])
def get_tags():
    res = []
    for i in typeDict.keys():
        res.append({
            'label': i,
            'size': len(typeDict[i]),
        })
    res.sort(key=lambda x: x['size'], reverse=True)
    return jsonify(res)


@app.route('/info', methods=['GET'])
def get_img_info():
    imageId = request.values.get('id')

    # 查看favorites文件夹
    with open('database/favorites.txt', mode='r') as f:
        isCollected = False
        for i in f.readlines():
            if i.strip() == imageId:
                isCollected = True
                break

    # 获取图片类型
    tags = []
    for i in typeDict.keys():
        if imageId in typeDict[i]:
            tags.append(i)

    return jsonify({
        'isCollected': isCollected,
        'tags': tags,
    })



# This function is used to do the image search/image retrieval
@app.route('/imgUpload', methods=['GET', 'POST'])
def upload_img():
    print("image upload")
    result = 'static/result'
    if not gfile.Exists(result):
        os.mkdir(result)
    shutil.rmtree(result)

    if request.method == 'POST' or request.method == 'GET':
        print(request.method)
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)

        file = request.files['file']
        print(file.filename)
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file:  # and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            inputloc = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_list = recommend(inputloc, extracted_features)
            return jsonify(image_list)



@app.route('/')
def main():
    return render_template('index.html', name='index')  # 使用模板插件，引入index.html。此处会自动Flask模板文件目录寻找index.html文件


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
