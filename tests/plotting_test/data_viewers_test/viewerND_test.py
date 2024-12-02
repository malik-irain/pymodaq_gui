import numpy as np
import pytest

from qtpy import QtWidgets
from pymodaq_gui.plotting.data_viewers.viewerND import ViewerND

from pymodaq_data import data as data_mod
from pymodaq_utils import math_utils as mutils


@pytest.fixture
def init_viewernd(qtbot):
    widget = QtWidgets.QWidget()
    prog = ViewerND(widget)
    qtbot.addWidget(widget)
    widget.show()
    yield prog
    widget.close()


class TestSpread:

    def test_linear_spread(self, init_viewernd):
        viewer = init_viewernd

        xaxis = data_mod.Axis(label='xaxis', data=np.array([0., 1, 2]), index=0, spread_order=0)
        yaxis = data_mod.Axis(label='yaxis', data=np.array([0., 1, 2]), index=0, spread_order=1)
        data = np.array([10, 12, 8])

        data_spread = data_mod.DataRaw(name='spread',
                                       distribution=data_mod.DataDistribution['spread'],
                                       data=[data],
                                       nav_indexes=(0,),
                                       axes=[xaxis, yaxis])


        viewer.show_data(data_spread)

        pass

    def test_2D_spread_1D_signal(self, init_viewernd):
        viewer = init_viewernd

        # Parameter
        param = np.linspace(1, 10, 10)

        # generating Npts of spread 2D data
        N = 200

        x_axis_array = np.random.randint(-20, 50, size=N)
        y_axis_array = np.random.randint(20, 40, size=N)

        x_axis = data_mod.Axis('xaxis', 'm', data=x_axis_array, index=0, spread_order=0)
        y_axis = data_mod.Axis('yaxis', 'm', data=y_axis_array, index=0, spread_order=1)
        param_axis = data_mod.Axis('Param', 'eV', data=param, index=1)

        data_spread_1x2 = []
        for i in param :
            data_list = []
            for ind in range(N):
                data_list.append(mutils.gauss2D(x_axis.get_data()[ind], 10+i, 15,
                                                y_axis.get_data()[ind], 30-i, 5))
            data_array = np.squeeze(np.array(data_list))
            data_spread_1x2.append(data_array)
        data_spread_1x2 = np.array(data_spread_1x2).T

        data_2D_1x2_spread = data_mod.DataRaw('data2DSpread', data=[data_spread_1x2],
                                     axes=[x_axis, y_axis, param_axis],
                                     distribution='spread',
                                     nav_indexes=(0,))

        data_2D_1x2_spread.plot('qt')
        QtWidgets.QApplication.processEvents()
        pass
