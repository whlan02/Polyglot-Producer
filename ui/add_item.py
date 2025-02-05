from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt5.QtGui import QGuiApplication
from core.database import DatabaseManager

class AddItemWindow(QDialog):
    def __init__(self, main_window, group_id, group_name, learning_language):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Add Knowledge Item")
        self.centerWindow()
        self.layout = QVBoxLayout()

        self.learning_lang_label = QLabel(f"Learning Language Content({main_window.learning_lang}):")
        self.learning_lang_input = QLineEdit()

        self.base_lang_label = QLabel(f"Base Language Explanation({main_window.base_lang}):")
        self.base_lang_input = QLineEdit()

        self.group_id = group_id
        self.group_name = group_name
        self.group_label = QLabel(f"Group: {group_name}")

        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_item)

        self.layout.addWidget(self.learning_lang_label)
        self.layout.addWidget(self.learning_lang_input)
        self.layout.addWidget(self.base_lang_label)
        self.layout.addWidget(self.base_lang_input)
        self.layout.addWidget(self.group_label)
        self.layout.addWidget(self.add_btn)

        self.setLayout(self.layout)

        self.db_manager = DatabaseManager(learning_language)

    def centerWindow(self):
        # PySide6获取屏幕信息的新方式
        screen = QGuiApplication.primaryScreen().availableGeometry()
        screen_center = screen.center()

        self.resize(600, 400)
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)
        self.move(window_geometry.topLeft())

    def add_item(self):
        target_lang = self.learning_lang_input.text()
        base_lang = self.base_lang_input.text()
        if target_lang and base_lang:
            self.main_window.add_item_to_group(target_lang, base_lang, self.group_id, self.group_name)
            self.close()
        else:
            QMessageBox.warning(self, "Warning", "Both fields must be filled.")