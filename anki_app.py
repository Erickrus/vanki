import json
import os
import sys

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import hashlib
import pygame
import random
import re
import requests
import threading
import time
import uuid
import websocket

from bs4 import BeautifulSoup
from datetime import datetime
from enum import Enum
from markdown import markdown

from PyQt6.QtWidgets import (
    QApplication, QMainWindow , QLabel, QCheckBox,
    QTabWidget, QWidget, QVBoxLayout, QTextEdit, QFileDialog, QMessageBox,
    QSpinBox, QPushButton, 
)
from PyQt6.QtGui import QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import pyqtSlot

# pip3 install pygame
# pip3 install PyQt6==6.5.0 PyQt6-WebEngine==6.5.0 PyQt6-WebEngine-Qt6==6.5.0
# pip list | grep -i qt

class TTS():
    def __init__(self):
        self.ipAddr = ""
        self.trustedClientToken = '6A5AA1D4EAFF4E9FB37E23D68491D6F4'
        self.synthesizeEndpoint = f"wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1?TrustedClientToken={self.trustedClientToken}"
        self.voiceListEndpoint = f'https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/voices/list?trustedclienttoken={self.trustedClientToken}'
        self.voices = {
            'zh-CN-XiaoxiaoNeural': {"gender": "female"},
            'zh-CN-XiaoyiNeural':  {"gender": "female"},
            'zh-CN-YunjianNeural':  {"gender": "male"},
            'zh-CN-YunxiNeural':  {"gender": "male"},
            'zh-CN-YunxiaNeural':  {"gender": "female"},
            'zh-CN-YunyangNeural':  {"gender": "male"},
            # 'zh-CN-liaoning-XiaobeiNeural':  {"gender": "female"}, # dont use them
            # 'zh-CN-shaanxi-XiaoniNeural':  {"gender": "female"} # dont use them
        }

        # These parameters are from previous TTS class
        self.ipAddr = "14.215.177.147"
        #self.ipAddr = "localhost"
        self.spd = 4
        self.pit = 4

    def get_voices(self):
        self.alllist = requests.get(self.voiceListEndpoint).json()
        return [_['ShortName'] for _ in self.alllist]

    def get_wav_ms(self, content, waveFilename, tts_spd_20=4, voice='zh-CN-XiaoxiaoNeural', waveRate=16000, mono=True):
        headers2 = [
            "Pragma: no-cache",
            "Cache-Control: no-cache",
            "Origin: chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold",
            "Accept-Encoding: gzip, deflate, br",
            "Accept-Language: en-US,en;q=0.9",
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.41",
        ]
        ws = websocket.create_connection(self.synthesizeEndpoint, header=headers2)

        date = self.date_to_string()

        ws.send("X-Timestamp:{}\r\n".format(date) +
                "Content-Type:application/json; charset=utf-8\r\n"
                "Path:speech.config\r\n\r\n"
                '{"context":{"synthesis":{"audio":{"metadataoptions":{'
                '"sentenceBoundaryEnabled":false,"wordBoundaryEnabled":true},'
                '"outputFormat":"audio-24khz-48kbitrate-mono-mp3"'
                "}}}}\r\n")
        ws.send(
            self._ssml_headers_plus_data(
                self._connect_id(),
                date,
                self._mk_ssml(content, voice, str(int(tts_spd_20/20*100))+'%'),
            )
        )

        end_resp_pat = re.compile('Path:turn.end')
        audio_stream = b''
        while(True):
            response = ws.recv()
            # print(response)
            # print(type(response),"++++++++++++")
            # Make sure the message isn't telling us to stop
            if (re.search(end_resp_pat, str(response)) == None):
                # Check if our response is text data or the audio bytes
                if type(response) == type(bytes()):
                    # Extract binary data
                    try:
                        needle = b'Path:audio\r\n'
                        start_ind = response.find(needle) + len(needle)
                        audio_stream += response[start_ind:]
                    except:
                        pass
            else:
                break
        ws.close()

        mp3Filename = waveFilename[:-4] + ".mp3"
        with open(mp3Filename, 'wb') as audio_out:
            audio_out.write(audio_stream)

        return mp3Filename

    # Fix the time to match Americanisms
    def _hr_cr(self, hr):
        corrected = (hr - 1) % 24
        return str(corrected)

    # Add zeros in the right places i.e 22:1:5 -> 22:01:05
    def _fr(self, input_string):
        corr = ''
        i = 2 - len(input_string)
        while (i > 0):
            corr += '0'
            i -= 1
        return corr + input_string

    # Generate X-Timestamp all correctly formatted
    def _get_x_time(self):
        now = datetime.now()
        return self._fr(str(now.year)) + '-' + self._fr(str(now.month)) + '-' + self._fr(str(now.day)) + 'T' + self._fr(self._hr_cr(int(now.hour))) + ':' + self._fr(str(now.minute)) + ':' + self._fr(str(now.second)) + '.' + str(now.microsecond)[:3] + 'Z'

    def date_to_string(self) -> str:
        # Return Javascript-style date string.
        #
        # Returns:
        #     str: Javascript-style date string.

        # %Z is not what we want, but it's the only way to get the timezone
        # without having to use a library. We'll just use UTC and hope for the best.
        # For example, right now %Z would return EEST when we need it to return
        # Eastern European Summer Time.
        return time.strftime(
            "%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)", time.gmtime()
        )

    def _ssml_headers_plus_data(self, request_id: str, timestamp: str, ssml: str) -> str:
        # Returns the headers and data to be used in the request.
        #
        # Returns:
        #     str: The headers and data to be used in the request.
        return (
            "X-RequestId:{}\r\n".format(request_id) +
            "Content-Type:application/ssml+xml\r\n"
            # This is not a mistake, Microsoft Edge bug.
            "X-Timestamp:{}Z\r\n".format(timestamp) +
            "Path:ssml\r\n\r\n"
            "{}".format(ssml)
        )

    def _mk_ssml(self, text, voice: str, rate: str) -> str:
        # Creates a SSML string from the given parameters.
        #
        # Returns:
        #     str: The SSML string.
        if isinstance(text, bytes):
            text = text.decode("utf-8")

        ssml = (
            "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
            "<voice name='{}'><prosody pitch='+0Hz' rate='{}'>".format(voice, rate) +
            "{}</prosody></voice></speak>".format(text)
        )
        return ssml

    def _connect_id(self) -> str:
        # Returns a UUID without dashes.
        #
        # Returns:
        #     str: A UUID without dashes.
        return str(uuid.uuid4()).replace("-", "")



    def get_wav(self, text, wavFilename, rate=16000, mono=True):
        self.get_wav_ms(text, wavFilename)



AnkiOrderType = Enum('AnkiOrderType', ['SEQUENCE', 'RANDOM'])
class Anki:
    def __init__(self):
        self.questionId = 0
        self.title = ""
        self.questions = []
        self.orderType = AnkiOrderType.SEQUENCE
        with open("anki_html_template.html", "r") as f:
            self.htmlTemplate = f.read()

    def load(self, filename):
        self.questionId = 0
        self.title = os.path.basename(filename).replace(".json", "")
        with open(filename, "r") as f:
            self.questions = json.loads(f.read())["questions"]
    
    def save(self, filename):
        self.title = os.path.basename(filename).replace(".json", "")
        with open(filename, "w") as f:
            f.write(
                json.dumps({
                        "questions": self.questions
                    }, 
                    indent=2, 
                    ensure_ascii=False
                )
            )
    
    def _pass_question(self, question):
        return "pass" in question.keys() and question["pass"]

    def get_next_question(self):
        questionId = -1
        question = None
        if len(self.questions) > 0:
            if self.orderType == AnkiOrderType.SEQUENCE:
                self.questionId = self.questionId % len(self.questions)
                questionId = self.questionId
                question = self.questions[self.questionId]
                self.questionId += 1
            elif self.orderType == AnkiOrderType.RANDOM:
                self.questionId += random.randint(0, len(self.questions)-1)
                self.questionId = self.questionId % len(self.questions)
                questionId = self.questionId
                question = self.questions[questionId]

        if questionId >= 0 and len(self.questions)>0:
            if self._pass_question(self.questions[questionId]):
                #print("looking for new question")
                for i in range(len(self.questions)-1):
                    currQuestion = self.questions[i % len(self.questions)]
                    if not self._pass_question(currQuestion):
                        questionId = i
                        question = currQuestion
                        self.questionId = i + 1
                        return questionId, question
                questionId, question = -1, None
                #print("not enough question")

        return questionId, question
    
    def _get_hash(self, text):
        result = hashlib.md5(text.encode())
        return result.hexdigest()

    def say(self, content):
        os.makedirs("voices", exist_ok=True)
        html = markdown(content)
        content = ''.join(BeautifulSoup(html, "html.parser").findAll(text=True))
        content = content.replace('&','').replace("[#!","").replace("#!]","").replace("\\n","")
        #waveFilename = "voices/%s.wav" % self._get_hash(content)

        waveFilename = "voices/%s.mp3" % self._get_hash(content)
        if not os.path.exists(waveFilename):
            ttsInstance = TTS()
            ttsInstance.ipAddr = "wss://speech.platform.bing.com/"
            ttsInstance.get_wav(
                content,
                waveFilename,
                mono=True
            )

        sound_thread = threading.Thread(target=self.play_sound, args=(waveFilename,))
        sound_thread.start()

    def play_sound(self, waveFilename):
        pygame.mixer.init()
        pygame.mixer.music.stop()
        pygame.mixer.music.load(waveFilename)
        pygame.mixer.music.play()
    
    def answer_to_html(self, answer):
        lines = answer.split("\\n")
        pattern = re.compile(r'\[#!(.*?)#!\]')

        html_lines = []
        button_id = 1
        for line in lines:
            def replace_with_button(match):
                nonlocal button_id
                text = match.group(1)
                spaces = ' ' * len(text)
                button_html = f"<input style='border: none; border-bottom: 2px solid black; background: none; padding: 5px; cursor: pointer; font-size: 16px; outline: none;' id='btn{button_id:04}' type='button' value='{spaces}' onclick=\"toggle('{text}')\" />"
                button_id += 1
                return button_html

            html_line = pattern.sub(replace_with_button, line)
            html_lines.append(html_line)
        html_result = "<br/>\n".join(html_lines) + "<br/>"
        return html_result

class AnkiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.anki = Anki()

    def initUI(self):
        self.setWindowTitle('v-anki 语音暗记')
        self.setGeometry(100, 100, 800, 520)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        helpMenu = menubar.addMenu('Help')

        openAct = QAction('Open', self)
        openAct.triggered.connect(self.open_file)
        saveAct = QAction('Save', self)
        saveAct.triggered.connect(self.save_file)
        saveAsAct = QAction('Save As', self)
        saveAsAct.triggered.connect(self.save_as_file)
        exitAct = QAction('Exit', self)
        exitAct.triggered.connect(self.close)

        fileMenu.addAction(openAct)
        fileMenu.addAction(saveAct)
        fileMenu.addAction(saveAsAct)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAct)

        aboutAct = QAction('About', self)
        aboutAct.triggered.connect(self.show_about)
        helpMenu.addAction(aboutAct)

        # Anki name label
        self.ankiNameLabel = QLabel('Anki name', self)
        self.ankiNameLabel.move(10, 10)

        # Checkboxes
        self.randomOrderCheckbox = QCheckBox('Random order', self)
        self.randomOrderCheckbox.move(10, 40)
        self.randomOrderCheckbox.adjustSize()
        self.voiceCheckbox = QCheckBox('Voice', self)
        self.voiceCheckbox.move(10, 50)
        self.voiceCheckbox.setChecked(True)

        # Question label
        self.questionIdLabel = QLabel('QuestionId :', self)
        self.questionIdLabel.move(10, 80)

        # Question ID input
        self.questionIdInput = QSpinBox(self)
        self.questionIdInput.setValue(0)
        self.questionIdInput.move(85, 85)
        self.questionIdInput.setFixedHeight(20)
        self.questionIdInput.setFixedWidth(40)

        # Anki button
        self.ankiButton = QPushButton('Anki', self)
        self.ankiButton.move(5, 110)
        self.ankiButton.adjustSize()
        self.ankiButton.clicked.connect(self.anki)

        # Show Answer button
        self.showAnswerButton = QPushButton('Show Answer', self)
        self.showAnswerButton.move(70, 110)
        self.showAnswerButton.adjustSize()
        self.showAnswerButton.clicked.connect(self.show_answer)

        self.questionLabel = QLabel('', self)
        self.questionLabel.move(10, 145)

        # Tab widget
        self.tabs = QTabWidget(self)
        self.tabs.setGeometry(10, 165, 780, 350)

        # Display tab
        self.displayTab = QWidget()
        self.displayLayout = QVBoxLayout()
        self.htmlView = QWebEngineView(self)
        self.displayLayout.addWidget(self.htmlView)
        self.displayTab.setLayout(self.displayLayout)

        # Edit tab
        self.editTab = QWidget()
        self.editLayout = QVBoxLayout()
        self.editor = QTextEdit(self)
        self.editor.textChanged.connect(self.save_editor_content)
        self.editLayout.addWidget(self.editor)
        self.editTab.setLayout(self.editLayout)

        self.tabs.addTab(self.displayTab, 'Display')
        self.tabs.addTab(self.editTab, 'Edit')

    def get_next_question(self):
        self.anki.orderType = {
            True: AnkiOrderType.RANDOM, 
            False: AnkiOrderType.SEQUENCE
        } [self.randomOrderCheckbox.isChecked()] 
        questionId, question = self.anki.get_next_question()
        if questionId == -1:
            return
        self.questionIdInput.setRange(0, len(self.anki.questions)-1)
        self.questionIdInput.setValue(questionId)
        self.questionLabel.setText(question["question"])
        self.questionLabel.adjustSize()
        self.editor.setText(
            json.dumps(
                question, 
                ensure_ascii=False, 
                indent=2
            )
        )
        self.htmlView.setHtml("")

    def open_file(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open File", "", "ANKI Files (*.json)")
        try:
            if filePath:
                self.anki = Anki()
                self.anki.load(filePath)
                self.ankiNameLabel.setText(self.anki.title)
                self.editor.setText("")
                self.htmlView.setHtml("")
                self.questionLabel.setText("")
                self.questionIdInput.setValue(0)
                self.currentFile = filePath
        except:
            pass

    def save_file(self):
        if hasattr(self, 'currentFile') and self.currentFile:
            self.anki.save(self.currentFile)
            self.ankiNameLabel.setText(self.anki.title)
        else:
            self.save_as_file()

    def save_as_file(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save As", "", "ANKI Files (*.json)")
        if filePath:
            self.currentFile = filePath
            self.save_file()

    def show_about(self):
        QMessageBox.about(self, "About", "v-anki 语音暗记\nVersion 1.0\nDeveloped with Hu, Ying-Hao")

    def anki(self):
        self.get_next_question()
    
    def show_answer(self):
        questionId = int(self.questionIdInput.value())
        question = self.anki.questions[questionId]
        
        html = self.anki.htmlTemplate % self.anki.answer_to_html(question["answer"])
        self.htmlView.setHtml(html)

        if self.voiceCheckbox.isChecked():
            self.anki.say(question["answer"])
    
    @pyqtSlot()
    def save_editor_content(self):

        text = self.editor.toPlainText()
        try:
            question = json.loads(text)
            questionId = int(self.questionIdInput.value())
            self.anki.questions[questionId] = question
        except:
            pass
            #import traceback
            #print(traceback.format_exc())

def main():
    app = QApplication(sys.argv)
    ex = AnkiApp()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

