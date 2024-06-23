import sys
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
    QFileDialog, QColorDialog, QGraphicsView, QGraphicsScene, QMessageBox
)
from PyQt5.QtSvg import QGraphicsSvgItem, QSvgRenderer
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPainter

class SvgViewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.svg_item = None
        self.setAcceptDrops(True)

    def load_svg(self, svg_content):
        self.scene.clear()
        svg_renderer = QSvgRenderer()
        if svg_renderer.load(svg_content.encode('utf-8')):
            self.svg_item = QGraphicsSvgItem()
            self.svg_item.setSharedRenderer(svg_renderer)
            self.scene.addItem(self.svg_item)
            self.svg_item.setFlag(QGraphicsSvgItem.ItemIsMovable)
            self.setSceneRect(self.svg_item.boundingRect())
        else:
            print("Failed to load SVG")

    def wheelEvent(self, event):
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)

    def fit_to_window(self):
        if self.svg_item:
            self.fitInView(self.svg_item, Qt.KeepAspectRatio)

    def reset_zoom(self):
        self.resetTransform()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.svg'):
                    try:
                        with open(file_path, 'r') as file:
                            svg_content = file.read()
                            self.parentWidget().text_edit.setPlainText(svg_content)
                    except Exception as e:
                        print(f"Failed to open file: {e}")

class SvgTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.svg'):
                    try:
                        with open(file_path, 'r') as file:
                            svg_content = file.read()
                            self.setPlainText(svg_content)
                    except Exception as e:
                        print(f"Failed to open file: {e}")

class SvgEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setAcceptDrops(True)

    def initUI(self):
        self.setWindowTitle('SVG Inspector')

        # Main layout
        layout = QHBoxLayout()

        # Text edit for SVG code
        self.text_edit = SvgTextEdit()
        self.text_edit.setPlaceholderText("Write SVG code here...")
        layout.addWidget(self.text_edit)

        # SVG viewer
        self.viewer = SvgViewer()
        layout.addWidget(self.viewer)

        # Button layout
        vbox = QVBoxLayout()
        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self.open_svg)
        vbox.addWidget(self.open_button)

        self.save_button = QPushButton("Save As")
        self.save_button.clicked.connect(self.save_svg)
        vbox.addWidget(self.save_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_svg)
        vbox.addWidget(self.clear_button)

        self.fit_button = QPushButton("Fit to Window")
        self.fit_button.clicked.connect(self.viewer.fit_to_window)
        vbox.addWidget(self.fit_button)

        self.reset_button = QPushButton("Reset Zoom")
        self.reset_button.clicked.connect(self.viewer.reset_zoom)
        vbox.addWidget(self.reset_button)

        self.validate_button = QPushButton("Validate SVG")
        self.validate_button.clicked.connect(self.validate_svg)
        vbox.addWidget(self.validate_button)

        self.color_picker_button = QPushButton("Pick Color")
        self.color_picker_button.clicked.connect(self.pick_color)
        vbox.addWidget(self.color_picker_button)

        vbox.addStretch()
        layout.addLayout(vbox)

        # Connect text change to update SVG
        self.text_edit.textChanged.connect(self.update_svg)
        
        # Set main layout
        self.setLayout(layout)
        self.resize(1000, 600)

    def update_svg(self):
        svg_content = self.text_edit.toPlainText()
        self.viewer.load_svg(svg_content)

    def open_svg(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open SVG", "", "SVG Files (*.svg);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    svg_content = file.read()
                    self.text_edit.setPlainText(svg_content)
            except Exception as e:
                print(f"Failed to open file: {e}")

    def save_svg(self):
        svg_content = self.text_edit.toPlainText()
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save SVG", "", "SVG Files (*.svg);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'w') as file:
                    file.write(svg_content)
            except Exception as e:
                print(f"Failed to save file: {e}")

    def clear_svg(self):
        self.text_edit.clear()

    def validate_svg(self):
        svg_content = self.text_edit.toPlainText()
        try:
            ET.fromstring(svg_content)
            QMessageBox.information(self, "Validation", "SVG is valid.")
        except ET.ParseError as e:
            QMessageBox.critical(self, "Validation Error", f"SVG is invalid: {e}")

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            color_code = color.name()
            self.text_edit.insertPlainText(color_code)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.svg'):
                    try:
                        with open(file_path, 'r') as file:
                            svg_content = file.read()
                            self.text_edit.setPlainText(svg_content)
                    except Exception as e:
                        print(f"Failed to open file: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = SvgEditor()
    editor.show()
    sys.exit(app.exec_())
