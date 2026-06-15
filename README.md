# Tree Painter

A Blender add-on for painting tree instances into a scene by clicking on surfaces. Each placed instance gets randomized rotation and scale based on percentage ranges you define, relative to the source object's original values.

## Requirements

- Blender 2.90 or later

## Installation

1. Download `treepainter.py`.
2. In Blender, go to **Edit > Preferences > Add-ons > Install**.
3. Select the file and enable the add-on.
4. The panel appears in the **3D Viewport > Sidebar (N) > Tree Painter** tab.

## Usage

1. In the Tree Painter panel, assign a source object (your base tree mesh).
2. Adjust rotation and scale variation percentages to control how much each instance can differ from the source.
3. Optionally set a Z offset to raise or lower all instances from the surface hit point.
4. Click **Paint Trees** and left-click anywhere in the viewport to place instances. Press Escape or right-click to stop.

Rotation variation for X and Y is relative to the source object's existing angles. Z rotation varies across the full 360 degrees. Scale variation applies uniformly across all axes to preserve proportions.

## License

MIT
