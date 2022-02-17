import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from gui import Ui_MainWindow
from scraper import GroupsScraper
from facebook_scraper.exceptions import LoginError


class Main:
    progress_id = 1
    progress = ""

    def __init__(self, ui):
        self.ui = ui

    def add_group(self):
        # get group id
        group_id = ui.groupid_edit.text()

        # create list item
        item = QTreeWidgetItem(ui.groups_list)
        item.setCheckState(0, Qt.Checked)
        item.setText(1, group_id)
        item.setText(2, group_id)

        # remove button (icon)
        remove_btn = QPushButton(parent=ui.groups_list)
        remove_btn.setFixedSize(QSize(20, 20))
        remove_btn.setIcon(QApplication.style().standardIcon(
            QStyle.SP_DialogCloseButton))
        remove_btn.clicked.connect(lambda: self.remove_group(item))

        ui.groups_list.setItemWidget(item, 3, remove_btn)

        # add to tree widget
        ui.groups_list.addTopLevelItems([item])
        ui.groupid_edit.clear()

    def remove_group(self, item):
        ui.groups_list.takeTopLevelItem(
            ui.groups_list.indexOfTopLevelItem(item))

    def add_keyword(self):
        keyword = ui.keyword_edit.text()
        item = QTreeWidgetItem(ui.keywords_list)
        item.setCheckState(0, Qt.Checked)
        item.setText(1, keyword)

        # remove button (icon)
        remove_btn = QPushButton(parent=ui.keywords_list)
        remove_btn.setFixedSize(QSize(20, 20))
        remove_btn.setIcon(QApplication.style().standardIcon(
            QStyle.SP_DialogCloseButton))
        remove_btn.clicked.connect(lambda: self.remove_keyword(item))

        ui.keywords_list.setItemWidget(item, 2, remove_btn)

        # add to tree widget
        ui.keywords_list.addTopLevelItems([item])
        ui.keyword_edit.clear()

    def remove_keyword(self, item):
        ui.keywords_list.takeTopLevelItem(
            ui.keywords_list.indexOfTopLevelItem(item))

    def update_progress(self, new_progress):
        self.progress += f"{self.progress_id}. {new_progress}<br>"
        ui.progress_edit.setText(self.progress)

        # update gui immediately
        QApplication.processEvents()

        self.progress_id += 1

    def start_scraping(self):
        # check if login info isn't empty
        if ui.email_edit.text() == "" or ui.password_edit.text() == "":
            self.error_dialog(
                "Please enter your login credentials.", "Login Error")
            return

        # disable start button
        ui.start_btn.setEnabled(False)
        QApplication.processEvents()

        # if save login info is checked, save login info to a file
        if ui.save_login_chkbx.isChecked():
            with open("credentials.txt", "w") as f:
                f.write(ui.email_edit.text() + "\n")
                f.write(ui.password_edit.text() + "\n")
        else:
            # delete credentials file if it exists
            if os.path.exists("credentials.txt"):
                os.remove("credentials.txt")

        self.update_progress("Starting scraper...")

        email = ui.email_edit.text()
        password = ui.password_edit.text()
        scraper = GroupsScraper(email,
                                password,
                                [2786770884931764])
        # connect the scraping complete signal to the set_scraping_result function,
        # so when the scraping is done, a signal will be emitted, and the function will be called
        scraper.scrape_complete_sig.connect(self.set_scraping_result)

        try:
            scraper.start()
        except LoginError as e:
            # error_dialog(str(e))
            self.update_progress(
                f"<span style='color:red'>Login error: {e}</span>")

    # this function is being called once the scraping is done
    def set_scraping_result(self, result):
        # write results to file utf 8
        # with open("results.txt", "w", encoding="") as f:
        #     f.write(str(result))
        print(result)
        self.update_progress("Scraping done.")
        ui.start_btn.setEnabled(True)

    def error_dialog(self, message, title="Error"):
        error_icon = QPixmap("./icons/error.png")
        error_icon = error_icon.scaled(QSize(24, 24))

        msg = QMessageBox()
        msg.setIconPixmap(error_icon)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    def load_credentials(self):
        # check if credentials file exists
        if os.path.exists("credentials.txt"):
            # load credentials from file
            with open("credentials.txt", "r") as f:
                lines = f.readlines()
                ui.email_edit.setText(lines[0].strip())
                ui.password_edit.setText(lines[1].strip())

    def set_gui(self):
        self.load_credentials()

        # change groups list column widths
        ui.groups_list.setColumnWidth(0, 20)
        ui.groups_list.setColumnWidth(1, 180)
        ui.groups_list.setColumnWidth(2, 180)
        ui.groups_list.setColumnWidth(3, 20)

        # set progress edit to bold
        ui.progress_edit.setFontWeight(QFont.Bold)

    def set_listeners(self):
        ui.start_btn.clicked.connect(self.start_scraping)
        ui.add_group_btn.clicked.connect(self.add_group)
        ui.add_keyword_btn.clicked.connect(self.add_keyword)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    main = Main(ui)

    main.set_gui()
    main.set_listeners()

    sys.exit(app.exec_())
