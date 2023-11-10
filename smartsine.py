# Useful references
# https://doc.qt.io/qtforpython-6/tutorials/basictutorial/uifiles.html
# https://david.roesel.cz/notes/posts/matplotlib-figure-embedded-in-qt/

import os
import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QTableWidgetItem
from PySide6.QtCore import QFile, QIODevice
import numpy as np
import pyperclip

import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class MainWindow():
    def __init__(self, ui_file_name):

        ####################################################
        # Load .ui QT designer file and load main window
        ####################################################
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
            sys.exit(-1)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()
        if not self.window:
            print(loader.errorString())
            sys.exit(-1)

        #########################################################
        # Show window and speicfy fixed size
        #########################################################
        self.window.show()
        self.window.setFixedSize(self.window.width(), self.window.height())

        #########################################################
        # Populate default values in the input table.
        # One row is already created and specified in .ui file.
        #########################################################
        inputs = [32, 250, 0, 0, 180]
        for colidx, inp in enumerate(inputs):
            self.window.tbl.setItem(0, colidx, QTableWidgetItem(str(inp)))

        #########################################################
        # Assign callback functions for "events".
        # These are signals associated with the widgets.
        #########################################################
        self.window.btn_calculate.clicked.connect(self.calculate)
        self.window.btn_copy.clicked.connect(self.copy)
        self.window.slider.valueChanged.connect(self.slider_changed)

        #########################################################
        # Update label text with default slider value.
        # This could also be manually done in the designer.
        #########################################################
        self.vals_per_line = int(self.window.slider.value())
        self.window.lbl_slider.setText(str(self.vals_per_line))

        #########################################################
        # Add matplotplib canvas for plotting
        #########################################################
        self.figure = Figure()
        self.axis = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.window.plotLayout.addWidget(self.canvas)
        self.canvas.draw()
        self.figure.tight_layout()

        #########################################################
        # Initialize other variables
        #########################################################
        self.sine_txt = ""

    #########################################################
    # Callback function for button
    #########################################################
    def calculate(self):
        # Read in the 5 parameters from the table:
        #   n = number of entries in table
        #   amplitude = sine wave amplitude (0 to peak)
        #   offset = dc offset of sine wave
        #   ang_start = starting angle for sine wave, in degrees
        #   ang_end = ending angle for sine wave, in degrees
        #
        # Default values of 32, 250, 0, 0, 180:
        #   32 entries in table
        #   Sine wave amplitude = 250 from center point,
        #       so this would be +/- 250 form center point
        #       for a peak to peak amplitude of 500
        #   Offset = 0
        #   Generate from 0 to 180 degrees - a half sine wave
        n, amplitude, offset, ang_start, ang_end = [
            float(self.window.tbl.item(0, i).text())
            for i in range(0, 5)
        ]
        n = int(n)

        # Create series of angles based on provided parameters.
        # Do not include the end angle.
        angles_deg = np.linspace(start=ang_start, stop=ang_end,
                                 num=n, endpoint=False)

        # Input parameter is in degrees, so convert to radians:
        angles_rad = np.deg2rad(angles_deg)

        # Compute sine table entries based on provided parameters:
        sin_table = np.empty((n))
        sin_text = ""
        for i, ang in enumerate(angles_rad):
            sin_val = int(round(amplitude * np.sin(ang) + offset))
            sin_table[i] = sin_val
            sin_text += f"{sin_val}"
            if i < len(angles_rad) - 1:
                # Only add comma if not the last element
                sin_text += ", "
            if (i+1) % self.vals_per_line == 0:
                # Add new line after specified number of entries
                # as per slider in UI.
                sin_text += "\n"

        # Update text browser widget:
        self.window.txt.setText(sin_text)

        self.sine_txt = sin_text

        # Generate plot based on computed table:
        self.axis.clear()
        self.axis.set_xlabel("Index")
        self.axis.plot(range(n), sin_table, marker='o')
        self.figure.tight_layout()
        self.canvas.draw()

    #########################################################
    # Callback function for button
    #########################################################
    def copy(self):
        pyperclip.copy(self.sine_txt)

    #########################################################
    # Callback function for slider
    #########################################################
    def slider_changed(self):
        self.vals_per_line = int(self.window.slider.value())
        self.window.lbl_slider.setText(str(self.vals_per_line))


matplotlib.use("Qt5Agg")

# Assume smartsine.ui is in the same directory as this script.
# Create absolute path to it so it doesn't matter where the script is run from.
script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
fname = "smartsine.ui"
ui_file_name = os.path.abspath(os.path.join(script_directory, fname))

app = QApplication(sys.argv)

mw = MainWindow(ui_file_name)

sys.exit(app.exec())
