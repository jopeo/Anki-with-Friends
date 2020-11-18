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


class Ui_AskDialog(object):
    def setupUi(self, AskDialog):
        AskDialog.setObjectName("AskDialog")
        AskDialog.resize(330, 400)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AskDialog.sizePolicy().hasHeightForWidth())
        AskDialog.setSizePolicy(sizePolicy)
        AskDialog.setMinimumSize(QtCore.QSize(330, 400))
        AskDialog.setMaximumSize(QtCore.QSize(330, 400))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("battle_anki_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AskDialog.setWindowIcon(icon)
        self.button_ask_BD = QtWidgets.QDialogButtonBox(AskDialog)
        self.button_ask_BD.setGeometry(QtCore.QRect(70, 320, 191, 51))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_ask_BD.sizePolicy().hasHeightForWidth())
        self.button_ask_BD.setSizePolicy(sizePolicy)
        self.button_ask_BD.setMaximumSize(QtCore.QSize(200, 200))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.button_ask_BD.setFont(font)
        self.button_ask_BD.setOrientation(QtCore.Qt.Horizontal)
        self.button_ask_BD.setStandardButtons(QtWidgets.QDialogButtonBox.No|QtWidgets.QDialogButtonBox.Yes)
        self.button_ask_BD.setCenterButtons(True)
        self.button_ask_BD.setObjectName("button_ask_BD")
        self.lab_ask_bd_title = QtWidgets.QLabel(AskDialog)
        self.lab_ask_bd_title.setGeometry(QtCore.QRect(130, 10, 71, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lab_ask_bd_title.setFont(font)
        self.lab_ask_bd_title.setAlignment(QtCore.Qt.AlignCenter)
        self.lab_ask_bd_title.setObjectName("lab_ask_bd_title")
        self.lab_ask_bd_name = QtWidgets.QLabel(AskDialog)
        self.lab_ask_bd_name.setGeometry(QtCore.QRect(10, 50, 311, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.lab_ask_bd_name.setFont(font)
        self.lab_ask_bd_name.setAlignment(QtCore.Qt.AlignCenter)
        self.lab_ask_bd_name.setObjectName("lab_ask_bd_name")
        self.lab_ask_bd_text = QtWidgets.QLabel(AskDialog)
        self.lab_ask_bd_text.setGeometry(QtCore.QRect(60, 80, 201, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lab_ask_bd_text.setFont(font)
        self.lab_ask_bd_text.setAlignment(QtCore.Qt.AlignCenter)
        self.lab_ask_bd_text.setWordWrap(True)
        self.lab_ask_bd_text.setObjectName("lab_ask_bd_text")
        self.lab_ask_bd_options = QtWidgets.QLabel(AskDialog)
        self.lab_ask_bd_options.setGeometry(QtCore.QRect(230, 120, 71, 151))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lab_ask_bd_options.setFont(font)
        self.lab_ask_bd_options.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lab_ask_bd_options.setWordWrap(True)
        self.lab_ask_bd_options.setObjectName("lab_ask_bd_options")
        self.lab_ask_bd_text_2 = QtWidgets.QLabel(AskDialog)
        self.lab_ask_bd_text_2.setGeometry(QtCore.QRect(50, 260, 231, 71))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lab_ask_bd_text_2.setFont(font)
        self.lab_ask_bd_text_2.setAlignment(QtCore.Qt.AlignCenter)
        self.lab_ask_bd_text_2.setWordWrap(True)
        self.lab_ask_bd_text_2.setObjectName("lab_ask_bd_text_2")
        self.lab_ask_bd_options_text = QtWidgets.QLabel(AskDialog)
        self.lab_ask_bd_options_text.setGeometry(QtCore.QRect(10, 130, 211, 131))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lab_ask_bd_options_text.setFont(font)
        self.lab_ask_bd_options_text.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lab_ask_bd_options_text.setWordWrap(True)
        self.lab_ask_bd_options_text.setObjectName("lab_ask_bd_options_text")

        self.retranslateUi(AskDialog)
        self.button_ask_BD.accepted.connect(AskDialog.accept)
        self.button_ask_BD.rejected.connect(AskDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AskDialog)

    def retranslateUi(self, AskDialog):
        _translate = QtCore.QCoreApplication.translate
        AskDialog.setWindowTitle(_translate("AskDialog", "Battle Deck Invitation"))
        self.lab_ask_bd_title.setText(_translate("AskDialog", "Hello!"))
        self.lab_ask_bd_name.setText(_translate("AskDialog", "(name)"))
        self.lab_ask_bd_text.setText(_translate("AskDialog", "has invited you to a battle deck with the following options:"))
        self.lab_ask_bd_options.setText(_translate("AskDialog", "(options)"))
        self.lab_ask_bd_text_2.setText(_translate("AskDialog", "Click \"Yes\" to start the game!\n"
"Do you accept?"))
        self.lab_ask_bd_options_text.setText(_translate("AskDialog", "Deck size:\n"
"Matched (identical cards):\n"
"New cards:\n"
"Review cards:\n"
"Mature cards:\n"
"Reschedule based on answers:\n"
"Due today only:"))
