import os
import subprocess
from PyQt5 import QtCore, QtGui, QtWidgets


class SettingsWidget(QtWidgets.QWidget):
    start_clicked = QtCore.pyqtSignal()

    def __init__(self, common):
        super(SettingsWidget, self).__init__()
        self.common = common

        # Dangerous document
        self.dangerous_doc_label = QtWidgets.QLabel()
        self.dangerous_doc_label.setAlignment(QtCore.Qt.AlignCenter)
        self.dangerous_doc_label.setStyleSheet(
            "QLabel { font-size: 16px; font-weight: bold; color: #572606; }"
        )

        # Save safe version
        self.save_checkbox = QtWidgets.QCheckBox("Save safe PDF")
        self.save_checkbox.clicked.connect(self.update_ui)
        self.save_lineedit = QtWidgets.QLineEdit()
        self.save_lineedit.setReadOnly(True)
        self.save_browse_button = QtWidgets.QPushButton("Save as...")
        self.save_browse_button.clicked.connect(self.save_browse_button_clicked)
        save_layout = QtWidgets.QHBoxLayout()
        save_layout.addWidget(self.save_checkbox)
        save_layout.addWidget(self.save_lineedit)
        save_layout.addWidget(self.save_browse_button)
        save_layout.addStretch()

        # Open safe document
        self.open_checkbox = QtWidgets.QCheckBox(
            "Open safe document after converting, using"
        )
        self.open_checkbox.clicked.connect(self.update_ui)
        self.open_combobox = QtWidgets.QComboBox()
        for k in self.common.pdf_viewers:
            self.open_combobox.addItem(k, QtCore.QVariant(self.common.pdf_viewers[k]))
        open_layout = QtWidgets.QHBoxLayout()
        open_layout.addWidget(self.open_checkbox)
        open_layout.addWidget(self.open_combobox)
        open_layout.addStretch()

        # OCR document
        self.ocr_checkbox = QtWidgets.QCheckBox("OCR document, language")
        self.ocr_combobox = QtWidgets.QComboBox()
        for k in self.common.ocr_languages:
            self.ocr_combobox.addItem(k, QtCore.QVariant(self.common.ocr_languages[k]))
        ocr_layout = QtWidgets.QHBoxLayout()
        ocr_layout.addWidget(self.ocr_checkbox)
        ocr_layout.addWidget(self.ocr_combobox)
        ocr_layout.addStretch()

        # Update container
        self.update_checkbox = QtWidgets.QCheckBox("Update container")
        update_layout = QtWidgets.QHBoxLayout()
        update_layout.addWidget(self.update_checkbox)
        update_layout.addStretch()

        # Button
        self.start_button = QtWidgets.QPushButton("Convert to Safe Document")
        self.start_button.clicked.connect(self.start_button_clicked)
        self.start_button.setStyleSheet(
            "QPushButton { font-size: 16px; font-weight: bold; }"
        )
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addStretch()

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.dangerous_doc_label)
        layout.addLayout(save_layout)
        layout.addLayout(open_layout)
        layout.addLayout(ocr_layout)
        layout.addLayout(update_layout)
        layout.addLayout(button_layout)
        layout.addStretch()
        self.setLayout(layout)

        # Load values from settings
        if self.common.settings.get("save"):
            self.save_checkbox.setCheckState(QtCore.Qt.Checked)
        else:
            self.save_checkbox.setCheckState(QtCore.Qt.Unchecked)

        if self.common.settings.get("ocr"):
            self.ocr_checkbox.setCheckState(QtCore.Qt.Checked)
        else:
            self.ocr_checkbox.setCheckState(QtCore.Qt.Unchecked)

        index = self.ocr_combobox.findText(self.common.settings.get("ocr_language"))
        if index != -1:
            self.ocr_combobox.setCurrentIndex(index)

        if self.common.settings.get("open"):
            self.open_checkbox.setCheckState(QtCore.Qt.Checked)
        else:
            self.open_checkbox.setCheckState(QtCore.Qt.Unchecked)

        index = self.open_combobox.findText(self.common.settings.get("open_app"))
        if index != -1:
            self.open_combobox.setCurrentIndex(index)

        if self.common.settings.get("update_container"):
            self.update_checkbox.setCheckState(QtCore.Qt.Checked)
        else:
            self.update_checkbox.setCheckState(QtCore.Qt.Unchecked)

        # Is update containers required?
        output = subprocess.check_output(
            [self.common.container_runtime, "image", "ls", "dangerzone"]
        )
        if b"dangerzone" not in output:
            self.update_checkbox.setCheckState(QtCore.Qt.Checked)
            self.update_checkbox.setEnabled(False)

    def update_ui(self):
        # Either save or open must be checked
        if (
            self.save_checkbox.checkState() == QtCore.Qt.Checked
            or self.open_checkbox.checkState() == QtCore.Qt.Checked
        ):
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)

    def document_selected(self):
        # Update the danger doc label
        self.dangerous_doc_label.setText(
            f"Dangerous: {os.path.basename(self.common.document_filename)}"
        )

        # Update the save location
        self.common.save_filename = (
            f"{os.path.splitext(self.common.document_filename)[0]}-safe.pdf"
        )
        self.save_lineedit.setText(os.path.basename(self.common.save_filename))

    def save_browse_button_clicked(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save safe PDF as...",
            self.common.save_filename,
            filter="Documents (*.pdf)",
        )
        if filename[0] != "":
            self.common.save_filename = filename[0]
            self.save_lineedit.setText(os.path.basename(self.common.save_filename))

    def start_button_clicked(self):
        # Update settings
        self.common.settings.set(
            "save", self.save_checkbox.checkState() == QtCore.Qt.Checked
        )
        self.common.settings.set(
            "ocr", self.ocr_checkbox.checkState() == QtCore.Qt.Checked
        )
        self.common.settings.set("ocr_language", self.ocr_combobox.currentText())
        self.common.settings.set(
            "open", self.open_checkbox.checkState() == QtCore.Qt.Checked
        )
        self.common.settings.set("open_app", self.open_combobox.currentText())
        self.common.settings.set(
            "update_container", self.update_checkbox.checkState() == QtCore.Qt.Checked
        )
        self.common.settings.save()

        # Start!
        self.start_clicked.emit()
