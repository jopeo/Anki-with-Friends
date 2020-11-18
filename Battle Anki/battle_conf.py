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


class Ui_bat_conf_Dialog(object):
    def setupUi(self, bat_conf_Dialog):
        bat_conf_Dialog.setObjectName("bat_conf_Dialog")
        bat_conf_Dialog.setWindowModality(QtCore.Qt.WindowModal)
        bat_conf_Dialog.resize(320, 150)
        bat_conf_Dialog.setMouseTracking(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("battle_anki_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        bat_conf_Dialog.setWindowIcon(icon)
        bat_conf_Dialog.setModal(False)
        self.buttonBox_conf_dialog = QtWidgets.QDialogButtonBox(bat_conf_Dialog)
        self.buttonBox_conf_dialog.setGeometry(QtCore.QRect(60, 90, 201, 50))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox_conf_dialog.sizePolicy().hasHeightForWidth())
        self.buttonBox_conf_dialog.setSizePolicy(sizePolicy)
        self.buttonBox_conf_dialog.setAutoFillBackground(False)
        self.buttonBox_conf_dialog.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox_conf_dialog.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox_conf_dialog.setCenterButtons(True)
        self.buttonBox_conf_dialog.setObjectName("buttonBox_conf_dialog")
        self.lab_dialog_text = QtWidgets.QLabel(bat_conf_Dialog)
        self.lab_dialog_text.setGeometry(QtCore.QRect(30, 20, 261, 61))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lab_dialog_text.setFont(font)
        self.lab_dialog_text.setAlignment(QtCore.Qt.AlignCenter)
        self.lab_dialog_text.setWordWrap(True)
        self.lab_dialog_text.setObjectName("lab_dialog_text")

        self.retranslateUi(bat_conf_Dialog)
        self.buttonBox_conf_dialog.accepted.connect(bat_conf_Dialog.accept)
        self.buttonBox_conf_dialog.rejected.connect(bat_conf_Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(bat_conf_Dialog)

    def retranslateUi(self, bat_conf_Dialog):
        _translate = QtCore.QCoreApplication.translate
        bat_conf_Dialog.setWindowTitle(_translate("bat_conf_Dialog", "Confirmation dialog"))
        self.lab_dialog_text.setText(_translate("bat_conf_Dialog", "Please double check your options!\n"
"\n"
"Clicking OK will send the request..."))
