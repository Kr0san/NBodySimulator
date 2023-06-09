from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal


class ColorButton(QtWidgets.QPushButton):
    """
    Custom Qt Widget to show a chosen color.

    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).
    """

    colorChanged = pyqtSignal(object)

    def __init__(self, *args, color=None, **kwargs):
        super(ColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self._default = color
        self.pressed.connect(self.on_color_picker)

        # Set the initial/default state.
        self.set_color(self._default)

    def set_color(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit(color)

        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def on_color_picker(self):
        """
        Show color-picker dialog to select color.
        Qt will use the native dialog by default.
        """

        dlg = QtWidgets.QColorDialog(self)
        dlg.setStyleSheet("background-color: white")  # Overrides color picker background to white
        if self._color:
            dlg.setCurrentColor(QtGui.QColor(self._color))

        if dlg.exec():
            self.set_color(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.RightButton:
            self.set_color(self._default)

        return super(ColorButton, self).mousePressEvent(e)
