from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel, QLineEdit, QDesktopWidget
from core.database import DatabaseManager

class SettingsWindow(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.centerWindow()
        self.setWindowTitle("Settings")

        self.layout = QVBoxLayout()

        # Base Language
        self.base_lang_label = QLabel("Base Language:")
        self.base_lang_input = QComboBox()
        self.base_lang_input.addItems(["English", "Chinese", "Spanish", "German"])
        self.base_lang_input.setCurrentText(self.main_window.base_lang)  

        # Learning Language
        self.learning_lang_label = QLabel("Learning Language:")
        self.learning_lang_input = QComboBox()
        self.learning_lang_input.addItems(["English", "Chinese", "Spanish", "German"])
        self.learning_lang_input.setCurrentText(self.main_window.learning_lang)  

        # API Key
        self.api_key_label = QLabel("OpenAI API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(self.main_window.api_key)  

        # Save Button
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save_settings)

       
        self.layout.addWidget(self.base_lang_label)
        self.layout.addWidget(self.base_lang_input)
        self.layout.addWidget(self.learning_lang_label)
        self.layout.addWidget(self.learning_lang_input)
        self.layout.addWidget(self.api_key_label)
        self.layout.addWidget(self.api_key_input)
        self.layout.addWidget(self.save_btn)

        self.setLayout(self.layout)

    def centerWindow(self):
        
        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()

       
        self.resize(400, 300)

        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)


        self.move(window_geometry.topLeft())

    def save_settings(self):

        base_lang = self.base_lang_input.currentText()
        learning_lang = self.learning_lang_input.currentText()
        api_key = self.api_key_input.text()


        print(f"Settings saved: API Key={api_key}, Base Lang={base_lang}, Learning Lang={learning_lang}")


        self.main_window.learning_lang = learning_lang
        self.main_window.base_lang = base_lang
        self.main_window.api_key = api_key


        self.main_window.db_manager = DatabaseManager(learning_lang)


        self.main_window.group_tree.clear()
        self.main_window.groups = {}
        self.main_window.selected_group = None
        self.main_window.selected_item = None
        self.main_window.item_detail_label.setText("No item selected.")


        self.main_window.load_groups_from_database()


        self.accept()