from pyqtgraph import functions as fn
from qtpy import QtCore, QtGui
from pyqtgraph.graphicsItems.GraphicsObject import GraphicsObject


class Curve(GraphicsObject):
    """
    **Bases:** :class:`GraphicsObject <pyqtgraph.GraphicsObject>`

    Item displaying an isocurve of a 2D array. To align this item correctly with an
    ImageItem, call ``isocurve.setParentItem(image)``.
    """

    def __init__(self, pen='w'):
        """
        Create a new isocurve item.

        ==============  ===============================================================
        **Arguments:**
        data            A 2-dimensional ndarray. Can be initialized as None, and set
                        later using :func:`setData <pyqtgraph.IsocurveItem.setData>`
        level           The cutoff value at which to draw the isocurve.
        pen             The color of the curve item. Can be anything valid for
                        :func:`mkPen <pyqtgraph.mkPen>`
        axisOrder       May be either 'row-major' or 'col-major'. By default this uses
                        the ``imageAxisOrder``
                        :ref:`global configuration option <apiref_config>`.
        ==============  ===============================================================
        """
        GraphicsObject.__init__(self)

        self.path: QtGui.QPainterPath = None
        self.pen: QtGui.QPen = None
        self.data = [(0, 3), (1, 2), (2, 4), (3.5, 0), (3.5, -1),]

        self.setPen(pen)

    def setData(self, data, level=None):
        """
        Set the data/image to draw isocurves for.

        ==============  ========================================================================
        **Arguments:**
        data            A 2-dimensional ndarray.
        level           The cutoff value at which to draw the curve. If level is not specified,
                        the previously set level is used.
        ==============  ========================================================================
        """

        self.data = data
        self.path = None
        self.prepareGeometryChange()
        self.update()

    def setPen(self, *args, **kwargs):
        """Set the pen used to draw the isocurve. Arguments can be any that are valid
        for :func:`mkPen <pyqtgraph.mkPen>`"""
        self.pen = fn.mkPen(*args, **kwargs)
        self.update()

    def setBrush(self, *args, **kwargs):
        """Set the brush used to draw the isocurve. Arguments can be any that are valid
        for :func:`mkBrush <pyqtgraph.mkBrush>`"""
        self.brush = fn.mkBrush(*args, **kwargs)
        self.update()

    def boundingRect(self):
        if self.data is None:
            return QtCore.QRectF()
        if self.path is None:
            self.generatePath()
        return self.path.boundingRect()

    def generatePath(self):
        self.path = QtGui.QPainterPath()
        self.path.moveTo(*self.data[0])
        for line in self.data[1:]:
            self.path.lineTo(*line)

    def paint(self, p, *args):
        if self.data is None:
            return
        if self.path is None:
            self.generatePath()
        p.setPen(self.pen)
        p.drawPath(self.path)


if __name__ == '__main__':
    import numpy as np
    import pyqtgraph as pg
    app = pg.mkQApp("Isocurve Example")

    win = pg.GraphicsLayoutWidget(show=True)
    win.setWindowTitle('pyqtgraph example: Isocurve')
    vb = win.addViewBox()

    curve = Curve()

    vb.addItem(curve)



    pg.exec()