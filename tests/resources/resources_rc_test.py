import ast

def test_import_from_qtpy():
    from pymodaq_gui.QtDesigner_Ressources import QtDesigner_ressources_rc
    filename = QtDesigner_ressources_rc.__file__

    with open(filename, "r") as f:
        tree = ast.parse(f.read(), filename=filename)

    # Get the first import statement in the file if it exists
    first_import = next((node for node in tree.body if isinstance(node, ast.ImportFrom)), None)

    # Check for import existence & validity (qtpy and not directly a backend)
    assert first_import is not None, f"No import found in {filename}. Please check the file."
    assert first_import.module == "qtpy", f"First import is not from 'qtpy': please replace {first_import.module} by qtpy in {filename}"
    