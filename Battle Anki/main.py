#                     Copyright © 2020 Joseph Policarpio

#     Battle Anki, an addon for Anki, a program for studying flash cards.

#     This file is part of Battle Anki
#
#     Battle Anki is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License (AGPL)
#     version 3 of the License, as published by the Free Software Foundation.
#                               AGPL-3.0-only.
#
#     Battle Anki is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.


from PyQt5 import QtCore, QtGui, QtWidgets
from aqt import mw, gui_hooks
from aqt.qt import *
from anki.consts import *
from anki.lang import _
from aqt.utils import *
import json
import threading
import concurrent.futures
from anki import hooks
import socket
import select
import time
import sys

from .BAmainwin import *
from .battle_conf import *
from .ask_BD import *
from .reb_comms import *
from .ty import *
import os
import shutil

config = mw.addonManager.getConfig(__name__)
use_deck = str(config['use_deck'])
port = int(config['server_port'])
server = str(config['server_ip_address'])
password = str(config['server_password'])
config['Your Anki Version'] = anki.buildinfo.version

ba_ver = "1.20"

config['Your Battle Anki version'] = ba_ver
mw.addonManager.writeConfig(__name__, config)

decksize = 0
matched_box = False
new_box = False
learn_box = False
mature_box = False
resched_box = False
today_only = False

can_sendittt = False
popped_req = False
popped_comms = False
accepted_req = False
inbattle = False
ready_for_request = True
window_open = False
invite_timed_out = False

requester = str()
terms_of_battle = str()
matched_list = list()
matched_terms = str()
matched_size = int()
challenger_name = str()
requesters_cards = list()
loc_rem_ip = None
myprogress = 0
challenger_ip = None
challenger_progress = 0
startup = True
shutdown = False
will_sync = False
mw.is_connected = False

local_data = {'ver': ba_ver,
              'card ids': [{}],
              'matched terms': str(),
              'matched size': int(),
              'user info': {'name': str(mw.pm.name),
                            'Connected': mw.is_connected,
                            'in battle?': inbattle,
                            'Remote IP': loc_rem_ip,
                            'accepted req': accepted_req,
                            'progress': myprogress},
              'request options': {'req name': '',
                                  'req Remote IP': str()}}

n = int()
server_data = {'clients connected': []}

header = 32
msg_format = 'utf-8'
disconn_msg = 'Disconnected'
print(f"""[SERVER IP] {server} on port {port}""")
threadlocker = threading.Lock()


class MainWindow:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_win = QMainWindow()
        self.main_win.hide()
        self.ui = Ui_BatMainWin()
        self.ui.setupUi(self.main_win)
        self.main_win.closeEvent = self.closeEvent

        # center main_win
        qtRectangle = self.main_win.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.main_win.move(qtRectangle.topLeft())

        self.ui.stackedWidget.setCurrentWidget(self.ui.page_1)
        self.ui.page_2.hide()
        self.ui.page_3.hide()
        self.ui.tableWidget_users_connected.setHorizontalHeaderItem(0, QTableWidgetItem("Name"))
        self.ui.tableWidget_users_connected.setHorizontalHeaderItem(1, QTableWidgetItem("In Battle?"))
        self.ui.tableWidget_users_connected.setHorizontalHeaderItem(2, QTableWidgetItem("Remote IP"))
        self.ui.tableWidget_users_connected.setColumnWidth(0, 135)
        self.ui.tableWidget_users_connected.setColumnWidth(1, 62)
        self.ui.tableWidget_users_connected.setColumnWidth(2, 1)
        self.ui.tableWidget_users_connected.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.ui.tableWidget_users_connected.setStyleSheet("QHeaderView::section{font-size: 12 pt; "
                                                          "Background-color:rgb(182,182,182);}")
        self.ui.tableWidget_users_connected.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.tableWidget_users_connected.setSelectionMode(QtWidgets.QAbstractItemView. SingleSelection)

        self.ui.progressBar_waiting.setStyleSheet("QProgressBar::chunk{background: QLinearGradient(x1: 0, y1: 0, x2: 1,"
                                                  " y2: 0, stop: 0 rgb(147, 34, 245), stop: 0.5 rgb(211, 90, 219),"
                                                  " stop: 1 rgb(245, 220, 34));}"
                                                  "QProgressBar{border:1px solid black;border-radius:4px;color:black;}")
        self.ui.progressBar_loading.setStyleSheet("QProgressBar::chunk{background:QLinearGradient(x1:0,y1:0,x2:1,"
                                                  "y2:0,stop: 0 rgb(167,167,167), stop: 0.9 rgb(30, 152, 235), stop: 1"
                                                  " rgb(0, 132, 221));}QProgressBar{border: 1px solid black; "
                                                  "border-radius: 3px; color: black;}")
        self.ui.lab_batform_connected.hide()
        self.ui.lab_batform_connected.setStyleSheet("color: rgb(27, 135, 7)")

        self.ui.progressBar_p1.valueChanged.connect(self.ss_p1)
        self.ui.progressBar_p2.valueChanged.connect(self.ss_p2)

        self.ui.but_sendittt.clicked.connect(lambda: sendittt())

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: running())
        self.timer.timeout.connect(self.hb)

        self.timer_bar = QTimer()
        self.timer_bar.timeout.connect(self.updateWaitingBar)
        self.step = 0

        self.timer_load = QTimer()
        self.timer_load.timeout.connect(self.updateLoadBar)
        self.step_load = 0

        self.timer_undo_accepted = QTimer()
        self.timer_undo_accepted.timeout.connect(self.undoaccept)

        self.timer_undo_request = QTimer()
        self.timer_undo_request.timeout.connect(self.undorequest)

        self.timer_undo_rejected = QTimer()
        self.timer_undo_rejected.timeout.connect(lambda: undo_rejected())

        self.timer_denied = QTimer()
        self.timer_denied.timeout.connect(lambda: req_was_denied())

        self.timer_hb = QTimer()
        self.timer_hb.timeout.connect(self.hb_dias)

        self.timer_reset = QTimer()
        self.timer_reset.timeout.connect(self.reset)

        end_dest = os.path.join(os.getcwd(), 'battle_anki_icon.png')

        if os.path.isfile(f'{end_dest}') is False:
            back_len_join = len(os.path.join(mw.pm.name, 'collection.media'))
            # dirlen = len(f'{mw.pm.name}/collection.media')
            com_root = os.getcwd()[:-back_len_join]
            source_fold = os.path.join(com_root, 'addons21', 'Battle Anki', 'res')
            # source = f'{os.getcwd()[:-dirlen]}addons21/Battle_Anki_beta/res/battle_anki_icon.png'
            source = os.path.join(source_fold, 'battle_anki_icon.png')
            dest = f'{os.getcwd()}'
            shutil.move(source, dest)
            # source = f'{os.getcwd()[:-dirlen]}addons21/Battle_Anki_beta/res'
            # dest = f'{os.getcwd()}/battle_anki_icon.png'
            shutil.copy(end_dest, source_fold)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("battle_anki_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.main_win.setWindowIcon(icon)
        self.BA_logo = QPixmap("battle_anki_icon.png")
        self.ui.lab_BA_logo.setScaledContents(True)
        self.ui.lab_BA_logo.setPixmap(self.BA_logo)

        self.reset_progBar_styles()

    def reset_progBar_styles(self):
        self.ui.progressBar_p1.setStyleSheet("QProgressBar::chunk"
                                             "{"
                                             "border: 1px solid rgb(31, 68, 125);"
                                             "border-style: outset;"
                                             "border-top-left-radius: 24px;"
                                             "border-bottom-left-radius: 24px;"
                                             "background: QLinearGradient( x1: 0.4, y1: 0,"
                                             " x2: 0, y2: 1,"
                                             " stop: 0 rgb(31, 68, 125),"
                                             " stop: 1 rgb(118, 118, 118));"
                                             "}"
                                             "QProgressBar"
                                             "{"
                                             "border: 2px solid rgb(26, 51, 89);"
                                             "border-style: inset;"
                                             "border-radius: 24px;"
                                             "background: QLinearGradient( x1: 0, y1: 0,"
                                             " x2: 0.6, y2: 1,"
                                             " stop: 0 rgb(83, 83, 89),"
                                             " stop: 1 rgb(184, 184, 184));"
                                             "color: rgb(232, 74, 39);"
                                             "}")
        self.ui.progressBar_p2.setStyleSheet("QProgressBar::chunk"
                                             "{"
                                             "border: 1px solid rgb(237, 78, 43);"
                                             "border-style: outset;"
                                             "border-top-left-radius: 24px;"
                                             "border-bottom-left-radius: 24px;"
                                             "background: QLinearGradient( x1: 0.4, y1: 0,"
                                             " x2: 0, y2: 1,"
                                             " stop: 0 rgb(237, 78, 43),"
                                             " stop: 1 rgb(38, 89, 166));"
                                             "}"
                                             "QProgressBar"
                                             "{"
                                             "border: 2px solid rgb(240, 106, 77);"
                                             "border-style: inset;"
                                             "border-radius: 24px;"
                                             "background: QLinearGradient( x1: 0, y1: 0,"
                                             " x2: 0.9, y2: 1,"
                                             " stop: 0 rgb(176, 23, 40),"
                                             " stop: 1 rgb(237, 78, 43));"
                                             "color: rgb(22, 56, 110);"
                                             "}")

    def undorequest(self):
        global local_data
        global accepted_req
        global matched_terms
        accepted_req = False
        matched_terms = ''
        local_data['matched terms'] = ''
        local_data['request options'] = {'req name': '',
                                         'req Remote IP': str()}
        local_data['card ids'] = [{}]
        self.timer_undo_request.stop()

    def undoaccept(self):
        global accepted_req
        global matched_terms
        accepted_req = False
        matched_terms = ''
        local_data['matched terms'] = ''
        self.timer_undo_accepted.stop()

    def reset(self):
        global local_data
        global matched_list
        global inbattle
        global decksize
        global ready_for_request
        global matched_size
        # global card_ids
        global matched_terms
        global window_open
        global myprogress
        global popped_req
        global popped_comms
        delete_battle_decks()
        self.reset_progBar_styles()
        inbattle = False
        window_open = False
        matched_terms = str()
        matched_list = []
        matched_size = 0
        myprogress = 0
        local_data['request options'] = {'req name': '',
                                         'req Remote IP': str()}
        decksize = 0
        ready_for_request = True
        popped_comms = False
        popped_req = False
        self.ui.progressBar_loading.hide()
        self.main_win.show()

    def updateBattleBars(self):
        global local_data
        global server_data
        global myprogress
        global challenger_progress
        global decksize
        global challenger_ip
        global dyn_id
        global challenger_name
        if inbattle:
            cidss = mw.col.decks.cids(dyn_id)
            lencids = len(cidss)
            myprogress = int((1 - (lencids / decksize)) * 100)
            if server_data['clients connected']:
                if server_data['clients connected'][0]['user info']['Remote IP'] and challenger_ip:
                    for i in range(0, len(server_data['clients connected'])):
                        if server_data['clients connected'][i]['user info']['Remote IP']:
                            chick_ip = str(server_data['clients connected'][i]['user info']['Remote IP'])
                            if chick_ip == challenger_ip:
                                if challenger_progress != 100:
                                    challenger_progress = server_data['clients connected'][i]['user info']['progress']
                                break
            self.ui.progressBar_p1.setFormat(f"{mw.pm.name}   {myprogress}%")
            self.ui.progressBar_p2.setFormat(f"{challenger_name}   {challenger_progress}%")
            if myprogress >= 100:
                get_local_data()
                send_pulse()
                self.ui.progressBar_p1.setValue(myprogress)
                self.ui.progressBar_p1.update()
                if challenger_progress >= 100:
                    showInfo("Keep up the good work!\nBetter luck next time!")
                if challenger_progress < 100:
                    showInfo("Nice work! You are almost an AnKing!")
                self.reset()
                self.showHome()
            elif myprogress < 7:
                self.ui.progressBar_p1.setValue(7)
                self.ui.progressBar_p1.update()
            elif 7 <= myprogress < 100:
                self.ui.progressBar_p1.setValue(myprogress)
                self.ui.progressBar_p1.update()
            if challenger_progress < 7:
                self.ui.progressBar_p2.setValue(7)
                self.ui.progressBar_p2.update()
            elif challenger_progress >= 7:
                self.ui.progressBar_p2.setValue(challenger_progress)
                self.ui.progressBar_p2.update()

    def updateLoadBar(self):
        if self.step_load <= 90:
            self.step_load += 1
            self.main_win.setDisabled(True)
            if not self.ui.progressBar_loading.isVisible():
                self.ui.progressBar_loading.show()
        else:
            self.main_win.setDisabled(False)
            self.timer_load.stop()
            self.ui.progressBar_loading.hide()
            self.ui.lab_batform_connected.show()
        self.ui.progressBar_loading.setValue(self.step_load * (100/90))
        self.ui.progressBar_loading.update()

    def updateWaitingBar(self):
        if self.step <= 180:
            self.step += 1
        else:
            self.step = 0
        self.ui.progressBar_waiting.setValue(self.step * (100/180))
        self.ui.progressBar_waiting.update()

    def show(self):
        self.main_win.show()

    def showBattle(self):
        global myprogress
        global challenger_progress
        global inbattle

        self.ui.stackedWidget.setCurrentWidget(self.ui.page_3)

        self.ui.progressBar_p1.setFormat(f"{mw.pm.name}   {myprogress}%")
        self.ui.progressBar_p2.setFormat(f"{challenger_name}   {challenger_progress}%")

        myprogress = 0
        challenger_progress = 0

        self.ui.page_3.show()
        self.ui.page_2.hide()
        self.ui.page_1.hide()
        self.ui.page_3.setFocus()

        self.timer_bar.stop()
        inbattle = True

        self.ui.progressBar_p1.setValue(7)
        self.ui.progressBar_p2.setValue(7)

        if not self.main_win.isVisible():
            self.main_win.show()

    def closeEvent(self, event):
        try:
            if not shutdown:
                self.reset()
                mw.tybox = QDialog()
                mw.tybox = TY()
                mw.tybox.show()
        finally:
            return

    def close_all(self):
        try:
            bye_to_server()
            self.main_win.close()
        except:
            pass
        finally:
            return

    def update_boxes(self):
        global local_data
        global matched_box
        global new_box
        global learn_box
        global mature_box
        global resched_box
        global today_only
        global decksize
        global requester
        try:
            decksize = self.ui.spinbox_bdecksize.value()
            if self.ui.checkBox_match_q.isChecked():
                matched_box = True
            else:
                matched_box = False
            if self.ui.checkBox_card_new.isChecked():
                new_box = True
            else:
                new_box = False
            if self.ui.checkBox_card_learn.isChecked():
                learn_box = True
            else:
                learn_box = False
            if self.ui.checkBox_card_mature.isChecked():
                mature_box = True
            else:
                mature_box = False
            if self.ui.checkBox_apply_resched.isChecked():
                resched_box = True
            else:
                resched_box = False
            if self.ui.checkBox_todayonly.isChecked():
                today_only = True
            else:
                today_only = False
            if self.ui.checkBox_newANDreview.isChecked():
                new_box = False
                learn_box = False
                local_data['request options']['both box'] = True
            else:
                local_data['request options']['both box'] = False
            local_data['request options']['deck size'] = decksize
            local_data['request options']['matched box'] = matched_box
            local_data['request options']['new box'] = new_box
            local_data['request options']['learn box'] = learn_box
            local_data['request options']['mature box'] = mature_box
            local_data['request options']['resched box'] = resched_box
            local_data['request options']['due box'] = today_only
            local_data['request options']['requester'] = str(mw.pm.name)
        except Exception as err:
            showInfo(f'There was a problem...'
                     f'Sorry!'
                     f'EC 400m')
            self.timer.stop()

    # from local window
    def get_request_data(self):
        global local_data
        global can_sendittt
        global challenger_ip
        global challenger_name
        self.update_boxes()
        can_sendittt = False
        if new_box and mature_box:
            can_sendittt = False
            showInfo("New cards can't be mature...\n"
                     "you haven't done them yet!")
            return False
        if new_box and today_only:
            can_sendittt = False
            showInfo("New cards can't be due today...\n"
                     "you haven't done them yet!")
            return False
        if decksize != 0:
            if new_box or learn_box or mature_box or self.ui.checkBox_newANDreview.isChecked():
                if self.ui.tableWidget_users_connected.selectedItems() is not None:
                    try:
                        self.ui.tableWidget_users_connected.setSortingEnabled(False)
                        challenger_name = str(self.ui.tableWidget_users_connected.selectedItems()[0].text())
                        if str(self.ui.tableWidget_users_connected.selectedItems()[1].text()) == 'False':
                            # check to make sure not self...
                            mystr = self.ui.tableWidget_users_connected.selectedItems()[2].text()
                            myip = str(mystr.split(',')[0])[2:-1]
                            myport = int(mystr.split(',')[1][1:-1])
                            if str(mw.pm.name) != challenger_name and loc_rem_ip != str(f"('{myip}', {myport})"):
                                local_data['request options']['req name'] = challenger_name
                                local_data['request options']['req in battle?'] = str(
                                    self.ui.tableWidget_users_connected.selectedItems()[1].text())
                                challenger_ip = str(f"('{myip}', {myport})")
                                local_data['request options']['req Remote IP'] = challenger_ip
                                can_sendittt = True
                                return True
                            else:
                                can_sendittt = False
                                challenger_name = ''
                                showInfo(f"As fun as it sounds, you can't\n"
                                         f"battle yourself on Battle Anki...")
                                return False

                        else:
                            can_sendittt = False
                            showInfo(f"Sorry... {challenger_name} is \n"
                                     f"currently in battle!")
                            return False

                    except Exception:
                        showInfo(f"Sorry, there was a problem...\n"
                                 f"you'll have to restart Anki to be able to play.\n"
                                 f"EC 445")
                        return False

                    finally:
                        self.ui.tableWidget_users_connected.setSortingEnabled(True)
                else:
                    can_sendittt = False
                    showInfo("You need to choose someone to invite!")
                    return False

            else:
                can_sendittt = False
                showInfo("You need to choose the type of cards!")
                return False

        else:
            can_sendittt = False
            showInfo("You need to choose the number of cards!")
            return False

    def showWait(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_2)
        self.ui.page_2.show()
        self.ui.page_1.hide()
        self.ui.page_2.setFocus()

    def startWaitingBar(self):
        self.step = 0
        self.timer_bar.start(50)

    def refresh_users(self):
        try:
            selected_ip = str()
            self.ui.tableWidget_users_connected.setSortingEnabled(False)
            if self.ui.tableWidget_users_connected.selectedItems():
                selected_list = self.ui.tableWidget_users_connected.selectedItems()
                selected_ip = str(QTableWidgetItem(selected_list[2]).text())
            # update the contents
            self.ui.tableWidget_users_connected.clearContents()
            self.ui.tableWidget_users_connected.setRowCount(len(server_data['clients connected']))
            for i in range(0, len(server_data['clients connected'])):
                self.ui.tableWidget_users_connected.setItem(i, 0, QTableWidgetItem(
                    str(server_data['clients connected'][i]['user info']['name'])))
                self.ui.tableWidget_users_connected.setItem(i, 1, QTableWidgetItem(
                    str(server_data['clients connected'][i]['user info']['in battle?'])))
                self.ui.tableWidget_users_connected.setItem(i, 2, QTableWidgetItem(
                    str(server_data['clients connected'][i]['user info']['Remote IP'])))
            if selected_ip:
                for z in range(0, len(server_data['clients connected'])):
                    servip = str(server_data['clients connected'][z]['user info']["Remote IP"])
                    if servip == selected_ip:
                        self.ui.tableWidget_users_connected.selectRow(z)
            self.ui.tableWidget_users_connected.setSortingEnabled(True)
            self.ui.tableWidget_users_connected.update()
        except Exception:
            showInfo(f'Sorry, there was a problem with Battle Anki...\n'
                     f'EC 478')
            mw.battle_window.timer.stop()
            self.main_win.close()

    def showHome(self):
        global popped_comms
        popped_comms = False
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_1)
        self.main_win.show()
        self.ui.page_1.show()
        self.ui.page_1.setFocus()

    def startLoadBar(self):
        self.ui.progressBar_loading.setFormat(f'Loading... %p%')
        self.step_load = 0
        self.timer_load.start(50)

    def hb(self):
        self.main_win.setWindowTitle('Battle Ankı')
        self.timer_hb.start(700)

    def hb_dias(self):
        self.main_win.setWindowTitle('Battle Anki')

    def ss_p1(self):
        if self.ui.progressBar_p1.value() >= 95:
            self.ui.progressBar_p1.setStyleSheet("QProgressBar::chunk"
                                                 "{"
                                                 "border: 1px solid rgb(31, 68, 125);"
                                                 "border-style: outset;"
                                                 "border-radius: 24px;"
                                                 "background: QLinearGradient( x1: 0.4, y1: 0,"
                                                 " x2: 0, y2: 1,"
                                                 " stop: 0 rgb(31, 68, 125),"
                                                 " stop: 1 rgb(118, 118, 118));"
                                                 "}"
                                                 "QProgressBar"
                                                 "{"
                                                 "border: 2px solid rgb(26, 51, 89);"
                                                 "border-style: inset;"
                                                 "border-radius: 24px;"
                                                 "background: QLinearGradient( x1: 0, y1: 0,"
                                                 " x2: 0.6, y2: 1,"
                                                 " stop: 0 rgb(83, 83, 89),"
                                                 " stop: 1 rgb(184, 184, 184));"
                                                 "color: rgb(232, 74, 39);"
                                                 "}")

    def ss_p2(self):
        if self.ui.progressBar_p2.value() >= 95:
            self.ui.progressBar_p2.setStyleSheet("QProgressBar::chunk"
                                                 "{"
                                                 "border: 1px solid rgb(237, 78, 43);"
                                                 "border-style: outset;"
                                                 "border-radius: 24px;"
                                                 "background: QLinearGradient( x1: 0.4, y1: 0,"
                                                 " x2: 0, y2: 1,"
                                                 " stop: 0 rgb(237, 78, 43),"
                                                 " stop: 1 rgb(38, 89, 166));"
                                                 "}"
                                                 "QProgressBar"
                                                 "{"
                                                 "border: 2px solid rgb(240, 106, 77);"
                                                 "border-style: inset;"
                                                 "border-radius: 24px;"
                                                 "background: QLinearGradient( x1: 0, y1: 0,"
                                                 " x2: 0.9, y2: 1,"
                                                 " stop: 0 rgb(176, 23, 40),"
                                                 " stop: 1 rgb(237, 78, 43));"
                                                 "color: rgb(22, 56, 110);"
                                                 "}")


class ConfDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set the form on the new battle window
        self.ui = Ui_bat_conf_Dialog()
        self.ui.setupUi(self)
        self.setModal(True)

        # center it
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.ui.buttonBox_conf_dialog.accepted.connect(lambda: confOK())


class AskDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set the form on the ask window
        self.ui = Ui_AskDialog()
        self.ui.setupUi(self)

        # center it
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.timer_ask = QTimer()
        self.timer_ask.timeout.connect(lambda: auto_timeout_reject())

        # custom callbacks
        self.ui.button_ask_BD.accepted.connect(lambda: accepted())
        self.ui.button_ask_BD.rejected.connect(lambda: rejected())

    def closeEvent(self, event):
        global ready_for_request
        ready_for_request = False
        self.timer_ask.stop()

    def fill_options(self, indict=dict):
        global decksize
        global matched_box
        global new_box
        global learn_box
        global mature_box
        global resched_box
        global today_only
        global requester
        decksize = indict['deck size']
        matched_box = indict['matched box']
        new_box = indict['new box']
        learn_box = indict['learn box']
        mature_box = indict['mature box']
        resched_box = indict['resched box']
        today_only = indict['due box']
        requester = indict['requester']
        req_in_bat = indict['req in battle?']

        if indict['both box']:
            buildstring = f"""{decksize}
{matched_box}
{not new_box}
{not learn_box}
{mature_box}
{resched_box}
{today_only}"""
        else:
            buildstring = f"""{decksize}
{matched_box}
{new_box}
{learn_box}
{mature_box}
{resched_box} 
{today_only}"""
        self.ui.lab_ask_bd_name.setText(str(requester))
        self.ui.lab_ask_bd_options.setText(buildstring)


class RebComms(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set the form on the rebcoms window
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setModal(True)

        # center it
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())


class TY(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set the form on the ty window
        self.ui = Ui_Dialog_ty()
        self.ui.setupUi(self)
        self.setModal(True)

        # center the window
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())


def auto_timeout_reject():
    mw.ask_deck.timer_ask.stop()
    if inbattle is False:
        mw.ask_deck.close()
        mw.battle_window.timer_undo_rejected.start(6*1000)


def check_socks(readables=None, writeables=None, exceptioners=None, tmout: float = 0.0):
    try:
        if readables is None:
            readables = []
        if writeables is None:
            writeables = []
        if exceptioners is None:
            exceptioners = []
        ready_reads, ready_writes, in_errors = select.select(readables, writeables, exceptioners, tmout)
        return [ready_reads, ready_writes, in_errors]
    except:
        showInfo(f'Sorry, there was a problem with Battle Anki...'
                 f'EC 606m')


def receive():
    global server_data
    try:
        while True:
            list_socks_ready = check_socks(readables=[mw.socket], tmout=10.0)
            if len(list_socks_ready[0]) > 0:
                try:
                    full_msg = ''
                    msg_len = int(mw.socket.recv(header))
                    while len(full_msg) < msg_len:
                        chunk = mw.socket.recv(msg_len - len(full_msg))
                        if chunk == b'':
                            break
                        full_msg += chunk.decode(msg_format)
                    if len(full_msg) != msg_len:
                        showInfo(f'Sorry, there was a problem with Battle Anki...'
                                 f'EC 629m')
                    if len(full_msg) == msg_len:
                        try:
                            threadlocker.acquire()
                            server_data = str_to_dict(full_msg)
                        finally:
                            threadlocker.release()
                except:
                    pass
    except Exception as excepti:
        showInfo(f'Sorry, there was a problem with Battle Anki...\n'
                 f'EC 638m')
    finally:
        return


def send_pulse():
    global local_data
    last_send = 0
    try:
        if time.time() - last_send > 2.2:
            last_send = time.time()
            send_str = dict_to_str(local_data)
            msg_whead = f'{len(send_str):<{header}}' + send_str
            msg_send = msg_whead.encode(msg_format)
            ready_to_send = check_socks(writeables=[mw.socket])
            if len(ready_to_send[1]) > 0:
                mw.socket.send(msg_send)
    except:
        showInfo(f'There was a problem...\n'
                 f'Sorry!\n'
                 f'EC 641m')
        mw.battle_window.timer.stop()


def start_client_conn():
    global loc_rem_ip
    try:
        mw.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mw.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096 * 2)
        print('Socket Created')
        global startup
        if startup:
            mw.socket.settimeout(0.3)
            startup = False
        mw.socket.connect((server, port))
        loc_rem_ip = str(mw.socket.getsockname())
        print('Connection initiated with', server)
        mw.is_connected = True
    except socket.error as e:
        showInfo(f"There was a problem starting Battle Anki...\n\n"
                 f"Please check the config options in\n"
                 f"Tools -> Addons -> Battle Anki -> Config\n\n"
                 f"And then restart Anki:\n\n"
                 f"Battle Anki Error Code 937")
        mw.is_connected = False
        mw.battle_window.timer.stop()
        mw.battle_window.timer_bar.stop()
        if mw.battle_window.main_win.isVisible():
            mw.battle_window.main_win.setDisabled(True)


def dict_to_str(in_dict: dict):
    # try:
    out_str = json.dumps(in_dict, indent=2)
    return out_str
    # except json.JSONDecodeError as jsonerr:
    #     showInfo(f'there was a problem dict_to_str\n'
    #              f'{jsonerr}')


def str_to_dict(in_str: str):
    try:
        out_dict = json.loads(in_str)
        return out_dict
    except json.JSONDecodeError as jsonerro:
        showInfo(f'there was a problem\n'
                 f'{jsonerro}'
                 f'str_to_dict\n'
                 f'EC 189m')
    except RecursionError as recur:
        showInfo(f'there was a problem\n'
                 f'{recur}'
                 f'str_to_dict\n'
                 f'EC 195m')


def delete_battle_decks():
    try:
        d = 1
        while mw.col.decks.id_for_name(_("Battle Deck %d") % d):
            the_id = mw.col.decks.id_for_name(_("Battle Deck %d") % d)
            mw.col.sched.emptyDyn(the_id)
            mw.col.decks.rem(the_id)
            d += 1
        mw.moveToState("deckBrowser")
    except:
        pass
    finally:
        return


def requesters_cards_for_matching():
    global local_data
    the_ids = list(mw.col.find_cards(terms_of_battle))
    i = 0
    if len(the_ids) > 0:
        while i < len(the_ids) and i <= 2000:
            id_to_add = int(the_ids[i])
            add = {'id': id_to_add}
            local_data['card ids'].append(add)
            i += 1
    else:
        showWarning(f"Sorry, no cards matched the criteria provided."
                    f"requesters_cards_for_matching"
                    f"EC 719m")


def build_terms_of_battle():
    global new_box
    global learn_box
    global mature_box
    global today_only
    global terms_of_battle
    terms_of_battle = f'deck:"{use_deck}" '
    if new_box:
        terms_of_battle += " is:new"
    if learn_box:
        terms_of_battle += " -is:new"
    if mature_box:
        terms_of_battle += " prop:ivl>21"
    if today_only:
        terms_of_battle += " is:due"


def accepted():
    global accepted_req
    global ready_for_request
    global matched_size
    global dyn_id
    ready_for_request = False
    build_terms_of_battle()
    if matched_box:
        # send applicable cards to server
        build_matched_list()
        if matched_size >= decksize:
            accepted_req = True
            dyn_id = make_battle_deck(matched_terms)
        else:
            showInfo(f'There are not enough cards that match\n'
                     f' the criteria! Try again!\n'
                     f'      Matched cards: {matched_size}'
                     f'Requested deck size: {decksize}')
    elif not matched_box:
        accepted_req = True
        dyn_id = make_battle_deck(terms_of_battle)
    get_local_data()
    mw.battle_window.timer_undo_accepted.start(15*1000)


def rejected():
    global ready_for_request
    ready_for_request = False
    showInfo(f'You are unable to receive requests for 30 seconds...')
    mw.battle_window.timer_undo_rejected.start(30*1000)


def req_was_denied():
    mw.battle_window.timer_denied.stop()
    if inbattle is False:
        global local_data
        global accepted_req
        global matched_terms
        global challenger_name
        global requesters_cards
        global terms_of_battle
        global challenger_ip
        global challenger_progress
        global myprogress
        accepted_req = False
        local_data['card ids'] = [{}]
        challenger_name = str()
        requesters_cards = list()
        terms_of_battle = str()
        challenger_ip = ''
        challenger_progress = 0
        myprogress = 0
        get_local_data()
        send_pulse()
        mw.battle_window.reset()
        mw.battle_window.undorequest()
        mw.battle_window.timer_bar.stop()
        mw.battle_window.showHome()
        showInfo(f"Sorry, looks like they can't play right now...\n"
                 f"Maybe you are too strong of an AnKing?")


def undo_rejected():
    global popped_req
    global ready_for_request
    popped_req = False
    ready_for_request = True
    global challenger_name
    global requesters_cards
    global challenger_ip
    global challenger_progress
    challenger_name = str()
    requesters_cards = list()
    challenger_ip = None
    challenger_progress = 0
    mw.battle_window.timer_undo_rejected.stop()


def latestart():
    global challenger_name
    global challenger_ip
    global server_data
    global local_data
    global dyn_id
    if matched_box is False:
        dyn_id = make_battle_deck(terms_of_battle)
    elif matched_box is True:
        dyn_id = make_battle_deck(matched_terms)
    mw.battle_window.timer_undo_request.start(15*1000)


def check_if_req_accepted():
    global matched_list
    global decksize
    global challenger_name
    global challenger_ip
    global server_data
    global local_data
    global popped_comms
    global matched_terms
    # try:
    if len(local_data['request options']['req Remote IP']) > 0:
        req_ip = str(local_data['request options']['req Remote IP'])
        for i in range(0, len(server_data['clients connected'])):
            if server_data['clients connected'][i]['user info']['Remote IP']:
                chck_ip = str(server_data['clients connected'][i]['user info']['Remote IP'])
                if req_ip == chck_ip:
                    # challenger name and IP pulled from qtablewidget when sent request
                    if server_data['clients connected'][i]['user info']['accepted req'] is True:
                        if matched_box is True:
                            matched_terms = server_data['clients connected'][i]['matched terms']
                        if popped_comms is False:
                            popped_comms = True
                            global challenger_progress
                            challenger_progress = 0
                            mw.comms = QDialog()
                            mw.comms = RebComms()
                            mw.comms.show()
                            latestart()
                            mw.battle_window.ui.progressBar_waiting.reset()
                        return


def check_for_requests():
    global popped_req
    global challenger_name
    global challenger_ip
    global server_data
    global local_data
    global requesters_cards
    global ready_for_request
    if popped_req is False and ready_for_request is True:
        if local_data['user info']['in battle?'] is False:
            if len(server_data['clients connected']) > 1:
                for rd in server_data['clients connected']:
                    if len(rd['request options']['req Remote IP']) > 0:
                        check_ip = str(rd['request options']['req Remote IP'])
                        if local_data['user info']['Remote IP']:
                            local_ip = str(local_data['user info']['Remote IP'])
                            if local_ip == check_ip:
                                mw.ask_deck = QDialog()
                                mw.ask_deck = AskDialog()
                                mw.ask_deck.fill_options(rd['request options'])
                                popped_req = True
                                ready_for_request = False
                                requesters_cards = list(rd['card ids'])
                                challenger_name = str(rd['user info']['name'])
                                challenger_ip = str(rd['user info']['Remote IP'])
                                global challenger_progress
                                challenger_progress = 0
                                mw.ask_deck.timer_ask.start(26*1000)
                                mw.ask_deck.show()
                                break


def confOK():
    if mw.battle_window.get_request_data():
        mw.battle_window.startWaitingBar()
        build_terms_of_battle()
        if matched_box is True:
            requesters_cards_for_matching()
        get_local_data()
        if can_sendittt is True:
            mw.battle_window.showWait()
            mw.battle_window.timer_denied.start(30*1000)


def sendittt():
    # try:
    mw.confpopup = QDialog()
    mw.confpopup = ConfDialog()
    mw.confpopup.show()
    # except:
    #     showInfo("something went wrong...")


def get_local_data():
    global local_data
    global server_data
    global loc_rem_ip
    global inbattle
    global accepted_req
    global myprogress
    global matched_size
    global window_open
    local_data['matched size'] = matched_size
    local_data['matched terms'] = matched_terms
    local_data['window open'] = window_open
    local_data['user info']['Connected'] = mw.is_connected
    local_data['user info']['in battle?'] = inbattle
    local_data['user info']['accepted req'] = accepted_req
    local_data['user info']['progress'] = myprogress
    local_data['user info']['Remote IP'] = loc_rem_ip
    local_data['user info']['name'] = str(mw.pm.name)


def running():
    global window_open
    global ready_for_request
    global popped_req
    try:
        if mw.battle_window.main_win.isVisible():
            window_open = True
        if mw.is_connected:
            get_local_data()
            send_pulse()
            mw.battle_window.refresh_users()
            if inbattle is False:
                check_if_req_accepted()
                if ready_for_request is True:
                    check_for_requests()
            if inbattle is True:
                mw.battle_window.updateBattleBars()
    except Exception:
        mw.battle_window.timer.stop()
        if mw.battle_window.main_win.isVisible():
            mw.battle_window.main_win.setDisabled(True)


def battle_connect():
    global window_open
    try:
        mw.battle_window.showHome()
        mw.battle_window.startLoadBar()
        if mw.is_connected is False:
            start_client_conn()
        if 'utd_ver' in server_data.keys():
            running()
            mw.battle_window.timer.start(2500)
            if server_data['utd_ver'] is not None:
                if int(str(local_data['ver'])[-2:]) < int(str(server_data['utd_ver'])[-2:]):
                    utd_ver = str(server_data['utd_ver'])
                    showInfo(f'A Battle Anki upgrade is available!\n\n'
                             f'     The most current version is:\n'
                             f'         {utd_ver}\n\n'
                             f'     Your version is:\n'
                             f'         {ba_ver}\n\n')
    except Exception:
        showInfo(f"There was a problem starting Battle Anki...\n\n"
                 f"Please check the config options in\n"
                 f"Tools -> Addons -> Battle Anki -> Config\n"
                 f"If problems persist, please report:\n\n"
                 f"Battle Anki Error Code 1282")
        mw.battle_window.timer.stop()
        if mw.battle_window.main_win.isVisible():
            mw.battle_window.main_win.setDisabled(True)


def ba_startup():
    mw.battle_window = MainWindow()
    try:
        start_client_conn()
        running()
        mw.battle_window.timer.start(2500)
        r_th = threading.Thread(target=receive, daemon=True)
        r_th.start()
    except socket.error:
        showInfo(f"There was a problem starting Battle Anki... Sorry!\n\n"
                 f"Please remember this code:\n"
                 f"Error Code 1208")
        mw.battle_window.timer.stop()


def bye_to_server():
    mw.socket.settimeout(0.0)
    try:
        msg_whead = f'{len(disconn_msg):<{header}}' + disconn_msg
        msg_send = msg_whead.encode(msg_format)
        ready_to_send = check_socks(writeables=[mw.socket])
        if len(ready_to_send[1]) > 0:
            mw.socket.send(msg_send)
    except:
        pass
    finally:
        return


def close_down():
    global shutdown
    shutdown = True
    # need to stop timer for error code above
    try:
        mw.battle_window.timer.stop()
    except:
        showInfo(f'There was a problem closing Battle Anki...\n'
                 f'Sorry!\n'
                 f'EC 1068')
    if will_sync is True:
        try:
            mw.battle_window.close_all()
        finally:
            return
    if will_sync is False:
        try:
            mw.battle_window.close_all()
        finally:
            sys.exit()


def sync_done():
    if shutdown is True:
        sys.exit()


def will_it_sync():
    global will_sync
    will_sync = True


def make_battle_deck(searchterms):
    global matched_list
    global decksize
    global resched_box
    global inbattle
    global n
    import aqt.dyndeckconf
    created_b_deck = False
    n = 1
    deck = mw.col.decks.byName(f"{use_deck}")
    did = mw.col.decks.id_for_name(f"{use_deck}")
    did = int(did)
    mw.col.decks.select(did)
    conf = mw.col.decks.confForDid(did)
    if mw.col.decks.selected() != did:
        mw.col.decks.select(did)
        deck = mw.col.decks.confForDid(did)
        cur = mw.col.decks.current()
        showInfo(f'There may have been a problem creating the deck...\n'
                 f"if something doesn't look right, just delete\n"
                 f"the blue deck named 'Battle Deck 1'")
    elif mw.col.decks.selected() == did:
        deck = mw.col.decks.current()
    else:
        showInfo(f'There was a problem making the deck...\n'
                 f'Sorry!')
    while mw.col.decks.id_for_name(_("Battle Deck %d") % n):
        n += 1
    name = _("Battle Deck %d") % n
    did = mw.col.decks.newDyn(name)
    dyn = mw.col.decks.get(did)
    if resched_box:
        dyn["resched"] = True
    else:
        dyn["resched"] = False

    dyn["delays"] = None
    dyn["terms"] = [[str(searchterms), int(decksize), DYN_DUEPRIORITY]]  # DYN_RANDOM]]
    mw.col.decks.save(dyn)
    created_b_deck = True
    if not mw.col.sched.rebuildDyn():  # dyn["id"]
        delete_battle_decks()
        mw.battle_window.reset()
        return showWarning(_("No cards matched the criteria you provided."))
    mw.moveToState("review")
    mw.battle_window.showBattle()
    return did


def build_matched_list():
    global matched_list
    global decksize
    global matched_size
    global matched_terms
    # try:
    matched_list = []
    # get challenger's applicable cards back and make deck
    card_ids = mw.col.find_cards(terms_of_battle)
    for z in requesters_cards:
        for key, value in z.items():
            if value in card_ids:
                matched_list.append(value)
                if len(matched_list) >= decksize:
                    break
    matched_size = len(matched_list)
    if matched_size > 0:
        matched_terms = str()
        count = 0
        while count <= decksize:
            matched_terms += f" or cid:{matched_list[count]}"
            count += 1
    matched_terms = matched_terms[4:]
    local_data['matched terms'] = matched_terms
    # except:
    #     pass

action = QAction("Battle Anki...", mw)
action.triggered.connect(lambda: battle_connect())
mw.form.menuTools.addAction(action)

gui_hooks._ProfileDidOpenHook().append(ba_startup)
gui_hooks._ProfileWillCloseHook().append(close_down)
gui_hooks._SyncDidFinishHook().append(sync_done)
gui_hooks._SyncWillStartHook().append(will_it_sync)

