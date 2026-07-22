import os
import re
import zipfile

src_dir_name = 'fspy_blender'
manifest_name = 'blender_manifest.toml'
manifest_path = os.path.join(src_dir_name, manifest_name)

# Extract the version number from the extension manifest
version = None
with open(manifest_path) as manifest_file:
    for line in manifest_file:
        match = re.match(r'^version\s*=\s*"([^"]+)"', line.strip())
        if match:
            version = match.group(1)
            break

if version is None:
    raise RuntimeError("Could not extract version number from " + manifest_path)

dist_archive_name = "fSpy-Blender-" + version + ".zip"

dist_dir_name = "dist"

os.makedirs(dist_dir_name, exist_ok=True)

# The archive contains the add-on package in a single nested directory.
# This layout works both when the zip is installed as an extension
# (Blender 4.2+) and as a legacy add-on.
file_names = sorted(
    name for name in os.listdir(src_dir_name)
    if name.endswith('.py') or name == manifest_name
)

dist_archive_path = os.path.join(dist_dir_name, dist_archive_name)
with zipfile.ZipFile(dist_archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file_name in file_names:
        zipf.write(os.path.join(src_dir_name, file_name))

print("Built " + dist_archive_path)
