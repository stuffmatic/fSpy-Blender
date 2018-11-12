from fspy_blender import fspy

# Test cases
# no parameters
# wrong project version

project = fspy.Project('test_data/canon5d_16mm.fspy')
print(project.file_name)