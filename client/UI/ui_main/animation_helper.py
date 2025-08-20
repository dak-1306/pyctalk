from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

class AnimationHelper:
    """Helper class for UI animations"""
    @staticmethod
    def fade_in(widget: QtWidgets.QWidget, duration: int = 300):
        effect = QtWidgets.QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        animation.start()
        return animation
    @staticmethod
    def slide_in(widget: QtWidgets.QWidget, direction: str = "left", duration: int = 400):
        start_pos = widget.pos()
        if direction == "left":
            widget.move(start_pos.x() - 100, start_pos.y())
        elif direction == "right":
            widget.move(start_pos.x() + 100, start_pos.y())
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(widget.pos())
        animation.setEndValue(start_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutBack)
        animation.start()
        return animation
