from PyQt6.QtWidgets import QLayout

def reset_window(layout: QLayout):
    while layout.count():
        item = layout.takeAt(0)

        widget = item.widget()
        if widget is not None:
            layout.removeWidget(widget)
            widget.deleteLater()

        elif item.layout():
            reset_window(item.layout())
