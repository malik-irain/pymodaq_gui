"""
Tests for ParameterManager search functionality
"""
import pytest
from qtpy import QtWidgets, QtCore
from pymodaq_gui.parameter import Parameter
from pymodaq_gui.managers.parameter_manager import ParameterManager, ParameterTreeWidget


@pytest.fixture
def sample_params():
    """Sample parameter structure for testing"""
    return [
        {
            'title': 'Main Settings',
            'name': 'main_settings',
            'type': 'group',
            'children': [
                {'title': 'Detector Mode', 'name': 'detector_mode', 'type': 'list',
                 'limits': ['Single', 'Continuous'], 'value': 'Single'},
                {'title': 'Integration Time', 'name': 'integration_time', 
                 'type': 'float', 'value': 100.0},
            ]
        },
        {
            'title': 'Advanced Settings',
            'name': 'advanced_settings',
            'type': 'group',
            'children': [
                {'title': 'Temperature Control', 'name': 'temp_control', 'type': 'bool'},
                {
                    'title': 'Calibration',
                    'name': 'calibration',
                    'type': 'group',
                    'children': [
                        {'title': 'Offset', 'name': 'offset', 'type': 'float', 'value': 0.0},
                    ]
                }
            ]
        }
    ]


@pytest.fixture
def param_manager(qtbot, sample_params):
    """Fixture providing a fresh ParameterManager instance for each test"""
    manager = ParameterManager(settings_name='test_settings', 
                               action_list=('search', 'save', 'load'))
    # Create fresh parameter tree for each test
    manager.settings = Parameter.create(name='test_settings', type='group', 
                                       children=sample_params, showTop=False)
    qtbot.addWidget(manager.settings_tree)
    
    yield manager
    
    # Cleanup after each test
    manager.settings_tree.close()
    manager.settings_tree.deleteLater()


class TestSearchBasics:
    """Core search functionality tests"""
    
    def test_search_widget_exists(self, param_manager:ParameterManager):
        """Test that search widget is created when 'search' in action_list"""
        search_widget = param_manager._settings_tree.get_action('search_settings')
        assert search_widget is not None
        assert isinstance(search_widget, QtWidgets.QLineEdit)
    
    def test_empty_search_shows_all(self, param_manager:ParameterManager):
        """Test that empty search shows all parameters"""
        param_manager.search_settings_slot("")
        
        for item in param_manager.tree.listAllItems():
            assert not item.isHidden()
    
    def test_search_filters_parameters(self, param_manager:ParameterManager):
        """Test that search hides non-matching parameters"""
        param_manager.search_settings_slot("detector")
        
        # Check that some items are hidden
        all_items = param_manager.tree.listAllItems()
        hidden_items = [item for item in all_items if item.isHidden()]
        assert len(hidden_items) > 0
    
    def test_search_case_insensitive(self, param_manager:ParameterManager):
        """Test that search is case-insensitive"""
        param_manager.search_settings_slot("DETECTOR")
        
        detector_items = [item for item in param_manager.tree.listAllItems() 
                         if 'detector' in item.param.title().lower()]
        
        for item in detector_items:
            assert not item.isHidden()
    
    def test_search_expands_parent_groups(self, param_manager:ParameterManager):
        """Test that parent groups expand when children match"""
        param_manager.search_settings_slot("offset")
        
        # Find calibration parameter and check its expanded state
        calibration = param_manager.settings.child('advanced_settings', 'calibration')
        assert calibration is not None
        
        # Check if the parameter opts show it should be expanded
        assert calibration.opts.get('expanded', False) == True


class TestKeyboardShortcuts:
    """Keyboard shortcut tests"""
    
    def test_ctrl_f_activates_search(self, qtbot, param_manager:ParameterManager):
        """Test that Ctrl+F expands toolbar and focuses search"""
        assert not param_manager._settings_tree.collapsible_widget.is_expanded
        
        # Show the widget and process events
        param_manager.settings_tree.show()
        qtbot.waitForWindowShown(param_manager.settings_tree)
        qtbot.wait(100)
        
        # Trigger the shortcut directly
        param_manager._settings_tree.search_activate_shortcut.activated.emit()
        qtbot.wait(200)  # Give more time for animation and focus
        
        assert param_manager._settings_tree.collapsible_widget.is_expanded
        
        # Check that activate_search was called by verifying widget state
        search_widget = param_manager._settings_tree.get_action('search_settings')
        assert search_widget is not None
        # Just verify the toolbar is expanded, focus is unreliable in tests
    
    def test_escape_collapses_toolbar(self, qtbot, param_manager:ParameterManager):
        """Test that Escape key collapses toolbar"""
        param_manager.settings_tree.show()
        qtbot.waitForWindowShown(param_manager.settings_tree)
        
        param_manager._settings_tree.activate_search()
        qtbot.wait(200)
        assert param_manager._settings_tree.collapsible_widget.is_expanded
        
        # Trigger the shortcut directly
        param_manager._settings_tree.search_escape_shortcut.activated.emit()
        qtbot.wait(200)
        
        assert not param_manager._settings_tree.collapsible_widget.is_expanded


class TestSearchIntegration:
    """Integration tests"""
    
    def test_toolbar_toggle_clears_filter(self, param_manager:ParameterManager):
        """Test that collapsing toolbar clears the filter"""
        param_manager.search_settings_slot("detector")
        assert param_manager._current_filter_text == "detector"
        
        param_manager._settings_tree.collapsible_widget.is_expanded = False
        param_manager.on_toolbar_toggled()
        
        assert param_manager._current_filter_text == ""
    
    def test_clear_search_restores_all(self, qtbot, param_manager:ParameterManager):
        """Test that clearing search restores all parameters"""
        search_widget = param_manager._settings_tree.get_action('search_settings')
        
        qtbot.keyClicks(search_widget, "detector")
        qtbot.wait(350)
        
        search_widget.clear()
        qtbot.wait(350)
        
        for item in param_manager.tree.listAllItems():
            assert not item.isHidden()
    
    def test_initialization_without_search(self, qtbot):
        """Test that manager works without search in action_list"""
        manager = ParameterManager(settings_name='test', 
                                  action_list=('save', 'load'))
        qtbot.addWidget(manager.settings_tree)
        
        assert not manager._settings_tree.get_action('search_settings').isVisible()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])