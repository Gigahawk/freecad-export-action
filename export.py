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


def main(input_paths, output_path, export_types):
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    for _p in input_paths:
        for p in glob(_p, recursive=True):
            input = Path(p)
            print(f"Opening {input}")
            doc = FreeCAD.open(str(input))

            print(f"Looking for root level objects")
            root_objs = [o for o in doc.Objects if not o.Parents]
            for o in root_objs:
                print(o.Label)

            for e in export_types:
                output = output_path / input.with_suffix(f".{e}")
                output.parent.mkdir(parents=True, exist_ok=True)
                print(f"Exporting to {output}")
                export_func = get_export_func(output)
                export_func(root_objs, str(output))

            print(f"Closing {input}")
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
