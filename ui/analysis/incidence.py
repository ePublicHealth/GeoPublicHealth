# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'incidence.ui'
#
# Created: Wed Oct 28 16:19:11 2015
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

class Ui_Incidence(object):
    def setupUi(self, Incidence):
        Incidence.setObjectName(_fromUtf8("Incidence"))
        Incidence.resize(651, 748)
        self.verticalLayout = QtGui.QVBoxLayout(Incidence)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.messageBar = gui.QgsMessageBar(Incidence)
        self.messageBar.setObjectName(_fromUtf8("messageBar"))
        self.verticalLayout.addWidget(self.messageBar)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_4 = QtGui.QLabel(Incidence)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_4)
        self.cbx_case_layer = QtGui.QComboBox(Incidence)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbx_case_layer.sizePolicy().hasHeightForWidth())
        self.cbx_case_layer.setSizePolicy(sizePolicy)
        self.cbx_case_layer.setObjectName(_fromUtf8("cbx_case_layer"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.cbx_case_layer)
        self.label = QtGui.QLabel(Incidence)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label)
        self.cbx_aggregation_layer = QtGui.QComboBox(Incidence)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbx_aggregation_layer.sizePolicy().hasHeightForWidth())
        self.cbx_aggregation_layer.setSizePolicy(sizePolicy)
        self.cbx_aggregation_layer.setObjectName(_fromUtf8("cbx_aggregation_layer"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.cbx_aggregation_layer)
        self.label_7 = QtGui.QLabel(Incidence)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_7)
        self.cbx_population_field = QtGui.QComboBox(Incidence)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbx_population_field.sizePolicy().hasHeightForWidth())
        self.cbx_population_field.setSizePolicy(sizePolicy)
        self.cbx_population_field.setObjectName(_fromUtf8("cbx_population_field"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.cbx_population_field)
        self.label_2 = QtGui.QLabel(Incidence)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_2)
        self.cbx_ratio = QtGui.QComboBox(Incidence)
        self.cbx_ratio.setEditable(True)
        self.cbx_ratio.setObjectName(_fromUtf8("cbx_ratio"))
        self.cbx_ratio.addItem(_fromUtf8(""))
        self.cbx_ratio.addItem(_fromUtf8(""))
        self.cbx_ratio.addItem(_fromUtf8(""))
        self.cbx_ratio.addItem(_fromUtf8(""))
        self.cbx_ratio.addItem(_fromUtf8(""))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.cbx_ratio)
        self.label_3 = QtGui.QLabel(Incidence)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_3)
        self.le_new_column = QtGui.QLineEdit(Incidence)
        self.le_new_column.setMaxLength(10)
        self.le_new_column.setObjectName(_fromUtf8("le_new_column"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.le_new_column)
        self.checkBox_addNbIntersections = QtGui.QCheckBox(Incidence)
        self.checkBox_addNbIntersections.setObjectName(_fromUtf8("checkBox_addNbIntersections"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.checkBox_addNbIntersections)
        self.checkBox_incidence_runStats = QtGui.QCheckBox(Incidence)
        self.checkBox_incidence_runStats.setChecked(True)
        self.checkBox_incidence_runStats.setObjectName(_fromUtf8("checkBox_incidence_runStats"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.FieldRole, self.checkBox_incidence_runStats)
        self.label_8 = QtGui.QLabel(Incidence)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.LabelRole, self.label_8)
        self.label_6 = QtGui.QLabel(Incidence)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.formLayout.setWidget(8, QtGui.QFormLayout.LabelRole, self.label_6)
        self.label_5 = QtGui.QLabel(Incidence)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.formLayout.setWidget(8, QtGui.QFormLayout.FieldRole, self.label_5)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.formLayout.setLayout(9, QtGui.QFormLayout.FieldRole, self.horizontalLayout)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.le_output_filepath = QtGui.QLineEdit(Incidence)
        self.le_output_filepath.setObjectName(_fromUtf8("le_output_filepath"))
        self.horizontalLayout_6.addWidget(self.le_output_filepath)
        self.button_browse = QtGui.QPushButton(Incidence)
        self.button_browse.setObjectName(_fromUtf8("button_browse"))
        self.horizontalLayout_6.addWidget(self.button_browse)
        self.formLayout.setLayout(7, QtGui.QFormLayout.FieldRole, self.horizontalLayout_6)
        self.verticalLayout.addLayout(self.formLayout)
        self.symbology = gui.QgsCollapsibleGroupBox(Incidence)
        self.symbology.setCheckable(True)
        self.symbology.setCollapsed(False)
        self.symbology.setObjectName(_fromUtf8("symbology"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.symbology)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_9 = QtGui.QLabel(self.symbology)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.horizontalLayout_3.addWidget(self.label_9)
        self.color_low_value = gui.QgsColorButtonV2(self.symbology)
        self.color_low_value.setColor(QtGui.QColor(255, 246, 246))
        self.color_low_value.setObjectName(_fromUtf8("color_low_value"))
        self.horizontalLayout_3.addWidget(self.color_low_value)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label_10 = QtGui.QLabel(self.symbology)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.horizontalLayout_3.addWidget(self.label_10)
        self.color_high_value = gui.QgsColorButtonV2(self.symbology)
        self.color_high_value.setColor(QtGui.QColor(202, 33, 36))
        self.color_high_value.setObjectName(_fromUtf8("color_high_value"))
        self.horizontalLayout_3.addWidget(self.color_high_value)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_11 = QtGui.QLabel(self.symbology)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.horizontalLayout_4.addWidget(self.label_11)
        self.spinBox_classes = QtGui.QSpinBox(self.symbology)
        self.spinBox_classes.setMinimum(1)
        self.spinBox_classes.setProperty("value", 5)
        self.spinBox_classes.setObjectName(_fromUtf8("spinBox_classes"))
        self.horizontalLayout_4.addWidget(self.spinBox_classes)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.label_12 = QtGui.QLabel(self.symbology)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.horizontalLayout_4.addWidget(self.label_12)
        self.cbx_mode = QtGui.QComboBox(self.symbology)
        self.cbx_mode.setObjectName(_fromUtf8("cbx_mode"))
        self.horizontalLayout_4.addWidget(self.cbx_mode)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.verticalLayout.addWidget(self.symbology)
        self.button_box_ok = QtGui.QDialogButtonBox(Incidence)
        self.button_box_ok.setOrientation(QtCore.Qt.Horizontal)
        self.button_box_ok.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.button_box_ok.setObjectName(_fromUtf8("button_box_ok"))
        self.verticalLayout.addWidget(self.button_box_ok)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.tableWidget = QtGui.QTableWidget(Incidence)
        self.tableWidget.setMinimumSize(QtCore.QSize(200, 0))
        self.tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        self.tableWidget.verticalHeader().setVisible(False)
        self.horizontalLayout_2.addWidget(self.tableWidget)
        self.layout_plot = QtGui.QVBoxLayout()
        self.layout_plot.setObjectName(_fromUtf8("layout_plot"))
        self.horizontalLayout_2.addLayout(self.layout_plot)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Incidence)
        self.cbx_ratio.setCurrentIndex(4)
        QtCore.QMetaObject.connectSlotsByName(Incidence)

    def retranslateUi(self, Incidence):
        Incidence.setWindowTitle(_translate("Incidence", "Incidence", None))
        self.label_4.setText(_translate("Incidence", "Case layer", None))
        self.label.setText(_translate("Incidence", "Layer for aggregation", None))
        self.label_7.setText(_translate("Incidence", "Column population", None))
        self.label_2.setText(_translate("Incidence", "Ratio", None))
        self.cbx_ratio.setItemText(0, _translate("Incidence", "10", None))
        self.cbx_ratio.setItemText(1, _translate("Incidence", "100", None))
        self.cbx_ratio.setItemText(2, _translate("Incidence", "1 000", None))
        self.cbx_ratio.setItemText(3, _translate("Incidence", "10 000", None))
        self.cbx_ratio.setItemText(4, _translate("Incidence", "100 000", None))
        self.label_3.setText(_translate("Incidence", "New column", None))
        self.le_new_column.setPlaceholderText(_translate("Incidence", "incidence", None))
        self.checkBox_addNbIntersections.setToolTip(_translate("Incidence", "Add the number of cases per unit to the attribute table", None))
        self.checkBox_addNbIntersections.setText(_translate("Incidence", "Add the number of cases per unit to the attribute table", None))
        self.checkBox_incidence_runStats.setText(_translate("Incidence", "Calculate statistics", None))
        self.label_8.setText(_translate("Incidence", "Output", None))
        self.label_6.setText(_translate("Incidence", "<html><head/><body><p><span style=\" font-style:italic;\">Incidence =</span></p></body></html>", None))
        self.label_5.setText(_translate("Incidence", "<html><head/><body><p><span style=\" font-style:italic;\">number of cases / population * ratio</span></p></body></html>", None))
        self.le_output_filepath.setPlaceholderText(_translate("Incidence", "Save to temporary file", None))
        self.button_browse.setText(_translate("Incidence", "Browse", None))
        self.symbology.setTitle(_translate("Incidence", "Add a symbology", None))
        self.label_9.setText(_translate("Incidence", "Low incidence", None))
        self.label_10.setText(_translate("Incidence", "High incidence", None))
        self.label_11.setText(_translate("Incidence", "Classes", None))
        self.label_12.setText(_translate("Incidence", "Mode", None))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Incidence", "Parameter", None))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Incidence", "Value", None))

from qgis import gui