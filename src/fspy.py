import os
import json
from struct import *

class CameraParameters:
  def __init__(self, json_dict):
    principal_point_dict = json_dict["principalPoint"]
    self.principal_point = (principal_point_dict["x"], principal_point_dict["y"])
    self.fov_horiz = json_dict["horizontalFieldOfView"]
    print(json_dict["cameraTransform"]["rows"])
    self.camera_transfrom = json_dict["cameraTransform"]["rows"]
    self.image_width = json_dict["imageWidth"]
    self.image_height = json_dict["imageHeight"]

class Project:
  def __init__(self, project_path):

    project_file = open(project_path, "rb")

    file_id = unpack('<I', project_file.read(4))[0]
    self.project_version = unpack('<I', project_file.read(4))[0]
    state_string_size = unpack('<I', project_file.read(4))[0]
    image_buffer_size = unpack('<I', project_file.read(4))[0]
    project_file.seek(16)
    state = json.loads(project_file.read(state_string_size).decode('utf-8'))
    self.camera_parameters = CameraParameters(state["cameraParameters"])

    self.image_data = project_file.read(image_buffer_size)

    self.file_name = os.path.basename(project_path)

    self.file_size = 0 # TODO
