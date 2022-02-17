import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from gui import Ui_MainWindow
from scraper import GroupsScraper
from facebook_scraper.exceptions import LoginError
from html_generator import HtmlGenerator
import utils


class Main:
    progress_id = 1
    progress = ""

    def __init__(self, ui):
        self.ui = ui

    def add_group(self):
        # get group id
        group_id = ui.groupid_edit.text()

        # check if group id already exists
        for i in range(ui.groups_list.topLevelItemCount()):
            if ui.groups_list.topLevelItem(i).text(1) == group_id:
                self.error_dialog("Group ID already exists.")
                ui.groupid_edit.clear()
                return

        # get group name
        self.update_progress("Getting group name...")
        group_name = utils.get_group_name(group_id)

        if group_name == "Error" or group_name == "Facebook":
            self.update_progress("Error getting group name...", error=True)
            ui.groupid_edit.clear()
            return

        # create list item
        item = QTreeWidgetItem(ui.groups_list)
        item.setCheckState(0, Qt.Checked)
        item.setText(1, group_id)
        item.setText(2, group_name)

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

        # add to file
        with open("groups.txt", "ab") as f:
            f.write(f"{Qt.Checked},{group_id},{group_name}\n".encode("utf-8"))

        self.update_progress(f"Group {group_name} ({group_id}) added.")

    def remove_group(self, item):
        ui.groups_list.takeTopLevelItem(
            ui.groups_list.indexOfTopLevelItem(item))

        group_id = item.text(1)

        # remove from file
        with open("groups.txt", "r+", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                _, group_id, _ = line.strip().split(",")
                if group_id == item.text(1):
                    lines.remove(line)
                    break

            f.seek(0)
            f.truncate()
            f.writelines(lines)

    def add_keyword(self):
        keyword = ui.keyword_edit.text()

        # check if keyword already exists
        for i in range(ui.keywords_list.topLevelItemCount()):
            if ui.keywords_list.topLevelItem(i).text(1) == keyword:
                self.error_dialog("Keyword already exists.")
                ui.keyword_edit.clear()
                return

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

        # add to file
        with open("keywords.txt", "ab") as f:
            f.write(f"{Qt.Checked},{keyword}\n".encode("utf-8"))

        self.update_progress(f"Keyword {keyword} added.")

    def remove_keyword(self, item):
        ui.keywords_list.takeTopLevelItem(
            ui.keywords_list.indexOfTopLevelItem(item))

        keyword = item.text(1)

        # remove from file
        with open("keywords.txt", "r+", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                _, keyword = line.strip().split(",")
                if keyword == item.text(1):
                    lines.remove(line)
                    break

            f.seek(0)
            f.truncate()
            f.writelines(lines)

    def update_progress(self, new_progress, error=False):
        if error:
            self.progress += f"<span style='color:red'>{self.progress_id}. {new_progress}</span><br>"
        else:
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

        # get group ids
        group_ids = []
        for i in range(ui.groups_list.topLevelItemCount()):
            group_ids.append(ui.groups_list.topLevelItem(i).text(1))

        # get keywords
        keywords = []
        for i in range(ui.keywords_list.topLevelItemCount()):
            keywords.append(ui.keywords_list.topLevelItem(i).text(1))

        print("from lists:", group_ids, keywords)

        scraper = GroupsScraper(email,
                                password,
                                group_ids,
                                keywords)

        # connect the scraping complete signal to the set_scraping_result function,
        # so when the scraping is done, a signal will be emitted, and the function will be called
        scraper.scrape_complete_sig.connect(self.set_scraping_result)

        try:
            scraper.start()
        except LoginError as e:
            # error_dialog(str(e))
            self.update_progress(f"Login error: {e}", error=True)

    # this function is being called once the scraping is done
    def set_scraping_result(self, result):
        self.update_progress("Scraping done, outputing to file...")

        try:
            HtmlGenerator(result).generate_html()
            self.update_progress("Posts file generated in web folder.")
        except Exception as e:
            self.update_progress(f"Error: {e}", error=True)

        ui.start_btn.setEnabled(True)

    def error_dialog(self, message, title="Error"):
        error_icon = QPixmap("./icons/error.png")
        error_icon = error_icon.scaled(QSize(24, 24))

        msg = QMessageBox()
        msg.setIconPixmap(error_icon)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    # load login info from file
    def load_credentials(self):
        # check if credentials file exists
        if os.path.exists("credentials.txt"):
            # load credentials from file
            with open("credentials.txt", "r") as f:
                lines = f.readlines()
                ui.email_edit.setText(lines[0].strip())
                ui.password_edit.setText(lines[1].strip())

    # load already existing groups from groups.txt
    def load_groups(self):
        if os.path.exists("groups.txt"):
            with open("groups.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    checked_state, group_id, group_name = line.strip().split(",")
                    item = QTreeWidgetItem(ui.groups_list)
                    item.setCheckState(0, int(checked_state))
                    item.setText(1, group_id)
                    item.setText(2, group_name)

                    # remove button (icon)
                    remove_btn = QPushButton(parent=ui.groups_list)
                    remove_btn.setFixedSize(QSize(20, 20))
                    remove_btn.setIcon(QApplication.style().standardIcon(
                        QStyle.SP_DialogCloseButton))
                    remove_btn.clicked.connect(lambda: self.remove_group(item))

                    ui.groups_list.setItemWidget(item, 3, remove_btn)

    # load already existing keywords from keywords.txt
    def load_keywords(self):
        if os.path.exists("keywords.txt"):
            with open("keywords.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    checked_state, keyword = line.strip().split(",")
                    item = QTreeWidgetItem(ui.keywords_list)
                    item.setCheckState(0, int(checked_state))
                    item.setText(1, keyword)

                    # remove button (icon)
                    remove_btn = QPushButton(parent=ui.keywords_list)
                    remove_btn.setFixedSize(QSize(20, 20))
                    remove_btn.setIcon(QApplication.style().standardIcon(
                        QStyle.SP_DialogCloseButton))
                    remove_btn.clicked.connect(
                        lambda: self.remove_keyword(item))

                    ui.keywords_list.setItemWidget(item, 2, remove_btn)

    def set_gui(self):
        self.load_credentials()
        self.load_groups()
        self.load_keywords()

        # groups list
        ui.groups_list.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        # keywords list
        ui.keywords_list.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        # connect enter key to adding group/keyword
        ui.groupid_edit.returnPressed.connect(self.add_group)
        ui.keyword_edit.returnPressed.connect(self.add_keyword)

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
