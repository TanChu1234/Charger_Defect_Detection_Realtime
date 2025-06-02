# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Home.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QLabel,
    QLineEdit, QMainWindow, QPushButton, QSizePolicy,
    QTabWidget, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1920, 1080)
        MainWindow.setStyleSheet(u"QMainWindow {\n"
"                background-color: rgb(255, 255, 255); /* Dark background for the main window */\n"
"            }\n"
"\n"
"            QLabel, QPushButton, QTextEdit {\n"
"                color: #ffffff; /* White text for readability */\n"
"                background-color: #333333; /* Slightly lighter dark gray for widgets */\n"
"                border: 1px solid #444444;\n"
"                padding: 5px;\n"
"                border-radius: 4px;\n"
"            }\n"
"			\n"
"            QTabWidget::pane { /* The tab widget frame */\n"
"                border-top: 2px solid #333333;\n"
"            }\n"
"\n"
"            QTabBar::tab {\n"
"                background: #2b2b2b;\n"
"                color: #ccc;\n"
"                border: 2px solid #333333;\n"
"                border-bottom-color: #333333; /* same as the pane color */\n"
"                border-top-left-radius: 4px;\n"
"                border-top-right-radius: 4px;\n"
"                min-width: 8ex;\n"
"                padding: "
                        "5px;\n"
"            }\n"
"\n"
"            QTabBar::tab:selected, QTabBar::tab:hover {\n"
"                background: #3c3c3c;\n"
"                color: #ffffff;\n"
"                border-color: #0057b7; /* Blue border for selected/hover */\n"
"            }\n"
"\n"
"            QTabBar::tab:selected {\n"
"                border-color: #333333;\n"
"                border-bottom-color: #3c3c3c; /* same as pane color */\n"
"            }\n"
"\n"
"            QPushButton:hover {\n"
"                background-color: #505050;\n"
"                border: 3px solid #0066cc;; /* Blue border for button hover */\n"
"            }\n"
"\n"
"     		QMessageBox {\n"
"        			background-color: #ffffff; /* White background for the message box */\n"
"        			color: rgb(255, 255, 255); /* Black text for general content */\n"
"    			}\n"
"    		QMessageBox QPushButton {\n"
"        			background-color: #8c8c8c;\n"
"        			border: none;\n"
"       			}\n"
"    		QMessageBox QLabel {\n"
"        			background-color"
                        ": #ffffff; /* White background for the message box */\n"
"        			color: rgb(0, 0, 0); /* Explicitly setting label text color to black */\n"
"        			border: none;\n"
"    			}")
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(9, 10, 1901, 991))
        font = QFont()
        font.setPointSize(12)
        self.tabWidget.setFont(font)
        self.tabWidget.setStyleSheet(u"            QMainWindow {\n"
"                background-color: #333333; /* Dark background for the main window */\n"
"            }\n"
"\n"
"            QPushButton, QTextEdit {\n"
"                color: black; /* White text for readability */\n"
"                background-color: #e7e7e7; /* Slightly lighter dark gray for widgets */\n"
"                border: 1px solid #444444;\n"
"                padding: 5px;\n"
"                border-radius: 4px;\n"
"            }\n"
"			\n"
"            QTabWidget::pane { /* The tab widget frame */\n"
"                border-top: 2px solid #f3f3f3;\n"
"            }\n"
"            QTabBar::tab {\n"
"                background: #f3f3f3;\n"
"                color: rgb(0, 0, 0);\n"
"                border: 1px;\n"
"                min-width: 8ex;\n"
"                padding: 5px;\n"
"            }\n"
"\n"
"            QTabBar::tab:selected, QTabBar::tab:hover {\n"
"				background: #e7e7e7;\n"
"				border-top: 3px solid #0f52ba;\n"
"            }\n"
"\n"
"\n"
"          "
                        "  QPushButton:hover {\n"
" 				 background-color: rgb(60, 170, 255);\n"
"                border: 1px solid #0066cc;; /* Blue border for button hover */\n"
"            }\n"
"\n"
"QScrollBar:vertical {\n"
"                background: #2e2e2e;\n"
"                width: 14px;\n"
"                margin: 15px 3px 15px 3px;\n"
"                border: 1px solid #222222;\n"
"                border-radius: 5px;\n"
"            }\n"
"\n"
"QScrollBar::handle:vertical {\n"
"                background: #5c90d2;\n"
"                min-height: 20px;\n"
"                border-radius: 5px;\n"
"            }\n"
"\n"
"QScrollBar::handle:vertical:hover {\n"
"                background: #787878;\n"
"            }\n"
"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {\n"
"                background: none;\n"
"            }\n"
"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"                background: none;\n"
"            }\n"
"\n"
" 			QRadioButton {\n"
"    			color: #b1b1b1; /* Default text c"
                        "olor */\n"
"    			spacing: 5px; /* Spacing around text and icon */\n"
"			}\n"
"			QRadioButton::indicator {\n"
"    			width: 13px;\n"
"    			height: 13px;\n"
"    			border-radius: 7px; /* Circular indicators */\n"
"			}\n"
"			QRadioButton::indicator:unchecked {\n"
"    			background-color: #cae1ff; /* Light gray background when unchecked */\n"
"   			 	border: 1px solid #0066cc; /* Gray border */\n"
"			}\n"
"			QRadioButton::indicator:checked {\n"
"    			background-color: #5c90d2; /* Blue background when checked */\n"
"    			border: 1px solid #0066cc; /* Darker blue border */\n"
"			}\n"
"\n"
"			QRadioButton::indicator:hover {\n"
"    			background-color: #5c90d2; /* Darker grey background when checked */\n"
"                border: 2px solid #0066cc; /* White border when checked */\n"
"			}\n"
"			QRadioButton::indicator:checked:hover {\n"
"    			background-color: #5c90d2; /* Darker grey background when checked */\n"
"                border: 1px solid #0066cc; /* White border when checked */\n"
"		"
                        "	}\n"
"QMessageBox {\n"
"        			background-color: #ffffff; /* White background for the message box */\n"
"        			color: rgb(255, 255, 255); /* Black text for general content */\n"
"    			}\n"
"    		QMessageBox QPushButton {\n"
"        			background-color: #8c8c8c;\n"
"        			border: none;\n"
"       			}\n"
"    		QMessageBox QLabel {\n"
"        			background-color: #ffffff; /* White background for the message box */\n"
"        			color: rgb(0, 0, 0); /* Explicitly setting label text color to black */\n"
"        			border: none;\n"
"    			}\n"
"")
        self.tab_Onl = QWidget()
        self.tab_Onl.setObjectName(u"tab_Onl")
        self.label_img_out = QLabel(self.tab_Onl)
        self.label_img_out.setObjectName(u"label_img_out")
        self.label_img_out.setGeometry(QRect(10, 20, 1241, 931))
        self.label_img_out.setStyleSheet(u"border-radius: 0px;\n"
"border: 1px solid rgb(0, 0, 0);\n"
"background-color:  rgb(0, 0, 127);")
        self.label_img_out.setAlignment(Qt.AlignCenter)
        self.label_Roi = QLabel(self.tab_Onl)
        self.label_Roi.setObjectName(u"label_Roi")
        self.label_Roi.setGeometry(QRect(940, 100, 281, 31))
        font1 = QFont()
        font1.setPointSize(11)
        self.label_Roi.setFont(font1)
        self.label_Roi.setStyleSheet(u"background-color: none;\n"
"border:none;\n"
"color: rgb(255, 0, 0);")
        self.label_Roi.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.widget = QWidget(self.tab_Onl)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(1260, 20, 631, 931))
        self.widget.setStyleSheet(u"")
        self.label_check = QLabel(self.widget)
        self.label_check.setObjectName(u"label_check")
        self.label_check.setGeometry(QRect(30, 720, 571, 211))
        font2 = QFont()
        font2.setPointSize(48)
        font2.setBold(True)
        font2.setKerning(True)
        self.label_check.setFont(font2)
        self.label_check.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"border: 1px solid rgb(0, 0, 0);\n"
"background-color: rgb(85, 170, 0);\n"
"border-radius: 0px;")
        self.label_check.setAlignment(Qt.AlignHCenter|Qt.AlignTop)
        self.label_check.setMargin(0)
        self.label_check.setIndent(60)
        self.label_6 = QLabel(self.widget)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(30, 720, 571, 61))
        font3 = QFont()
        font3.setPointSize(28)
        font3.setBold(True)
        self.label_6.setFont(font3)
        self.label_6.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"border: 1px solid rgb(0, 0, 0);\n"
"background-color: none;\n"
"border-radius: 0px;")
        self.label_6.setAlignment(Qt.AlignCenter)
        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(330, 10, 291, 91))
        self.label_2.setFont(font3)
        self.label_2.setStyleSheet(u"color: none;\n"
"background-color: rgb(255, 255, 255);\n"
"border:none;")
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_logo = QLabel(self.widget)
        self.label_logo.setObjectName(u"label_logo")
        self.label_logo.setGeometry(QRect(10, 0, 321, 111))
        self.label_logo.setStyleSheet(u"background-color: none;\n"
"border:none")
        self.label_logo.setPixmap(QPixmap(u"image/logo.png"))
        self.label_time = QLabel(self.widget)
        self.label_time.setObjectName(u"label_time")
        self.label_time.setGeometry(QRect(130, 850, 401, 41))
        font4 = QFont()
        font4.setPointSize(16)
        font4.setBold(True)
        self.label_time.setFont(font4)
        self.label_time.setStyleSheet(u"border: none;\n"
"background-color:none;\n"
"color: rgb(0, 0, 0);")
        self.label_time.setAlignment(Qt.AlignCenter)
        self.groupBox = QGroupBox(self.widget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(110, 360, 421, 211))
        self.groupBox.setStyleSheet(u"\n"
"				border: 1px solid rgb(0, 0, 0);\n"
"")
        self.edtFrameRate = QLineEdit(self.groupBox)
        self.edtFrameRate.setObjectName(u"edtFrameRate")
        self.edtFrameRate.setGeometry(QRect(210, 110, 121, 31))
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(100, 110, 91, 31))
        self.label.setStyleSheet(u"background-color: none;\n"
"color: rgb(0, 0, 0);\n"
"border:none;\n"
"")
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(100, 10, 101, 31))
        font5 = QFont()
        font5.setPointSize(10)
        self.label_3.setFont(font5)
        self.label_3.setStyleSheet(u"background-color: none;\n"
"color: rgb(0, 0, 0);\n"
"border:none;\n"
"")
        self.edtExposureTime = QLineEdit(self.groupBox)
        self.edtExposureTime.setObjectName(u"edtExposureTime")
        self.edtExposureTime.setGeometry(QRect(210, 10, 121, 31))
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(100, 60, 91, 31))
        self.label_4.setFont(font5)
        self.label_4.setStyleSheet(u"background-color: none;\n"
"color: rgb(0, 0, 0);\n"
"border:none;\n"
"")
        self.edtGain = QLineEdit(self.groupBox)
        self.edtGain.setObjectName(u"edtGain")
        self.edtGain.setGeometry(QRect(210, 60, 121, 31))
        self.bnSet = QPushButton(self.groupBox)
        self.bnSet.setObjectName(u"bnSet")
        self.bnSet.setEnabled(True)
        self.bnSet.setGeometry(QRect(160, 160, 131, 41))
        font6 = QFont()
        font6.setPointSize(12)
        font6.setBold(True)
        self.bnSet.setFont(font6)
        self.bnSet.setFocusPolicy(Qt.ClickFocus)
        self.bnSet.setStyleSheet(u"")
        self.bnEnum = QPushButton(self.widget)
        self.bnEnum.setObjectName(u"bnEnum")
        self.bnEnum.setGeometry(QRect(100, 180, 121, 41))
        self.bnEnum.setFont(font6)
        self.bnOpen = QPushButton(self.widget)
        self.bnOpen.setObjectName(u"bnOpen")
        self.bnOpen.setGeometry(QRect(260, 180, 121, 41))
        self.bnOpen.setFont(font6)
        self.ComboDevices = QComboBox(self.widget)
        self.ComboDevices.setObjectName(u"ComboDevices")
        self.ComboDevices.setGeometry(QRect(60, 110, 521, 41))
        self.ComboDevices.setFont(font6)
        self.ComboDevices.setStyleSheet(u"")
        self.ComboDevices.setFrame(True)
        self.bnClose = QPushButton(self.widget)
        self.bnClose.setObjectName(u"bnClose")
        self.bnClose.setEnabled(True)
        self.bnClose.setGeometry(QRect(410, 180, 131, 41))
        self.bnClose.setFont(font6)
        self.bnClose.setFocusPolicy(Qt.ClickFocus)
        self.bnClose.setStyleSheet(u"")
        self.label_7 = QLabel(self.widget)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(30, 630, 121, 31))
        self.label_7.setFont(font6)
        self.label_7.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"border: none;\n"
"background-color: none;\n"
"border-radius: 0px;")
        self.label_7.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_8 = QLabel(self.widget)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(30, 670, 161, 31))
        self.label_8.setFont(font6)
        self.label_8.setLayoutDirection(Qt.LeftToRight)
        self.label_8.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"border: none;\n"
"background-color: none;\n"
"border-radius: 0px;")
        self.label_8.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.qr_code = QLabel(self.widget)
        self.qr_code.setObjectName(u"qr_code")
        self.qr_code.setGeometry(QRect(110, 630, 231, 31))
        self.qr_code.setFont(font6)
        self.qr_code.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"border: none;\n"
"background-color: none;\n"
"border-radius: 0px;")
        self.qr_code.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.serial = QLabel(self.widget)
        self.serial.setObjectName(u"serial")
        self.serial.setGeometry(QRect(160, 670, 371, 31))
        self.serial.setFont(font6)
        self.serial.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"border: none;\n"
"background-color: none;\n"
"border-radius: 0px;")
        self.serial.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.bnStart = QPushButton(self.widget)
        self.bnStart.setObjectName(u"bnStart")
        self.bnStart.setEnabled(True)
        self.bnStart.setGeometry(QRect(100, 240, 121, 41))
        self.bnStart.setFont(font6)
        self.bnStart.setFocusPolicy(Qt.ClickFocus)
        self.bnStart.setStyleSheet(u"")
        self.bnStop = QPushButton(self.widget)
        self.bnStop.setObjectName(u"bnStop")
        self.bnStop.setEnabled(True)
        self.bnStop.setGeometry(QRect(260, 240, 121, 41))
        self.bnStop.setFont(font6)
        self.bnStop.setFocusPolicy(Qt.ClickFocus)
        self.bnStop.setStyleSheet(u"")
        self.label_9 = QLabel(self.widget)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(30, 590, 121, 31))
        self.label_9.setFont(font6)
        self.label_9.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"border: none;\n"
"background-color: none;\n"
"border-radius: 0px;")
        self.label_9.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.position = QLabel(self.widget)
        self.position.setObjectName(u"position")
        self.position.setGeometry(QRect(110, 590, 231, 31))
        self.position.setFont(font6)
        self.position.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"border: none;\n"
"background-color: none;\n"
"border-radius: 0px;")
        self.position.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.bnFolder = QPushButton(self.widget)
        self.bnFolder.setObjectName(u"bnFolder")
        self.bnFolder.setEnabled(True)
        self.bnFolder.setGeometry(QRect(410, 240, 131, 41))
        self.bnFolder.setFont(font6)
        self.bnFolder.setFocusPolicy(Qt.ClickFocus)
        self.bnFolder.setStyleSheet(u"")
        self.dir = QLabel(self.widget)
        self.dir.setObjectName(u"dir")
        self.dir.setGeometry(QRect(70, 300, 511, 41))
        self.dir.setFont(font6)
        self.dir.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"background-color: none;\n"
"border-radius: 5px;")
        self.dir.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.tabWidget.addTab(self.tab_Onl, "")
        self.widget.raise_()
        self.label_img_out.raise_()
        self.label_Roi.raise_()
        self.tab_Off = QWidget()
        self.tab_Off.setObjectName(u"tab_Off")
        self.tabWidget.addTab(self.tab_Off, "")
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_img_out.setText("")
        self.label_Roi.setText("")
        self.label_check.setText(QCoreApplication.translate("MainWindow", u"OK", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"RESULT", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"VISION SYSTEM", None))
        self.label_logo.setText("")
        self.label_time.setText(QCoreApplication.translate("MainWindow", u"0 ms", None))
        self.groupBox.setTitle("")
        self.edtFrameRate.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Frame Rate:", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Exposure Time:", None))
        self.edtExposureTime.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Gain:", None))
        self.edtGain.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.bnSet.setText(QCoreApplication.translate("MainWindow", u"Set Parameter", None))
        self.bnEnum.setText(QCoreApplication.translate("MainWindow", u"Search Device", None))
        self.bnOpen.setText(QCoreApplication.translate("MainWindow", u"Open Device", None))
        self.bnClose.setText(QCoreApplication.translate("MainWindow", u"Close Device", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"QR Code:", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Serial Number:", None))
        self.qr_code.setText("")
        self.serial.setText("")
        self.bnStart.setText(QCoreApplication.translate("MainWindow", u"Start Camera", None))
        self.bnStop.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Position:", None))
        self.position.setText("")
        self.bnFolder.setText(QCoreApplication.translate("MainWindow", u"Choose Folder", None))
        self.dir.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_Onl), QCoreApplication.translate("MainWindow", u"Process Image", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_Off), QCoreApplication.translate("MainWindow", u"Connect Camera", None))
    # retranslateUi

