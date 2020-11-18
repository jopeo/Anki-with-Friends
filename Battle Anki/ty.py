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


class Ui_Dialog_ty(object):
    def setupUi(self, Dialog_ty):
        Dialog_ty.setObjectName("Dialog_ty")
        Dialog_ty.resize(315, 160)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("battle_anki_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog_ty.setWindowIcon(icon)
        self.lab_text = QtWidgets.QLabel(Dialog_ty)
        self.lab_text.setGeometry(QtCore.QRect(40, 20, 241, 61))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lab_text.setFont(font)
        self.lab_text.setAlignment(QtCore.Qt.AlignCenter)
        self.lab_text.setObjectName("lab_text")
        self.lab_link = QtWidgets.QLabel(Dialog_ty)
        self.lab_link.setGeometry(QtCore.QRect(30, 100, 261, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.lab_link.setFont(font)
        self.lab_link.setFocusPolicy(QtCore.Qt.NoFocus)
        self.lab_link.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lab_link.setTextFormat(QtCore.Qt.RichText)
        self.lab_link.setScaledContents(False)
        self.lab_link.setAlignment(QtCore.Qt.AlignCenter)
        self.lab_link.setOpenExternalLinks(True)
        self.lab_link.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.lab_link.setObjectName("lab_link")

        self.retranslateUi(Dialog_ty)
        QtCore.QMetaObject.connectSlotsByName(Dialog_ty)

    def retranslateUi(self, Dialog_ty):
        _translate = QtCore.QCoreApplication.translate
        Dialog_ty.setWindowTitle(_translate("Dialog_ty", "TYVM from Battle Anki"))
        self.lab_text.setText(_translate("Dialog_ty", "Thank you for playing Battle Anki!\n"
"If you enjoyed the experience,\n"
"buy me a coffee?"))
        self.lab_link.setText(_translate("Dialog_ty", "<a href=\"https://ko-fi.com/battleanki\">Ko-fi.com/BattleAnki</a>"))
