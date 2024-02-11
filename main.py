import sys
from PyQt6.QtGui import QPen, QColor, QPolygonF, QValidator, \
    QRegularExpressionValidator, QPainter, QAction, QBrush
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsView, \
    QGraphicsScene, QGraphicsItem, QSplitter, QTableWidget, QHBoxLayout, \
    QTableWidgetItem, QMessageBox, QItemDelegate, QLineEdit, QFileDialog, \
    QGraphicsTextItem, QHeaderView, QMenu, QGraphicsRectItem, QProgressDialog
from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QObject, QLocale, \
    QRegularExpression, QTimer

import os
import model
# import pandas as pd

from main_window import Ui_MainWindow

import math
import json
import re


class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        self.setRenderHint(
            QPainter.RenderHint.Antialiasing, True)

        self.min_zoom = 0.035
        self.max_zoom = 6.0
        # Set the anchor point for the zoom
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

    def scale_items(self, scale):
        for item in self.scene().items():
            if isinstance(item, Boat):
                item.scale(scale, self.transform().m11())

    def wheelEvent(self, event):
        zoom_out_factor = 0.8  # Zoom-out factor
        zoom_in_factor = 1.25  # Zoom-in factor

        mouse_position = event.position().toPoint()

        # scene_position = self.mapToScene(mouse_position)

        h_scrollbar = self.horizontalScrollBar()
        v_scrollbar = self.verticalScrollBar()

        h_scrollbar_rect = h_scrollbar.geometry()
        v_scrollbar_rect = v_scrollbar.geometry()

        if not (h_scrollbar_rect.contains(mouse_position) or v_scrollbar_rect.contains(mouse_position)):
            current_scale = self.transform().m11()

            if event.angleDelta().y() > 0:
                if current_scale * zoom_in_factor <= self.max_zoom:
                    self.scale(zoom_in_factor, zoom_in_factor)
                    self.scale_items(zoom_out_factor)
            else:
                if current_scale * zoom_out_factor >= self.min_zoom:
                    self.scale(zoom_out_factor, zoom_out_factor)
                    self.scale_items(zoom_in_factor)

        else:
            super().wheelEvent(event)


class Boat(QGraphicsItem):

    shared_COG = None

    def __init__(self, ID: int, BRG: float, RB: float, DST: float, COG: float, SOG: float, N_Status: int, Priority_T: int, OV: float, HO: float, CS: float, row: int):
        super().__init__()

        self.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, False)
        self.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIgnoresParentOpacity, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsPanel, True)

        self.ID = ID
        self.BRG = BRG
        self.RB = RB
        self.DST = DST
        self.COG = COG
        self.SOG = SOG
        self.OV = OV
        self.HO = HO
        self.CS = CS

        self.N_Status = N_Status
        self.Priority_T = Priority_T

        self.row = row

        self.polygon = QPolygonF([QPointF(-3, 6), QPointF(0, -6),
                                  QPointF(3, 6), QPointF(0, 3.5)])

        self.std_polygon = QPolygonF([QPointF(-3, 6), QPointF(0, -6),
                                      QPointF(3, 6), QPointF(0, 3.5)])

        # self.bounding_rect = QGraphicsRectItem(self.boundingRect(), self)
        # self.bounding_rect.setPen(QPen(QColor(0, 0, 255, 100)))
        # self.bounding_rect.setBrush(Qt.GlobalColor.transparent)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)
        self.setAcceptHoverEvents(True)
        self.is_hovered = False
        self.activation_zone = None

        self.text_item = QGraphicsTextItem(self)
        self.text_item.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)

        if self.ID == 0:
            Boat.shared_COG = self.COG

        self.hover_timer = QTimer()
        self.hover_timer.setInterval(300)
        self.hover_timer.timeout.connect(self.show_hover_text)

        self.signals = BoatSignal()

        self.const_pix = 16.666666667
        self.center_x, self.center_y = 25000.0, 25000.0
        self.const_m_in_mil = 0.62 / 1000

    def boundingRect(self):
        return self.polygon.boundingRect()

    def paint(self, painter, option, widget):
        pen = QPen()
        pen.setWidth(0)
        painter.setPen(pen)

        if self.is_hovered:  # self.isSelected() or
            painter.setBrush(QColor(0, 255, 0, 180))
        else:
            painter.setBrush(QColor(255, 0, 0, 180))

        painter.drawPolygon(self.polygon)

    def scale(self, scale, current_scale):
        if current_scale <= 2.5:
            scaled_polygon = QPolygonF()
            for point in self.polygon:
                scaled_point = QPointF(point.x() * scale, point.y() * scale)
                scaled_polygon.append(scaled_point)
            self.polygon = scaled_polygon
        else:
            scaled_polygon = QPolygonF()
            scale = 0.9
            for point in self.std_polygon:
                scaled_point = QPointF(point.x() * scale, point.y() * scale)
                scaled_polygon.append(scaled_point)
            self.polygon = scaled_polygon

    def mousePressEvent(self, event):
        # self.setCursor(Qt.CursorShape.ClosedHandCursor)
        self.text_item.setPlainText('')
        self.hover_timer.stop()
        self.signals.clicked_boat.emit(self.row)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.hover_timer.start()
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.is_hovered = True
        self.activation_zone = self.boundingRect()
        self.update()
        # self.update_hover_text()
        self.hover_timer.start()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.is_hovered = False
        self.activation_zone = None
        self.text_item.setPlainText('')
        self.update()
        self.hover_timer.stop()
        super().hoverLeaveEvent(event)

    def show_hover_text(self):
        if self.is_hovered and self.ID != 0:
            font = self.text_item.font()
            font.setPointSize(12)
            self.text_item.setFont(font)

            text = f"ID: {self.ID}"
            self.text_item.setPlainText(text)
            # Calculate the position for displaying the text near the boat
            offset_x = -self.boundingRect().width()
            offset_y = -self.boundingRect().height() - self.boundingRect().height() / \
                2  # - self.text_item.boundingRect().height() - 5
            text_position = QPointF(offset_x, offset_y)
            self.text_item.setPos(text_position)

    def update_speed(self, new_speed):
        self.SOG = new_speed

    def itemChange(self, change, value):
        if change == self.GraphicsItemChange.ItemPositionChange and self.scene():
            self.signals.positionChanged.emit(self)
        return QGraphicsItem.itemChange(self, change, value)

    def calculate_distance(self):
        if self.ID != 0:
            boat_x, boat_y = self.pos().x(), self.pos().y()
            DST = ((boat_x - self.center_x) ** 2 +
                   ((boat_y - self.center_y) ** 2)) ** 0.5
            self.DST = DST * self.const_pix * self.const_m_in_mil

    def calculate_pelling(self):
        boat_x, boat_y = self.pos().x(), self.pos().y()
        angle = math.degrees(math.atan2(
            boat_x - self.center_x, self.center_y - boat_y))
        if angle < 0:
            angle += 360
        self.BRG = angle

    def calculate_RB(self):
        tmp_RB = self.BRG - self.shared_COG
        if tmp_RB >= 180:
            self.RB = tmp_RB - 360
        else:
            self.RB = tmp_RB

    def rotate_boat(self, rot):
        self.COG = float(rot)
        self.setRotation(self.COG)

        if self.ID == 0:
            Boat.shared_COG = self.COG

    def contextMenuEvent(self, event):
        contextMenu = QMenu()
        deleteAction = QAction("Delete")
        if self.ID != 0:
            contextMenu.addAction(deleteAction)
            action = contextMenu.exec(event.screenPos())
            if action == deleteAction:
                self.signals.boat_deleted.emit(self)
        # return super().contextMenuEvent(event)

    def change_distance(self, new_DST):

        new_DST = float(new_DST) / self.const_pix / self.const_m_in_mil
        DST = self.DST / self.const_pix / self.const_m_in_mil
        x, y = self.pos().x(), self.pos().y()

        if DST != 0:
            x2 = self.center_x - (new_DST/DST) * (self.center_x - x)
            y2 = self.center_y - (new_DST/DST) * (self.center_y - y)
        else:
            x2 = self.center_x
            y2 = self.center_y - new_DST

        self.signals.blockSignals(True)
        self.setPos(x2, y2)
        self.signals.blockSignals(False)

        self.DST = new_DST * self.const_pix * self.const_m_in_mil

    def change_pelling(self, new_BRG):
        new_BRG = float(new_BRG)
        x2 = self.center_x + self.DST / self.const_pix / self.const_m_in_mil * \
            math.sin(new_BRG * math.pi / 180)
        y2 = self.center_y - self.DST / self.const_pix / self.const_m_in_mil * \
            math.cos(new_BRG * math.pi / 180)
        self.signals.blockSignals(True)
        self.setPos(x2, y2)
        self.signals.blockSignals(False)
        self.BRG = new_BRG

    def change_RB(self, new_RB):
        new_BRG = self.BRG - self.RB + float(new_RB)
        self.RB = float(new_RB)
        self.change_pelling(new_BRG)


class BoatSignal(QObject):
    positionChanged = pyqtSignal(QGraphicsItem)
    boat_deleted = pyqtSignal(QGraphicsItem)
    clicked_boat = pyqtSignal(int)


class row_edit(QObject):
    row_changed = pyqtSignal(QTableWidgetItem, Boat)
    row_delete = pyqtSignal(Boat)


class ValidatorDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.validators = {}

    def setValidator(self, column, validator):
        self.validators[column] = validator

    def createEditor(self, parent, option, index):
        column = index.column()
        if column in self.validators:
            editor = QLineEdit(parent)
            validator = self.validators[column]
            editor.setValidator(validator)
            return editor

        return super().createEditor(parent, option, index)

    def setModelData(self, editor, model, index):
        column = index.column()
        text = editor.text()
        text = text.replace(QLocale().decimalPoint(), '.')
        if column in self.validators:
            validator = self.validators[column]
            state, _, pos = validator.validate(text, 0)

            text = re.findall(r'[0-9.,-]+', text)
            text = text[0] if len(text) >= 1 else text

            if state != QValidator.State.Acceptable or not check_float(text):
                QMessageBox.warning(None, "Invalid Data",
                                    "Invalid data type entered.")
                return

            if text[0] == '.':
                text = '0' + text

            if text[0] == '-' and text[1] == '.':
                text = text[0] + '0' + text[1:]

            if column in [8, 9, 10] and not (0 <= float(text) <= 1):
                QMessageBox.warning(None, "Invalid Data",
                                    "Value must be between 0 and 1.")
                return

            if column == 0 and not text.isdigit():
                QMessageBox.warning(None, "Invalid Data",
                                    "Value must be integer.")
                return

            if column == 3 and float(text) < 0:
                QMessageBox.warning(None, "Invalid Data",
                                    "Value must be positive.")
                return

        editor.setText(text)

        super().setModelData(editor, model, index)


def check_float(num):
    try:
        float(num)
        return True
    except:
        return False


class Table(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(12)
        self.setHorizontalHeaderLabels(
            ['ID', 'BRG', 'RB', 'DST', 'COG', 'SOG', 'N Status', 'Priority T',
             'OV', 'HO', 'CS', 'Situation'])

        self.signals = row_edit()

        self.connected_boats = []

        self.validatorDelegate = ValidatorDelegate(self)
        self.setItemDelegate(self.validatorDelegate)

        validator = QRegularExpressionValidator(
            QRegularExpression(''))

        for column in range(0, self.columnCount()-1):
            self.validatorDelegate.setValidator(column, validator)

        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)

        self.cellChanged.connect(self.resizeColumnsToContents)

    def add_row(self, boat):
        row = self.rowCount()
        self.insertRow(row)

        OV_item = QTableWidgetItem(str())
        HO_item = QTableWidgetItem(str())
        CS_item = QTableWidgetItem(str())

        Priority_T = QTableWidgetItem(str(boat.Priority_T))

        pred_NN = QTableWidgetItem(str())

        pred_NN.setFlags(pred_NN.flags() & ~Qt.ItemFlag.ItemIsEditable)

        # OV_item.setFlags(OV_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        # HO_item.setFlags(HO_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        # CS_item.setFlags(CS_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        Priority_T.setFlags(Priority_T.flags() & ~Qt.ItemFlag.ItemIsEditable)

        boat.row = row
        boat.calculate_distance()
        boat.calculate_pelling()
        boat.calculate_RB()

        self.setItem(row, 0, QTableWidgetItem(str(boat.ID)))

        self.setItem(row, 1, QTableWidgetItem(f'{round(boat.BRG, 2)}°'))
        self.setItem(row, 2, QTableWidgetItem(f'{round(boat.RB, 2)}°'))
        self.setItem(row, 3, QTableWidgetItem(f'{round(boat.DST, 2)} nm'))
        self.setItem(row, 4, QTableWidgetItem(f'{round(boat.COG, 2)}°'))
        self.setItem(row, 5, QTableWidgetItem(f'{round(boat.SOG)} kn'))

        self.setItem(row, 6, QTableWidgetItem(str(boat.N_Status)))
        self.setItem(row, 7, Priority_T)

        self.setItem(row, 8, QTableWidgetItem(str(boat.OV)))
        self.setItem(row, 9, QTableWidgetItem(str(boat.HO)))
        self.setItem(row, 10, QTableWidgetItem(str(boat.CS)))
        self.setItem(row, 11, pred_NN)

        self.connected_boats.append(boat)
        boat.signals.clicked_boat.connect(self.on_boat_clicked)

        self.itemChanged.connect(self.boat_row_changed)

    def on_boat_clicked(self, row):
        # Programmatically click on the corresponding row in the table
        # if row >= 0 and row < self.rowCount():
        self.selectRow(row)

    def update_row(self, boat):
        row = boat.row
        boat.calculate_distance()
        boat.calculate_pelling()
        boat.calculate_RB()
        self.setItem(row, 1, QTableWidgetItem(f'{round(boat.BRG, 2)}°'))
        self.setItem(row, 2, QTableWidgetItem(f'{round(boat.RB, 2)}°'))
        self.setItem(row, 3, QTableWidgetItem(f'{round(boat.DST, 2)} nm'))

        # self.setItem(row, 3, QTableWidgetItem(str(boat.display_cog())))
        # self.setItem(row, 4, QTableWidgetItem(str(boat.display_sog())))
        # self.blockSignals(False)

    def boat_row_changed(self, item):
        row = item.row()
        column = item.column()

        if row not in range(len(self.connected_boats)):
            return

        boat = self.connected_boats[row]

        # and check_float(item.text()):
        if (column in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] or column == 0) and row == boat.row:
            if column == 0:
                boat.ID = item.text()

            if check_float(item.text()):
                if column == 1:
                    boat.change_pelling(item.text())
                    boat.calculate_RB()
                    self.setItem(row, 1, QTableWidgetItem(
                        f'{round(boat.BRG, 2)}°'))
                    self.setItem(row, 2, QTableWidgetItem(
                        f'{round(boat.RB, 2)}°'))

                elif column == 2:
                    boat.change_RB(item.text())
                    boat.calculate_pelling()
                    self.setItem(row, 2, QTableWidgetItem(
                        f'{round(boat.RB, 2)}°'))
                    self.setItem(row, 1, QTableWidgetItem(
                        f'{round(boat.BRG, 2)}°'))

                elif column == 3:
                    boat.change_distance(item.text())
                    self.setItem(row, 3, QTableWidgetItem(
                        f'{round(boat.DST, 2)} nm'))

                elif column == 4:
                    if boat.ID != 0:
                        boat.rotate_boat(item.text())
                        self.setItem(row, 4, QTableWidgetItem(
                            f'{round(boat.COG, 2)}°'))
                    else:
                        boat.rotate_boat(item.text())
                        self.setItem(row, 4, QTableWidgetItem(
                            f'{round(boat.COG, 2)}°'))
                        for boat in self.connected_boats[1:]:
                            boat.calculate_RB()
                            self.update_row(boat)

                elif column == 5:
                    boat.SOG = float(item.text())
                    self.setItem(row, 5, QTableWidgetItem(
                        f'{round(boat.SOG, 2)} kn'))

                elif column == 6:
                    boat.N_Status = int(item.text())

                elif column == 7:
                    boat.Priority_T = int(item.text())

                elif column == 8:
                    boat.OV = float(item.text())
                elif column == 9:
                    boat.HO = float(item.text())
                elif column == 10:
                    boat.CS = float(item.text())

    def delete_boat_row(self, boat):
        self.removeRow(boat.row)
        self.connected_boats.remove(boat)

    def boats_disconnect(self):
        self.disconnect()
        self.connected_boats = []


class Main_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

        self.graphicsView = CustomGraphicsView(self.ui.centralwidget)

        self.NN = model.NN()

        self.ui.create_file.triggered.connect(self.create_file)
        self.ui.save_file.triggered.connect(self.save_file)
        self.ui.open_file.triggered.connect(self.open_file)
        self.ui.training.triggered.connect(self.training)

        self.ui.start_classification.triggered.connect(
            self.start_classification)
        self.ui.open_weights.triggered.connect(self.open_weights)
        self.ui.save_weights.triggered.connect(self.save_weights)
        self.ui.reset_training.triggered.connect(self.reset_weights)

        self.tableWidget = Table()

        layout = QHBoxLayout(self.ui.centralwidget)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(10)
        self.splitter.addWidget(self.graphicsView)
        self.splitter.addWidget(self.tableWidget)

        self.splitter.setStretchFactor(0, 5)
        self.splitter.setStretchFactor(1, 1)

        layout.addWidget(self.splitter)

        self.boats = []
        self.possible_id_boat = None

        self.default_path_boats = 'data_boats'
        self.default_path_weights = 'NN_weights'

        self.weights = None
        # self.default_open_path = ""

        # self.setStyleSheet("background: white;")

    def contextMenuEvent(self, event):
        event_position = event.pos()

        if self.graphicsView.viewport().rect().contains(event_position):
            self.context_menu_position = event_position
            context_menu = QMenu(self)
            create_boat_action = QAction('Create Boat', self)
            create_boat_action.triggered.connect(self.add_boat)
            context_menu.addAction(create_boat_action)
            context_menu.exec(event.globalPos())

    def add_boat(self):
        self.create_unique_ID()
        boat = Boat(self.possible_id_boat, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.possible_id_boat += 1
        self.boats.append(boat)

        self.graphicsView.scene().addItem(boat)

        boat.polygon = self.boats[0].polygon

        boat.setPos(self.graphicsView.mapToScene(self.context_menu_position))

        self.tableWidget.add_row(boat)

        boat.signals.positionChanged.connect(self.tableWidget.update_row)
        boat.signals.boat_deleted.connect(self.delete_boat)

    def create_unique_ID(self):
        boat_ids = set(map(int, (boat.ID for boat in self.boats)))

        while self.possible_id_boat in boat_ids:
            self.possible_id_boat += 1

    def delete_boat(self, boat=None):
        if boat in self.boats:
            self.boats.remove(boat)
            self.tableWidget.delete_boat_row(boat)

            self.graphicsView.scene().removeItem(boat)
            self.update_rows_boats(boat.row)
            del boat

        elif boat is None:
            for boat in self.boats:
                del boat

            self.tableWidget.boats_disconnect()
            self.possible_id_boat = 1

            self.tableWidget.setRowCount(0)
            self.boats.clear()

    def update_rows_boats(self, row):
        for boat in self.boats[row:]:
            boat.row = boat.row-1

    def create_file(self, COG_main_boat=0, SOG_main_boat=0):
        self.delete_boat()
        scene = QGraphicsScene()
        scene_width = 50000
        scene_height = 50000
        scene.setSceneRect(0, 0, scene_width, scene_height)

        scene.setBackgroundBrush(QColor(64, 64, 64))

        rings = 5  # Number of concentric rings
        radial_lines = 72  # Number of radial lines
        inner_rings = 50  # 9

        outer_radius = 1160

        center_x = scene_width / 2
        center_y = scene_height / 2

        # Calculate the circle_radius for the outer ring
        circle_radius = outer_radius / (rings + 1)

        # Create the yellow cross lines
        cross_length = 18
        cross_pen = QPen(QColor(0, 255, 0))
        cross_pen.setWidth(2)

        cross_line1 = scene.addLine(
            center_x, center_y - 20.5, center_x, center_y - 19.5 - cross_length, cross_pen)
        cross_line2 = scene.addLine(
            center_x + 20.5, center_y, center_x + 19.5 + cross_length, center_y, cross_pen)

        grid_pen = QPen(QColor(46, 102, 200))
        edge_pen = QPen(QColor(56, 60, 255))

        grid_pen_2 = QPen(QColor(46, 102, 148, 90))

        grid_pen_2.setWidth(0)

        grid_pen.setWidth(0)
        edge_pen.setWidth(0)

        for r in range(rings):
            radius = circle_radius * (r + 1)
            scene.addEllipse(center_x - radius, center_y -
                             radius, radius * 2, radius * 2, grid_pen)

        for r in range(inner_rings):
            radius = circle_radius / 10 * (r + 1)
            scene.addEllipse(center_x - radius, center_y -
                             radius, radius * 2, radius * 2, grid_pen_2)

        for i in range(radial_lines):
            angle = 360 * i / radial_lines
            angle_radians = math.radians(angle)
            x1 = center_x + circle_radius * math.cos(angle_radians)
            y1 = center_y + circle_radius * math.sin(angle_radians)

            for r in range(1, rings):
                radius = circle_radius * (r + 1)
                x2 = center_x + radius * math.cos(angle_radians)
                y2 = center_y + radius * math.sin(angle_radians)

                if i % 3 == 0:
                    scene.addLine(x1, y1, x2, y2, grid_pen)
                else:
                    scene.addLine(x1, y1, x2, y2, grid_pen_2)

        self.graphicsView.setScene(scene)

        # Show scrollbar slider immediately
        self.graphicsView.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.graphicsView.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.graphicsView.fitInView(
            scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

        self.graphicsView.scale(25, 25)

        boat = Boat(0, 0, 0, 0, COG_main_boat, SOG_main_boat, 0, 0, 0, 0, 0, 0)
        boat.rotate_boat(COG_main_boat)
        self.boats.append(boat)

        boat.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

        scene = self.graphicsView.scene()

        scene.addItem(boat)

        boat.polygon = QPolygonF([QPointF(-25.286, 50.573), QPointF(0, -50.573),
                                  QPointF(25.286, 50.573), QPointF(0, 29.5)])

        boat_offset_x = boat.boundingRect().width() / 2
        boat_offset_y = boat.boundingRect().height() / 2
        boat.setPos(center_x, center_y)

        row = 0
        self.tableWidget.insertRow(row)

        for x in range(0, 12):
            unrecorded_item = QTableWidgetItem(str())
            unrecorded_item.setFlags(
                unrecorded_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tableWidget.setItem(row, x, unrecorded_item)

        self.tableWidget.setItem(
            row, 4, QTableWidgetItem(f'{round(boat.COG, 2)}°'))

        self.tableWidget.setItem(
            row, 5, QTableWidgetItem(f'{round(boat.SOG, 2)} kn'))

        self.tableWidget.connected_boats.append(boat)

        self.tableWidget.itemChanged.connect(self.tableWidget.boat_row_changed)

    def start_classification(self):
        if len(self.boats) > 1:
            targets, _ = self.NN.preprocessing(self.boats[1:])
            # print(labels)
            prediction = self.NN.classification(targets, _)
            # print(prediction)

            for row in range(1, self.tableWidget.rowCount()):

                pred = prediction[row-1]

                situation = 'OV' if pred == 0 else 'HO' if pred == 1 else 'CS'

                pred_NN = QTableWidgetItem(str(situation))

                pred_NN.setFlags(pred_NN.flags() & ~Qt.ItemFlag.ItemIsEditable)

                self.tableWidget.setItem(row, self.tableWidget.columnCount(
                ) - 1, pred_NN)
        else:
            QMessageBox.warning(None, "Warning",
                                "Boats must be more than 1.")

    def training(self):
        if len(self.boats) > 1:
            targets, labels = self.NN.preprocessing(self.boats[1:])
            # print(labels)

            self.NN.trained_model(targets, labels)
            # prediction = self.NN.classification(targets)
            QMessageBox.information(None, "Notification",
                                    "Training complete.")
        else:
            QMessageBox.warning(None, "Warning",
                                "Boats must be more than 1.")

    def reset_weights(self):
        self.NN.reset_weights()

    def open_weights(self):
        file_dialog = QFileDialog()

        if not os.path.exists(self.default_path_weights):
            os.mkdir(self.default_path_weights)

        file_path, _ = file_dialog.getOpenFileName(
            self, 'Open File', self.default_path_weights, '')

        self.NN.load_weights(file_path.split('.')[0])

    def save_weights(self):
        file_dialog = QFileDialog()

        if not os.path.exists(self.default_path_weights):
            os.mkdir(self.default_path_weights)

        file_path, _ = file_dialog.getSaveFileName(
            self, 'Save File', self.default_path_weights, '')

        self.NN.save_weights(file_path)

    def save_file(self):
        if len(self.boats) != 0 and self.graphicsView.scene():
            json_boats = {}
            for boat in self.boats:
                json_boats[boat.ID] = (boat.BRG, boat.RB, boat.DST, boat.COG,
                                       boat.SOG, boat.N_Status,
                                       boat.Priority_T, boat.OV, boat.HO,
                                       boat.CS, boat.row, boat.pos().x(), boat.pos().y())

            file_dialog = QFileDialog()

            if not os.path.exists(self.default_path_boats):
                os.mkdir(self.default_path_boats)

            file_path, _ = file_dialog.getSaveFileName(
                self, 'Save File', self.default_path_boats, 'JSON Files (*.json)')

            if file_path:

                if not file_path.endswith('.json'):
                    file_path += '.json'

                with open(file_path, 'w') as f:
                    json.dump(json_boats, f, indent=4)

    def open_file(self):
        file_dialog = QFileDialog()

        if not os.path.exists(self.default_path_boats):
            os.mkdir(self.default_path_boats)

        file_path, _ = file_dialog.getOpenFileName(
            self, 'Open File', self.default_path_boats, 'JSON Files (*.json)')

        if file_path:
            load_boats = None
            try:
                with open(file_path, 'r') as f:
                    load_boats = json.load(f)

                main_boat_COG_SOG = [load_boats['0'][3], load_boats['0'][4]]
                self.create_file(
                    COG_main_boat=main_boat_COG_SOG[0], SOG_main_boat=main_boat_COG_SOG[1])
                load_boats.pop('0')

                if load_boats is not None:
                    for boat_id, boat_data in load_boats.items():
                        boat = Boat(boat_id, *boat_data[:-2])
                        self.boats.append(boat)
                        self.graphicsView.scene().addItem(boat)
                        boat.polygon = self.boats[0].polygon
                        boat.setPos(boat_data[-2], boat_data[-1])
                        boat.setRotation(boat.COG)
                        self.tableWidget.add_row(boat)
                        boat.signals.positionChanged.connect(
                            self.tableWidget.update_row)
                        boat.signals.boat_deleted.connect(self.delete_boat)
            except Exception as exp:
                QMessageBox.warning(
                    self, 'Error', f'Failed to open file: {str(exp)}')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMainWindow {
            background-color: #333333;
            color: #f0f0f0;
        }

        QScrollBar:vertical {
            border: none;
            background-color: #404040; /* Scrollbar background color */
            width: 12px;
            margin: 0px 0px 0px 0px;
        }

        QScrollBar:horizontal {
            border: none;
            background-color: #404040; /* Scrollbar background color */
            height: 12px;
            margin: 0px 0px 0px 0px;
        }

        QScrollBar::handle:vertical {
            background-color: #606060; /* Scrollbar handle color */
            min-height: 20px;
        }

        QScrollBar::handle:horizontal {
            background-color: #606060; /* Scrollbar handle color */
            min-width: 20px;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            background: none;
            color: none;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
            color: none;
        }

        QMenuBar {
            background-color: #404040;
            color: #f0f0f0;
        }

        QMenuBar::item:selected {
            background-color: #606060;
        }

        QMenu::item:selected {
            background-color: #606060;
        }

        QMenu {
            background-color: #404040;
            color: #f0f0f0;
        }

        QTableWidget {
            color: #f0f0f0;
            selection-background-color: #545454;
            background-color: #333333;
        }

        QTableWidget QTableCornerButton::section {
            background-color: #404040;
            color: #f0f0f0;
        }

        QGraphicsView {
            background-color: #333333;
            color: #f0f0f0;
        }

        QHeaderView::section {
            background-color: #333333;
            color: #f0f0f0;
        }

        QHeaderView::section:selected {
            background-color: #606060;
        }

        QTableWidget::verticalHeader::section:selected {
            background-color: #606060; /* Selected line numbers background color */
        }

        QSplitter::handle {
            background-color: #333333;
        }
    """)

    window = Main_Window()
    window.showMaximized()
    sys.exit(app.exec())
