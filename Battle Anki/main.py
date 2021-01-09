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


import json
import select
import shutil
import socket
import threading
import time
import sys
import os
import subprocess
import datetime

from PyQt5 import QtCore, QtGui, QtWidgets
from anki.consts import *
from anki.lang import _
from anki.stats import CollectionStats

from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.utils import *

from .myclass import *
from .BAmainwin import *
from .OptDia import *
from .ask_BD import *
from .battle_conf import *
from .reb_comms import *
from .ty import *

ba_ver = "2.17"    # ###########################################################

config_ba = mw.addonManager.getConfig(__name__)
use_deck = str(config_ba['use_deck']).strip()
port = int(config_ba['server_port'])
server = str(config_ba['server_ip_address']).strip()
password = str(config_ba['server_password']).strip()
xtra_search = str(config_ba['Extra Search Criteria']).strip()
config_ba['Your Anki Version'] = anki.buildinfo.version
config_ba['Your Battle Anki version'] = ba_ver
config = config_ba
mw.addonManager.writeConfig(__name__, config)

spinbox_decksize = 100
decksize = 100
matched_box = False
new_box = False
learn_box = True
new_AND_review_box = False
mature_box = False
resched_box = True
today_only = True
joiners_box = True
card_type_str = 'Review'
card_order = int(DYN_DUEPRIORITY)
card_order_str = 'In order of relative overdueness'

can_sendittt = False
popped_req = False
popped_comms = False
accepted_req = False
inbattle = False
inbattle_str = 'Ready'
ready_for_request = True
window_open = False
invite_timed_out = False
isloading = False
badgeview = True

requester = str()
terms_of_battle = str()
matched_list = list()
matched_terms = str()
matched_size = int()
requesters_cards = list()
loc_rem_ip = None
myprogress = 0
challenger_name = list()
challenger_ip = list()
challenger_progress = list()
chal_index = int()
acc_list = list()
conn = list()
startup = True
shutdown = False
will_sync = False
mw.is_connected = False
make_deck_problem = False
opponent_problem = False
made_count = None
tried = int()
told_problem = False
cards_left = 0
cards_today = 0
time_today = '0:00'
mehost = False

one_to_ten = False
ff_ff = False
nty = False

if socket.gethostname() == 'DESKTOP-F1NF0JO':
    mehost = True
else:
    mehost = False

local_data = {'ver': ba_ver,
              'card ids': [{}],
              'matched terms': str(),
              'matched size': int(),
              'user info': {'name': str(mw.pm.name),
                            'Connected': mw.is_connected,
                            'in battle?': inbattle,
                            'Remote IP': loc_rem_ip,
                            'accepted req': accepted_req,
                            'progress': myprogress,
                            'pfrac': [cards_left, decksize],
                            'deck problem': make_deck_problem,
                            'cards today': cards_today,
                            'time today': time_today},
              'request options': {'req name': str(),
                                  'req names': [],
                                  'req Remote IP': str(),
                                  'req Remote IPs': []}}

store_data = {'request options': dict()}
store_data['request options']['both box'] = new_AND_review_box
store_data['request options']['deck size'] = decksize
store_data['request options']['matched box'] = matched_box
store_data['request options']['new box'] = new_box
store_data['request options']['learn box'] = learn_box
store_data['request options']['mature box'] = mature_box
store_data['request options']['resched box'] = resched_box
store_data['request options']['due box'] = today_only
store_data['request options']['requester'] = str(mw.pm.name)

n = int()

server_data = {'clients connected': []}
sd = server_data['clients connected']

readys = {
    'my last bat start': int(),
    'last battle start': [],
    'ips': [],
    'names': [],
    'last status': [],
    'cc': []
}

header = 32
msg_format = 'utf-8'
disconn_msg = 'Disconnected'
print(f"""[SERVER IP] {server} on port {port}""")
threadlocker = threading.Lock()

rejoined = ' rejoined the game!'  # 0
joined = ' joined the game!'  # 1
left = ' left the game...'  # 2
not_here = ' is starting...'  # 3
name_only = ''  # 4
tails = [rejoined, joined, left, not_here, name_only]

bw = object
logger = logging.Logger
logger_ui = logging.Logger
logger_utils = logging.Logger
logger_comms = logging.Logger
logger_user = logging.Logger
BAlog = logging.Handler
formatter = logging.Formatter
log_fold = str()


def start_logger():
    global logger
    global logger_ui
    global logger_utils
    global logger_comms
    global logger_user
    global BAlog
    global formatter
    global log_fold

    log_fold = os.path.join(os.getcwd(), "..", "..", 'addons21', 'BA_logfiles')
    if not os.path.exists(log_fold):
        os.makedirs(log_fold)
    log_nm = 'BA_logfile.log'
    log_path = os.path.join(log_fold, log_nm)

    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    switch_daily_at = datetime.datetime(datetime.datetime.now().year,
                                        datetime.datetime.now().month,
                                        datetime.datetime.now().day,
                                        hour=4, minute=0, fold=1)
    BAlog = logging.handlers.TimedRotatingFileHandler(filename=log_path,
                                                      when='midnight',
                                                      backupCount=14,
                                                      atTime=switch_daily_at)
    formatter = MyFormatter(fmt='%(asctime)-33s %(name)-7s %(levelname)-8s %(message)s',
                            datefmt='%Y/%m/%d  %I:%M:%S.%f %p')
    BAlog.setFormatter(formatter)
    logger.addHandler(BAlog)

    logger_ui = logging.getLogger('BA_UI')
    logger_utils = logging.getLogger('Utils')
    logger_comms = logging.getLogger('Comms')
    logger_user = logging.getLogger('User')

    logger_ui.setLevel(logging.INFO)
    logger_utils.setLevel(logging.INFO)
    logger_comms.setLevel(logging.INFO)
    logger_user.setLevel(logging.INFO)

    s0 = (f'version: {ba_ver}', '', False)
    s1 = ('[Logger Initiated by start_logger()]', '=')
    s2 = (f'Next log file rollover:       '
          f'{str(datetime.datetime.fromtimestamp(BAlog.computeRollover(time.time())))[:-7]}', ' ')
    s3 = ('', '=')
    so = fmt_n_log([s0, s1, s2, s3])
    logger_utils.info(so)
    logger_utils.info(dict_to_str(config_ba))
    return


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

        self.main_win.setFixedSize(self.main_win.size())

        self.ui.stackedWidget.setCurrentWidget(self.ui.page_1)
        self.ui.page_2.hide()
        self.ui.page_3.hide()

        self.ui.label_version.setText(f'v{ba_ver}')
        self.ui.label_version.clicked.connect(lambda: openfolder(log_fold))

        self.update_home_labels()

        self.ui.but_away.clicked.connect(self.set_away)
        self.ui.but_badge.clicked.connect(self.toggle_badges)
        self.ui.but_join.clicked.connect(self.join_battle)
        self.ui.but_sendittt.clicked.connect(lambda: sendittt())

        self.ui.but_options.clicked.connect(lambda: opts_open())

        self.timer = QTimer()  # heartbeat timer
        self.timer.timeout.connect(lambda: running())
        self.timer.timeout.connect(self.hb)

        self.ui.tableWidget_users_connected.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.ui.tableWidget_users_connected.setStyleSheet("QHeaderView::section{font-size: 12 pt; "
                                                          "Background-color:rgb(182,182,182);}")
        self.ui.tableWidget_users_connected.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.tableWidget_users_connected.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.ui.tableWidget_users_connected.horizontalHeader().setVisible(True)

        self.set_badgeview()

        self.ui.progressBar_waiting.setStyleSheet("QProgressBar::chunk{background: QLinearGradient(x1: 0, y1: 0, x2: 1,"
                                                  " y2: 0, stop: 0 rgb(147, 34, 245), stop: 0.5 rgb(211, 90, 219),"
                                                  " stop: 1 rgb(245, 220, 34));}"
                                                  "QProgressBar{border:1px solid black;border-radius:4px;color:black;}")

        self.timer_battle = QTimer()
        self.timer_battle.timeout.connect(self.updateBattleBars)

        self.timer_bar = QTimer()  # waiting after send request
        self.timer_bar.timeout.connect(self.updateWaitingBar)
        self.step = 0

        self.timer_load = QTimer()  # loading on startup timer
        self.timer_load.timeout.connect(self.updateLoadBar)
        self.step_load = 0

        self.timer_undo_accepted = QTimer()  # undoing accepted request, now in battle timer
        self.timer_undo_accepted.timeout.connect(self.undoaccept)

        self.timer_undo_request = QTimer()  # undoing a request, maybe in battle timer
        self.timer_undo_request.timeout.connect(self.undorequest)

        self.timer_undo_rejected = QTimer()  # undoing saying no to a battle timer
        self.timer_undo_rejected.timeout.connect(lambda: undo_rejected())

        self.timer_denied = QTimer()  # my request was denied timer
        self.timer_denied.timeout.connect(lambda: req_was_denied())

        self.timer_joined = QTimer()
        self.timer_joined.timeout.connect(self.undojoin)

        self.timer_hb = QTimer()  # another heartbeat timer
        self.timer_hb.timeout.connect(self.hb_dias)

        self.cards_left = 0

        self.move_resource('battle_anki_icon.png')
        self.move_resource('ba_bronze.png')
        self.move_resource('ba_silver.png')
        self.move_resource('ba_gold.png')
        self.move_resource('ba_black.png')
        self.move_resource('ba_platinum.png')
        self.move_resource('star.png', repl=True)

        self.BA_log = QPixmap("battle_anki_icon.png")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("battle_anki_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        w = 25
        h = 25
        self.sc_7 = self.scale_img('ba_platinum.png', w, h)
        self.sc_6 = self.scale_img('ba_black.png', w, h)
        self.sc_5 = self.scale_img('ba_gold.png', w, h)
        self.sc_4 = self.scale_img('ba_silver.png', w, h)
        self.sc_3 = self.scale_img('ba_bronze.png', w, h)
        self.sc_2 = self.scale_img('battle_anki_icon.png', w, h)
        self.sc_1 = self.scale_img('star.png', 18, 18)

        self.main_win.setWindowIcon(icon)

        # self.ui.lab_logo_home.setPixmap(self.fireworks_logo2)
        # self.ui.lab_logo_home_2.setPixmap(self.fireworks_logo2)

        self.bar_left_radius = ("border-top-left-radius: 24px;"
                                "border-bottom-left-radius: 24px;")
        self.bar_radius = "border-radius: 24px;"

        self.odd_bar_bot_color = '#093657'  # 'rgb(0, 179, 44)'
        self.odd_bar_top_color = '#E3DDD9'  # 'rgb(230, 230, 230)'
        self.odd_backgr_top_color = '#051b2e'  # 'rgb(13, 89, 1)'
        self.odd_backgr_bot_color = '#E3DDD9'  # 'rgb(141, 199, 175)'

        self.even_bar_bot_color = '#7c4c1d'  # 'rgb(236,29,30)'
        self.even_bar_top_color = '#E3DDD9'  # 'rgb(230, 230, 230)'
        self.even_backgr_top_color = '#7c4c1d'  # 'rgb(179, 0, 12)'
        self.even_backgr_bot_color = '#c7bca8'  # 'rgb(233, 139, 146)'

        self.odd_bar_text_color = self.even_bar_bot_color
        self.even_bar_text_color = self.odd_bar_bot_color

        self.odd_bar_head = (f"QProgressBar::chunk"
                             f"{{"
                             f"border: 1px solid {self.odd_bar_bot_color};"
                             f"border-style: outset;")
        #                    # RADIUS HERE
        self.odd_bar_tail = (f"background: QLinearGradient( x1: 0.2, y1: 0.2,"
                             f" x2: 0.4, y2: 1,"
                             f" stop: 0 {self.odd_bar_top_color},"
                             f" stop: 1 {self.odd_bar_bot_color});"
                             f"}}"
                             f"QProgressBar"
                             f"{{"
                             f"border: 2px solid {self.odd_bar_bot_color};"
                             f"border-style: inset;"
                             f"border-radius: 24px;"
                             f"background: QLinearGradient( x1: 0, y1: 0,"
                             f" x2: 0.9, y2: 1,"
                             f" stop: 0 {self.odd_backgr_top_color},"
                             f" stop: 1 {self.odd_backgr_bot_color});"
                             f"color: {self.odd_bar_text_color};"
                             f"}}")

        self.even_bar_head = (f"QProgressBar::chunk"
                              f"{{"
                              f"border: 1px solid {self.even_bar_bot_color};"
                              f"border-style: outset;")
        #                     # RADIUS HERE
        self.even_bar_tail = (f"background: QLinearGradient( x1: 0.2, y1: 0.2,"
                              f" x2: 0.4, y2: 1,"
                              f" stop: 0 {self.even_bar_top_color},"
                              f" stop: 1 {self.even_bar_bot_color});"
                              f"}}"
                              f"QProgressBar"
                              f"{{"
                              f"border: 2px solid {self.even_bar_bot_color};"
                              f"border-style: inset;"
                              f"border-radius: 24px;"
                              f"background: QLinearGradient( x1: 0, y1: 0,"
                              f" x2: 0.9, y2: 1,"
                              f" stop: 0 {self.even_backgr_top_color},"
                              f" stop: 1 {self.even_backgr_bot_color});"
                              f"color: {self.even_bar_text_color};"
                              f"}}")

        self.ss_odd_bar_left_radius = self.odd_bar_head + self.bar_left_radius + self.odd_bar_tail
        self.ss_odd_bar_round = self.odd_bar_head + self.bar_radius + self.odd_bar_tail

        self.ss_even_bar_left_radius = self.even_bar_head + self.bar_left_radius + self.even_bar_tail
        self.ss_even_bar_round = self.even_bar_head + self.bar_radius + self.even_bar_tail

        self.ui.progressBar_p1.valueChanged.connect(lambda: self.ss_update_any_bar(self.ui.progressBar_p1))
        self.ui.progressBar_p2.valueChanged.connect(lambda: self.ss_update_any_bar(self.ui.progressBar_p2))

        # self.reset_progBar_styles()
        self.ss_set_2_bars()

        s = self.ui
        s.away_hovered = '#ff877a'
        s.away_hov_bd = colorscale(s.away_hovered, .7)
        s.away_hv_chck = '#7cf283'
        s.away_hv_chck_bd = colorscale(s.away_hv_chck, .7)
        s.away_chckd = colorscale(s.away_hovered, .9)
        s.away_chckd_bd = colorscale(s.away_chckd, .7)

        s.away_hv_prs = colorscale(s.away_chckd, .9)
        s.away_hv_prs_bd = colorscale(s.away_hv_prs, .7)

        s.bdg_hovered = '#ffdab9'
        s.bdg_hov_bd = colorscale(s.bdg_hovered, .8)
        s.bdg_hv_chck = '#ffa866'
        s.bdg_hv_chck_bd = colorscale(s.bdg_hv_chck, .8)
        s.bdg_hvprs = '#e87720'
        s.bdg_hvprs_bd = colorscale(s.bdg_hvprs, .8)
        s.bdg_chckd = '#f08b3e'
        s.bdg_chckd_bd = colorscale(s.bdg_chckd, .8)

        s.join_hovered = '#7edbfc'
        s.join_hov_bd = colorscale(s.join_hovered, .8)
        s.join_prs = '#4fbfe8'
        s.join_prs_bd = colorscale(s.join_prs, .7)

        s.send_hov = '#78e387'
        s.send_hov_bd = colorscale(s.send_hov, .8)
        s.send_prs = '#48c759'
        s.send_prs_bd = colorscale(s.send_prs, .8)

        s.opt_hovered = '#c0a8ed'
        s.opt_hov_bd = colorscale(s.opt_hovered, .7)
        s.opt_prs = '#e07ee0'
        s.opt_prs_bd = colorscale(s.opt_prs, .5)

        self.ui.but_away.setStyleSheet(f"QPushButton#but_away:hover:!pressed{{background-color: {s.away_hovered};"
                                       f"border-style: solid; border-width: 2px; border-color: {s.away_hov_bd};}}"
                                       f"QPushButton#but_away:hover:checked{{background-color: {s.away_hv_chck};"
                                       f"border-style: solid; border-width: 2px; border-color: {s.away_hv_chck_bd};}}"
                                       f"QPushButton#but_away:hover:pressed{{background-color: {s.away_hv_prs};"
                                       f"border-style: solid; border-width: 2px; border-color: {s.away_hv_prs_bd};}}"
                                       f"QPushButton#but_away:checked{{background-color: {s.away_chckd};"
                                       f"border-style: solid; border-width: 2px; border-color: {s.away_chckd_bd};}}")
        self.ui.but_badge.setStyleSheet(f"QPushButton#but_badge:hover:!pressed{{background-color: {s.bdg_hovered};"
                                        f"border-style: solid; border-width: 2px; border-color: {s.bdg_hov_bd};}}"
                                        f"QPushButton#but_badge:hover:checked{{background-color: {s.bdg_hv_chck};"
                                        f"border-style: solid; border-width: 2px; border-color: {s.bdg_hv_chck_bd};}}"
                                        f"QPushButton#but_badge:hover:pressed{{background-color: {s.bdg_hvprs};"
                                        f"border-style: solid; border-width: 2px; border-color: {s.bdg_hvprs_bd};}}"
                                        f"QPushButton#but_badge:checked{{background-color: {s.bdg_chckd};"
                                        f"border-style: solid; border-width: 2px; border-color: {s.bdg_chckd_bd};}}")
        self.ui.but_join.setStyleSheet(f"QPushButton#but_join:hover:!pressed{{background-color: {s.join_hovered};"
                                       f"border-style: solid; border-width: 2px; border-color: {s.join_hov_bd};}}"
                                       f"QPushButton#but_join:pressed{{background-color: {s.join_prs};"
                                       f"border-style: solid; border-width: 2px; border-color: {s.join_prs_bd};}}")
        self.ui.but_sendittt.setStyleSheet(f"QPushButton#but_sendittt:hover:!pressed{{background-color: {s.send_hov};"
                                           f"border-style: solid; border-width: 2px; border-color: {s.send_hov_bd};}}"
                                           f"QPushButton#but_sendittt:pressed{{background-color: {s.send_prs};"
                                           f"border-style: solid; border-width: 2px; border-color: {s.send_prs_bd};}}")
        self.ui.but_options.setStyleSheet(f"QPushButton#but_options:hover:!pressed{{background-color: {s.opt_hovered};"
                                          f"border-style: solid; border-width: 2px; border-color: {s.opt_hov_bd};}}"
                                          f"QPushButton#but_options:pressed{{background-color: {s.opt_prs};"
                                          f"border-style: solid; border-width: 2px; border-color: {s.opt_prs_bd};}}")
        logger_ui.info('Mainwindow instance initiated')

    def update_home_labels(self):
        self.ui.lab_pg1_matched.hide()
        self.ui.lab_pg1_tit_matched.hide()
        self.ui.lab_pg1_tit_cardorder.hide()

        self.ui.lab_pg1_cards.setText(str(decksize))
        self.ui.lab_pg1_cardtype.setText(card_type_str)
        self.ui.lab_pg1_cardorder.setText(card_order_str)

        if today_only:
            self.ui.lab_pg1_due_today.show()
            self.ui.lab_pg1_overdues.show()
        else:
            self.ui.lab_pg1_due_today.hide()
            self.ui.lab_pg1_overdues.hide()

        if resched_box:
            self.ui.lab_pg1_resched.setText('Yes')
        else:
            self.ui.lab_pg1_resched.setText('do NOT')

        if joiners_box:
            self.ui.lab_pg1_joiners.setText('Yes')
        else:
            self.ui.lab_pg1_joiners.setText('do NOT')

        logger_ui.info(f'update_home_labels() completed')
        return

    def scale_img(self, name: str, w: int, h: int):
        img = QPixmap(name)
        scaled = img.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logger_utils.debug('scale_img() completed')
        return scaled

    def make_table_item(self, img: QPixmap):
        lbl = QLabel()
        lbl.setPixmap(img)
        lbl.setAlignment(Qt.AlignCenter)
        itm = lbl
        logger_ui.debug('make_table_item() completed')
        return itm

    def undojoin(self):
        self.timer_joined.stop()
        global accepted_req
        accepted_req = False
        logger_utils.info('info() completed')

    def move_resource(self, res_name: str, repl=False):
        end_dest = os.path.join(os.getcwd(), res_name)
        if repl:
            back_len_join = len(os.path.join(mw.pm.name, 'collection.media'))
            com_root = os.getcwd()[:-back_len_join]
            source_fold = os.path.join(com_root, 'addons21', '613520216', 'res')
            source = os.path.join(source_fold, res_name)
            dest = f'{os.getcwd()}'
            shutil.move(source, end_dest)
            shutil.copy(end_dest, source_fold)
            logger_ui.debug('move_resource() completed')
        else:
            if os.path.isfile(f'{end_dest}') is False:
                back_len_join = len(os.path.join(mw.pm.name, 'collection.media'))
                com_root = os.getcwd()[:-back_len_join]
                source_fold = os.path.join(com_root, 'addons21', '613520216', 'res')
                source = os.path.join(source_fold, res_name)
                dest = f'{os.getcwd()}'
                shutil.move(source, dest)
                shutil.copy(end_dest, source_fold)
                logger_ui.debug('move_resource() completed')

    def set_away(self):
        logger_user.debug('set_away() clicked')
        global inbattle
        if self.ui.but_away.isChecked():
            inbattle = None
            self.ui.but_away.setText('Ready\nStatus')
        else:
            inbattle = False
            self.ui.but_away.setText('Away\nStatus')
        get_local_data()
        send_pulse()
        logger_ui.info(f'set_away() clicked & completed [Status: {inbattle_status()}]')

    def ss_set_2_bars(self):
        self.ui.progressBar_p1.setValue(7)
        self.ui.progressBar_p2.setValue(7)
        self.ui.progressBar_p1.setStyleSheet(self.ss_odd_bar_left_radius)
        self.ui.progressBar_p2.setStyleSheet(self.ss_even_bar_left_radius)
        logger_ui.debug('ss_set_2_bars() completed')

    def undorequest(self):
        global local_data
        global matched_terms
        global matched_list
        global matched_size
        matched_list = []
        matched_size = 0
        matched_terms = ''
        local_data['matched terms'] = ''
        local_data['card ids'] = [{}]
        local_data['request options']['req Remote IP'] = ''
        local_data['request options']['req name'] = ''
        self.timer_undo_request.stop()
        logger_utils.info('undorequest() completed')

    def undoaccept(self):
        global accepted_req
        global matched_terms

        accepted_req = False
        matched_terms = ''
        local_data['matched terms'] = ''

        for rd in [d for d in sd if d['user info']['Remote IP'] in challenger_ip
                   if d['user info']['in battle?'] is not True]:
            i = challenger_ip.index(rd['user info']['Remote IP'])
            try:
                challenger_ip.pop(i)
                challenger_name.pop(i)
                challenger_progress.pop(i)
                acc_list.pop(i)
                conn.pop(i)
            except IndexError:
                pass
        self.timer_undo_accepted.stop()
        logger_utils.info('undoaccept() completed')

    def reset(self):
        global local_data
        global matched_list
        global inbattle
        global decksize
        global ready_for_request
        global matched_size
        global matched_terms
        global window_open
        global myprogress
        global popped_req
        global popped_comms
        global make_deck_problem
        global opponent_problem
        global told_problem
        global acc_list
        global challenger_name
        global challenger_ip
        global challenger_progress
        global conn
        global accepted_req

        delete_battle_decks()

        self.undorequest()

        if acc_list and max(acc_list) > 2:
            self.remove_progressbars()

        myprogress = 0

        challenger_name = []
        challenger_ip = []
        challenger_progress = []
        acc_list = []
        conn = []

        local_data['request options'] = {'req name': '',
                                         'req names': [],
                                         'req Remote IP': str(),
                                         'req Remote IPs': []}
        accepted_req = False
        told_problem = False
        window_open = False
        opponent_problem = False
        make_deck_problem = False
        ready_for_request = True
        popped_comms = False
        popped_req = False
        inbattle = False

        recall_after_battle()

        self.ss_set_2_bars()
        self.main_win.show()

        logger_ui.info('reset() completed')

    def updateBattleBars(self):
        global local_data
        global sd
        global myprogress
        global challenger_progress
        global decksize
        global challenger_ip
        global dyn_id
        global challenger_name
        global told_problem
        global cards_left
        global acc_list
        global conn

        if joiners_box:
            check_for_joins()

        if inbattle:
            myprogress = int(((1 - (cards_left / decksize)) * 100))  # - (100/decksize))
            self.ui.progressBar_p1.setFormat(f"{mw.pm.name}   {myprogress}%")

            if sd and challenger_ip:

                for rd in [d for d in sd if d['user info']['Remote IP'] in challenger_ip]:

                    if joiners_box and 'req Remote IPs' in rd['request options'].keys():
                        for nc in [c for c in sd
                                   if rd['user info']['progress'] != 0
                                   if c['user info']['Remote IP'] not in challenger_ip
                                   if c['user info']['Remote IP'] in rd['request options']['req Remote IPs']
                                   if c['user info']['Remote IP'] != loc_rem_ip if c['user info']['in battle?']
                                   ]:
                            challenger_ip.append(nc['user info']['Remote IP'])
                            challenger_name.append(nc['user info']['name'])
                            challenger_progress.append(0)
                            acc_list.append(0)
                            conn.append(0)

                    idx = challenger_ip.index(rd['user info']['Remote IP'])
                    pr = int(rd['user info']['progress'])
                    ib = bool(rd['user info']['in battle?'])

                    if conn[idx] == 0:
                        # they are connected
                        conn[idx] = 1

                    if acc_list[idx] == 0 and rd['user info']['in battle?'] and idx != 0:
                        # they they need a progress bar
                        acc_list[idx] = p = max(acc_list) + 1
                        if conn[idx] == 2:
                            # they just ' joined the game!'
                            challenger_name[idx] = name_str(str(challenger_name[idx]), 1)
                            conn[idx] = 1
                        self.add_progressbar(p, idx)
                        challenger_progress[idx] = 0

                    if acc_list[idx] != 0:
                        # they have a progressbar...

                        if challenger_progress[idx] == 100:
                            if ib and pr == 0:
                                # they started a new match, need to forget their IP
                                challenger_ip[idx] = ''
                                challenger_name[idx] = name_str(str(challenger_name[idx]), 2)  # left
                            elif ib and pr != 0 and \
                                    rd['user info']['accepted req'] and \
                                    'req Remote IPs' in rd['request options'].keys() and \
                                    loc_rem_ip in rd['request options']['req Remote IPs']:
                                # they finished, and then ' rejoined the game!'
                                challenger_progress[idx] = pr
                                challenger_name[idx] = name_str(str(challenger_name[idx]), 0)  # rejoin

                        elif challenger_progress[idx] >= 98 and ib is not True and pr == 0:
                            # they just finished and ' left the game...'
                            challenger_progress[idx] = 100
                            challenger_name[idx] = name_str(str(challenger_name[idx]), 2)  # left

                        if ib:
                            if pr != 0 and challenger_progress[idx] != 100:
                                # in battle, playing
                                challenger_progress[idx] = pr
                                if challenger_name[idx][-len(left):] == left:
                                    # they ' rejoined the game!' after previously leaving
                                    challenger_name[idx] = name_str(str(challenger_name[idx]), 0)  # rejoin
                                elif challenger_name[idx][-len(rejoined):] == rejoined:
                                    pass
                                else:
                                    # set name to only name
                                    challenger_name[idx] = name_str(str(challenger_name[idx]), 4)  # name only
                            elif pr == 0 and challenger_progress[idx] != 100:
                                challenger_name[idx] = name_str(str(challenger_name[idx]), 3)  # starting
                        else:
                            # they are not in battle
                            if challenger_progress[idx] > 0:
                                # they ' left the game...'
                                challenger_name[idx] = name_str(str(challenger_name[idx]), 2)  # left
                            elif challenger_progress[idx] == 0:
                                if rd['user info']['accepted req']:
                                    # they are just starting
                                    challenger_name[idx] = name_str(str(challenger_name[idx]), 3)  # starting
                                else:
                                    challenger_name[idx] = name_str(str(challenger_name[idx]), 2)  # left

                        if challenger_progress[idx] and acc_list[idx]:
                            player = int(acc_list[idx])
                            if challenger_progress[idx] < 7:
                                exec(f'self.ui.progressBar_p{player}.setValue(7)\n'
                                     f'self.ui.progressBar_p{player}.setFormat(f"{challenger_name[idx]}   '
                                     f'{challenger_progress[idx]}%")\n'
                                     f'self.ui.progressBar_p{player}.update()\n')
                            elif challenger_progress[idx] >= 7:
                                exec(f'self.ui.progressBar_p{player}.setValue({challenger_progress[idx]})\n'
                                     f'self.ui.progressBar_p{player}.setFormat(f"{challenger_name[idx]}   '
                                     f'{challenger_progress[idx]}%")\n'
                                     f'self.ui.progressBar_p{player}.update()\n')
                    if True not in [x['user info']['in battle?'] for x in sd
                                    if x['user info']['Remote IP'] in challenger_ip
                                    ]:
                        # only tell me someone has makedeckproblem if no one else is in battle!!!
                        global opponent_problem
                        if 'deck problem' in rd['user info'].keys() and rd['user info']['deck problem'] is True and \
                                (told_problem is False) and (popped_comms is False):
                            told_problem = True
                            show_and_log(f"We were unable to make a Battle Deck for one of\n"
                                         f"your opponents. You can still complete the deck\n"
                                         f"if you would like...\n\n"
                                         f"If you'd rather end this battle and try again,\n"
                                         f"just close the battle window and reopen it!\n"
                                         f"Sorry about that!")

                if 0 in conn:
                    ded = conn.index(0)
                    challenger_name[ded] = name_str(str(challenger_name[ded]), 2)  # left
                    if acc_list[ded] != 0:
                        exec(f'self.ui.progressBar_p{acc_list[ded]}.setFormat(f"{challenger_name[ded]}   '
                             f'{challenger_progress[ded]}%")\n'
                             f'self.ui.progressBar_p{acc_list[ded]}.update()\n')

            conn = [0] * len(conn)

            if myprogress >= 100:
                get_local_data()
                send_pulse()
                self.ui.progressBar_p1.setValue(myprogress)
                self.ui.progressBar_p1.update()
                self.timer_battle.stop()
                if max(challenger_progress) >= 100:
                    show_and_log("Keep up the good work!\nBetter luck next time!")
                if max(challenger_progress) < 100:
                    show_and_log("Nice work! You are almost an AnKing!")
                self.reset()
                self.showHome()
                self.log_fin()
            elif myprogress < 7:
                self.ui.progressBar_p1.setValue(7)
                self.ui.progressBar_p1.update()
            elif 7 <= myprogress < 100:
                self.ui.progressBar_p1.setValue(myprogress)
                self.ui.progressBar_p1.update()
        logger_ui.debug('updateBattleBars() completed')
        return

    def log_fin(self):
        s1 = (f'[Total Connected to Server: {len(sd)} ]', '')
        s2 = (f'[{mw.pm.name} FINISHED battle]', '%')
        so = fmt_n_log([s1, s2])
        log_bat_info(so)

    def updateLoadBar(self):
        global isloading
        if self.step_load < 20:
            self.step_load += 1
            self.main_win.setWindowTitle(f'Battle Anki is Loading...{round(self.step_load * (100 / 20))}%')
        else:
            self.ui.centralwidget.setDisabled(False)
            self.main_win.setDisabled(False)
            self.timer_load.stop()
            isloading = False
            self.main_win.setWindowTitle(f'Battle Ankı')
        logger_ui.debug('updateLoadBar() completed')

    def updateWaitingBar(self):
        if self.step <= 180:
            self.step += 1
        else:
            self.step = 0
        self.ui.progressBar_waiting.setValue(self.step * (100 / 180))
        self.ui.progressBar_waiting.update()
        logger_ui.debug('updateWaitingBar() completed')


    def show(self):
        self.main_win.show()
        logger_ui.info('show() completed')


    def showBattle(self):
        logger_ui.info(f'showBattle() called...')
        global myprogress
        global challenger_progress
        global inbattle
        global cards_left
        global acc_list
        global conn

        myprogress = 0

        ch = len(challenger_ip)
        challenger_progress = [0] * ch
        conn = [0] * ch
        acc_list = [0] * ch
        acc_list[0] = 2

        self.ui.stackedWidget.setCurrentWidget(self.ui.page_3)

        self.ui.progressBar_p1.setFormat(f"{mw.pm.name}   {myprogress}%")
        self.ui.progressBar_p2.setFormat(f"{challenger_name[0]}   {challenger_progress[0]}%")

        self.ui.page_3.show()
        self.ui.page_2.hide()
        self.ui.page_1.hide()
        self.ui.page_3.setFocus()

        self.timer_bar.stop()
        self.ui.progressBar_waiting.reset()

        inbattle = True

        self.ui.progressBar_p1.setValue(7)
        self.ui.progressBar_p2.setValue(7)

        cards_left = sum(list(mw.col.sched.counts())) + 1
        self.timer_battle.start(300)

        if not self.main_win.isVisible():
            self.main_win.show()

        s1 = (f'[Total Connected to Server: {len(sd)} ]', '', False)
        s2 = (f'[{mw.pm.name} is STARTED BATTLE]', '%')
        so = fmt_n_log([s1, s2])
        logger_ui.info(so)


    def closeEvent(self, event):
        try:
            self.timer_battle.stop()
            if not shutdown:
                self.reset()
                mw.tybox = QDialog()
                mw.tybox = TY()
                mw.tybox.show()
        except Exception as msg:
            show_and_log(f'Sorry, there was an error\n'
                         f'closing the window\n'
                         f'Error Code 1775\n'
                         f'{msg}')
        finally:
            logger_ui.info('Mainwindow closeEvent() completed')
            return

    def close_all(self):
        global startup
        try:
            self.timer.stop()
            # bye_to_server()
            self.main_win.close()
            mw.is_connected = False
            startup = True
        except:
            pass
        finally:
            logger_ui.info('close_all() completed')
            return

    # from local window
    def get_request_data(self, join=False):
        logger_ui.info('get_request_data() started')

        global local_data
        global can_sendittt
        global challenger_ip
        global challenger_name
        global challenger_progress
        global matched_box
        global inbattle
        challenger_ip = []
        challenger_name = []
        challenger_progress = []
        can_sendittt = False
        if inbattle is None:
            show_and_log("Your status is currently set to 'Away' !\n"
                         "you have to be 'Ready' to initiate a battle...")
            return False

        if decksize == 0 and join is False:
            show_and_log("You need to choose the number of cards!")
            return False
        else:
            if new_box or learn_box or mature_box or new_AND_review_box:
                if len(self.ui.tableWidget_users_connected.selectionModel().selectedRows()) > 0:
                    if join and len(self.ui.tableWidget_users_connected.selectionModel().selectedRows(0)) > 1:
                        show_and_log(f"You can only join one person\n"
                                     f"at a time...")
                        return False
                    else:
                        try:
                            self.ui.tableWidget_users_connected.setSortingEnabled(False)
                            for item in self.ui.tableWidget_users_connected.selectionModel().selectedRows(0):
                                challenger_name.append(item.data(0))
                            inbattle_str = []
                            if badgeview is True:
                                for item in self.ui.tableWidget_users_connected.selectionModel().selectedRows(3):
                                    inbattle_str.append(item.data(0))
                            elif badgeview is False:
                                for item in self.ui.tableWidget_users_connected.selectionModel().selectedRows(1):
                                    inbattle_str.append(item.data(0))
                            if 'Away' not in inbattle_str:
                                c1 = bool('In Battle' not in inbattle_str)
                                c2 = bool(c1 is False and join is True)  # pass: inbattle, joining
                                c3 = bool(c1 is True and join is False)  # pass: not in battle, inviting
                                c4 = bool(c1 is False and join is False)  # fail: in battle, not joining
                                c5 = bool(c1 is True and join is True)  # fail: not in battle, trying to join

                                if c5:
                                    show_and_log('To join a battle, the player\n'
                                                 'you selected has to be in battle!')
                                    challenger_name = []
                                    return False
                                elif c4:
                                    show_and_log(f"Sorry... {challenger_name} is \n"
                                                 f"currently in battle!")
                                    challenger_name = []
                                    return False
                                elif c2 or c3:
                                    sel_ips = []
                                    # check to make sure not self...
                                    if badgeview is True:
                                        for item in self.ui.tableWidget_users_connected.selectionModel().selectedRows(
                                                4):
                                            sel_ips.append(self.str_to_ip(item.data(0)))
                                    elif badgeview is False:
                                        for item in self.ui.tableWidget_users_connected.selectionModel().selectedRows(
                                                2):
                                            sel_ips.append(self.str_to_ip(item.data(0)))
                                    if (str(mw.pm.name) not in challenger_name) and (loc_rem_ip not in sel_ips):
                                        incompatible = None
                                        if join:
                                            for p in [d for d in sd if d['user info']['Remote IP'] in sel_ips]:
                                                if 'ver' in p.keys():
                                                    cv = str(p['ver']).split('.')
                                                    if int(cv[0]) < 2:
                                                        incompatible = True
                                        else:
                                            pass
                                        if join and incompatible:
                                            show_and_log(f"Sorry, {challenger_name[0]}'s\n"
                                                         f"Battle Anki version (v{cv[0]}.{cv[1]})\n"
                                                         f"does not support the 'Join Battle' function...\n\n"
                                                         f"        Please tell them to update!!!\n\n"
                                                         f"Your version:\n\n"
                                                         f"             v{ba_ver}\n\n")
                                            incompatible = None
                                            return False
                                        else:
                                            local_data['request options']['req names'] = challenger_name
                                            local_data['request options']['req Remote IPs'] = challenger_ip = sel_ips
                                            local_data['request options']['req in battle?'] = False
                                            logger_ui.info('get_request_data() JOIN data pulled from tablewidget')
                                            if c3:
                                                logger_ui.info('get_request_data() INVITE data pulled from tablewidget')
                                                local_data['request options']['req name'] = challenger_name[0]
                                                local_data['request options']['req Remote IP'] = challenger_ip[0]
                                            challenger_progress = [0] * len(sel_ips)
                                            if len(sel_ips) > 1:
                                                local_data['request options']['matched box'] = matched_box = False
                                            can_sendittt = True
                                            inbattle = None
                                            logger_ui.info('get_request_data() passed True')
                                            return True
                                    else:
                                        can_sendittt = False
                                        challenger_name = []
                                        show_and_log(f"As fun as it sounds, you can't\n"
                                                     f"battle yourself on Battle Anki...\n"
                                                     f"If you got this message incorrectly,\n"
                                                     f"Please report it\n"
                                                     f"EC 732")
                                        return False
                            else:
                                can_sendittt = False
                                challenger_name = []
                                show_and_log(f"Sorry... someone you selected\n "
                                             f"is currently away!")
                                return False
                        except Exception as msge:
                            show_and_log(f"{msge}"
                                         f"Sorry, there was a problem...\n"
                                         f"you'll have to restart Anki to be able to play.\n"
                                         f"EC 607")
                            return False
                        finally:
                            self.ui.tableWidget_users_connected.setSortingEnabled(True)
                else:
                    can_sendittt = False
                    show_and_log("You need to choose someone to battle!")
                    return False

            else:
                can_sendittt = False
                show_and_log("You need to choose the type of cards!")
                return False

    def str_to_ip(self, mystr: str):
        myip = str(mystr.split(',')[0])[2:-1]
        myport = int(mystr.split(',')[1][1:-1])
        ip = str(f"('{myip}', {myport})")
        logger_utils.debug('str_to_ip() completed')
        return ip

    def showWait(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_2)
        self.ui.page_2.show()
        self.ui.page_1.hide()
        self.ui.page_2.setFocus()
        logger_ui.info('showWait() completed')

    def startWaitingBar(self):
        self.step = 0
        self.timer_bar.start(50)
        logger_ui.debug('startWaitingBar() completed')

    def refresh_users(self):
        global card_order
        self.ui.tableWidget_users_connected.setSortingEnabled(False)
        if badgeview is False:
            self.refresh_regview()
        if badgeview is True:
            self.refresh_badgeview()
        self.ui.tableWidget_users_connected.setSortingEnabled(True)
        self.ui.tableWidget_users_connected.update()
        logger_ui.debug('refresh_users() completed')

    def showHome(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_1)
        self.main_win.show()
        self.ui.page_1.show()
        self.ui.page_1.setFocus()
        logger_ui.info('showHome() completed')

    def startLoadBar(self):
        global isloading
        isloading = True
        # self.ui.progressBar_loading.setFormat(f'Loading... %p%')
        self.main_win.setWindowTitle('Battle Anki is Loading...0%')
        self.step_load = 0
        # self.ui.lab_batform_connected.hide()
        # self.ui.lab_users_connected.hide()
        # self.ui.tableWidget_users_connected.hide()
        # self.ui.frame.hide()
        self.ui.centralwidget.setDisabled(True)
        self.timer_load.start(50)
        logger_ui.debug('startLoadBar() completed')

    def hb(self):
        if isloading is False:
            self.main_win.setWindowTitle('Battle Ankı')
            self.timer_hb.start(700)
        logger_ui.debug('hb() completed')

    def hb_dias(self):
        if isloading is False:
            self.main_win.setWindowTitle('Battle Anki')
        logger_ui.debug('hb_dias() completed')

    def ss_update_any_bar(self, bar: QtWidgets.QProgressBar):
        dig = int(bar.objectName()[-1:])
        if (dig % 2) != 0:
            # odd
            if bar.value() >= 95:
                bar.setStyleSheet(self.ss_odd_bar_round)
            else:
                bar.setStyleSheet(self.ss_odd_bar_left_radius)
        else:
            # even
            if bar.value() >= 95:
                bar.setStyleSheet(self.ss_even_bar_round)
            else:
                bar.setStyleSheet(self.ss_even_bar_left_radius)
        logger_ui.debug('ss_update_any_bar() completed')

    def ss_p1(self):
        if self.ui.progressBar_p1.value() >= 95:
            self.ui.progressBar_p1.setStyleSheet(f"QProgressBar::chunk"
                                                 f"{{"
                                                 f"border: 1px solid {self.odd_bar_bot_color};"
                                                 f"border-style: outset;"
                                                 f"border-radius: 24px;"
                                                 f"background: QLinearGradient( x1: 0.2, y1: 0.2,"
                                                 f" x2: 0.4, y2: 1,"
                                                 f" stop: 0 {self.odd_bar_top_color},"
                                                 f" stop: 1 {self.odd_bar_bot_color});"
                                                 f"}}"
                                                 f"QProgressBar"
                                                 f"{{"
                                                 f"border: 2px solid {self.odd_bar_bot_color};"
                                                 f"border-style: inset;"
                                                 f"border-radius: 24px;"
                                                 f"background: QLinearGradient( x1: 0, y1: 0,"
                                                 f" x2: 0.9, y2: 1,"
                                                 f" stop: 0 {self.odd_backgr_top_color},"
                                                 f" stop: 1 {self.odd_backgr_bot_color});"
                                                 f"color: {self.even_bar_bot_color};"
                                                 f"}}")
        logger_ui.debug('ss_p1() completed')

    def ss_p2(self):
        if self.ui.progressBar_p2.value() >= 95:
            self.ui.progressBar_p2.setStyleSheet(f"QProgressBar::chunk"
                                                 f"{{"
                                                 f"border: 1px solid {self.even_bar_bot_color};"
                                                 f"border-style: outset;"
                                                 f"border-radius: 24px;"
                                                 f"background: QLinearGradient( x1: 0.2, y1: 0.2,"
                                                 f" x2: 0.4, y2: 1,"
                                                 f" stop: 0 {self.even_bar_top_color},"
                                                 f" stop: 1 {self.even_bar_bot_color});"
                                                 f"}}"
                                                 f"QProgressBar"
                                                 f"{{"
                                                 f"border: 2px solid {self.even_bar_bot_color};"
                                                 f"border-style: inset;"
                                                 f"border-radius: 24px;"
                                                 f"background: QLinearGradient( x1: 0, y1: 0,"
                                                 f" x2: 0.9, y2: 1,"
                                                 f" stop: 0 {self.even_backgr_top_color},"
                                                 f" stop: 1 {self.even_backgr_bot_color});"
                                                 f"color: {self.odd_bar_bot_color};"
                                                 f"}}")
        logger_ui.debug('ss_p2() completed')

    def toggle_badges(self):
        logger_user.debug('toggle_badges() clicked')
        global badgeview
        self.ui.tableWidget_users_connected.clearContents()
        if self.main_win.width() == 550:
            self.set_regview()
            badgeview = False
            self.refresh_users()
        elif self.main_win.width() == 460:
            self.set_badgeview()
            badgeview = True
            self.refresh_users()
        logger_ui.info('toggle_badges() clicked & completed')

    def set_regview(self):
        logger_user.debug('set_regview() clicked')
        self.main_win.setFixedSize(460, 410)
        self.ui.but_badge.setText('Show\nBadges')
        self.main_win.resize(460, 410)
        self.ui.tableWidget_users_connected.setColumnCount(3)
        self.ui.tableWidget_users_connected.setHorizontalHeaderItem(0, QTableWidgetItem("Name"))
        self.ui.tableWidget_users_connected.setHorizontalHeaderItem(1, QTableWidgetItem("Status"))
        self.ui.tableWidget_users_connected.setColumnWidth(1, 71)
        self.ui.tableWidget_users_connected.setHorizontalHeaderItem(2, QTableWidgetItem("IP"))
        self.ui.tableWidget_users_connected.setColumnWidth(2, 1)
        # self.main_win.update()
        logger_ui.info('set_regview() clicked & completed')

    def set_badgeview(self):
        logger_user.debug('set_badgeview() clicked')
        self.main_win.setFixedSize(550, 410)
        self.ui.but_badge.setText('Hide\nBadges')
        self.main_win.resize(550, 410)
        self.ui.tableWidget_users_connected.setColumnCount(5)
        self.ui.tableWidget_users_connected.setIconSize(QSize(26, 26))
        self.ui.tableWidget_users_connected.setHorizontalHeaderItem(0, QTableWidgetItem("Name"))
        self.ui.tableWidget_users_connected.setHorizontalHeaderItem(1, QTableWidgetItem("Badge"))
        self.ui.tableWidget_users_connected.setColumnWidth(1, 45)
        self.ui.tableWidget_users_connected.setHorizontalHeaderItem(2, QTableWidgetItem("t Today"))
        self.ui.tableWidget_users_connected.setColumnWidth(2, 60)
        self.ui.tableWidget_users_connected.setHorizontalHeaderItem(3, QTableWidgetItem("Status"))
        self.ui.tableWidget_users_connected.setColumnWidth(3, 68)
        self.ui.tableWidget_users_connected.setHorizontalHeaderItem(4, QTableWidgetItem("IP"))
        self.ui.tableWidget_users_connected.setColumnWidth(4, 1)
        logger_ui.info('set_badgeview() clicked & completed')

    def refresh_regview(self):
        logger_ui.debug('refresh_regview() STARTED')
        try:
            sel_ip = []
            if self.ui.tableWidget_users_connected.selectedItems():
                for item in self.ui.tableWidget_users_connected.selectionModel().selectedRows(2):
                    sel_ip.append(item.data(0))
            player_count = len(sd)
            if player_count > 7:
                self.ui.tableWidget_users_connected.setColumnWidth(0, 172)
            else:
                self.ui.tableWidget_users_connected.setColumnWidth(0, 190)
            # update the contents
            self.ui.tableWidget_users_connected.clearContents()
            self.ui.tableWidget_users_connected.setRowCount(player_count)
            for i in range(0, len(sd)):
                self.ui.tableWidget_users_connected.setItem(i, 0, QTableWidgetItem(
                    str(sd[i]['user info']['name'])))
                self.ui.tableWidget_users_connected.setItem(i, 2, QTableWidgetItem(
                    str(sd[i]['user info']['Remote IP'])))
                if sd[i]['user info']['in battle?'] is True:
                    self.ui.tableWidget_users_connected.setItem(i, 1, QTableWidgetItem('In Battle'))
                elif sd[i]['user info']['in battle?'] is False:
                    self.ui.tableWidget_users_connected.setItem(i, 1, QTableWidgetItem('Ready'))
                elif sd[i]['user info']['in battle?'] is None:
                    self.ui.tableWidget_users_connected.setItem(i, 1, QTableWidgetItem('Away'))
                else:
                    show_and_log(f'Sorry, there was a problem with Battle Anki...\n\n'
                                 f'                 EC 955')
            if sel_ip:
                for i in range(self.ui.tableWidget_users_connected.rowCount()):
                    if self.ui.tableWidget_users_connected.item(i, 2).data(0) in sel_ip:
                        self.ui.tableWidget_users_connected.selectRow(i)
            logger_ui.debug('refresh_regview() completed')
        except Exception as mesg:
            show_and_log(f'Sorry, there was a problem with Battle Anki...\n'
                         f'EC 1458\n'
                         f'{mesg}')
            mw.battle_window.timer.stop()
            self.main_win.close()

    def refresh_badgeview(self):
        logger_ui.debug('refresh_badgeview() STARTED')
        try:
            sel_ip = []
            if self.ui.tableWidget_users_connected.selectedItems():
                for item in self.ui.tableWidget_users_connected.selectionModel().selectedRows(4):
                    sel_ip.append(item.data(0))

            player_count = len(sd)
            if player_count > 7:
                self.ui.tableWidget_users_connected.setColumnWidth(0, 145)
            else:
                self.ui.tableWidget_users_connected.setColumnWidth(0, 163)

            # update the contents
            self.ui.tableWidget_users_connected.clearContents()
            self.ui.tableWidget_users_connected.setRowCount(player_count)
            for i in range(0, len(sd)):
                self.ui.tableWidget_users_connected.setItem(i, 0, QTableWidgetItem(
                    str(sd[i]['user info']['name'])))
                self.ui.tableWidget_users_connected.setItem(i, 4, QTableWidgetItem(
                    str(sd[i]['user info']['Remote IP'])))

                if sd[i]['user info']['in battle?'] is True:
                    self.ui.tableWidget_users_connected.setItem(i, 3, QTableWidgetItem('In Battle'))
                elif sd[i]['user info']['in battle?'] is False:
                    self.ui.tableWidget_users_connected.setItem(i, 3, QTableWidgetItem('Ready'))
                elif sd[i]['user info']['in battle?'] is None:
                    self.ui.tableWidget_users_connected.setItem(i, 3, QTableWidgetItem('Away'))
                else:
                    show_and_log(f'Sorry, there was a problem with Battle Anki...\n\n'
                                 f'                 EC 994')

                if 'time today' in sd[i]['user info'].keys():
                    t = QTableWidgetItem(str(sd[i]['user info']['time today']))
                    t.setTextAlignment(Qt.AlignCenter)
                    self.ui.tableWidget_users_connected.setItem(i, 2, t)
                else:
                    self.ui.tableWidget_users_connected.setItem(i, 2, QTableWidgetItem(' '))

                if 'cards today' in sd[i]['user info'].keys():
                    c_t = int(sd[i]['user info']['cards today'])
                    if c_t >= 5000:
                        itm_7 = self.make_table_item(self.sc_7)
                        self.ui.tableWidget_users_connected.setCellWidget(i, 1, itm_7)
                    elif c_t >= 2500:
                        itm_6 = self.make_table_item(self.sc_6)
                        self.ui.tableWidget_users_connected.setCellWidget(i, 1, itm_6)
                    elif c_t >= 1000:
                        itm_5 = self.make_table_item(self.sc_5)
                        self.ui.tableWidget_users_connected.setCellWidget(i, 1, itm_5)
                    elif c_t >= 750:
                        itm_4 = self.make_table_item(self.sc_4)
                        self.ui.tableWidget_users_connected.setCellWidget(i, 1, itm_4)
                    elif c_t >= 500:
                        itm_3 = self.make_table_item(self.sc_3)
                        self.ui.tableWidget_users_connected.setCellWidget(i, 1, itm_3)
                    elif c_t >= 250:
                        itm_2 = self.make_table_item(self.sc_2)
                        self.ui.tableWidget_users_connected.setCellWidget(i, 1, itm_2)
                    elif c_t > 0:
                        itm_1 = self.make_table_item(self.sc_1)
                        self.ui.tableWidget_users_connected.setCellWidget(i, 1, itm_1)
                    else:
                        self.ui.tableWidget_users_connected.setItem(i, 1, QTableWidgetItem(' '))
                else:
                    self.ui.tableWidget_users_connected.setItem(i, 1, QTableWidgetItem(' '))

            if sel_ip:
                for i in range(self.ui.tableWidget_users_connected.rowCount()):
                    if self.ui.tableWidget_users_connected.item(i, 4).data(0) in sel_ip:
                        self.ui.tableWidget_users_connected.selectRow(i)
            logger_ui.debug('refresh_badgeview() completed')
        except Exception as mesg:
            show_and_log(f'Sorry, there was a problem with Battle Anki...\n'
                         f'EC 1536\n'
                         f'{mesg}')
            mw.battle_window.timer.stop()
            self.main_win.close()

    def add_progressbar(self, p: int, ind: int):
        logger_ui.debug('add_progressbar() STARTED')
        s = p + 20
        name = f'progressBar_p{p}'
        name_sp = f'spacerItem{s}'
        setattr(self.ui, name, QtWidgets.QProgressBar(self.ui.page_3))
        bar = f'self.ui.{name}'
        exec(f'''
{bar}.setEnabled(True)
sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
sizePolicy.setHorizontalStretch(0)
sizePolicy.setVerticalStretch(0)
sizePolicy.setHeightForWidth({bar}.sizePolicy().hasHeightForWidth())
{bar}.setSizePolicy(sizePolicy)
{bar}.setMinimumSize(QtCore.QSize(300, 61))
{bar}.setMaximumSize(QtCore.QSize(510, 61))
font = QtGui.QFont()
font.setPointSize(14)
{bar}.setFont(font)
{bar}.setAutoFillBackground(False)
{bar}.setProperty("value", 24)
{bar}.setAlignment(QtCore.Qt.AlignCenter)
{bar}.setTextVisible(True)
{bar}.setInvertedAppearance(False)
{bar}.setTextDirection(QtWidgets.QProgressBar.BottomToTop)
{bar}.setObjectName("{name}")
self.ui.verticalLayout_12.addWidget({bar})
{name_sp} = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
self.ui.verticalLayout_12.addItem({name_sp})
{bar}.valueChanged.connect(lambda: mw.battle_window.ss_update_any_bar(mw.battle_window.ui.progressBar_p{p}))
{bar}.setValue(7)
{bar}.setFormat(f'{challenger_name[ind]}   {challenger_progress[ind]}%')
{bar}.update()
''')
        self.ui.page_3.update()
        logger_ui.info('add_progressbar() completed')

    def remove_progressbars(self):
        logger_ui.debug('remove_progressbars() STARTED')
        try:
            for nu in [x for x in acc_list if x > 2 if self.ui.verticalLayout_12.count() > 7]:
                child = self.ui.verticalLayout_12.takeAt(7)
                if child.widget():
                    child.widget().deleteLater()
                    child2 = self.ui.verticalLayout_12.takeAt(7)
                    if child2.spacerItem():
                        self.ui.verticalLayout_12.removeItem(child2.spacerItem())
                elif child.spacerItem():
                    self.ui.verticalLayout_12.removeItem(child.spacerItem())
                    child2 = self.ui.verticalLayout_12.takeAt(7)
                    if child2.widget():
                        child2.widget().deleteLater()
                logger_ui.info('remove_progressbars() 1 ITEM REMOVED')
            else:
                logger_ui.info('remove_progressbars() completed')
                return
        except Exception as excp:
            show_and_log(f'Sorry, something went wrong...\n'
                         f'Error Code 1352\n'
                         f'{excp}')

    def join_battle(self):
        logger_user.info('join_battle() clicked')
        global ready_for_request
        global matched_size
        global dyn_id
        global challenger_ip
        global challenger_name
        global challenger_progress
        global acc_list
        global decksize
        global local_data
        global accepted_req

        local_data['request options']['req name'] = ''
        local_data['request options']['req Remote IP'] = ''

        max_cl = 0
        m_ds = 0
        ib = [False]
        real_decksize = int()
        ready_for_request = False

        if self.get_request_data(True):
            c = str(challenger_ip[0])
            d = next((x for x in sd if x['user info']['Remote IP'] == c), None)
            if sd and d:
                if 'req Remote IPs' in d['request options'].keys():
                    ips = list(d['request options']['req Remote IPs'])
                    for item in [ip for ip in ips if ip is not None if ip not in challenger_ip if ip != loc_rem_ip]:
                        challenger_ip.append(item)

                np = len(challenger_ip)
                challenger_name = [''] * np
                challenger_progress = [0] * np
                acc_list = [0] * np
                acc_list[0] = 2
                mc = [0] * np
                ds = [0] * np
                ib = [False] * np

                for v in challenger_ip:
                    i = challenger_ip.index(v)
                    for q in [z for z in sd if z['user info']['Remote IP'] == v]:
                        challenger_name[i] = q['user info']['name']
                        if 'pfrac' in q['user info'].keys():
                            mc[i] = q['user info']['pfrac'][0]
                            ds[i] = q['user info']['pfrac'][1]
                        if q['user info']['in battle?'] is True and q['user info']['progress'] != 0:
                            ib[i] = True
                            challenger_progress[i] = q['user info']['progress']
                max_cl = max([0 if r is None else r for r in mc])
                m_ds = max([0 if s is None else s for s in ds])
            build_terms_of_battle()
            if max_cl > 0:
                buildn = max_cl
            else:
                deck = mw.col.decks.byName(f"{use_deck}")
                buildn = min(mw.col.sched.counts()[2], 100)
            if m_ds > 0:
                decksize = m_ds
            # else:
            #     decksize = self.ui.spinbox_bdecksize.value()  # shouldnt need this - join battle disabled for v < 1.35

            accepted_req = True
            self.timer_joined.start(10 * 1000)

            dyn_id = make_battle_deck(terms_of_battle, buildn)
            logger_ui.info('join_battle() completed')
            return
        else:
            logger_ui.info('join_battle() FAILED')
            ready_for_request = True
            return


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
        logger_ui.info('ConfDialog() instance initiated')


# noinspection PyCallByClass,PyArgumentList
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

        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        self.timer_ask = QTimer()
        self.timer_ask.timeout.connect(lambda: auto_timeout_reject())

        # custom callbacks
        self.ui.button_ask_BD.accepted.connect(lambda: accepted())
        self.ui.button_ask_BD.rejected.connect(lambda: rejected())
        logger_ui.info('AskDialog() instance initiated')


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
        # req_in_bat = indict['req in battle?']

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
        self.ui.lab_ask_bd_title.adjustSize()
        self.ui.lab_ask_bd_name.adjustSize()
        tit_w = self.ui.lab_ask_bd_title.width()
        nam_w = self.ui.lab_ask_bd_name.width()
        tand_w = tit_w + nam_w
        win_w = self.width()
        nam_x = int((win_w - tand_w) / 2)
        tit_x = int(nam_x + nam_w)
        self.ui.lab_ask_bd_name.move(nam_x, self.ui.lab_ask_bd_name.y())
        self.ui.lab_ask_bd_title.move(tit_x, self.ui.lab_ask_bd_title.y())
        logger_ui.debug('fill_options() completed')


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

        global opponent_problem
        if opponent_problem is True:
            self.ui.lab_reb_comms_title.setText(f"We were unable to make a full battle deck for\n"
                                                f"your opponent. You can still complete this deck\n"
                                                f"if you would like...\n\n"
                                                f"If you'd rather end this battle, just close\n"
                                                f"the Battle Anki window and reopen it!\n"
                                                f"Sorry about that!")
            ow = self.ui.lab_reb_comms_title.width()
            oh = self.ui.lab_reb_comms_title.height()
            self.ui.lab_reb_comms_title.adjustSize()
            w = self.ui.lab_reb_comms_title.width()
            h = self.ui.lab_reb_comms_title.height()
            dw = w - ow
            dh = h - oh
            self.resize((self.width() + dw), (self.height() + dh))
            bb_ox = self.ui.buttonBox_reb_comms.x()
            bb_oy = self.ui.buttonBox_reb_comms.y()
            bb_nx = bb_ox + (dw / 2)
            bb_ny = bb_oy + dh
            bb_w = self.ui.buttonBox_reb_comms.width()
            bb_h = self.ui.buttonBox_reb_comms.height()
            self.ui.buttonBox_reb_comms.setGeometry(bb_nx, bb_ny, bb_w, bb_h)

        global make_deck_problem
        if make_deck_problem is True:
            if made_count is None:
                self.ui.lab_reb_comms_title.setText(f"No cards matched the criteria you provided.\n"
                                                    f"Please try again...")
            elif type(made_count) == list:
                self.ui.lab_reb_comms_title.setText(f"We couldn't find enough cards with\n"
                                                    f"the criteria you provided\n\n"
                                                    f"Found:     {len(made_count)}\n"
                                                    f"Requested: {tried}\n"
                                                    f"Please try again...")
            elif type(made_count) == int:
                self.ui.lab_reb_comms_title.setText(f"We couldn't find enough cards with\n"
                                                    f"the criteria you provided\n\n"
                                                    f"Found:     {made_count}\n"
                                                    f"Requested: {tried}\n"
                                                    f"Please try again...")
            else:
                self.ui.lab_reb_comms_title.setText(f"There was a problem.\n"
                                                    f"Please try again..."
                                                    f"EC 892")
            ow = self.ui.lab_reb_comms_title.width()
            oh = self.ui.lab_reb_comms_title.height()
            self.ui.lab_reb_comms_title.adjustSize()
            w = self.ui.lab_reb_comms_title.width()
            h = self.ui.lab_reb_comms_title.height()
            dw = w - ow
            dh = h - oh
            self.resize((self.width() + dw), (self.height() + dh))
            bb_ox = self.ui.buttonBox_reb_comms.x()
            bb_oy = self.ui.buttonBox_reb_comms.y()
            bb_nx = bb_ox + (dw / 2)
            bb_ny = bb_oy + dh
            bb_w = self.ui.buttonBox_reb_comms.width()
            bb_h = self.ui.buttonBox_reb_comms.height()
            self.ui.buttonBox_reb_comms.setGeometry(bb_nx, bb_ny, bb_w, bb_h)
            mw.battle_window.showHome()
        logger_ui.info('RebComms() instance initiated')


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
        logger_ui.info('RebComms() instance initiated')


class OptDia(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set the form on the ask window
        self.ui = Ui_OptionsDialog()
        self.ui.setupUi(self)

        # center it
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        self.ui.label_version.setText(f'v{ba_ver}')
        self.ui.label_version.clicked.connect(lambda: openfolder(log_fold))

        self.ui.but_apply.clicked.connect(self.accept_Opts)

        if mw.pm.night_mode() is True:
            self.ui.frame_ctype.setStyleSheet("QFrame{background-color: rgb(255, 250, 250, 50);}"
                                              "QLabel#lab_cardtype{background-color: rgb(0, 0, 0, 0);}"
                                              "QLabel#lab_cardtype_2{background-color: rgb(0, 0, 0, 0);}")
            self.ui.frame_corder.setStyleSheet("QFrame{background-color: rgb(255, 250, 250, 50);}"
                                               "QLabel#lab_cardtype_3{background-color: rgb(0, 0, 0, 0);}"
                                               "QLabel#lab_cardtype_4{background-color: rgb(0, 0, 0, 0);}")
        else:
            self.ui.frame_ctype.setStyleSheet("QFrame{background-color: rgb(255, 250, 250);}"
                                              "QLabel#lab_cardtype{background-color: rgb(0, 0, 0, 0);}"
                                              "QLabel#lab_cardtype_2{background-color: rgb(0, 0, 0, 0);}")
            self.ui.frame_corder.setStyleSheet("QFrame{background-color: rgb(255, 250, 250);}"
                                               "QLabel#lab_cardtype_3{background-color: rgb(0, 0, 0, 0);}"
                                               "QLabel#lab_cardtype_4{background-color: rgb(0, 0, 0, 0);}")

        self.ui.checkBox_match_q.hide()
        self.ui.lab_matched_desc.hide()
        self.ui.checkBox_card_mature.hide()
        self.ui.checkBox_no_overdue.hide()

        self.set_OptDia_ui()

        logger_ui.info('OptDia() instance initiated')
        return

    def closeEvent(self, event):
        self.accept_Opts()

    def update_boxes(self):
        global matched_box
        global new_box
        global learn_box
        global mature_box
        global resched_box
        global today_only
        global decksize
        global requester
        global new_AND_review_box
        global card_order
        global joiners_box
        global card_order_str
        global card_type_str
        global spinbox_decksize

        try:
            spinbox_decksize = self.ui.spinbox_bdecksize.value()
            decksize = self.ui.spinbox_bdecksize.value()

            if self.ui.radioButton_random.isChecked():
                card_order = DYN_RANDOM
                card_order_str = 'Random order'
            elif self.ui.radioButton_due.isChecked():
                card_order = DYN_DUE
                card_order_str = 'In order due'
            elif self.ui.radioButton_odue.isChecked():
                card_order = DYN_DUEPRIORITY
                card_order_str = 'In order of relative overdueness'

            # if self.ui.checkBox_match_q.isChecked():
            #     matched_box = True
            # else:
            #     matched_box = False

            if self.ui.checkBox_card_new.isChecked():
                new_box = True
                card_type_str = 'New'
            else:
                new_box = False
            if self.ui.checkBox_card_learn.isChecked():
                learn_box = True
                card_type_str = 'Review'
            else:
                learn_box = False
            if self.ui.checkBox_newANDreview.isChecked():
                new_box = False
                learn_box = False
                new_AND_review_box = True
                card_type_str = 'New & Review'
            else:
                new_AND_review_box = False

            # if self.ui.checkBox_card_mature.isChecked():
            #     mature_box = True
            # else:
            #     mature_box = False

            if self.ui.checkBox_apply_resched.isChecked():
                resched_box = True
            else:
                resched_box = False
            if self.ui.checkBox_todayonly.isChecked():
                today_only = True
            else:
                today_only = False

            if self.ui.checkBox_joins.isChecked():
                joiners_box = True
            else:
                joiners_box = False

            if hasattr(mw, 'battle_window'):
                mw.battle_window.update_home_labels()

            logger_ui.debug('update_boxes() completed')
            return
        except Exception as err:
            show_and_log(f'There was a problem...'
                         f'Sorry!'
                         f'EC 545')
            mw.battle_window.timer.stop()

    def set_OptDia_ui(self):
        self.ui.spinbox_bdecksize.setValue(spinbox_decksize)
        self.ui.checkBox_card_learn.setChecked(learn_box)
        self.ui.checkBox_newANDreview.setChecked(new_AND_review_box)
        self.ui.checkBox_card_new.setChecked(new_box)
        if card_order == DYN_RANDOM:
            self.ui.radioButton_random.setChecked(True)
        else:
            self.ui.radioButton_random.setChecked(False)
        if card_order == DYN_DUE:
            self.ui.radioButton_due.setChecked(True)
        else:
            self.ui.radioButton_due.setChecked(False)
        if card_order == DYN_DUEPRIORITY:
            self.ui.radioButton_odue.setChecked(True)
        else:
            self.ui.radioButton_odue.setChecked(False)
        self.ui.checkBox_apply_resched.setChecked(resched_box)
        self.ui.checkBox_todayonly.setChecked(today_only)
        self.ui.checkBox_joins.setChecked(joiners_box)

        self.show()

        logger_ui.info(f'set_OptDia_ui() completed')
        return

    def accept_Opts(self):
        # if new_box and mature_box:
        #     show_and_log("New cards can't be mature...\n"
        #                  "you haven't done them yet!")
        #     return False
        if self.ui.checkBox_card_new.isChecked() and self.ui.checkBox_todayonly.isChecked():
            show_and_log("New cards can't be due today because  \n"
                         "   they don't have a due date\n\n"
                         " You'll need to uncheck Bailey Mode\n"
                         "    if you want to do new cards...")
            return False
        if self.ui.checkBox_card_new.isChecked() and\
                (self.ui.radioButton_due.isChecked() or self.ui.radioButton_odue.isChecked()):
            show_and_log("New cards can't be due today because\n"
                         "   they don't have a due date\n\n"
                         "You'll need to change the order to random  \n"
                         "    if you want to do new cards...")
            return False

        else:
            self.update_boxes()
            get_loc_req_opts()
            self.close()

            logger_user.info('accept_Opts() completed')
            return


def opts_open():
    mw.opts = QDialog()
    mw.opts = OptDia()
    mw.opts.set_OptDia_ui()

    logger_user.info('opts_open() clicked & completed: tried new OptDia()')
    return


def inbattle_status():
    global inbattle_str
    if inbattle is False:
        inbattle_str = 'Ready'
        logger_utils.debug(f'inbattle_status() completed: {inbattle_str}')
        return 'Ready'
    elif inbattle is True:
        inbattle_str = 'In Battle'
        logger_utils.debug(f'inbattle_status() completed: {inbattle_str}')
        return 'In Battle'
    elif inbattle is None:
        inbattle_str = 'Away'
        logger_utils.debug(f'inbattle_status() completed: {inbattle_str}')
        return 'Away'


def show_and_log(instr: object):
    showInfo(instr)
    logger_ui.warning(f'\n{instr}')


def name_str(instr: str, tail: int) -> str:
    # rejoined = ' rejoined the game!'  # 0
    # joined = ' joined the game!'      # 1
    # left = ' left the game...'        # 2
    # not_here = ' is starting...'      # 3
    # name_only = ''                    # 4
    # tails = [rejoined, joined, left, not_here, name_only]
    x = next((len(t) for t in tails if t in instr), None)
    if x:
        logger_utils.debug('name_str() completed')
        return str(instr[:-x] + tails[tail])

    else:
        logger_utils.debug('name_str() completed')
        return str(instr + tails[tail])


def cards_time_today():
    global cards_today
    global time_today
    today_stats = mw.col.stats().todayStats()
    today_list = today_stats.split(" ")
    cards_td, time_td = mw.col.db.first("select count(), sum(time)/1000 "
                                        "from revlog where id > ? ",
                                        (mw.col.sched.dayCutoff - 86400) * 1000,
                                        )
    cards_today = cards_td or 0
    time_secs = time_td or 0  # in seconds!!!
    if time_secs > 0:
        ty_res = time.gmtime(time_secs)
        time_today = time.strftime("%H:%M", ty_res)
        if int(time_today[0]) == 0:
            time_today = time_today[1:]
    else:
        time_today = '0:00'
    logger_utils.info('cards_time_today() completed')


def answered_card(*args, **kwargs):
    global cards_left
    if inbattle:
        cards_left = sum(list(mw.col.sched.counts()))
    cards_time_today()
    logger_user.info('answered_card() completed')


def auto_timeout_reject():
    mw.ask_deck.timer_ask.stop()
    if inbattle is not True:
        mw.ask_deck.close()
        mw.battle_window.timer_undo_rejected.start(6 * 1000)
    logger_utils.info('auto_timeout_reject() completed')


def check_socks(readables=None, writeables=None, exceptioners=None, tmout: float = 0.0) -> list:
    try:
        if readables is None:
            readables = []
        if writeables is None:
            writeables = []
        if exceptioners is None:
            exceptioners = []
        ready_reads, ready_writes, in_errors = select.select(readables, writeables, exceptioners, tmout)
        logger_utils.debug('check_socks() completed')
        return [ready_reads, ready_writes, in_errors]
    except:
        show_and_log(f'Sorry, there was a problem with Battle Anki...'
                     f'EC 981')


def receive():
    global server_data
    global sd
    try:
        logger_comms.warning('receive() STARTING OUTER WHILE LOOP')
        while True:
            if shutdown is True:
                break
            if threading.main_thread().is_alive() is False:
                break
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
                        show_and_log(f'Sorry, there was a problem with Battle Anki...'
                                     f'EC 999')
                    if len(full_msg) == msg_len:
                        try:
                            threadlocker.acquire()
                            server_data = str_to_dict(full_msg)
                            if mehost:
                                sd = ifimhost(server_data['clients connected'])
                            else:
                                sd = server_data['clients connected']
                        finally:
                            threadlocker.release()
                            logger_comms.debug('receive() completed')
                except:
                    pass
    except Exception as excepti:
        show_and_log(f'Sorry, there was a problem with Battle Anki...\n'
                     f'EC 1010')
    finally:
        logger_comms.warning('receive() BROKE OUTER WHILE LOOP')
        return


def send_pulse():
    global local_data
    last_send = 0
    try:
        if time.time() - last_send > 1.5:
            last_send = time.time()
            send_str = dict_to_str(local_data)
            msg_whead = f'{len(send_str):<{header}}' + send_str
            msg_send = msg_whead.encode(msg_format)
            ready_to_send = check_socks(writeables=[mw.socket])
            if len(ready_to_send[1]) > 0:
                mw.socket.send(msg_send)
        logger_comms.debug('send_pulse() completed')
    except Exception as hj:
        show_and_log(f'There was a problem...\n'
                     f'Sorry!\n'
                     f'EC 1865\n'
                     f'{hj}')
        mw.battle_window.timer.stop()


def start_client_conn():  # ba_startup and battle_connect
    global loc_rem_ip
    global startup
    exists = hasattr(mw, 'socket')
    try:
        logger_comms.info('start_client_conn() STARTED')
        if not exists:  # or (exists is True and 'closed' not in mw.socket):
            mw.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mw.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096 * 2)
            print('Socket Created')
            if startup:
                mw.socket.settimeout(0.3)
                startup = False
            mw.socket.connect((server, port))
            loc_rem_ip = str(mw.socket.getsockname())
            print('Connection initiated with', server)
            mw.is_connected = True
        logger_comms.info('start_client_conn() completed')

    except socket.error as e:
        show_and_log(f"There was a problem starting Battle Anki...\n\n"
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
    logger_utils.debug('dict_to_str() completed')
    return out_str


def str_to_dict(in_str: str):
    try:
        out_dict = json.loads(in_str)
        logger_utils.debug('str_to_dict() completed')
        return out_dict
    except json.JSONDecodeError as jsonerro:
        show_and_log(f'there was a problem\n'
                     f'{jsonerro}'
                     f'str_to_dict\n'
                     f'EC 189m')
    except RecursionError as recur:
        show_and_log(f'there was a problem\n'
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
            logger_utils.warning('delete_battle_decks() DELETED 1 Battle Deck')
            d += 1
        mw.moveToState("deckBrowser")
        mw.maybeReset()
    except Exception as msg:
        show_and_log(f'Sorry, there was an error removing the Battle Deck...\n'
                     f'Error Code 1775\n'
                     f'{msg}')
    finally:
        logger_utils.info('delete_battle_decks() completed')
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
        logger_comms.info('requesters_cards_for_matching() completed')
    else:
        show_and_log(f"Sorry, no cards matched the criteria provided."
                     f"requesters_cards_for_matching"
                     f"EC 1079")


def build_terms_of_battle():
    global new_box
    global learn_box
    global mature_box
    global today_only
    global terms_of_battle
    terms_of_battle = f'deck:{use_deck} {xtra_search} ' if xtra_search else f'deck:{use_deck} '
    if new_box:
        terms_of_battle += " is:new"
    if learn_box:
        terms_of_battle += " -is:new"
    if mature_box:
        terms_of_battle += " prop:ivl>21"
    if today_only:
        terms_of_battle += " is:due"
    logger_utils.info('build_terms_of_battle() completed')


def accepted():
    logger_user.info('accepted() clicked')
    global accepted_req
    global ready_for_request
    global matched_size
    global dyn_id
    global make_deck_problem
    ready_for_request = False
    build_terms_of_battle()
    if matched_box:
        # send applicable cards to server
        build_matched_list()
        if matched_size >= decksize:
            accepted_req = True
            dyn_id = make_battle_deck(matched_terms)
        else:
            accepted_req = True
            make_deck_problem = True
            show_and_log(f'There are not enough cards that match\n'
                         f'the criteria! Try again!\n\n'
                         f'      Only this many match:  {matched_size}\n'
                         f'But we tried for this many:  {decksize}')
    elif not matched_box:
        accepted_req = True
        dyn_id = make_battle_deck(terms_of_battle)
    get_local_data()
    mw.battle_window.timer_undo_accepted.start(15 * 1000)
    logger_utils.info('accepted() completed')


def rejected():
    logger_user.debug('rejected() clicked')
    global ready_for_request
    mw.ask_deck.timer_ask.stop()
    ready_for_request = False
    show_and_log(f'You are unable to receive requests for 30 seconds...')
    mw.battle_window.timer_undo_rejected.start(30 * 1000)
    logger_utils.info('rejected() clicked & completed')


def req_was_denied(show: bool = True):
    global inbattle
    global local_data
    global challenger_ip
    global challenger_name
    global challenger_progress
    global acc_list
    global conn

    mw.battle_window.timer_denied.stop()
    local_data['request options']['req Remote IP'] = ''
    local_data['request options']['req name'] = ''

    if inbattle is True:
        for rd in [x for x in sd if x['user info']['Remote IP'] in challenger_ip
                   if x['user info']['in battle?'] is not True]:
            i = challenger_ip.index(rd['user info']['Remote IP'])
            challenger_ip.pop(i)
            challenger_name.pop(i)
            challenger_progress.pop(i)
            acc_list.pop(i)
            conn.pop(i)

    if inbattle is not True:
        global requesters_cards
        global terms_of_battle
        requesters_cards = list()
        terms_of_battle = str()
        mw.battle_window.undorequest()
        mw.battle_window.showHome()
        mw.battle_window.timer_bar.stop()
        mw.battle_window.reset()
        show_and_log(f"Sorry, looks like the people you invited\n"
                     f"can't play right now...\n\n"
                     f"Maybe you are too strong of an AnKing?")
    logger_utils.info('req_was_denied() completed')


def undo_rejected():
    global popped_req
    global ready_for_request
    popped_req = False
    ready_for_request = True
    global challenger_name
    global requesters_cards
    global challenger_ip
    global challenger_progress
    challenger_name = []
    requesters_cards = list()
    challenger_ip = []
    challenger_progress = []
    mw.battle_window.timer_undo_rejected.stop()
    logger_utils.info('undo_rejected() completed')


def latestart():
    global challenger_name
    global challenger_ip
    global local_data
    global dyn_id
    if matched_box is False:
        dyn_id = make_battle_deck(terms_of_battle)
    elif matched_box is True:
        dyn_id = make_battle_deck(matched_terms)
    mw.battle_window.timer_undo_request.start(15 * 1000)
    logger_utils.info('latestart() completed')


def check_if_req_accepted():
    global matched_list
    global decksize
    global challenger_name
    global challenger_ip
    global sd
    global local_data
    global popped_comms
    global matched_terms
    global chal_index
    # try:
    if (popped_comms is False) and (inbattle is not True) and len(local_data['request options']['req Remote IP']) > 0:
        for rd in [d for d in sd if d['user info']['Remote IP'] in challenger_ip
                   if d['user info']['accepted req'] is True if d['user info']['in battle?']]:
            chal_index = challenger_ip.index(rd['user info']['Remote IP'])
            challenger_ip.insert(0, challenger_ip.pop(chal_index))
            challenger_name.insert(0, challenger_name.pop(chal_index))
            global opponent_problem
            if 'deck problem' in rd['user info'].keys():
                if rd['user info']['deck problem'] is True:
                    opponent_problem = rd['user info']['deck problem']
            if matched_box is True:
                matched_terms = rd['matched terms']
            popped_comms = True
            global challenger_progress
            challenger_progress[0] = 0
            latestart()
            mw.comms = QDialog()
            mw.comms = RebComms()
            mw.comms.show()
            logger_utils.info('check_if_req_accepted() and yes it was')
            return
    logger_utils.debug('check_if_req_accepted() completed OUTSIDE of IF FOR loop')


def check_for_joins():
    global challenger_name
    global challenger_ip
    global sd
    global local_data
    global challenger_progress
    global acc_list
    global conn

    if inbattle and sd:
        for rd in [d for d in sd
                   if 'req Remote IPs' in d['request options'].keys()
                   if loc_rem_ip in d['request options']['req Remote IPs']
                   if d['user info']['Remote IP'] not in challenger_ip
                   if d['request options']['req Remote IP'] == ''
                   if d['user info']['accepted req']
                   if d['user info']['in battle?']
                   ]:
            challenger_ip.append(rd['user info']['Remote IP'])
            challenger_name.append(rd['user info']['name'])
            challenger_progress.append(0)
            acc_list.append(0)
            conn.append(2)  # will add 'joined the game' to progbar text
    logger_utils.debug('check_for_joins() completed')


def check_for_requests():
    global popped_req
    global challenger_name
    global challenger_ip
    global chal_index
    global sd
    global local_data
    global requesters_cards
    global ready_for_request
    # try:
    if popped_req is False and ready_for_request is True and inbattle is False:
        # if local_data['user info']['in battle?'] is False:
        if len(sd) > 1:
            for rd in [c for c in sd
                       if len(c['request options']['req Remote IP']) > 0
                       if (loc_rem_ip in c['request options']['req Remote IP'] or
                           ('req Remote IPs' in c['request options'].keys() and
                            loc_rem_ip in c['request options']['req Remote IPs']))
                       ]:
                if not_dup_request(rd['user info']['Remote IP'], rd['user info']['in battle?']):
                    if str(rd['user info']['name']) not in challenger_name:
                        challenger_name.insert(0, str(rd['user info']['name']))
                    if str(rd['user info']['Remote IP']) not in challenger_ip:
                        challenger_ip.insert(0, str(rd['user info']['Remote IP']))

                    if 'req Remote IPs' in rd['request options'].keys():
                        for nc in [c for c in sd if c['user info']['Remote IP'] not in challenger_ip
                                   if c['user info']['Remote IP'] != loc_rem_ip
                                   if c['user info']['Remote IP'] in rd['request options']['req Remote IPs']
                                   ]:
                            challenger_ip.append(nc['user info']['Remote IP'])
                            challenger_name.append(nc['user info']['name'])
                            challenger_progress.append(0)

                    if len(rd['card ids']) > 1:
                        requesters_cards = list(rd['card ids'])
                    mw.ask_deck = QDialog()
                    mw.ask_deck = AskDialog()
                    mw.ask_deck.fill_options(rd['request options'])

                    popped_req = True
                    ready_for_request = False

                    mw.ask_deck.timer_ask.start(26 * 1000)
                    mw.ask_deck.show()
                    logger_comms.debug('check_for_requests() completed and initiatied AskDialog')
    logger_comms.debug('check_for_requests() completed WITHOUT AskDialog')
    # except Exception as meg:
    #     show_and_log(f'{meg}')


def not_dup_request(ip, c_status):
    i = readys['ips'].index(ip)
    ct = int(time.time())
    ts = readys['last battle start'][i]
    ms = readys['my last bat start']
    if ct - ms <= 30:
        logger_utils.debug('not_dup_request() returned False'
                          'if ct - ms <= 30:')
        return False
    elif c_status is True and ct - ts >= 15:
        # they are IN battle and started MORE than 15s ago
        logger_utils.debug('not_dup_request() returned False'
                          'elif c_status is True and ct - ts >= 15:')
        return False
    else:
        logger_utils.debug('not_dup_request() returned True')
        return True


def record_readys():
    global readys
    global sd

    readys['cc'] = []

    for rd in sd:
        readys['cc'].append(rd['user info']['Remote IP'])

        if rd['user info']['Remote IP'] == loc_rem_ip:
            if rd['user info']['in battle?'] is not True and inbattle is True:
                readys['my last bat start'] = int(time.time())
        elif rd['user info']['Remote IP'] in readys['ips']:
            i = readys['ips'].index(rd['user info']['Remote IP'])
            if rd['user info']['in battle?'] is True and readys['last status'][i] is not True:
                readys['last battle start'][i] = int(time.time())
                readys['last status'][i] = rd['user info']['in battle?']
            else:
                readys['last status'][i] = rd['user info']['in battle?']
        elif rd['user info']['Remote IP'] not in readys['ips']:
            readys['ips'].append(rd['user info']['Remote IP'])
            readys['names'].append(rd['user info']['name'])
            readys['last status'].append(rd['user info']['in battle?'])
            readys['last battle start'].append(0)

    for ip in [x for x in readys['ips'] if x not in readys['cc']]:
        z = readys['ips'].index(ip)
        readys['ips'].pop(z)
        readys['names'].pop(z)
        readys['last status'].pop(z)
        readys['last battle start'].pop(z)

    logger_utils.debug('record_readys() completed')


def confOK():
    logger_user.debug('confOK() clicked')
    global inbattle
    get_loc_req_opts()
    if mw.battle_window.get_request_data():
        mw.battle_window.startWaitingBar()
        build_terms_of_battle()
        if matched_box is True:
            requesters_cards_for_matching()
        get_local_data()
        if can_sendittt is True:
            mw.battle_window.showWait()
            mw.battle_window.timer_denied.start(30 * 1000)
        logger_utils.info('confOK() completed and passed')
    else:
        logger_utils.info('confOK() FAILED')
        inbattle = False


def sendittt():
    logger_user.info('sendittt() clicked')
    # try:
    mw.confpopup = QDialog()
    mw.confpopup = ConfDialog()
    mw.confpopup.show()
    # except:
    #     show_and_log("something went wrong...")


def store_before_send():
    global store_data
    store_data['request options']['both box'] = new_AND_review_box
    store_data['request options']['deck size'] = decksize
    store_data['request options']['matched box'] = matched_box
    store_data['request options']['new box'] = new_box
    store_data['request options']['learn box'] = learn_box
    store_data['request options']['mature box'] = mature_box
    store_data['request options']['resched box'] = resched_box
    store_data['request options']['due box'] = today_only
    store_data['request options']['requester'] = str(mw.pm.name)

    logger_ui.debug('store_before_send() completed')
    return


def recall_after_battle():
    global new_AND_review_box
    global decksize
    global matched_box
    global new_box
    global learn_box
    global mature_box
    global resched_box
    global today_only
    new_AND_review_box = store_data['request options']['both box']
    decksize = store_data['request options']['deck size']
    matched_box = store_data['request options']['matched box']
    new_box = store_data['request options']['new box']
    learn_box = store_data['request options']['learn box']
    mature_box = store_data['request options']['mature box']
    resched_box = store_data['request options']['resched box']
    today_only = store_data['request options']['due box']

    logger_ui.debug('store_before_send() completed')
    return


def get_loc_req_opts():
    global local_data
    local_data['request options']['both box'] = new_AND_review_box
    local_data['request options']['deck size'] = decksize
    local_data['request options']['matched box'] = matched_box
    local_data['request options']['new box'] = new_box
    local_data['request options']['learn box'] = learn_box
    local_data['request options']['mature box'] = mature_box
    local_data['request options']['resched box'] = resched_box
    local_data['request options']['due box'] = today_only
    local_data['request options']['requester'] = str(mw.pm.name)

    logger_ui.debug('get_loc_req_opts() completed')
    return


def get_local_data():
    logger_utils.debug('get_local_data() STARTED')
    global local_data
    global loc_rem_ip
    global inbattle
    global accepted_req
    global myprogress
    global matched_size
    global make_deck_problem
    global challenger_ip
    global challenger_name

    record_readys()

    local_data['matched size'] = matched_size
    local_data['matched terms'] = matched_terms
    local_data['window open'] = window_open
    local_data['user info']['Connected'] = mw.is_connected
    local_data['user info']['in battle?'] = inbattle
    local_data['user info']['accepted req'] = accepted_req
    local_data['user info']['progress'] = myprogress
    local_data['user info']['Remote IP'] = loc_rem_ip
    local_data['user info']['name'] = str(mw.pm.name)
    local_data['user info']['deck problem'] = make_deck_problem
    local_data['user info']['pfrac'] = [cards_left, decksize]

    if challenger_name and challenger_ip:
        local_data['request options']['req names'] = challenger_name
        local_data['request options']['req Remote IPs'] = challenger_ip

    if badgeview is True:
        local_data['user info']['cards today'] = cards_today
        local_data['user info']['time today'] = time_today
    if badgeview is False:
        if 'cards today' in local_data['user info'].keys():
            del local_data['user info']['cards today']
            local_data['c_t'] = cards_today
        local_data['user info']['time today'] = ' '
    logger_utils.debug('get_local_data() completed')


def fmt_n_log(str_chr: list, le=80, str_log=''):
    # str_char in fmt of a list of tuples [(s1,c1), (s2,c2)]
    # to omit the header linebreak '\n',
    # place False as third item in tuple [(s1,c1, False), (s2,c2)]
    try:
        for s in range(len(str_chr)):
            if len(str_chr[s]) > 2 and str_chr[s][2] is False:
                str_log += str_chr[s][0]
            else:
                p1 = f'{str_chr[s][0]:{str_chr[s][1]}^{le}}'
                str_log += '\n' + p1
        return str_log
    except:
        show_and_log(f'There was a problem with Battle Anki...'
                     f'Error Code 2520')


def log_bat_info(add_str=''):
    l1 = f'[{mw.pm.name} vs. {challenger_name}]'
    l2 = f'[{myprogress}% vs. {challenger_progress}%]'
    l3 = f'[cards_left, decksize] = {[cards_left, decksize]}]'
    sl = fmt_n_log([(l1, '$'), (l2, '-'), (l3, '*')])
    if add_str:
        sl += add_str
    logger_user.info(sl)


def log_check_prog():
    global one_to_ten
    global ff_ff
    global nty

    if inbattle is not True:
        one_to_ten = False
        ff_ff = False
        nty = False
        return
    elif inbattle is True and (1 < myprogress < 10) and len(challenger_name) > 0 and one_to_ten is False:
        log_bat_info()
        one_to_ten = True
    elif inbattle is True and (45 < myprogress < 55) and len(challenger_name) > 0 and ff_ff is False:
        log_bat_info()
        ff_ff = True
    elif inbattle is True and myprogress > 90 and len(challenger_name) > 0 and nty is False:
        log_bat_info()
        nty = True
    else:
        return


def running():
    logger_utils.debug('running() STARTED')
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
            check_if_req_accepted()
            log_check_prog()
            if inbattle is False:
                check_for_requests()
        logger_utils.debug('running() completed')
    except Exception as meg:
        show_and_log(f'{meg}')
        mw.battle_window.timer.stop()
        if mw.battle_window.main_win.isVisible():
            mw.battle_window.main_win.setDisabled(True)


def battle_connect():  # on action.triggered.connect(lambda: battle_connect())
    logger_user.info('battle_connect() clicked')
    try:
        mw.battle_window.showHome()
        mw.battle_window.startLoadBar()
        if mw.is_connected is False:
            start_client_conn()
        if 'utd_ver' in server_data.keys():
            running()
            mw.battle_window.timer.start(2500)
            if server_data['utd_ver'] is not None:
                c1 = str(local_data['ver']).split('.')
                s1 = str(server_data['utd_ver']).split('.')

                if int(c1[0]) < int(s1[0]) or int(c1[1]) < int(s1[1]):
                    utd_ver = str(server_data['utd_ver'])
                    show_and_log(f'A Battle Anki upgrade is available!\n\n'
                                 f' The most current version is:\n'
                                 f'         {utd_ver}\n\n'
                                 f'     Your version is:\n'
                                 f'         {ba_ver}\n\n')
        logger_utils.info('battle_connect() completed')
    except Exception as e1:
        show_and_log(f"There was a problem starting Battle Anki...\n\n"
                     f"Please check the config options in\n"
                     f"Tools -> Addons -> Battle Anki -> Config\n"
                     f"If problems persist, please report:\n\n"
                     f"Battle Anki Error Code 1282")
        logger_comms.warning(f'battle_connect 2421\n'
                             f'{e1}')
        mw.battle_window.timer.stop()
        if mw.battle_window.main_win.isVisible():
            mw.battle_window.main_win.setDisabled(True)


def ba_startup():  # on gui_hooks._ProfileDidOpenHook().append(ba_startup)
    logger_user.info(f'ba_startup() clicked by: {mw.pm.name}')
    global bw

    if not hasattr(mw, 'battle_window'):
        mw.battle_window = MainWindow()
        bw = mw.battle_window
    try:
        start_client_conn()
        running()
        if not mw.battle_window.timer.isActive():
            mw.battle_window.timer.start(2500)
        if 'Battle Anki Receiver' not in threading.enumerate():
            r_th = threading.Thread(target=receive, daemon=False, name='Battle Anki Receiver')
            r_th.start()
            logger_comms.info(f'2358 Started receive thread from ba_startup')
        logger_utils.info('ba_startup() completed')
    except socket.error:
        show_and_log(f"There was a problem starting Battle Anki... Sorry!\n\n"
                     f"Please remember this code:\n"
                     f"Error Code 1208")
        mw.battle_window.timer.stop()


def bye_to_server():
    logger_comms.info('bye_to_server() STARTED')
    mw.socket.settimeout(0.0)
    try:
        msg_whead = f'{len(disconn_msg):<{header}}' + disconn_msg
        msg_send = msg_whead.encode(msg_format)
        ready_to_send = check_socks(writeables=[mw.socket])
        if len(ready_to_send[1]) > 0:
            mw.socket.send(msg_send)
            mw.socket.shutdown()
            mw.socket.close()
            logger_comms.info('bye_to_server() SHUTDOWN THE SOCKET')
        logger_comms.info('bye_to_server() completed')
    except:
        show_and_log(f'There was a problem closing the connection to the server...\n'
                     f'Error Code 2383\n')
    # finally:
    #     return


def close_down():
    global shutdown
    shutdown = True
    try:
        mw.battle_window.close_all()
    finally:
        logger_utils.info('close_down() completed')
        logging.shutdown()
        return


def dummy_close_down():
    show_and_log(f'For Battle Anki to work properly,'
                 f'you will need to restart Anki after'
                 f'you are done with the add-ons window...')
    close_down()
    return


def make_battle_deck(searchterms, buildsize=None):
    logger_utils.warning('make_battle_deck() STARTED')
    global decksize
    global matched_list
    global resched_box
    global inbattle
    global n
    global make_deck_problem
    global made_count
    global tried
    if buildsize is None:
        buildsize = decksize
    created_b_deck = False
    n = 1
    try:
        deck = mw.col.decks.byName(f"{use_deck}")
        did = mw.col.decks.id_for_name(f"{use_deck}")
        did = int(did)
        mw.col.decks.select(did)
        conf = mw.col.decks.confForDid(did)
        if mw.col.decks.selected() != did:
            mw.col.decks.select(did)
            deck = mw.col.decks.confForDid(did)
            cur = mw.col.decks.current()
            show_and_log(f'There may have been a problem creating the deck...\n'
                         f"if something doesn't look right, just delete\n"
                         f"the blue deck named 'Battle Deck 1'")
        elif mw.col.decks.selected() == did:
            deck = mw.col.decks.current()
        else:
            show_and_log(f'There was a problem making the deck...\n'
                         f'Sorry!')
    except:
        show_and_log(f'There seems to be a problem in your Config file...\n'
                     f'Please navigate to:\n\n'
                     f'Tools -> Add-ons -> (select Battle Anki) -> click Config\n\n'
                     f'and double check that the word for the "use_deck":\n'
                     f'matches a deck that actually exists in your collection\n'
                     f'Error Code 1298')
        logger_ui.info(f'')
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
    dyn["terms"] = [[str(searchterms), int(buildsize), card_order]]  # DYN_DUEPRIORITY]]
    mw.col.decks.save(dyn)
    created_b_deck = True
    made_count = mw.col.sched.rebuildDyn()
    if made_count is None:  # dyn["id"]
        delete_battle_decks()
        make_deck_problem = True
        if accepted_req is True:
            if inbattle is None:
                inbattle = False
            return show_and_log(_("No cards matched the criteria you provided."))
        else:
            return
    elif type(made_count) == list:
        if not len(made_count) == buildsize:
            delete_battle_decks()
            tried = buildsize
            make_deck_problem = True
            if accepted_req is True:
                return show_and_log(_(f"We couldn't find enough cards with\n"
                                      f"the criteria you provided\n"
                                      f"Found:     {len(made_count)}\n"
                                      f"Requested: {tried}\n"
                                      f"Please try again."))
            else:
                return
    elif type(made_count) == int:
        if not made_count == buildsize:
            delete_battle_decks()
            tried = buildsize
            make_deck_problem = True
            if accepted_req is True:
                return show_and_log(_(f"We couldn't find enough cards with\n"
                                      f"the criteria you provided\n"
                                      f"Found:     {made_count}\n"
                                      f"Requested: {tried}\n"
                                      f"Please try again."))
            else:
                return
    make_deck_problem = False
    mw.moveToState("review")
    mw.battle_window.showBattle()
    logger_utils.warning('make_battle_deck() COMPELTED SUCCESSFULLY')
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
    logger_utils.info('build_matched_list() completed')
    # except:
    #     pass


def openfolder(filename=log_fold):
    logger_user.info('openfolder() clicked')
    try:
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])
        logger_utils.info('openfolder() completed')
    except:
        pass
    finally:
        logger_utils.warning('openfolder() had a problem')


def ifimhost(inlist: list):
    logger_utils.debug(f'[SERVER DATA]:\n'
                       f'[Connected]: {len(sd)}\n'
                       f'{dict_to_str(server_data)}')
    logger_utils.debug('ifimhost() STARTED')
    for d in inlist:

        if 'cards today' in d['user info'].keys():
            cds = str(d['user info']['cards today'])
        elif 'c_t' in d['user info'].keys():
            cds = str(d['user info']['c_t'])
        else:
            cds = ''

        v = str(d['ver']) if 'ver' in d.keys() else ''

        idx = inlist.index(d)
        q = inlist.pop(idx)
        q['user info']['name'] = f"{v}${cds}${q['user info']['name']}"
        inlist.insert(idx, q)
    logger_utils.debug('ifimhost() completed')
    return inlist


# def test():

action = QAction("Battle Anki...", mw)
action.triggered.connect(lambda: battle_connect())
# action.triggered.connect(lambda: test())
mw.form.menuTools.addAction(action)

gui_hooks.profile_did_open.append(start_logger)
gui_hooks.profile_will_close.append(close_down)
# gui_hooks.addons_dialog_will_show.append(dummy_close_down)
gui_hooks.reviewer_did_answer_card.append(answered_card)
gui_hooks.profile_did_open.append(ba_startup)