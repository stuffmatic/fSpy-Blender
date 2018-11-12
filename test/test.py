from src import fspy

project = fspy.Project('test_data/canon5d_16mm.fspy')
print(project.file_name)
print(project.file_size)