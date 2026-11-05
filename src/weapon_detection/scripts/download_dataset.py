from roboflow import Roboflow
rf = Roboflow(api_key="3bcypcM8dIro6vrk4qUq")
project = rf.workspace("yolov7test-u13vc").project("weapon-detection-m7qso")
version = project.version(16)
dataset = version.download("yolov11")
                