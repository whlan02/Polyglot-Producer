import webbrowser
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QApplication, QProgressBar, QMessageBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QThread, QRect
from PySide6.QtGui import QGuiApplication
from core.ai import AIHelper
import gtts
import os
import sounddevice as sd
import soundfile as sf
import json
import pygame
import time
import numpy as np
import random

language_map = {
    "English": "en",
    "German": "de",
    "Spanish": "es",
    "French": "fr",
    "Italian": "it",
    "Japanese": "ja",
    "Chinese": "zh",
    "Russian": "ru",
}

class StudyWindow(QDialog):
    def __init__(self, group_name, db_manager, main_window):
        super().__init__()
        self.setWindowTitle("Study")
        self.centerWindow()
        self.main_window = main_window  
        self.group_name = group_name
        self.db_manager = db_manager
        self.ai_helper = AIHelper(api_key=self.main_window.api_key)
        self.current_item_index = 0
        self.current_item = None
        self.generated_sentences = {}
        self.translated_generated_sentences = {}
        self.items = []
        self.recording = False
        self.recorded_audio_path = "recorded_audio.wav"

        self.layout = QVBoxLayout()

        self.init_ui()
        self.load_next_item()

    def init_ui(self):

        self.current_group_label = QLabel()
        self.current_group_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.current_group_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.current_group_label)


        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.progress_label)

        #delete old progress bar
        # self.progress_bar = QProgressBar()
        # self.layout.addWidget(self.progress_bar)


        self.step1_layout = QVBoxLayout()
        self.step1_label = QLabel("Step 1:Listening Practice")
        self.step1_label.setAlignment(Qt.AlignCenter)
        self.step1_layout.addWidget(self.step1_label)

        self.play_item_audio_btn = QPushButton("Play Item Audio")
        self.play_item_audio_btn.clicked.connect(self.play_item_audio)
        self.step1_layout.addWidget(self.play_item_audio_btn)

        self.play_sentence_audio_btn = QPushButton("Play Sentence Audio")
        self.play_sentence_audio_btn.clicked.connect(self.play_sentence_audio1)
        self.step1_layout.addWidget(self.play_sentence_audio_btn)

        self.step1_layout.addLayout(QHBoxLayout())  # Placeholder for common buttons

        self.layout.addLayout(self.step1_layout)


        self.step2_layout = QVBoxLayout()
        self.step2_label = QLabel("Step 2:Visual Recall")
        self.step2_label.setAlignment(Qt.AlignCenter)
        self.step2_layout.addWidget(self.step2_label)

        self.image_search_btn = QPushButton("Search Image")
        self.image_search_btn.clicked.connect(self.search_image)
        self.step2_layout.addWidget(self.image_search_btn)

        self.step2_layout.addLayout(QHBoxLayout())  # Placeholder for common buttons

        self.layout.addLayout(self.step2_layout)


        self.step3_layout = QVBoxLayout()
        self.step3_label = QLabel("Step 3:Pronunciation Practice")
        self.step3_label.setAlignment(Qt.AlignCenter)
        self.step3_layout.addWidget(self.step3_label)

         # current item label
        self.current_item_label = QLabel()
        self.current_item_label.setAlignment(Qt.AlignCenter)
        self.step3_layout.addWidget(self.current_item_label)
        # current sentence label
        self.current_sentence_label = QLabel()
        self.current_sentence_label.setAlignment(Qt.AlignCenter)
        self.step3_layout.addWidget(self.current_sentence_label)

        self.play_item_audio_btn_2 = QPushButton("Play Item Audio")
        self.play_item_audio_btn_2.clicked.connect(self.play_item_audio)
        self.step3_layout.addWidget(self.play_item_audio_btn_2)

        self.play_sentence_audio_btn_2 = QPushButton("Play Sentence Audio")
        self.play_sentence_audio_btn_2.clicked.connect(self.play_sentence_audio2)
        self.step3_layout.addWidget(self.play_sentence_audio_btn_2)

        self.start_recording_btn = QPushButton("Start Recording")
        self.start_recording_btn.clicked.connect(self.start_recording)
        self.step3_layout.addWidget(self.start_recording_btn)

        self.play_recorded_audio_btn = QPushButton("Play Recorded Audio")
        self.play_recorded_audio_btn.clicked.connect(self.play_recorded_audio)
        self.step3_layout.addWidget(self.play_recorded_audio_btn)

        self.step3_layout.addLayout(QHBoxLayout())  # Placeholder for common buttons

        self.layout.addLayout(self.step3_layout)

  
        self.step4_layout = QVBoxLayout()
        self.step4_label = QLabel("Step 4:Translation Practice")
        self.step4_label.setAlignment(Qt.AlignCenter)
        self.step4_layout.addWidget(self.step4_label)

        self.translation_label = QLabel()
        self.translation_label.setAlignment(Qt.AlignCenter)
        self.step4_layout.addWidget(self.translation_label)

        self.translated_sentence_label = QLabel()
        self.translated_sentence_label.setAlignment(Qt.AlignCenter)
        self.step4_layout.addWidget(self.translated_sentence_label)

        self.user_sentence_input = QLineEdit()
        self.user_sentence_input.setPlaceholderText("Enter your Translation here")
        self.step4_layout.addWidget(self.user_sentence_input)

        self.show_answer_btn = QPushButton("Show Answer")
        self.show_answer_btn.clicked.connect(self.show_answer)
        self.step4_layout.addWidget(self.show_answer_btn)

        self.generated_sentence_label = QLabel()
        self.generated_sentence_label.setAlignment(Qt.AlignCenter)
        self.step4_layout.addWidget(self.generated_sentence_label)

        self.step4_layout.addLayout(QHBoxLayout())  # Placeholder for common buttons

        self.layout.addLayout(self.step4_layout)

        # Common buttons layout
        self.common_buttons_layout = QHBoxLayout()
        self.common_last_step_btn = QPushButton("Last Step")
        self.common_last_step_btn.clicked.connect(self.last_step)
        self.common_buttons_layout.addWidget(self.common_last_step_btn)

        self.common_next_step_btn = QPushButton("Next Step")
        self.common_next_step_btn.clicked.connect(self.next_step)
        self.common_buttons_layout.addWidget(self.common_next_step_btn)

        self.common_next_item_btn = QPushButton("Next Item")
        self.common_next_item_btn.clicked.connect(self.load_next_item)
        self.common_next_item_btn.setVisible(False)  # Initially hidden
        self.common_buttons_layout.addWidget(self.common_next_item_btn)

        self.layout.addLayout(self.common_buttons_layout)

        self.setLayout(self.layout)
        self.set_step_visible(1)

    def centerWindow(self):

        screen = QGuiApplication.primaryScreen().availableGeometry()
        screen_center = screen.center()


        self.resize(600, 400)
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)
        self.move(window_geometry.topLeft())

    def set_step_visible(self, step):
        print(f"Setting step {step} visible")

        for layout in [self.step1_layout, self.step2_layout, self.step3_layout, self.step4_layout]:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item.widget():
                    item.widget().setVisible(False)

        if step == 1:
            for i in range(self.step1_layout.count()):
                item = self.step1_layout.itemAt(i)
                if item.widget():
                    item.widget().setVisible(True)
            self.common_last_step_btn.setVisible(False)
            self.common_next_step_btn.setVisible(True)
            self.common_next_item_btn.setVisible(False)
            
        elif step == 2:
            for i in range(self.step2_layout.count()):
                item = self.step2_layout.itemAt(i)
                if item.widget():
                    item.widget().setVisible(True)
            self.common_last_step_btn.setVisible(True)
            self.common_next_step_btn.setVisible(True)
            self.common_next_item_btn.setVisible(False)
        elif step == 3:
            for i in range(self.step3_layout.count()):
                item = self.step3_layout.itemAt(i)
                if item.widget():
                    item.widget().setVisible(True)
            self.common_last_step_btn.setVisible(True)
            self.common_next_step_btn.setVisible(True)
            self.common_next_item_btn.setVisible(False)
        elif step == 4:
            for i in range(self.step4_layout.count()):
                item = self.step4_layout.itemAt(i)
                if item.widget():
                    item.widget().setVisible(True)
            self.common_last_step_btn.setVisible(True)
            self.common_next_step_btn.setVisible(False)
            self.common_next_item_btn.setVisible(True)

    def next_step(self):
        print("Next Step button clicked")
        if self.step1_layout.itemAt(0).widget().isVisible():
            print("Step 1 is visible, moving to Step 2")
            self.set_step_visible(2)
        elif self.step2_layout.itemAt(0).widget().isVisible():
            print("Step 2 is visible, moving to Step 3")
            self.set_step_visible(3)
        elif self.step3_layout.itemAt(0).widget().isVisible():
            print("Step 3 is visible, moving to Step 4")
            self.set_step_visible(4)

    def last_step(self):
        print("Last Step button clicked")
        if self.step2_layout.itemAt(0).widget().isVisible():
            print("Step 2 is visible, moving to Step 1")
            self.set_step_visible(1)
        elif self.step3_layout.itemAt(0).widget().isVisible():
            print("Step 3 is visible, moving to Step 2")
            self.set_step_visible(2)
        elif self.step4_layout.itemAt(0).widget().isVisible():
            print("Step 4 is visible, moving to Step 3")
            self.set_step_visible(3)

    def load_next_item(self):
        if not self.current_item_index:
            self.items = self.db_manager.get_items_by_group_name(self.group_name)
            random.shuffle(self.items)
            if not self.items:  
                self.current_group_label.setText("No items to learn in this group！")
                self.step1_layout.setEnabled(False)
                self.step2_layout.setEnabled(False)
                self.step3_layout.setEnabled(False)
                self.step4_layout.setEnabled(False)
                return

        if self.current_item_index < len(self.items):
            self.current_item = self.items[self.current_item_index]
            self.current_group_label.setText(f"You are learning the group: {self.group_name}")
            generated_sentences, translated_sentences = self.generate_sentences(self.current_item["target_lang"])
            self.generated_sentences[self.current_item_index] = generated_sentences
            self.translated_generated_sentences[self.current_item_index] = translated_sentences
            self.current_item_index += 1
            self.progress_label.setText(f"Current item: {self.current_item_index}/{len(self.items)}")

            progress_value = int((self.current_item_index / len(self.items)) * 100)
            #self.progress_bar.setValue(progress_value)

            if len(generated_sentences) >= 3 and len(translated_sentences) >= 3:
                third_translated_sentence = translated_sentences[2] 

                self.translated_sentence_label.setText(f"Please translate: {third_translated_sentence}")
                self.translated_sentence_label.setStyleSheet("color: green;")

                self.user_sentence_input.setPlaceholderText("Enter your Translation here")
                self.user_sentence_input.clear()  

            self.generated_sentence_label.setText("")
            self.generated_sentence_label.setStyleSheet("")

            # 更新当前 item 和句子的显示
            self.current_item_label.setText(f"Current Item: {self.current_item['target_lang']}")
            self.current_sentence_label.setText(f"Current Sentence: {generated_sentences[1]}")

            self.step1_layout.setEnabled(True)
            self.step2_layout.setEnabled(False)
            self.step3_layout.setEnabled(False)
            self.step4_layout.setEnabled(False)
            
            self.set_step_visible(1)
        else:
            self.current_group_label.setText("You have learned them all！")
            self.step1_layout.setEnabled(False)
            self.step2_layout.setEnabled(False)
            self.step3_layout.setEnabled(False)
            self.step4_layout.setEnabled(False)

    def generate_sentences(self, word):
        response = self.ai_helper.generate_sentence(word, self.main_window.learning_lang)
        print(response)
        
        try:
            sentences_data = json.loads(response)
            
            generated_sentences = []
            translated_sentences = []
            
            for item in sentences_data:
                generated_sentences.append(item['sentence'].strip())
                translated_sentences.append(item['translation'].strip())
            
            for i in range(len(generated_sentences)):
                print(f"Sentence {i+1}: {generated_sentences[i]}")
                print(f"Translation {i+1}: {translated_sentences[i]}")
            
            print(f"generated_sentences = {generated_sentences}")
            print(f"translated_sentences = {translated_sentences}")
            
            return generated_sentences, translated_sentences
        
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return [], []
        except Exception as e:
            print(f"An error occurred: {e}")
            return [], []

    def play_audio(file_path):
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.5)
        pygame.mixer.quit()

    def play_item_audio(self):
        learning_lang_name = self.main_window.learning_lang
        learning_lang_code = language_map.get(learning_lang_name)

        if learning_lang_code:
            tts = gtts.gTTS(self.current_item["target_lang"], lang=learning_lang_code)
            tts.save("item_audio.mp3")
            StudyWindow.play_audio("item_audio.mp3")
            os.remove("item_audio.mp3")
        else:
            print(f"Unsupported language: {learning_lang_name}")

    def play_sentence_audio1(self):
        learning_lang_name = self.main_window.learning_lang
        learning_lang_code = language_map.get(learning_lang_name)

        if learning_lang_code:
            sentence = self.generated_sentences.get(self.current_item_index - 1, [])[0]  
            tts = gtts.gTTS(sentence, lang=learning_lang_code)
            tts.save("sentence_audio.mp3")
            StudyWindow.play_audio("sentence_audio.mp3") 
            os.remove("sentence_audio.mp3")
        else:
            print(f"Unsupported language: {learning_lang_name}")
    
    def play_sentence_audio2(self):
        learning_lang_name = self.main_window.learning_lang
        learning_lang_code = language_map.get(learning_lang_name)

        if learning_lang_code:
            sentences = self.generated_sentences.get(self.current_item_index - 1, [])
            if len(sentences) > 1:  
                sentence = sentences[1]  
            else:
                sentence = sentences[0]  
            tts = gtts.gTTS(sentence, lang=learning_lang_code)
            tts.save("sentence_audio.mp3")
            StudyWindow.play_audio("sentence_audio.mp3") 
            os.remove("sentence_audio.mp3")
        else:
            print(f"Unsupported language: {learning_lang_name}")

    def search_image(self):
        word = self.current_item["target_lang"]
        url = f"https://www.google.com/search?q={word}&tbm=isch"
        webbrowser.open(url)

    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.start_recording_btn.setText("Stop Recording")
            self.recording_thread = RecordingThread()
            self.recording_thread.start()
        else:
            self.recording = False
            self.start_recording_btn.setText("Start Recording")
            self.recording_thread.stop()

    def play_recorded_audio(self):
        if os.path.exists(self.recorded_audio_path):
            pygame.mixer.init()
            pygame.mixer.music.load(self.recorded_audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(1)
            pygame.mixer.quit()
        else:
            QMessageBox.warning(self, "Warning", "No recorded audio found.")

    def show_answer(self):
        sentences = self.generated_sentences.get(self.current_item_index - 1, [])
        translated_sentences = self.translated_generated_sentences.get(self.current_item_index - 1, [])
        
        if len(sentences) >= 3 and len(translated_sentences) >= 3:
            third_sentence = sentences[2]
            
            self.generated_sentence_label.setText(third_sentence)
            self.generated_sentence_label.setStyleSheet("color: blue;")
            
        else:
            QMessageBox.warning(self, "Warning", "Not enough sentences generated for this item.")

class RecordingThread(QThread):
    def __init__(self):
        super().__init__()
        self.recording = False
        self.recorded_audio_path = "recorded_audio.wav"
        self.stop_recording = False  # 添加一个标志变量

    def run(self):
        self.recording = True
        fs = 44100  # Sample rate
        duration = 10  # longest recording duration in seconds
        channels = 2  
        dtype = 'int16'  # 数据类型

        # 创建一个空的数组来存储录制的数据
        myrecording = np.zeros((int(duration * fs), channels), dtype=dtype)

        # 开始录制
        with sd.InputStream(samplerate=fs, channels=channels, dtype=dtype) as stream:
            start_time = time.time()
            sample_count = 0  # 用于跟踪已录制的样本数量

            while self.recording and time.time() - start_time < duration:
                if self.stop_recording:
                    break
                data, _ = stream.read(fs)  # 每次读取一秒钟的数据
                actual_samples = data.shape[0]  # 实际读取的样本数量

                # 将数据复制到 myrecording 中
                myrecording[sample_count:sample_count + actual_samples] = data[:actual_samples]

                sample_count += actual_samples  # 更新已录制的样本数量

        # 保存录制的音频
        sf.write(self.recorded_audio_path, myrecording[:sample_count], fs)  # 只保存实际录制的部分

    def stop(self):
        self.recording = False
        self.stop_recording = True