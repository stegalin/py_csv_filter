import sys
import csv
import os
import re
import time, datetime
import threading
from PyQt5 import QtWidgets, QtCore

app = QtWidgets.QApplication(sys.argv)
main_layout = QtWidgets.QVBoxLayout()
w = QtWidgets.QWidget()
w.resize(400, 600)
w.setWindowTitle('CSV Converter')

### 1st STEP Layout ###
step1 = QtWidgets.QGridLayout()
step1.setSpacing(10)

step1_title = QtWidgets.QLabel("<b><font size=4>Step 1.</font></b> Select file for parsing")
step1.addWidget(step1_title, 1, 0)
step1.addWidget(QtWidgets.QLabel("File for parsing:"), 2, 0)

filename = QtWidgets.QLabel("Select file by click on <b>\"Browse...\"</b>")
step1.addWidget(filename, 3, 0, 1, 2)

browse_button = QtWidgets.QPushButton("Browse...")
step1.addWidget(browse_button, 4, 0)

step1.addWidget(QtWidgets.QLabel(""), 5, 0)

f = QtWidgets.QWidget()


def select_file(filename):
    filename.setText(QtWidgets.QFileDialog.getOpenFileName(f, 'Select File', '')[0])
    if filename.text() == "":
        filename.setText("Select file by click on <b>\"Browse...\"</b>")


browse_button.clicked.connect(lambda: select_file(filename))

### 2nd STEP Layout ###
step2 = QtWidgets.QGridLayout()
step2.setSpacing(10)

step2_title = QtWidgets.QLabel("<b><font size=4>Step 2.</font></b> Get Fields for filters")
step2.addWidget(step2_title, 1, 0)
step2.addWidget(QtWidgets.QLabel("Press <b>Get Fields/Input Parameters</b> to use and to apply filters"), 2, 0, 1, 2)

get_fields_button = QtWidgets.QPushButton("Get Fields/Input Parameters")
step2.addWidget(get_fields_button, 3, 0)

fields_label = QtWidgets.QLabel("")
step2.addWidget(fields_label, 4, 0)

header = QtWidgets.QComboBox()


def get_fields(filename, fields_label, header, list1, list2):
    if filename.text() == "Select file by click on <b>\"Browse...\"</b>" or filename.text() == "":
        fields_label.setText("File isn't chosen")
        list1.clear()
        list2.clear()
    else:
        if filename.text().lower().endswith(".csv"):
            header.clear()
            with open(filename.text(), 'rb') as file:#python3 - "r"
                headers = csv.DictReader(file).fieldnames
            if headers is None:
                fields_label.setText("<b>Missing lines in selected file</b>")
                return
            header.addItems(headers)
            list1.clear()
            list1.addItems(["empty"] + headers)
            list1.setCurrentIndex(1)
            list2.clear()
            list2.addItems(["empty"] + headers)
            list2.setCurrentIndex(0)
            fields_label.setText("Fields were got")
        else:
            list1.clear()
            list2.clear()
            fields_label.setText("Only \".csv\" file is expected")


### 3rd STEP Layout ###
step3 = QtWidgets.QGridLayout()
step3.setSpacing(10)

step3_title = QtWidgets.QLabel(
    "<b><font size=4>Step 3.</font></b> Input filter values. Each value should be in new line. <b>At least one filter is required</b>")
step3.addWidget(step3_title, 1, 0)
step3.addWidget(QtWidgets.QLabel(
    "<b>1st filter</b><p>\"Lun: \" are cut automatically<p>Symbol \"_\" corresponds to both \".\" and \"_\""), 2, 0)
list1 = QtWidgets.QComboBox()
step3.addWidget(list1, 3, 0)
parameters1 = QtWidgets.QTextEdit()
step3.addWidget(parameters1, 4, 0)

step3.addWidget(QtWidgets.QLabel("<b>2nd filter</b>"), 5, 0)
list2 = QtWidgets.QComboBox()
step3.addWidget(list2, 6, 0)
parameters2 = QtWidgets.QTextEdit()
step3.addWidget(parameters2, 7, 0)

step3.addWidget(QtWidgets.QLabel(""), 8, 0)

get_fields_button.clicked.connect(lambda: get_fields(filename, fields_label, header, list1, list2))

### 4th STEP Layout ###
step4 = QtWidgets.QGridLayout()
step4.setSpacing(10)

step4_title = QtWidgets.QLabel("<b><font size=4>Step 4.</font></b>  Input filename and click \"Generate\"")
step4.addWidget(step4_title, 1, 0)

path = (os.path.abspath(os.curdir) + "\\generated_" + time.strftime("%Y-%m-%d.%H_%M_%S") + ".csv").replace("\\\\", "\\")
new_file = QtWidgets.QLineEdit(path)
step4.addWidget(new_file, 2, 0, 1, 2)

save_path_button = QtWidgets.QPushButton("Select folder...")
step4.addWidget(save_path_button, 4, 0)


def set_path(new_file):
    temp_filename = new_file.text().split("\\")[-1]
    new_path = QtWidgets.QFileDialog.getExistingDirectory(f, 'Select Folder', '')
    if new_path != "":
        new_file.setText(new_path.replace("/", "\\") + "\\" + temp_filename)


save_path_button.clicked.connect(lambda: set_path(new_file))

generate_button = QtWidgets.QPushButton("Generate")
step4.addWidget(generate_button, 4, 1)

# $progress_bar = progress width: 1.0, margin: 2
time_label = QtWidgets.QLabel("Generating time: is not calculated")
step4.addWidget(time_label, 5, 0)

elapsed_time = QtWidgets.QLabel("")
elapsed_time.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
step4.addWidget(elapsed_time, 6, 0, 1, 2)

progress_bar = QtWidgets.QProgressBar()
step4.addWidget(progress_bar, 7, 0, 1, 2)


def generate():
    def write_csv_tread():
        try:
            start_time = datetime.datetime.now()

            values1 = set(parameters1.toPlainText().replace(",", "\n").split('\n'))
            values1 = {re.sub('(^Lun: |\r)', '', el) for el in values1}
            values2 = set(parameters2.toPlainText().replace(",", "\n").split('\n'))
            values2 = {re.sub('\r', '', el) for el in values2}
            header_items = [header.itemText(i) for i in range(header.count())]
            try:
                index1 = header_items.index(list1.currentText())
            except ValueError:
                index1 = None

            try:
                index2 = header_items.index(list2.currentText())
            except ValueError:
                index2 = None

            time_label.setText("Generating is running")
            generate_button.setEnabled(False)

            if filename.text() == "Select file by click on <b>\"Browse...\"</b>" or filename.text() == "":
                time_label.setText("Select file for parsing")
                generate_button.setEnabled(True)
                elapsed_time.setText("")
                return
            else:
                lines_count = sum(1 for line in open(filename.text(),"r"))

            def show_progress(counter, lines_count, start_time, progress_bar, elapsed_time):
                current_progress = round(float(counter) / lines_count,2) * 100
                if current_progress > 0.0:
                    progress_bar.setValue(current_progress)
                    elapsed_time.setText("Elapsed generating time: " + str((datetime.datetime.now() - start_time).seconds)
                                         + " from " + str(int((datetime.datetime.now() - start_time).seconds / current_progress * 100)) + " seconds")

            counter = 0
            if index1 is None and index2 is None:
                time_label.setText("Generating FAILED: select at least one filter")
                elapsed_time.setText("")
            elif index1 is None:
                with open(new_file.text(), "wb") as new_csv_file:#python3 - "w", newline=''
                    new_csv = csv.writer(new_csv_file)
                    new_csv.writerow(header_items)

                    with open(filename.text(), 'rb') as old_csv_file:#python3 - "r"
                        old_csv = csv.reader(old_csv_file)
                        for row in old_csv:
                            if (row[index2].lower() in values2) or (row[index2] in values2):
                                new_csv.writerow(row)
                            if counter % 100000 == 10:
                                show_progress(counter, lines_count, start_time, progress_bar, elapsed_time)
                            counter += 1
                time_label.setText(
                    "Generating time: " + str((datetime.datetime.now() - start_time).seconds) + " seconds")
                elapsed_time.setText("Generated: <b>" + new_file.text() + "</b>")
            elif index2 is None:
                with open(new_file.text(), "wb") as new_csv_file:#python3 - "w", newline=''
                    new_csv = csv.writer(new_csv_file)
                    new_csv.writerow(header_items)

                    with open(filename.text(), 'rb') as old_csv_file:#python3 - "r"
                        old_csv = csv.reader(old_csv_file)
                        for row in old_csv:
                            if (row[index1].lower() in values1) or (row[index1] in values1) \
                                    or (row[index1].replace(".", "_") in values1):
                                new_csv.writerow(row)
                            if counter % 100000 == 10:
                                show_progress(counter, lines_count, start_time, progress_bar, elapsed_time)
                            counter += 1
                time_label.setText(
                    "Generating time: " + str((datetime.datetime.now() - start_time).seconds) + " seconds")
                elapsed_time.setText("Generated: <b>" + new_file.text() + "</b>")
            else:
                with open(new_file.text(), "wb") as new_csv_file:#python3 - "w", newline=''
                    new_csv = csv.writer(new_csv_file)
                    new_csv.writerow(header_items)

                    with open(filename.text(), 'rb') as old_csv_file:#python3 - "r"
                        old_csv = csv.reader(old_csv_file)
                        for row in old_csv:
                            if ((row[index1].lower() in values1) or (row[index1] in values1) or (
                                row[index1].replace(".", "_") in values1)) \
                                    and ((row[index2].lower() in values2) or (row[index2] in values2)):
                                new_csv.writerow(row)
                            if counter % 100000 == 10:
                                show_progress(counter, lines_count, start_time, progress_bar, elapsed_time)
                            counter += 1
                time_label.setText(
                    "Generating time: " + str((datetime.datetime.now() - start_time).seconds) + " seconds")
                elapsed_time.setText("Generated: <b>" + new_file.text() + "</b>")

            temp_path = new_file.text()[::-1].split("\\", 1)[-1][::-1]
            new_file.setText(temp_path + "\\generated_" + time.strftime("%Y-%m-%d.%H_%M_%S") + ".csv")
            progress_bar.setValue(100)
            generate_button.setEnabled(True)
            w.repaint()
            return
        except Exception as err:
            print(err)
            time_label.setText("Generating time: Generating FAILED")
            generate_button.setEnabled(True)
            elapsed_time.setText("")
            return

    thread = threading.Thread(target=write_csv_tread, args=())
    thread.run()

generate_button.clicked.connect(lambda: generate())

### Main ###
main_layout.addStretch(1)
main_layout.addLayout(step1)
main_layout.addLayout(step2)
main_layout.addLayout(step3)
main_layout.addLayout(step4)
w.setLayout(main_layout)

w.show()
sys.exit(app.exec_())
