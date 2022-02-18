import os
import sys
import webbrowser
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from gui import Ui_MainWindow
from scraper import GroupsScraper
from facebook_scraper.exceptions import LoginError
from html_generator import *
import utils


class Main:
    log_id = 1
    log = ""
    group_id_name_dict = {}

    def __init__(self, ui):
        self.ui = ui

    # add a group to list, file and dict
    def add_group(self):
        # get group id
        group_id = ui.groupid_edit.text()

        # check if group id is empty
        if group_id == "":
            self.error_dialog("Group ID cannot be empty.")
            ui.groupid_edit.clear()
            return

        # check if group id already exists
        for i in range(ui.groups_list.topLevelItemCount()):
            if ui.groups_list.topLevelItem(i).text(1) == group_id:
                self.error_dialog("Group ID already exists.")
                ui.groupid_edit.clear()
                return

        # get group name
        self.add_to_log(f"Getting {group_id}'s group name...")
        group_name = utils.get_group_name(group_id)
        self.group_id_name_dict[group_id] = group_name

        if group_name == "Error" or group_name == "Facebook":
            self.add_to_log("Error getting group name...", error=True)
            ui.groupid_edit.clear()
            return

        # add list item
        self.add_group_list_item(group_id, group_name)

        # clear line edit
        ui.groupid_edit.clear()

        # add to file
        with open("groups.txt", "ab") as f:
            f.write(f"{Qt.Checked},{group_id},{group_name}\n".encode("utf-8"))

        self.add_to_log(f"Group {group_name} ({group_id}) added.")

    # remove a group from the list, file and dict
    def remove_group(self, item):
        ui.groups_list.takeTopLevelItem(
            ui.groups_list.indexOfTopLevelItem(item))

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

        self.add_to_log(f"Group {item.text(2)} ({item.text(1)}) removed.")

    # save new check state of group to file
    def toggle_group_check(self, item):
        chkbx = ui.groups_list.itemWidget(item, 0)
        new_checked_state = Qt.Checked if chkbx.isChecked() else Qt.Unchecked
        new_chcked_state_str = "Checked" if new_checked_state == Qt.Checked else "Unchecked"

        self.add_to_log(
            f"{new_chcked_state_str} {item.text(2)} ({item.text(1)})")

        # go through the file and change the check state of the item
        with open("groups.txt", "r+", encoding="utf-8") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                _, group_id, group_name = line.strip().split(",")
                if group_id == item.text(1):
                    lines[i] = f"{new_checked_state},{group_id},{group_name}\n"
                    break

            f.seek(0)
            f.truncate()
            f.writelines(lines)

    # add keyword to the list and file
    def add_keyword(self):
        keyword = ui.keyword_edit.text()

        # check if keyword is empty
        if keyword == "":
            self.error_dialog("Keyword cannot be empty.")
            ui.keyword_edit.clear()
            return

        # check if keyword already exists
        for i in range(ui.keywords_list.topLevelItemCount()):
            if ui.keywords_list.topLevelItem(i).text(1) == keyword:
                self.error_dialog("Keyword already exists.")
                ui.keyword_edit.clear()
                return

        self.add_keyword_list_item(keyword)
        ui.keyword_edit.clear()

        # add to file
        with open("keywords.txt", "ab") as f:
            f.write(f"{Qt.Checked},{keyword}\n".encode("utf-8"))

        self.add_to_log(f"Keyword {keyword} added.")

    # remove a keyword from the list and file
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

    # save new check state of keyword to file
    def toggle_keyword_check(self, item):
        chkbx = ui.keywords_list.itemWidget(item, 0)
        new_checked_state = Qt.Checked if chkbx.isChecked() else Qt.Unchecked
        new_chcked_state_str = "Checked" if new_checked_state == Qt.Checked else "Unchecked"

        self.add_to_log(f"{new_chcked_state_str} {item.text(1)} keyword")

        # go through the file and change the check state of the item
        with open("keywords.txt", "r+", encoding="utf-8") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                _, keyword = line.strip().split(",")
                if keyword == item.text(1):
                    lines[i] = f"{new_checked_state},{keyword}\n"
                    break

            f.seek(0)
            f.truncate()
            f.writelines(lines)

    # start the scraping process
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

        self.add_to_log("Starting scraper...")

        email = ui.email_edit.text()
        password = ui.password_edit.text()

        # get checked group ids
        group_ids = []
        for i in range(ui.groups_list.topLevelItemCount()):
            item = ui.groups_list.topLevelItem(i)
            chkbx = ui.groups_list.itemWidget(item, 0)
            if chkbx.isChecked():
                group_ids.append(item.text(1))

        # get checked keywords
        keywords = []
        for i in range(ui.keywords_list.topLevelItemCount()):
            item = ui.keywords_list.topLevelItem(i)
            chkbx = ui.keywords_list.itemWidget(item, 0)
            if chkbx.isChecked():
                keywords.append(item.text(1))

        scraper = GroupsScraper(email,
                                password,
                                group_ids,
                                keywords,
                                self.group_id_name_dict)

        # connect signals from scraper
        scraper.group_scrapeing_started_sig.connect(
            lambda group_name: self.handle_scraping_sig(group_name, 0))
        scraper.group_scrapeing_complete_sig.connect(
            lambda group_name: self.handle_scraping_sig(group_name, 1))
        scraper.scrape_complete_sig.connect(self.handle_scraping_result)

        try:
            scraper.start()
        except LoginError as e:
            # error_dialog(str(e))
            self.add_to_log(f"Login error: {e}", error=True)

    # handle scraping started/complete on group signal
    def handle_scraping_sig(self, group_name, is_complete):
        if is_complete:
            self.add_to_log(f"Complete scraping from {group_name}")
        else:
            self.add_to_log(f"Starting to scrape from {group_name}")

    # this function is being called once the scraping is done
    # (by a signal emitted from scraper.py)
    def handle_scraping_result(self, result):
        self.add_to_log("Scraping done, outputing to file...")

        try:
            output_file_name = generate_html(result)
            self.add_to_log("Posts file generated in output folder.")
            if ui.show_result_on_finish_chkbx.isChecked():
                path = os.path.join(os.getcwd(), "output", output_file_name)
                webbrowser.open("file:///" + path, new=0, autoraise=True)
        except Exception as e:
            print(e)
            self.add_to_log(f"Error: {e}", error=True)

        ui.start_btn.setEnabled(True)

    # update the log text block
    # appends new_log to existing one
    # use error=True for red text
    def add_to_log(self, new_log, error=False):
        if error:
            self.log += f"<span style='color:red'>{self.log_id}. {new_log}</span><br>"
        else:
            self.log += f"{self.log_id}. {new_log}<br>"

        ui.log_edit.setText(self.log)
        # scroll down
        ui.log_edit.verticalScrollBar().setValue(
            ui.log_edit.verticalScrollBar().maximum())

        # update gui immediately
        QApplication.processEvents()

        self.log_id += 1

    # pop up error dialog with no sound
    def error_dialog(self, message, title="Error"):
        error_icon = QPixmap("./icons/error.png")
        error_icon = error_icon.scaled(QSize(24, 24))

        msg = QMessageBox()
        msg.setWindowIcon(QIcon(error_icon))
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

    def add_group_list_item(self, group_id, group_name, checked_state=Qt.Checked):
        item = QTreeWidgetItem(ui.groups_list)

        # use checkbox
        use_chkbx = QCheckBox(parent=ui.groups_list)
        use_chkbx.setChecked(int(checked_state))
        use_chkbx.stateChanged.connect(lambda: self.toggle_group_check(item))
        ui.groups_list.setItemWidget(item, 0, use_chkbx)

        # group id and name
        item.setText(1, group_id)
        item.setText(2, group_name)

        # remove button (icon)
        remove_btn = QPushButton(parent=ui.groups_list)
        remove_btn.setFixedSize(QSize(20, 20))
        remove_btn.setIcon(QApplication.style().standardIcon(
            QStyle.SP_DialogCloseButton))
        remove_btn.clicked.connect(lambda: self.remove_group(item))
        ui.groups_list.setItemWidget(item, 3, remove_btn)

        # add item to tree and dictionary
        ui.groups_list.addTopLevelItems([item])
        self.group_id_name_dict[group_id] = group_name

    def add_keyword_list_item(self, keyword, checked_state=Qt.Checked):
        item = QTreeWidgetItem(ui.keywords_list)

        # use checkbox
        use_chkbx = QCheckBox(parent=ui.keywords_list)
        use_chkbx.setChecked(int(checked_state))
        use_chkbx.stateChanged.connect(lambda: self.toggle_keyword_check(item))
        ui.keywords_list.setItemWidget(item, 0, use_chkbx)

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

    # load already existing groups from groups.txt
    def load_groups(self):
        if os.path.exists("groups.txt"):
            with open("groups.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    checked_state, group_id, group_name = line.strip().split(",")
                    self.add_group_list_item(
                        group_id, group_name, checked_state)

    # load already existing keywords from keywords.txt
    def load_keywords(self):
        if os.path.exists("keywords.txt"):
            with open("keywords.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    checked_state, keyword = line.strip().split(",")
                    self.add_keyword_list_item(keyword, checked_state)

    # set all nessecary GUI things
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

    # set button listeners etc
    def set_listeners(self):
        ui.start_btn.clicked.connect(self.start_scraping)
        ui.add_group_btn.clicked.connect(self.add_group)
        ui.add_keyword_btn.clicked.connect(self.add_keyword)


# main function
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
