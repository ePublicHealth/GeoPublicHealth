# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created: Mon Oct 26 17:47:12 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName(_fromUtf8("About"))
        About.resize(629, 528)
        self.verticalLayout = QtGui.QVBoxLayout(About)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(About)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_7.addWidget(self.label_5)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_6 = QtGui.QLabel(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setText(_fromUtf8(""))
        self.label_6.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/GeoHealth/resources/espace-dev.png")))
        self.label_6.setScaledContents(False)
        self.label_6.setOpenExternalLinks(True)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout.addWidget(self.label_6)
        self.verticalLayout_6 = QtGui.QVBoxLayout()
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.label_8 = QtGui.QLabel(self.groupBox)
        self.label_8.setText(_fromUtf8("<html><head/><body><p><a href=\"mailto:vincent.herbreteau@ird.fr?subject=Plugin Blurring\"><span style=\" color:#0057ae;\" style=\"text-decoration:none;\">Vincent Herbreteau (IRD)</span></a></p></body></html>"))
        self.label_8.setOpenExternalLinks(True)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.verticalLayout_6.addWidget(self.label_8)
        self.label_7 = QtGui.QLabel(self.groupBox)
        self.label_7.setText(_fromUtf8("<a href=\"mailto:christophe.revillion@ird.fr?subject=Plugin Blurring\" style=\"text-decoration:none;\">Christophe Révillion (IRD)</a>"))
        self.label_7.setOpenExternalLinks(True)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout_6.addWidget(self.label_7)
        self.label_9 = QtGui.QLabel(self.groupBox)
        self.label_9.setText(_fromUtf8("<a href=\"mailto:therese.libourel@univ-montp2.fr?subject=Plugin Blurring\" style=\"text-decoration:none;\">Thérèse Libourel (UM2)</a>"))
        self.label_9.setOpenExternalLinks(True)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.verticalLayout_6.addWidget(self.label_9)
        self.horizontalLayout.addLayout(self.verticalLayout_6)
        self.verticalLayout_7.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(About)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.verticalLayout_10 = QtGui.QVBoxLayout()
        self.verticalLayout_10.setObjectName(_fromUtf8("verticalLayout_10"))
        self.label_11 = QtGui.QLabel(self.groupBox_2)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.verticalLayout_10.addWidget(self.label_11)
        self.horizontalLayout_4.addLayout(self.verticalLayout_10)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_4 = QtGui.QGroupBox(About)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.verticalLayout_11 = QtGui.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_11.setObjectName(_fromUtf8("verticalLayout_11"))
        self.gridLayout_5 = QtGui.QGridLayout()
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label_21 = QtGui.QLabel(self.groupBox_4)
        self.label_21.setAlignment(QtCore.Qt.AlignCenter)
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.gridLayout_5.addWidget(self.label_21, 0, 0, 1, 1)
        self.label_22 = QtGui.QLabel(self.groupBox_4)
        self.label_22.setText(_fromUtf8("<a href=\"https://github.com/Gustry/GeoHealth\" style=\"text-decoration:none;\">https://github.com/Gustry/GeoHealth</a>"))
        self.label_22.setOpenExternalLinks(True)
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.gridLayout_5.addWidget(self.label_22, 0, 1, 1, 1)
        self.verticalLayout_11.addLayout(self.gridLayout_5)
        self.verticalLayout.addWidget(self.groupBox_4)
        self.groupBox_3 = QtGui.QGroupBox(About)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_12 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_12.setObjectName(_fromUtf8("verticalLayout_12"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.label_15 = QtGui.QLabel(self.groupBox_3)
        self.label_15.setText(_fromUtf8("<html><head/><body><p><a href=\"http://www.gnu.org/licenses/gpl-2.0.html\"><span style=\" text-decoration: none; color:#0057ae;\">Licence GPL Version 2</span></a></p></body></html>"))
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.horizontalLayout_5.addWidget(self.label_15)
        self.label_16 = QtGui.QLabel(self.groupBox_3)
        self.label_16.setText(_fromUtf8("<html><head/><body><p><a href=\"https://www.gnu.org/licenses/gpl-2.0.html\"><img src=\":/plugins/GeoHealth/resources/gnu.png\"/></a></p></body></html>"))
        self.label_16.setAlignment(QtCore.Qt.AlignCenter)
        self.label_16.setOpenExternalLinks(True)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.horizontalLayout_5.addWidget(self.label_16)
        self.verticalLayout_12.addLayout(self.horizontalLayout_5)
        self.verticalLayout.addWidget(self.groupBox_3)

        self.retranslateUi(About)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        About.setWindowTitle(_translate("About", "Form", None))
        self.groupBox.setTitle(_translate("About", "Design", None))
        self.label_5.setText(_translate("About", "This plugin was designed by UMR Espace-Dev (IRD, UAG, UM2, UR)", None))
        self.groupBox_2.setTitle(_translate("About", "Realization", None))
        self.label_11.setText(_translate("About", "Etienne Trimaille", None))
        self.groupBox_4.setTitle(_translate("About", "Sources", None))
        self.label_21.setText(_translate("About", "Github\'s repository", None))
        self.groupBox_3.setTitle(_translate("About", "Licence", None))

from GeoHealth.resources import resources_rc
