# type: ignore
from PyQt5 import QtWidgets, uic, QtCore, QtGui, Qt
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from string import ascii_uppercase as alc
import sys
class ServerIcon(QtWidgets.QWidget):
    def __init__(self, filePath, serverName, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serverLabel = QLabel(serverName)
        self.iconLabel = QLabel()
        self.iconLabel.setPixmap(self._getIcon(filePath, 80))
        self.serverLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.iconLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.boxlayout = QHBoxLayout()
        self.boxlayout.addWidget(self.iconLabel, 1)
        self.boxlayout.addWidget(self.serverLabel, 0)
        self.setLayout(self.boxlayout)
    def set_data(self, data):
        self.data = data
    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)
    def _getIcon(self, filePath, size = 80):
        squareImage = QtGui.QImage()
        squareImage.load(filePath)
        squareImage.convertToFormat(QImage.Format_ARGB32)

        # Crop image to a square:   
        imgsize = min(squareImage.width(), squareImage.height())
        rect = QRect(
            int((squareImage.width() - imgsize) / 2),
            int((squareImage.height() - imgsize) / 2),
            int(imgsize),
            int(imgsize),
        )
        squareImage = squareImage.copy(rect)

        # Create the output image with the same dimensions and an alpha channel
        # and make it completely transparent:
        out_img = QImage(imgsize, imgsize, QImage.Format_ARGB32)
        out_img.fill(Qt.transparent)

        # Create a texture brush and paint a circle with the original image onto
        # the output image:
        brush = QtGui.QBrush(squareImage)        # Create texture brush
        painter = QtGui.QPainter(out_img)  # Paint the output image
        painter.setBrush(brush)      # Use the image texture brush
        painter.setPen(Qt.NoPen)     # Don't draw an outline
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)  # Use AA
        painter.drawEllipse(0, 0, imgsize, imgsize)  # Actually draw the circle
        painter.end()                # We are done (segfault if you forget this)

        # Convert the image to a pixmap and rescale it.  Take pixel ratio into
        # account to get a sharp image on retina displays:
        pr = QWindow().devicePixelRatio()
        pm = QtGui.QPixmap.fromImage(out_img)
        pm.setDevicePixelRatio(pr)
        size *= pr
        pm = pm.scaled(int(size), int(size), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        return pm   
class DragWidget(QWidget):
    """
    Generic list sorting handler.
    """

    orderChanged = pyqtSignal(list)

    def __init__(self, *args, orientation=Qt.Orientation.Vertical, **kwargs):
        super().__init__()
        self.setAcceptDrops(True)

        # Store the orientation for drag checks later.
        self.orientation = orientation

        if self.orientation == Qt.Orientation.Vertical:
            self.blayout = QVBoxLayout()
        else:
            self.blayout = QHBoxLayout()

        self.setLayout(self.blayout)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()

        for n in range(self.blayout.count()):
            # Get the widget at each index in turn.
            w = self.blayout.itemAt(n).widget()
            if self.orientation == Qt.Orientation.Vertical:
                # Drag drop vertically.
                drop_here = pos.y() < w.y() + w.size().height() // 2
            else:
                # Drag drop horizontally.
                drop_here = pos.x() < w.x() + w.size().width() // 2

            if drop_here:
                # We didn't drag past this widget.
                # insert to the left of it.
                self.blayout.insertWidget(n-1, widget)
                self.orderChanged.emit(self.get_item_data())
                break

        e.accept()
    def add_item(self, item):
        self.blayout.addWidget(item)

    def get_item_data(self):
        data = []
        for n in range(self.blayout.count()):
            # Get the widget at each index in turn.
            w = self.blayout.itemAt(n).widget()
            data.append(w.data)

        return data
class CurserScrollableArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(False)
        self.setGeometry(10, 0, 461, 881)
    def mouseMoveEvent(self, event):
        y = event.y()
        height = self.height()
        border = 80  # adjust the border value as needed

        if y < border:
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - border + y
            )
        elif y > height - border:
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + y - height + border
            )

        super().mouseMoveEvent(event)
class ClassWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(ClassWindow, self).__init__(*args, **kwargs)
        uic.loadUi('src/resources/ui/mainwindow.ui', self)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.scrollArea1 = CurserScrollableArea(self)
        self.scroll = self.scrollArea1          
        #self.scroll.setWidget(self.widget)
        self.setWindowTitle("Discord Server Manager")
        self.verticalLayout1 = DragWidget()
        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.verticalLayout1)
        layout.addStretch(1)
        self.scroll.setLayout(layout)
        self.confirmButton.clicked.connect(self._confirmButtonEvent)
        self.count = 0        
        self.dataOrder = {"before": [], "after": []}
    def _confirmButtonEvent(self):
        self.dataOrder['after'] = self.verticalLayout1.get_item_data()
        print(f"get_item_data: {self.verticalLayout1.get_item_data()}")
        self.event(self.dataOrder['before'], self.dataOrder['after'])
        self.dataOrder['before'] = self.dataOrder['after']
    def setConfirmButtonEvent(self, event):
        self.event = event
    def addServer(self, imagePath, serverName, widgetData):
        dragItem = ServerIcon(imagePath, serverName)
        dragItem.set_data(widgetData)
        self.verticalLayout1.add_item(dragItem)
        self.count += 1
    def show(self) -> None:
        self.dataOrder['before'] =  self.verticalLayout1.get_item_data()
        return super().show()
class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(LoginWindow, self).__init__(*args, **kwargs)
        uic.loadUi('src/resources/ui/login.ui', self)
        self.login_button = self.login
        self.is_not_logged = True
        self.setWindowTitle('Discord Server Manager Login Page')
        self.mainWindow = ClassWindow()
    def saved_token(self, token):
        self.discordTokenLineEdit.setText(token)
    def login_event(self):
        self.accept()
        window.close()
    def getToken(self):
        print('LoginWindow.getToken() has been executed')
        return self.discordTokenLineEdit.text()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = ClassWindow()
    for l, n in alc:
        mw.addServer("C:\\Users\\user\\AppData\\Local\\Temp\\Pastel-Indigo.png", n, l)
    mw.show()
    sys.exit(app.exec_())