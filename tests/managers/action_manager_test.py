1# -*- coding: utf-8 -*-
"""
Created the 08/11/2024

@author: Constant Schouder
"""
import pytest
from qtpy import QtWidgets,QtGui,QtCore
from pymodaq_gui.managers.action_manager import ActionManager

version = QtCore.qVersion()

@pytest.fixture
def ini_qt_widget(init_qt):
    qtbot = init_qt
    widget = QtWidgets.QWidget()
    qtbot.addWidget(widget)
    widget.show()
    yield qtbot, widget
    widget.close()

def get_icon_status(action_manager,action_name,):
    action = action_manager.get_action(action_name)
    return action.icon().isNull()



def test_icon(qtbot):
    action_manager = ActionManager(toolbar=QtWidgets.QToolBar(),menu=QtWidgets.QMenu())
    
    action_manager.add_action(short_name='no_icon', icon_name='')

    assert get_icon_status(action_manager,'no_icon') == True

    action_manager.add_action(short_name='icon_from_pymodaq', icon_name='NewFile')
    assert get_icon_status(action_manager,'icon_from_pymodaq') == False

    if tuple(map(int, version.split('.'))) > (6, 7):

        action_manager.add_action(short_name='icon_from_Qt', icon_name='WindowClose')
        assert get_icon_status(action_manager,'icon_from_Qt') == False

        icon = QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.WindowClose)        
        action_manager.add_action(short_name='icon', icon_name=icon)
        assert get_icon_status(action_manager,'icon') == False



