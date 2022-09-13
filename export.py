import FreeCADGui
print("Starting GUI")
FreeCADGui.showMainWindow()

from pathlib import Path
from glob import glob
import FreeCAD
import Import
import ImportGui
import Mesh
import os
from PySide import QtGui


def get_export_func(output):
    suffix = output.suffix.lower()
    if suffix in ['.stl']:
        print("Using Mesh exporter")
        return Mesh.export
    elif suffix in ['.wrl', '.vrml', '.x3d']:
        print("Using FreeCADGUI exporter")
        return FreeCADGui.export
    elif suffix in ['.step']:
        print("Using ImportGui exporter")
        return ImportGui.export
    print("Using default exporter")
    return Import.export

def set_step_export_prefs():
    # Set step export prefs for kicadStepUp according to popup screenshot
    # https://github.com/easyw/kicadStepUpMod/blob/master/demo/Import-Export-settings.png
    print("Setting up STEP export prefs")

    ### Export ###
    # Set "Units for export of STEP" to "mm"
    step_prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Part/STEP")
    step_prefs.SetInt("Unit", 0)

    # Disable "Write out curves in parametric space of surface"
    step_prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Part/General")
    step_prefs.SetInt("WriteSurfaceCurveMode", 0)

    # Enable "Export invisible objects"
    import_prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Import")
    import_prefs.SetBool("ExportHiddenObject", 1)

    # Disable "Export single object placement"
    import_prefs.SetBool("ExportKeepPlacement", 0)

    # Disable "Use legacy exporter"
    import_prefs.SetBool("ExportLegacy", 0)

    # Set "Scheme" to "AP214 International Standard"
    step_prefs.SetString("Scheme", "AP214IS")

    ### Import ###

    # Disable "Enable STEP Compound merge"
    hstep_prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Import/hSTEP")
    hstep_prefs.SetBool("ReadShapeCompoundMode", 0)

    # Disable "Use LinkGroup"
    import_prefs.SetBool("UseLinkGroup", 0)

    # Enable "Import invisible objects"
    import_prefs.SetBool("ImportHiddenObject", 1)

    # Disable "Reduce number of objects"
    import_prefs.SetBool("ReduceObjects", 0)

    # Enable "Expand compound shape"
    import_prefs.SetBool("ExpandCompound", 1)

    # Disable "Show progress bar when importing"
    import_prefs.SetBool("ShowProgress", 0)

    # Enable "Ignore instance names"
    import_prefs.SetBool("UseBaseName", 1)

    # Set "Mode" to "Single document"
    import_prefs.SetInt("ImportMode", 0)


def activate_kicad_wb():
    print("Activating KiCadStepUp Workbench")
    # Disable update checking (prevents blocking popups)
    kicadstepup_prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/kicadStepUp")
    kicadstepup_prefs.SetBool("checkUpdates", 0)

    # Set correct 3dmodel paths
    kicadstepup_prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/kicadStepUpGui")
    kicadstepup_prefs.SetString("prefix3d_1", "/usr/share/kicad/3dmodels")

    # Disable help warning (prevents blocking popups)
    import_prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Import")
    import_prefs.SetBool("help_warning_enabled", 0)

    # Activate KiCadStepUp
    FreeCADGui.activateWorkbench("KiCadStepUpWB")

    import SaveSettings
    SaveSettings.update_ksuGui()

def fake_infobox(parent, title, text, *args, **kwargs):
    print("info box shown")
    print(f"parent: {parent}")
    print(f"title: {title}")
    print(f"text: {text}")
    print(f"args: {args}")
    print(f"kwargs: {kwargs}")

QtGui.QMessageBox.information = fake_infobox


def main(input_paths, output_path, export_types):
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    for _p in input_paths:
        for p in glob(_p, recursive=True):
            input_path = Path(p)
            print(f"Opening {input_path}")
            if input_path.suffix.lower() == ".fcstd":
                print(f"Standard FreeCAD project detected")
                doc = FreeCAD.open(str(input_path))
            elif input_path.suffix.lower() == ".kicad_pcb":
                print(f"KiCad PCB file detected")
                doc = FreeCAD.newDocument(input_path.name)
                activate_kicad_wb()
                import kicadStepUptools
                kicadStepUptools.onLoadBoard(
                    file_name=str(input_path),
                    insert=True)

            print(f"Looking for root level objects")
            root_objs = [o for o in doc.Objects if not o.Parents]
            for o in root_objs:
                print(o.Label)

            for e in export_types:
                output = output_path / input_path.with_suffix(f".{e}")
                output.parent.mkdir(parents=True, exist_ok=True)
                print(f"Exporting to {output}")
                export_func = get_export_func(output)
                export_func(root_objs, str(output))

            print(f"Closing {input_path}")
            FreeCAD.closeDocument(doc.Name)


print("Starting export script")

print("Parsing args")
input_paths = os.environ['FREECAD_INPUT_PATHS'].splitlines()
output_path = os.environ['FREECAD_OUTPUT_PATH']
export_types = os.environ['FREECAD_EXPORT_TYPES'].splitlines()
print(f"input_paths: {input_paths}")
print(f"output_path: {output_path}")
print(f"export_types: {export_types}")

print("Running main")
main(input_paths, output_path, export_types)
