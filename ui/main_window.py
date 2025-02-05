from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QWidget, QScrollArea, QLabel, QTreeWidget, QTreeWidgetItem, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from ui.add_group import AddGroupWindow
from ui.add_item import AddItemWindow
from ui.study import StudyWindow
from ui.settings import SettingsWindow
from core.database import DatabaseManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Polyglot Producer")
        self.centerWindow()  
        self.selected_group = None
        self.selected_item = None
        self.groups = {}
        self.api_key = ""
        self.base_lang = "English"  
        self.learning_lang = "German"  
        self.db_manager = DatabaseManager(self.learning_lang) 
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()  

        # Group Tree
        group_scroll_area = QScrollArea()
        group_scroll_area.setWidgetResizable(True)
        self.group_tree = QTreeWidget()
        self.group_tree.setHeaderLabels(['Groups'])
        self.group_tree.itemSelectionChanged.connect(self.on_group_selection_changed)

        group_scroll_area.setWidget(self.group_tree)
        main_layout.addWidget(group_scroll_area)

        # Item Details
        item_detail_scroll_area = QScrollArea()
        item_detail_scroll_area.setWidgetResizable(True)
        self.item_detail_label = QLabel("No item selected.")
        self.item_detail_label.setAlignment(Qt.AlignCenter)
        item_detail_scroll_area.setWidget(self.item_detail_label)
        main_layout.addWidget(item_detail_scroll_area)

        # Buttons
        button_layout = QVBoxLayout()
        self.add_group_btn = QPushButton("Add Group")
        self.add_group_btn.clicked.connect(self.open_add_group)
        button_layout.addWidget(self.add_group_btn)

        self.delete_group_btn = QPushButton("Delete Group")
        self.delete_group_btn.clicked.connect(self.delete_group)
        button_layout.addWidget(self.delete_group_btn)

        self.add_item_btn = QPushButton("Add Item")
        self.add_item_btn.clicked.connect(self.open_add_item)
        button_layout.addWidget(self.add_item_btn)

        self.delete_item_btn = QPushButton("Delete Item")
        self.delete_item_btn.clicked.connect(self.delete_item)
        button_layout.addWidget(self.delete_item_btn)

        self.study_btn = QPushButton("Study")
        self.study_btn.clicked.connect(self.open_study)
        button_layout.addWidget(self.study_btn)

        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        button_layout.addWidget(self.settings_btn)

        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.load_groups_from_database()

    def centerWindow(self):
        # PySide6获取屏幕信息的新方式
        screen = QGuiApplication.primaryScreen().availableGeometry()
        screen_center = screen.center()

        self.resize(1000, 750)
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)
        self.move(window_geometry.topLeft())

    def load_groups_from_database(self):
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT name FROM groups")
        groups = cursor.fetchall()

        self.group_tree.clear()
        self.groups = {}

        for group in groups:
            group_name = group[0]
            group_item = QTreeWidgetItem([group_name])
            self.group_tree.addTopLevelItem(group_item)
            self.groups[group_name] = {"items": []}

            cursor.execute("SELECT target_lang, base_lang FROM items WHERE group_name = ?", (group_name,))
            items = cursor.fetchall()
            for item in items:
                target_lang, base_lang = item
                item_widget = QTreeWidgetItem([base_lang])
                group_item.addChild(item_widget)
                self.groups[group_name]["items"].append({"target_lang": target_lang, "base_lang": base_lang})

    def open_add_group(self):
        self.add_group_window = AddGroupWindow(self)
        self.add_group_window.exec_()

    def add_group_to_tree(self, group_name):
        group_item = QTreeWidgetItem([group_name])
        self.group_tree.addTopLevelItem(group_item)
        self.groups[group_name] = {"items": []}

    def open_add_item(self):
        if self.selected_group:
            group_id = self.get_group_id(self.selected_group)
            self.add_item_window = AddItemWindow(self, group_id, self.selected_group, self.learning_lang)
            self.add_item_window.exec_()
        else:
            QMessageBox.warning(self, "Warning", "Please select a group first.")

    def get_group_id(self, group_name):
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
        group_id_result = cursor.fetchone()
        if group_id_result:
            return group_id_result[0]
        else:
            return None

    def add_item_to_group(self, target_lang, base_lang, group_id, group_name):
        self.db_manager.add_item(target_lang, base_lang, group_id, group_name)
        self.load_groups_from_database()

    def open_study(self):
        if self.selected_group:
            self.study_window = StudyWindow(self.selected_group, self.db_manager, self)
            self.study_window.exec_()
        else:
            QMessageBox.warning(self, "Warning", "Please select a group first.")

    def open_settings(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.exec_()

    def save_settings(self, base_lang, learning_lang, api_key):
        self.base_lang = base_lang
        self.learning_lang = learning_lang
        self.api_key = api_key
        print(f"Settings saved in main window: API Key={self.api_key}, Base Lang={self.base_lang}, Learning Lang={self.learning_lang}")
        self.db_manager = DatabaseManager(self.learning_lang)

    def on_group_selection_changed(self):
        selected_items = self.group_tree.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            if selected_item.parent() is None:  
                self.selected_group = selected_item.text(0)
                self.selected_item = None
                self.item_detail_label.setText("No item selected.")
            else:  
                self.selected_group = selected_item.parent().text(0)
                item_name = selected_item.text(0)
                for item in self.groups[self.selected_group]["items"]:

                    if item["base_lang"] == item_name:
                        self.selected_item = item

                        self.item_detail_label.setText(f"Base Lang: {item['base_lang']}\nTarget Lang: {item['target_lang']}")
                        break
        else:
            self.selected_group = None
            self.selected_item = None
            self.item_detail_label.setText("No item selected.")

    def delete_group(self):
        if self.selected_group:
            self.db_manager.delete_group(self.selected_group)
            self.load_groups_from_database()
        else:
            QMessageBox.warning(self, "Warning", "Please select a group first.")

    def delete_item(self):
        if self.selected_group and self.selected_item:

            self.db_manager.delete_item(self.selected_item["base_lang"], self.selected_group)
            self.load_groups_from_database()
        else:
            QMessageBox.warning(self, "Warning", "Please select an item first.")
