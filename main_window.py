# Form implementation generated from reading ui file 'mainwindow_ts.ui'
#
# Created by: PyQt6 UI code generator 6.5.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        # MainWindow.setStyleSheet("background-color: white;")
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1366, 20))
        self.menubar.setObjectName("menubar")

        self.menu = QtWidgets.QMenu(parent=self.menubar)
        self.menu.setObjectName("menu")

        self.menu_3 = QtWidgets.QMenu(parent=self.menubar)
        self.menu_3.setObjectName("menu_3")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.create_file = QtGui.QAction(parent=MainWindow)
        self.create_file.setObjectName("create_file")

        self.open_file = QtGui.QAction(parent=MainWindow)
        self.open_file.setObjectName("open_file")

        self.save_file = QtGui.QAction(parent=MainWindow)
        self.save_file.setObjectName("save_file")

        self.playback = QtGui.QAction(parent=MainWindow)
        self.playback.setObjectName("playback")

        self.modeling = QtGui.QAction(parent=MainWindow)
        self.modeling.setObjectName("modeling")

        self.start_classification = QtGui.QAction(parent=MainWindow)
        self.start_classification.setObjectName("start_classification")

        self.open_weights = QtGui.QAction(parent=MainWindow)
        self.open_weights.setObjectName("open_weights")

        self.save_weights = QtGui.QAction(parent=MainWindow)
        self.save_weights.setObjectName("save_weights")

        self.reset_training = QtGui.QAction(parent=MainWindow)
        self.reset_training.setObjectName("reset_training")

        self.training = QtGui.QAction(parent=MainWindow)
        self.training.setObjectName("training")

        self.menu.addAction(self.create_file)
        self.menu.addAction(self.open_file)
        self.menu.addAction(self.save_file)

        # self.menu_2.addAction(self.playback)
        # self.menu_2.addAction(self.modeling)

        self.menu_3.addAction(self.start_classification)
        self.menu_3.addAction(self.training)
        self.menu_3.addAction(self.open_weights)
        self.menu_3.addAction(self.save_weights)
        self.menu_3.addAction(self.reset_training)

        self.menubar.addAction(self.menu.menuAction())
        # self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menu_3.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CWS"))
        self.menu.setTitle(_translate("MainWindow", "Файл"))
        # self.menu_2.setTitle(_translate("MainWindow", "Моделироване"))
        self.menu_3.setTitle(_translate("MainWindow", "ИИ"))
        self.create_file.setText(_translate(
            "MainWindow", "Создать новый файл"))
        self.open_file.setText(_translate("MainWindow", "Открыть файл"))
        self.save_file.setText(_translate("MainWindow", "Сохранить файл"))
        # self.playback.setText(_translate("MainWindow", "Проигрывание"))
        # self.modeling.setText(_translate("MainWindow", "Моделирование"))
        self.start_classification.setText(_translate("MainWindow", "Запустить классификацию"))
        self.training.setText(_translate("MainWindow", "Обучение"))
        self.reset_training.setText(_translate(
            "MainWindow", "Сбросить обучение"))
        self.save_weights.setText(_translate("MainWindow", "Сохранить веса"))
        self.open_weights.setText(_translate("MainWindow", "Открыть веса"))