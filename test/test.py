import os
import unittest
from fspy_blender import fspy

class TestfSpyProjectLoading(unittest.TestCase):

    def test_valid_project(self):
        """
        Opening a valid project should not raise
        """
        project = fspy.Project(self.project_path('canon5d_16mm.fspy'))

    def test_wrong_project_version(self):
        """
        Opening projects with an unsupported binary version should fail
        """
        with self.assertRaises(fspy.ParsingError):
            project = fspy.Project(self.project_path('invalid_project_version.fspy'))

    def test_invalid_file_type(self):
        """
        Opening files that are not fSpy project files should fail
        """
        with self.assertRaises(fspy.ParsingError):
            project = fspy.Project(self.project_path('json_export.json'))

    # Helper to get the path of a test project
    def project_path(self, project_name):
        return os.path.join('test_data', project_name)

