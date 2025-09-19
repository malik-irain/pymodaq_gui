from qtpy import QtWidgets, QtCore
from pyqtgraph.parametertree.parameterTypes.basetypes import ParameterItem, GroupParameter, GroupParameterItem


class GroupParameterItem(GroupParameterItem):
    """
    Group parameters are used mainly as a generic parent item that holds (and groups!) a set
    of child parameters. It also provides a simple mechanism for displaying a button or combo
    that can be used to add new parameters to the group.
    """

    def __init__(self, param, depth):
        ParameterItem.__init__(self, param, depth)
        self._initialFontPointSize = self.font(0).pointSize()
        self.updateDepth(depth)

        self.addItem = None
        if 'addText' in param.opts:
            self.addText(param)

        self.optsChanged(self.param, self.param.opts)
    
    def addText(self, param):
        addText = param.opts['addText']
        if 'addList' in param.opts:
            self.addWidget = QtWidgets.QComboBox()
            self.addWidget.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
            self.updateAddList()
            self.addWidget.currentIndexChanged.connect(self.addChanged)
        elif "addMenu" in param.opts:
            # Create a QPushButton that will show the menu
            self.addWidget = QtWidgets.QPushButton(addText)
            # Create the nested menu
            self.addMenu = QtWidgets.QMenu(self.addWidget)
            self.addWidget.setMenu(self.addMenu)
            # Populate the nested menu structure
            self.updateAddMenu()                  
        else:
            self.addWidget = QtWidgets.QPushButton(addText)
            self.addWidget.clicked.connect(self.addClicked)
        w = QtWidgets.QWidget()
        l = QtWidgets.QHBoxLayout()
        l.setContentsMargins(0, 0, 0, 0)
        w.setLayout(l)
        l.addWidget(self.addWidget)
        l.addStretch()
        self.addWidgetBox = w
        self.addItem = QtWidgets.QTreeWidgetItem([])
        self.addItem.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled)
        self.addItem.depth = self.depth + 1
        ParameterItem.addChild(self, self.addItem)
        self.addItem.setSizeHint(0, self.addWidgetBox.sizeHint())                

    def optsChanged(self, param, opts):
        ParameterItem.optsChanged(self, param, opts)

        if 'addList' in opts:
            self.updateAddList()

        if 'addMenu' in opts:
            self.updateAddMenu()            

        if hasattr(self, 'addWidget'):
            if 'enabled' in opts:
                self.addWidget.setEnabled(opts['enabled'])

            if 'tip' in opts:
                self.addWidget.setToolTip(opts['tip'])

    def updateAddMenu(self):
        self.addWidget.blockSignals(True)
        try:
            self.addMenu.clear()
            addMenu = self.param.opts.get('addMenu', [])
            self._buildMenuFromIterable(self.addMenu, addMenu)
        finally:
            self.addWidget.blockSignals(False)

    def _buildMenuFromIterable(self, menu, items, path=()):
        if isinstance(items, dict):
            for key, value in items.items():
                self._handleMenuItem(menu, key, value, path)
        elif isinstance(items, (list, tuple)):
            for item in items:
                if isinstance(item, dict):
                    for key, value in item.items():
                        self._handleMenuItem(menu, key, value, path)
                elif isinstance(item, str):
                    self._addLeafAction(menu, item, path + (item,))

    def _handleMenuItem(self, menu: QtWidgets.QMenu, key, value, path):
        """Handle a single menu item (key-value pair)"""
        new_path = path + (key,)

        if self._isNested(value):
            # Create submenu and recurse
            submenu = menu.addMenu(key)
            self._buildMenuFromIterable(submenu, value, new_path)
        else:
            # Create leaf action
            self._addLeafAction(menu, key, new_path)

    def _isNested(self, value):
        """Check if a value represents nested structure"""
        return isinstance(value, (dict, list, tuple)) and value  # Not empty

    def _addLeafAction(self, menu: QtWidgets.QMenu, name, path):
        """Add a leaf action to the menu"""
        action = menu.addAction(name)
        action.triggered.connect(lambda checked, data=path: self.addMenuItemSelected(data))

    def addMenuItemSelected(self, path_tuple):
        """Called when a menu item is selected from the nested add menu
        The parameter MUST have an 'addNew' method defined.
        """
        # Call the parameter's addNew method with the selected type
        self.param.addNew(path_tuple)

        # Reset the button text back to the original addText
        # (equivalent to setCurrentIndex(0) for the combo)
        if hasattr(self.param.opts, 'addText'):
            self.addWidget.setText(self.param.opts['addText'])

class GroupParameter(GroupParameter):
    
    itemClass = GroupParameterItem

    def __init__(self, **opts):
        super().__init__(**opts)
   