"""A layout that arranges child widgets left-to-right, wrapping onto new rows
as needed to fit the available width. Qt doesn't ship one, so this is the
standard adaptation of Qt's own C++ FlowLayout example for PySide6.
"""

from PySide6.QtCore import QMargins, QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QSizePolicy, QStyle, QWidget


class FlowLayout(QLayout):
    def __init__(self, parent: QWidget | None = None, margin: int = 0, spacing: int = -1) -> None:
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(QMargins(margin, margin, margin, margin))
        self.setSpacing(spacing)
        self._items: list = []

    def __del__(self) -> None:
        while self.count():
            self.takeAt(0)

    def addItem(self, item) -> None:
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index: int):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self) -> Qt.Orientations:
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(
            margins.left() + margins.right(),
            margins.top() + margins.bottom(),
        )
        return size

    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(left, top, -right, -bottom)
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        for item in self._items:
            widget = item.widget()
            space_x = self.spacing()
            space_y = self.spacing()
            if space_x == -1:
                space_x = widget.style().layoutSpacing(
                    QSizePolicy.ControlType.PushButton,
                    QSizePolicy.ControlType.PushButton,
                    Qt.Orientation.Horizontal,
                )
            if space_y == -1:
                space_y = widget.style().layoutSpacing(
                    QSizePolicy.ControlType.PushButton,
                    QSizePolicy.ControlType.PushButton,
                    Qt.Orientation.Vertical,
                )

            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y() + bottom