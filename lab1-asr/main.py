import difflib
import json
import time
import requests
import pyttsx3
import win32api
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QMovie, QIcon, QFont
import sys
import threading
from PyQt5 import QtCore
import speech_recognition as sr
from qtpy import QtMultimedia


class MyQLabel(QLabel):
    # 自定义信号, 注意信号必须为类属性
    button_clicked_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(MyQLabel, self).__init__(parent)

    def mouseReleaseEvent(self, QMouseEvent):
        self.button_clicked_signal.emit()

    # 可在外部与槽函数连接
    def connect_customized_slot(self, func):
        self.button_clicked_signal.connect(func)


class MainForm(QMainWindow):
    def __init__(self):
        super().__init__()

        '''
        窗体基本信息
        '''
        self.resize(900, 600)
        self.setWindowTitle('Voice Assistant')
        self.setWindowIcon(QIcon("icon/icon.ico"))

        '''
        绘制背景
        '''
        text = QLabel(self)
        text.resize(900, 600)

        self.gif = QMovie("icon/background.gif")
        self.gif.setScaledSize(QSize(900, 600))
        text.setMovie(self.gif)
        self.gif.start()

        '''
        字体设置
        '''
        self.font = QFont()
        self.font.setPointSize(11)
        self.font.setFamily("Comic Sans MS")  # 黑体

        '''
        初始文字
        '''
        self.introLabel = QLabel(self)
        self.introLabel.setFont(self.font)
        self.introLabel.setText("Hi, what can I do for you? You can start from saying 'help me'.")
        self.introLabel.setWordWrap(True)
        self.introLabel.move(130, 100)
        self.introLabel.setFixedWidth(300)
        self.introLabel.setMinimumHeight(30)
        self.introLabel.setStyleSheet("background-color: #00CCCC; "
                                      "color: white; "
                                      "font-size: 18px; "
                                      "border-radius: 10px; "
                                      "padding: 10px;"
                                      )
        self.introLabel.adjustSize()

        '''
        初始头像
        '''
        self.introProfile = QLabel(self)
        self.introProfile.resize(100, 50)
        self.introProfile.move(50, 100)
        self.introProfile.setStyleSheet("background-color: transparent;"
                                        "background-image:url(icon/root.png);"
                                        "background-repeat: no-repeat;")

        self.speaker = pyttsx3.init()

        '''
        输入指令
        '''
        self.supportCommand = ["help me", "play music", "open a text file", "weather", ]
        self.myCommand = "..."
        self.myLabel = QLabel(self)
        self.myLabel.setFont(self.font)
        self.myLabel.setText(self.myCommand)
        self.myLabel.setWordWrap(True)

        self.myLabel.move(450, 100 + self.introLabel.height() + 40)
        self.myLabel.setFixedWidth(300)
        self.myLabel.setMinimumHeight(30)
        self.myLabel.setStyleSheet("background-color: #AAAAAA; "
                                   "color: white; "
                                   "font-size: 18px; "
                                   "border-radius: 10px; "
                                   "padding: 10px;"
                                   )
        self.myLabel.adjustSize()

        '''
        用户头像
        '''
        self.userProfile = QLabel(self)
        self.userProfile.resize(150, 50)
        self.userProfile.move(720, 100 + self.introLabel.height() + 25)
        self.userProfile.setStyleSheet("background-color: transparent;"
                                       "background-image:url(icon/user.png);"
                                       "background-repeat: no-repeat;")

        self.speaker = pyttsx3.init()

        # 说话状态
        self.isSpeaking = False
        self.speakingGif = QMovie("icon/speaking.gif")
        self.speakingGif.setScaledSize(QSize(200, 100))
        self.isSpeakingLabel = QLabel(self)
        self.isSpeakingLabel.setMovie(self.speakingGif)
        self.isSpeakingLabel.resize(200, 100)
        self.isSpeakingLabel.move(330, 360)
        self.isSpeakingLabel.setStyleSheet("background-color:transparent;")
        self.speakingGif.start()
        self.isSpeakingLabel.setVisible(self.isSpeaking)

        # 语音识别组件
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # 对话框按钮
        self.speakMovie = QMovie("icon/speak.gif")
        self.speakMovie.setScaledSize(QSize(120, 120))
        self.speakLabel = MyQLabel(self)
        self.speakLabel.setMovie(self.speakMovie)
        self.speakLabel.setStyleSheet("background-color:transparent;")
        self.speakLabel.resize(120, 120)
        self.speakLabel.move(370, 430)
        self.speakMovie.start()
        self.speakLabel.connect_customized_slot(self.startSpeak)

        '''
        处理结果的对话框
        '''
        self.responseLabel = QLabel(self)
        self.responseLabel.setFont(self.font)
        self.responseLabel.setText("...")
        self.responseLabel.setWordWrap(True)
        self.responseLabel.adjustSize()
        self.responseLabel.move(130, 260)
        self.responseLabel.setFixedWidth(300)
        self.responseLabel.setMinimumHeight(30)

        self.responseLabel.setStyleSheet("background-color: #00CCCC; "
                                         "color: white; "
                                         "font-size: 18px; "
                                         "border-radius: 10px; "
                                         "padding: 10px;"
                                         )
        '''
        回复头像
        '''
        self.responseProfile = QLabel(self)
        self.responseProfile.resize(100, 50)
        self.responseProfile.move(50, 260)
        self.responseProfile.setStyleSheet("background-color: transparent;"
                                           "background-image:url(icon/root.png);"
                                           "background-repeat: no-repeat;")

        self.responseLabel.setVisible(False)
        self.responseProfile.setVisible(False)

        '''
        作者信息
        '''
        self.authorProfile = QLabel(self)
        self.authorProfile.resize(50, 50)
        self.authorProfile.move(600, 10)
        self.authorProfile.setStyleSheet("background-color: transparent;"
                                         "background-image:url(icon/author.png);"
                                         "background-repeat: no-repeat;")
        self.authorLabel = QLabel(self)
        self.authorLabel.setFont(self.font)
        self.authorLabel.setText("<a style='color: white; text-decoration: none' href = "
                                 "https://github.com/wangwangwang23333>@1851055 Mingjie Wang")
        self.authorLabel.setOpenExternalLinks(True)
        self.authorLabel.adjustSize()
        self.authorLabel.move(660, 25)

        # 开始说明
        threading.Thread(target=self.promptVoice, args=("Hi, what can I do for you? You can start from saying 'help "
                                                        "me'.",)).start()

    def startSpeak(self):
        if self.isSpeaking:
            return
        threading.Thread(target=self.playWav, args=(r'resource\button.wav',)).start()
        self.isSpeaking = True
        self.isSpeakingLabel.setVisible(self.isSpeaking)

        # 建立新线程来完成这件事情
        threading.Thread(target=self.handleSpeak).start()

    def handleSpeak(self):
        result = self.recognize_speech_from_mic(self.recognizer, self.microphone)

        # 结束输入UI
        self.isSpeaking = False
        self.isSpeakingLabel.setVisible(self.isSpeaking)
        threading.Thread(target=self.playWav, args=(r'resource\button.wav',)).start()
        if not result["success"]:
            self.handleCommand(-1)
        elif result["error"]:
            self.handleCommand(-1)
        else:
            # 设置输入
            self.handleInput(result["transcription"])

    def getWeather(self):
        rb = requests.get('http://wthrcdn.etouch.cn/weather_mini?city=嘉定')
        try:
            if rb.status_code == 200:
                res = json.loads(rb.text)
                return "The weather now is: " + res['data']['forecast'][0]['type']
            else:
                return "Please check your network first."
        except:
            return "Please check your network first."

    def handleInput(self, inputCommand):
        """
        处理用户输入
        """
        # 长度过小说明是无效输入
        if len(inputCommand) <= 3:
            return
        self.myCommand = inputCommand
        self.myLabel.setText(self.myCommand)
        self.myLabel.adjustSize()

        maxScore = 0
        maxIndex = -1
        for index, item in enumerate(self.supportCommand):
            score = self.calculateSimilarity(self.myCommand, item)
            # 分数过低则不考虑
            if score <= 0.2:
                continue
            if score > maxScore:
                maxScore = score
                maxIndex = index
        if maxIndex == -1:
            rootCommand = "Sorry, I can't understand. Could you please repeat?"
        elif maxIndex == 0:
            # help
            rootCommand = "You can: \n" + "\n".join(self.supportCommand[1:])
        elif maxIndex == 3:
            rootCommand = "..."
        else:
            rootCommand = "You mean '" + self.supportCommand[maxIndex] + "', I'll do that for you."
        self.handleCommand(maxIndex, rootCommand)

    def handleCommand(self, command: int, rootCommand: str = ""):
        self.responseLabel.setText(rootCommand)
        self.responseLabel.adjustSize()
        self.responseProfile.setVisible(True)
        self.responseLabel.setVisible(True)
        if command != 3:
            threading.Thread(target=self.promptVoice, args=(rootCommand,)).start()

        if command == 1:
            # 播放音乐
            win32api.ShellExecute(0, 'open', r'resource\Mt-Washington.mp3', '', '', 1)
        elif command == 2:
            # 打开文件
            win32api.ShellExecute(0, 'open', r'C:\Windows\System32\notepad.exe', '', '', 1)
        elif command == 3:
            res = self.getWeather()
            # 天气需要重新设置
            self.responseLabel.setText(res)
            self.responseLabel.adjustSize()
            self.responseProfile.setVisible(True)
            self.responseLabel.setVisible(True)
            threading.Thread(target=self.promptVoice, args=(rootCommand,)).start()

    def calculateSimilarity(self, current: str, target: str):
        return difflib.SequenceMatcher(None, current, target).quick_ratio()

    def recognize_speech_from_mic(self, recognizer, microphone):
        if not isinstance(recognizer, sr.Recognizer):
            raise TypeError("`recognizer` must be `Recognizer` instance")

        if not isinstance(microphone, sr.Microphone):
            raise TypeError("`microphone` must be `Microphone` instance")

        # adjust the recognizer sensitivity to ambient noise and record audio
        # from the microphone
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        # set up the response object
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        try:
            response["transcription"] = recognizer.recognize_sphinx(audio)
        except sr.RequestError:
            # API was unreachable or unresponsive
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            # speech was unintelligible
            response["error"] = "Unable to recognize speech"

        return response

    def playWav(self, mediaLocation: str):
        """
        播放音效
        """
        file = QUrl.fromLocalFile(mediaLocation)  # 音频文件路径
        content = QtMultimedia.QMediaContent(file)
        player = QtMultimedia.QMediaPlayer()
        player.setMedia(content)
        player.setVolume(50.0)
        player.play()
        time.sleep(2)

    def promptVoice(self, sentence: str):
        """
        语音提示
        """
        try:
            self.speaker.endLoop()
        except:
            pass
        self.speaker.say(sentence)
        self.speaker.runAndWait()
        self.speaker.stop()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    application = MainForm()
    application.show()
    sys.exit(app.exec())
