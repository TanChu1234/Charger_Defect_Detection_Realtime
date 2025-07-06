# import sys
# from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QFileDialog
# from PySide6.QtGui import QPixmap, QWheelEvent, QMouseEvent, QPainter
# from PySide6.QtCore import Qt, QPoint


from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import QLabel, QMenu
from PySide6.QtGui import QPixmap, QPainter, QWheelEvent, QMouseEvent, QContextMenuEvent, QAction
from PySide6.QtCore import Qt, QPoint, Signal

class ZoomDragLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setMinimumSize(400, 300)
        
        # Remove any conflicting settings
        self.setScaledContents(False)
        
        self._pixmap = None
        self._zoom = 1.0
        self._drag_pos = QPoint()
        self._offset = QPoint()
        self._is_dragging = False
        
        # Set background to see the widget boundaries
        self.setStyleSheet("border: 2px solid red; background-color: lightgray;")
        
        print("ZoomDragLabel initialized")

    def setImage(self, pixmap: QPixmap):
        # print(f"Setting image: {pixmap.size()}")
        self._pixmap = pixmap
        self._zoom = 1.0
        self._offset = QPoint()
        self.update()

    def wheelEvent(self, event: QWheelEvent):
        # print(f"Wheel event: {event.angleDelta().y()}")
        if self._pixmap is None:
            print("No pixmap, ignoring wheel event")
            return
            
        delta = event.angleDelta().y()
        factor = 1.25 if delta > 0 else 0.8
        # old_zoom = self._zoom
        self._zoom *= factor
        self._zoom = max(0.1, min(self._zoom, 10))
        
        # print(f"Zoom changed from {old_zoom:.2f} to {self._zoom:.2f}")
        
        # Simple zoom without mouse position adjustment for debugging
        self.update()
        
        # Accept the event to prevent it from propagating
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        # print(f"Mouse press: {event.pos()}, button: {event.button()}")
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.pos()
            self._is_dragging = True
            self.setCursor(Qt.ClosedHandCursor)
            # print("Started dragging")
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_dragging and self._pixmap:
            delta = event.pos() - self._drag_pos
            self._offset += delta
            self._drag_pos = event.pos()
            # print(f"Dragging, offset: {self._offset}")
            self.update()
        elif self._pixmap:
            self.setCursor(Qt.OpenHandCursor)
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        # print(f"Mouse release: {event.button()}")
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
            if self._pixmap:
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
            # print("Stopped dragging")
        event.accept()

    def contextMenuEvent(self, event: QContextMenuEvent):
        """Handle right-click context menu"""
        if self._pixmap is None:
            return
            
        menu = QMenu(self)
        
        # # Add "Fit to Window" action
        # fit_action = QAction("Fit to Window", self)
        # fit_action.triggered.connect(self.fitToWindow)
        # menu.addAction(fit_action)
        
        # # Add separator
        # menu.addSeparator()
        
        # Add "Reset View" action
        reset_action = QAction("Reset View", self)
        reset_action.triggered.connect(self.resetView)
        menu.addAction(reset_action)
        
        # Show the menu at the cursor position
        menu.exec_(event.globalPos())

    # def fitToWindow(self):
    #     """Fit the image to the window size while maintaining aspect ratio"""
    #     if self._pixmap is None:
    #         return
            
    #     # Get the widget size (minus some padding for borders)
    #     widget_size = self.size()
    #     available_width = widget_size.width() - 10  # Account for border
    #     available_height = widget_size.height() - 10
        
    #     # Get the original pixmap size
    #     pixmap_size = self._pixmap.size()
        
    #     # Calculate the scaling factor to fit the image in the window
    #     scale_x = available_width / pixmap_size.width()
    #     scale_y = available_height / pixmap_size.height()
        
    #     # Use the smaller scale to maintain aspect ratio
    #     self._zoom = min(scale_x, scale_y)
        
    #     # Center the image (reset offset)
    #     self._offset = QPoint()
        
    #     self.update()
    #     # print(f"Fit to window: zoom = {self._zoom:.2f}")
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        if self._pixmap:
            # Calculate scaled size
            scaled_size = self._pixmap.size() * self._zoom
            
            # Calculate position (center + offset)
            x = (self.width() - scaled_size.width()) / 2 + self._offset.x()
            y = (self.height() - scaled_size.height()) / 2 + self._offset.y()
            
            # print(f"Drawing at ({x:.1f}, {y:.1f}), zoom: {self._zoom:.2f}")
            
            # Draw the scaled pixmap
            scaled_pixmap = self._pixmap.scaled(
                scaled_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            painter.drawPixmap(int(x), int(y), scaled_pixmap)
        else:
            # Draw placeholder text
            painter.drawText(self.rect(), Qt.AlignCenter, "No Image Loaded\nClick 'Load Image' to test")
            
        painter.end()

    def resetView(self):
        """Reset zoom and position to default"""
        self._zoom = 1.0
        self._offset = QPoint()
        self.update()
        # print("View reset")

# class ZoomDragLabel(QLabel):
#     clicked = Signal()
#     crop_rect_changed = Signal(int, int, int, int)

#     def __init__(self, parent=None):
#         super().__init__(parent)
        
#         # Existing cropping variables
#         self.start_point = None
#         self.end_point = None
#         self.cropping = False
#         self.rect_roi = None
#         self.dragging_rect = False  # Renamed to avoid conflict
#         self.resizing = False
#         self.resize_direction = None
#         self.rect_handle_size = 5
#         self.active_clearRect = False
#         self.active_draw_rect = False
        
#         # New zoom/drag variables
#         self._pixmap = None
#         self._zoom = 1.0
#         self._drag_pos = QPoint()
#         self._offset = QPoint()
#         self._is_dragging_image = False  # For image dragging
        
#         # Mouse tracking and cursor
#         self.setMouseTracking(True)
#         self.setCursor(QtCore.Qt.CursorShape.CrossCursor)
        
#         # Disable scaled contents as we handle scaling manually
#         self.setScaledContents(False)

#     def setImage(self, pixmap: QPixmap):
#         """Set the image to display"""
#         self._pixmap = pixmap
#         self._zoom = 1.0
#         self._offset = QPoint()
#         self.update()

#     def wheelEvent(self, event: QWheelEvent):
#         """Handle zoom with mouse wheel"""
#         if self._pixmap is None:
#             return
            
#         # Get mouse position for zoom centering
#         mouse_pos = event.position().toPoint()
        
#         # Calculate zoom factor
#         delta = event.angleDelta().y()
#         factor = 1.25 if delta > 0 else 0.8
#         old_zoom = self._zoom
#         self._zoom *= factor
#         self._zoom = max(0.1, min(self._zoom, 10))
        
#         # Adjust offset to zoom towards mouse position
#         if old_zoom != 0:
#             zoom_ratio = self._zoom / old_zoom
#             widget_center = QPoint(self.width() // 2, self.height() // 2)
#             mouse_offset = mouse_pos - widget_center
#             self._offset = (self._offset - mouse_offset) * zoom_ratio + mouse_offset
        
#         self.update()
#         event.accept()

#     def mousePressEvent(self, event):
#         """Handle mouse press for both cropping and image dragging"""
#         if event.button() == QtCore.Qt.MouseButton.LeftButton:
            
#             # If in draw rect mode, handle cropping
#             if self.active_draw_rect:
#                 if self.rect_roi and self.rect_roi.contains(event.pos()):
#                     if self._is_on_handle(event.pos()):
#                         self.resizing = True
#                         self.resize_direction = self._get_resize_direction(event.pos())
#                     else:
#                         self.dragging_rect = True
#                         self.offset = event.pos() - self.rect_roi.topLeft()
#                 else:
#                     self.start_point = event.pos()
#                     self.end_point = event.pos()
#                     self.cropping = True
            
#             # If not in draw rect mode and we have an image, handle image dragging
#             elif self._pixmap and not self.active_draw_rect:
#                 self._drag_pos = event.pos()
#                 self._is_dragging_image = True
#                 self.setCursor(Qt.ClosedHandCursor)
                
#         self.update()

#     def mouseMoveEvent(self, event):
#         """Handle mouse move for cropping, resizing, and image dragging"""
        
#         # Handle cropping mode
#         if self.active_draw_rect:
#             if self.cropping:
#                 self.end_point = event.pos()
#                 self.update()
#             elif self.dragging_rect and self.rect_roi:
#                 self.rect_roi.moveTo(event.pos() - self.offset)
#                 self.update()
#             elif self.resizing and self.rect_roi:
#                 self._resize_rect(event.pos())
#                 self.update()
#             else:
#                 # Update cursor based on handle position
#                 if self.rect_roi:
#                     handle_index = self._get_handle_index(event.pos())
#                     if handle_index == 0:
#                         self.setCursor(QtCore.Qt.CursorShape.SizeFDiagCursor)
#                     elif handle_index == 1:
#                         self.setCursor(QtCore.Qt.CursorShape.SizeBDiagCursor)
#                     elif handle_index == 2:
#                         self.setCursor(QtCore.Qt.CursorShape.SizeBDiagCursor)
#                     elif handle_index == 3:
#                         self.setCursor(QtCore.Qt.CursorShape.SizeFDiagCursor)
#                     elif handle_index == 4:
#                         self.setCursor(QtCore.Qt.CursorShape.SizeVerCursor)
#                     elif handle_index == 5:
#                         self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
#                     elif handle_index == 6:
#                         self.setCursor(QtCore.Qt.CursorShape.SizeVerCursor)
#                     elif handle_index == 7:
#                         self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
#                     else:
#                         self.setCursor(QtCore.Qt.CursorShape.CrossCursor)
        
#         # Handle image dragging mode
#         elif self._is_dragging_image and self._pixmap:
#             delta = event.pos() - self._drag_pos
#             self._offset += delta
#             self._drag_pos = event.pos()
#             self.update()
        
#         # Show appropriate cursor when hovering
#         elif self._pixmap and not self.active_draw_rect:
#             self.setCursor(Qt.OpenHandCursor)

#     def mouseReleaseEvent(self, event):
#         """Handle mouse release"""
#         if event.button() == QtCore.Qt.MouseButton.LeftButton:
            
#             # Handle cropping mode
#             if self.active_draw_rect:
#                 if self.cropping:
#                     self.end_point = event.pos()
#                     self.cropping = False
#                     if self.start_point and self.end_point:
#                         self.rect_roi = QtCore.QRect(self.start_point, self.end_point).normalized()
#                         self.crop_rect_changed.emit(
#                             self.rect_roi.x(), self.rect_roi.y(), 
#                             self.rect_roi.width(), self.rect_roi.height()
#                         )
#                 self.dragging_rect = False
#                 self.resizing = False
            
#             # Handle image dragging mode
#             elif self._is_dragging_image:
#                 self._is_dragging_image = False
#                 if self._pixmap:
#                     self.setCursor(Qt.OpenHandCursor)
#                 else:
#                     self.setCursor(Qt.ArrowCursor)
                    
#         self.update()

#     def paintEvent(self, event):
#         """Custom paint event to handle both image and cropping overlay"""
#         painter = QtGui.QPainter(self)
#         painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
#         # Clear rect if requested
#         if self.active_clearRect:
#             self.rect_roi = None
#             self.start_point = None
#             self.end_point = None
#             self.active_clearRect = False
        
#         # Draw the image if available
#         if self._pixmap:
#             # Calculate scaled size and position
#             scaled_size = self._pixmap.size() * self._zoom
#             x = (self.width() - scaled_size.width()) / 2 + self._offset.x()
#             y = (self.height() - scaled_size.height()) / 2 + self._offset.y()
            
#             # Draw the scaled pixmap
#             scaled_pixmap = self._pixmap.scaled(
#                 scaled_size,
#                 Qt.KeepAspectRatio,
#                 Qt.SmoothTransformation
#             )
#             painter.drawPixmap(int(x), int(y), scaled_pixmap)
#         else:
#             # Call parent's paint event if no custom image
#             super().paintEvent(event)
        
#         # Draw cropping rectangle and handles if active
#         if self.active_draw_rect and (self.rect_roi or (self.cropping and self.start_point and self.end_point)):
#             painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.red, 2, QtCore.Qt.PenStyle.SolidLine))
#             if self.cropping:
#                 rect = QtCore.QRect(self.start_point, self.end_point).normalized()
#             else:
#                 rect = self.rect_roi
#             painter.drawRect(rect)
#             if rect:
#                 self._draw_handles(painter, rect)

#     def _draw_handles(self, painter, rect):
#         """Draw resize handles on the crop rectangle"""
#         handles = self._get_handles(rect)
#         painter.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.white))
#         painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.black, 1))
#         for handle in handles:
#             painter.drawRect(handle)

#     def _get_handles(self, rect):
#         """Get handle rectangles for resizing"""
#         handle_size = self.rect_handle_size
#         return [
#             QtCore.QRect(rect.topLeft().x() + 5 - handle_size // 2, rect.topLeft().y() + 5 - handle_size // 2, handle_size, handle_size),
#             QtCore.QRect(rect.topRight().x() - 5 - handle_size // 2, rect.topRight().y() + 5 - handle_size // 2, handle_size, handle_size),
#             QtCore.QRect(rect.bottomLeft().x() + 5 - handle_size // 2, rect.bottomLeft().y() - 5 - handle_size // 2, handle_size, handle_size),
#             QtCore.QRect(rect.bottomRight().x() - 5 - handle_size // 2, rect.bottomRight().y() - 5 - handle_size // 2, handle_size, handle_size),
#             QtCore.QRect(rect.center().x() - handle_size // 2, rect.top() + 5 - handle_size // 2, handle_size, handle_size),
#             QtCore.QRect(rect.right() - 5 - handle_size // 2, rect.center().y() - handle_size // 2, handle_size, handle_size),
#             QtCore.QRect(rect.center().x() - handle_size // 2, rect.bottom() - 5 - handle_size // 2, handle_size, handle_size),
#             QtCore.QRect(rect.left() + 5 - handle_size // 2, rect.center().y() - handle_size // 2, handle_size, handle_size)
#         ]

#     def _is_on_handle(self, pos):
#         """Check if position is on a resize handle"""
#         return self._get_handle_index(pos) is not None

#     def _get_handle_index(self, pos):
#         """Get the index of the handle at the given position"""
#         if not self.rect_roi:
#             return None
#         handles = self._get_handles(self.rect_roi)
#         for i, handle in enumerate(handles):
#             if handle.contains(pos):
#                 return i
#         return None

#     def _get_resize_direction(self, pos):
#         """Get resize direction based on handle position"""
#         handle_index = self._get_handle_index(pos)
#         directions = ['topleft', 'topright', 'bottomleft', 'bottomright', 
#                      'top', 'right', 'bottom', 'left']
#         return directions[handle_index] if handle_index is not None else None

#     def _resize_rect(self, pos):
#         """Resize the crop rectangle based on mouse position"""
#         if not self.resize_direction or not self.rect_roi:
#             return

#         if self.resize_direction == 'topleft':
#             self.rect_roi.setTopLeft(pos)
#         elif self.resize_direction == 'topright':
#             self.rect_roi.setTopRight(pos)
#         elif self.resize_direction == 'bottomleft':
#             self.rect_roi.setBottomLeft(pos)
#         elif self.resize_direction == 'bottomright':
#             self.rect_roi.setBottomRight(pos)
#         elif self.resize_direction == 'top':
#             self.rect_roi.setTop(pos.y())
#         elif self.resize_direction == 'right':
#             self.rect_roi.setRight(pos.x())
#         elif self.resize_direction == 'bottom':
#             self.rect_roi.setBottom(pos.y())
#         elif self.resize_direction == 'left':
#             self.rect_roi.setLeft(pos.x())

#         self.rect_roi = self.rect_roi.normalized()
#         self.crop_rect_changed.emit(
#             self.rect_roi.x(), self.rect_roi.y(), 
#             self.rect_roi.width(), self.rect_roi.height()
#         )

#     # Utility methods for zoom/drag functionality
#     def resetView(self):
#         """Reset zoom and position to default"""
#         self._zoom = 1.0
#         self._offset = QPoint()
#         self.update()

#     def fitToWindow(self):
#         """Fit image to window size"""
#         if not self._pixmap:
#             return
            
#         widget_size = self.size()
#         pixmap_size = self._pixmap.size()
        
#         # Calculate scale to fit image in widget
#         scale_x = widget_size.width() / pixmap_size.width()
#         scale_y = widget_size.height() / pixmap_size.height()
        
#         self._zoom = min(scale_x, scale_y) * 0.95  # 95% to add some padding
#         self._offset = QPoint()
#         self.update()

#     def setDrawRectMode(self, active):
#         """Enable/disable rectangle drawing mode"""
#         self.active_draw_rect = active
#         if active:
#             self.setCursor(QtCore.Qt.CursorShape.CrossCursor)
#         else:
#             if self._pixmap:
#                 self.setCursor(Qt.OpenHandCursor)
#             else:
#                 self.setCursor(Qt.ArrowCursor)

#     def clearRect(self):
#         """Clear the crop rectangle"""
#         self.active_clearRect = True
#         self.update()