from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QDesktopWidget


class AddGroupWindow(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.centerWindow()
        self.setWindowTitle("Add Group")
        self.layout = QVBoxLayout()

        self.group_name_label = QLabel("Group Name:")
        self.group_name_input = QLineEdit()

        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_group)

        self.layout.addWidget(self.group_name_label)
        self.layout.addWidget(self.group_name_input)
        self.layout.addWidget(self.add_btn)

        self.setLayout(self.layout)

    def centerWindow(self):

        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()


        self.resize(400, 200)
        
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)


        self.move(window_geometry.topLeft())

    def add_group(self):
        group_name = self.group_name_input.text()
        if group_name:
            self.main_window.db_manager.add_group(group_name)
            self.main_window.add_group_to_tree(group_name)
            self.close()
        else:
            QMessageBox.warning(self, "Warning", "Group name cannot be empty.")