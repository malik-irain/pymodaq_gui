# -*- coding: utf-8 -*-
"""
Created the 05/12/2022

@author: Sebastien Weber
"""
import numpy as np
from pymodaq.utils.logger import set_logger, get_module_name
from pymodaq.utils import math_utils as mutils
from pymodaq.utils import config as configmod

from .scan_factory import ScannerFactory, ScannerBase, ScanParameterManager

logger = set_logger(get_module_name(__file__))
config = configmod.Config()


@ScannerFactory.register('Scan2D', 'Linear')
class Scan2DLinear(ScannerBase, ScanParameterManager):
    params = [{'title': 'Start Ax1:', 'name': 'start_axis1', 'type': 'float',
               'value': config('scan', 'scan2D', 'linear', 'start1')},
              {'title': 'Start Ax2:', 'name': 'start_axis2', 'type': 'float',
               'value': config('scan', 'scan2D', 'linear', 'start2')},
              {'title': 'Step Ax1:', 'name': 'step_axis1', 'type': 'float',
               'value': config('scan', 'scan2D', 'linear', 'step1')},
              {'title': 'Step Ax2:', 'name': 'step_axis2', 'type': 'float',
               'value': config('scan', 'scan2D', 'linear', 'step2')},
              {'title': 'Stop Ax1:', 'name': 'stop_axis1', 'type': 'float',
               'value': config('scan', 'scan2D', 'linear', 'stop1')},
              {'title': 'Stop Ax2:', 'name': 'stop_axis2', 'type': 'float',
               'value': config('scan', 'scan2D', 'linear', 'stop2')},
              ]
    n_axes = 2

    def __init__(self, **_ignored):
        ScanParameterManager.__init__(self)
        ScannerBase.__init__(self)

    def get_pos(self):
        starts = np.array([self.settings['start_axis1'], self.settings['start_axis2']])
        stops = np.array([self.settings['stop_axis1'], self.settings['stop_axis2']])
        steps = np.array([self.settings['step_axis1'], self.settings['step_axis2']])
        return starts, stops, steps

    def evaluate_steps(self) -> int:
        starts, stops, steps = self.get_pos()
        n_steps = 1
        for ind in range(starts.size):
            n_steps *= np.abs((stops[ind] - starts[ind]) / steps[ind]) + 1
        return n_steps

    def set_scan(self):
        starts, stops, steps = self.get_pos()
        if np.any(np.abs(steps) < 1e-12) or \
                np.any(np.sign(stops - starts) != np.sign(steps)) or \
                np.any(starts == stops):

            return np.array([starts])

        else:
            axis_1_unique = mutils.linspace_step(starts[0], stops[0], steps[0])
            axis_2_unique = mutils.linspace_step(starts[1], stops[1], steps[1])

            positions = []
            for ind_x, pos1 in enumerate(axis_1_unique):
                for ind_y, pos2 in enumerate(axis_2_unique):
                    positions.append([pos1, pos2])

        self.get_info_from_positions(np.array(positions))


@ScannerFactory.register('Scan2D', 'LinearBack&Force')
class Scan2DLinearBF(Scan2DLinear):
    def __init__(self, **_ignored):
        super().__init__()

    def set_scan(self):
        starts, stops, steps = self.get_pos()
        if np.any(np.abs(steps) < 1e-12) or \
                np.any(np.sign(stops - starts) != np.sign(steps)) or \
                np.any(starts == stops):

            return np.array([starts])

        else:
            axis_1_unique = mutils.linspace_step(starts[0], stops[0], steps[0])
            axis_2_unique = mutils.linspace_step(starts[1], stops[1], steps[1])

            positions = []
            for ind_x, pos1 in enumerate(axis_1_unique):
                for ind_y, pos2 in enumerate(axis_2_unique):
                    if not mutils.odd_even(ind_x):
                        positions.append([pos1, pos2])
                    else:
                        positions.append([pos1, axis_2_unique[len(axis_2_unique) - ind_y - 1]])

        self.get_info_from_positions(np.array(positions))


@ScannerFactory.register('Scan2D', 'Random')
class Scan2DRandom(Scan2DLinear):
    def __init__(self, **_ignored):
        super().__init__()

    def set_scan(self):
        super().set_scan()
        np.random.shuffle(self.positions)
        self.get_info_from_positions(self.positions)


@ScannerFactory.register('Scan2D', 'Spiral')
class Scan2DSpiral(Scan2DLinear):
    params = [{'title': 'Center Ax1:', 'name': 'center_axis1', 'type': 'float',
               'value': config('scan', 'scan2D', 'spiral', 'center1')},
              {'title': 'Center Ax2:', 'name': 'center_axis2', 'type': 'float',
               'value': config('scan', 'scan2D', 'spiral', 'center2')},
              {'title': 'Rmax Ax1:', 'name': 'rmax_axis1', 'type': 'float',
               'value': config('scan', 'scan2D', 'spiral', 'rmax1')},
              {'title': 'Rmax Ax2:', 'name': 'rmax_axis2', 'type': 'float',
               'value': config('scan', 'scan2D', 'spiral', 'rmax2')},
              {'title': 'Npts/axis', 'name': 'npts_by_axis', 'type': 'int', 'min': 1,
               'value': config('scan', 'scan2D', 'spiral', 'npts')},
              {'title': 'Step Ax1:', 'name': 'step_axis1', 'type': 'float', 'value': 0., 'readonly': True},
              {'title': 'Step Ax2:', 'name': 'step_axis2', 'type': 'float', 'value': 0., 'readonly': True},
              ]

    def __init__(self, **_ignored):
        super().__init__()

    def value_changed(self, param):
        starts, rmaxs, rsteps = self.get_pos()
        self.settings.child('step_axis1').setValue(rsteps[0])
        self.settings.child('step_axis2').setValue(rsteps[1])

    def get_pos(self):
        """Get centers, radius and n steps from settings

        Returns
        ----------
        centers: np.ndarray
            containing the center positions of the scan
        rmaxs: np.ndarray
            containing the maximum radius (ellipse axes) in each direction
        r_steps: np.ndarray
            steps size in both directions
        """
        centers = np.array([self.settings['center_axis1'], self.settings['center_axis1']])
        rmaxs = np.array([self.settings['rmax_axis1'], self.settings['rmax_axis1']])
        r_steps = 2 * rmaxs / self.settings['npts_by_axis']
        return centers, rmaxs, r_steps

    def evaluate_steps(self) -> int:
        return (self.settings['npts_by_axis'] +1) ** 2

    def set_scan(self):
        starts, rmaxs, rsteps = self.get_pos()

        if np.any(np.array(rmaxs) == 0) or np.any(np.abs(rmaxs) < 1e-12) or np.any(np.abs(rsteps) < 1e-12):
            positions = np.array([starts])

        else:
            Nlin = self.settings['npts_by_axis'] / 2
            axis_1_indexes = [0]
            axis_2_indexes = [0]
            ind = 0
            flag = True

            while flag:
                if mutils.odd_even(ind):
                    step = 1
                else:
                    step = -1
                if flag:

                    for ind_step in range(ind):
                        axis_1_indexes.append(axis_1_indexes[-1] + step)
                        axis_2_indexes.append(axis_2_indexes[-1])
                        if len(axis_1_indexes) >= (2 * Nlin + 1) ** 2:
                            flag = False
                            break
                if flag:
                    for ind_step in range(ind):
                        axis_1_indexes.append(axis_1_indexes[-1])
                        axis_2_indexes.append(axis_2_indexes[-1] + step)
                        if len(axis_1_indexes) >= (2 * Nlin + 1) ** 2:
                            flag = False
                            break
                ind += 1

            positions = []
            for ind in range(len(axis_1_indexes)):
                positions.append(np.array([axis_1_indexes[ind] * rsteps[0] + starts[0],
                                           axis_2_indexes[ind] * rsteps[1] + starts[1]]))

        self.get_info_from_positions(np.array(positions))


try:
    import adaptive


    @ScannerFactory.register('Scan2D', 'Adaptive')
    class Scan2DAdaptive(Scan2DLinear):
        params = [
            {'title': 'Loss type', 'name': 'scan_loss', 'type': 'list',
             'limits': ['default', 'curvature', 'uniform'],
             'tip': 'Type of loss used by the algo. to determine next points'},

            {'title': 'Start Ax1:', 'name': 'start_axis1', 'type': 'float',
             'value': config('scan', 'scan2D', 'linear', 'start1')},
            {'title': 'Start Ax2:', 'name': 'start_axis2', 'type': 'float',
             'value': config('scan', 'scan2D', 'linear', 'start2')},
            {'title': 'Stop Ax1:', 'name': 'stop_axis1', 'type': 'float',
             'value': config('scan', 'scan2D', 'linear', 'stop1')},
            {'title': 'Stop Ax2:', 'name': 'stop_axis2', 'type': 'float',
             'value': config('scan', 'scan2D', 'linear', 'stop2')},
            ]

        def __init__(self, **_ignored):
            super().__init__()

        def set_scan(self):

            self.axes_unique = [np.array([]), np.array([])]
            self.axes_indexes = np.array([], dtype=np.int)
            self.positions = np.zeros((0, 2))

        def evaluate_steps(self) -> int:
            return 1

except ModuleNotFoundError:
    logger.info('adaptive module is not present, no adaptive scan possible')

