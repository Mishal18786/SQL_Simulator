import sys

import pandas as pd
import pyodbc
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QComboBox, QPushButton, QLineEdit, QWidget, QHBoxLayout, QTextEdit, QMessageBox,
                               QStackedLayout, QTableView)
from qt_material import apply_stylesheet


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Vertical:
                return str(self._data.index[section])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SQL Simuator - 1.0')

        # stacked layout for connection page and querry editor
        self.stacked_layout = QStackedLayout()
        self.Sql_Connector()
        self.Query_Editor()

        central_widget = QWidget()
        central_widget.setLayout(self.stacked_layout)
        self.setCentralWidget(central_widget)

    def Sql_Connector(self):
        connection_widget = QWidget()

        layout = QVBoxLayout(connection_widget)  # main layout
        layout2 = QHBoxLayout()  # username and passwrd layout

        # username and Password
        self.username = QLineEdit()
        self.username.setPlaceholderText('Enter Your Usename')
        layout2.addWidget(self.username)
        self.password = QLineEdit()
        self.password.setPlaceholderText('Enter Your Password')
        self.password.setEchoMode(QLineEdit.Password)
        layout2.addWidget(self.password)
        layout.addLayout(layout2)

        # Hint Messagebox
        message_button = QPushButton("HELP")
        message_button.clicked.connect(self.Help)
        layout2.addWidget(message_button)

        # Displaying the avaiable Drivers
        self.drivers = QComboBox()
        self.drivers.addItems(pyodbc.drivers())
        layout.addWidget(self.drivers)

        # connect Button
        connection = QPushButton("Connect")
        connection.clicked.connect(self.Establish_Connection)
        layout.addWidget(connection)

        self.stacked_layout.addWidget(connection_widget)

        # Restriction Message
        self.statusBar().showMessage('This Program only Supports MySQL')

    def Query_Editor(self):

        # self.setWindowTitle('SQL Simulator - Query Editor')
        query_widget = QWidget()
        layout = QVBoxLayout(query_widget)
        layout2 = QHBoxLayout()

        # BackButton
        backbuton = QPushButton('Back To Connection Page')
        backbuton.clicked.connect(self.previous_page)
        layout2.addWidget(backbuton)

        # help button
        message_b = QPushButton("HELP")
        message_b.clicked.connect(self.help2)
        layout2.addWidget(message_b)
        layout.addLayout(layout2)

        # Query Editor
        self.queryeditor = QTextEdit()
        self.queryeditor.setPlaceholderText('Enter your Query here')
        layout.addWidget(self.queryeditor)

        # Execute Button
        Execute = QPushButton("Execute")
        Execute.clicked.connect(self.Query_executer)
        layout.addWidget(Execute)

        # Displaying Results
        self.results = QTableView()
        layout.addWidget(self.results)
        self.GridModel = QStandardItemModel()

        self.stacked_layout.addWidget(query_widget)

    def Help(self):
        requirments_message = ("Check your requirments \n"
                                    "MySQL DataBase Application version -- 8.0.36, \n SQL ODBC Connector Application \n"
                                    "Create a username and password on mysql Database or use that exists \n")

        QMessageBox.information(None, 'Requirments', requirments_message, buttons=QMessageBox.Ok)

    def help2(self):
        Database_instructions = ("Use the below comands for creating user credentials and Grant previllages \n"
                                      "CREATE USER 'ODBC'@'localhost' IDENTIFIED BY 'your-password';\n"
                                      "ALTER USER 'ODBC'@'localhost' IDENTIFIED BY 'your-password'; \n"
                                      "GRANT ALL PRIVILEGES ON *.* TO 'ODBC'@'localhost'; ")

        QMessageBox.information(None, 'Instructions', Database_instructions, buttons=QMessageBox.Ok)

    def Establish_Connection(self):
        Driver = self.drivers.currentText()
        Username = self.username.text()
        Password = self.password.text()
        database = 'mysql'
        try:
            if Username and Password:
                if 'MySQL' in Driver:
                    self.connection = pyodbc.connect(driver=Driver,
                                                     username=Username,
                                                     password=Password,
                                                     database=database)  # default database
                    # self.messagebox.setText(self.connection.getinfo(pyodbc.SQL_DATABASE_NAME))
                    QMessageBox.information(self, 'Connection Successful',
                                            'You are Connected to MySQL Database (Default database is mysql)')
                    self.stacked_layout.setCurrentIndex(1)  # Changing the next page
                else:
                    QMessageBox.warning(self, 'Database Warning', 'Select only MySQL ODBC Drivers')
            else:
                QMessageBox.warning(self, 'Warning', 'Please enter Username and Password')
        except pyodbc.Error as err:
            QMessageBox.warning(self, 'Connection Error', str(err) + '\nEnter the correct username and Password \n')

    def previous_page(self):
        self.stacked_layout.setCurrentIndex(0)
    def Query_executer(self):
        querry = self.queryeditor.toPlainText()
        cursor = self.connection.cursor()

        try:
            cursor.execute(querry)
            if cursor.description:
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                data = []

                for row in rows:
                    rows_dict = {}
                    for i, column_name in enumerate(columns):
                        rows_dict[column_name] = row[i]
                    data.append(rows_dict)

                dataframe = pd.DataFrame(data)
                self.model = TableModel(dataframe)
                self.results.setModel(self.model)
            else:
                QMessageBox.information(self, 'Success Message', 'Querry Executed Successful', )
        except pyodbc.Error as er:
            QMessageBox.warning(self, 'Error Message', str(er))





if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_pink.xml')

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
