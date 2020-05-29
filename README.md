# Carla Exploration

CARLA is an open source simulation based on the Unreal engine created for autonomous driving research. Although it's still very much under development, it has a lot to offer and this repository is meant to demonstrate some of the possible tasks that can be performed in the simulation. Specifically, I explored the capabilities of lidar, other sensors, pedestrian detection, and using reinforcement learning to build a self-driving agent in CARLA. For more information about CARLA, [view the latest docs](https://carla.readthedocs.io/en/latest/).

## Getting Started

### Prerequisites
> Although this code should theoretically work on Linux, it was developed on a Windows 10 environment

To run any of the code in this repository, you will first need: 
- The latest version of [Python](https://www.python.org/downloads/)
- A Python virtual environment such as [venv](https://docs.python.org/3/tutorial/venv.html)
- A package manager such as [pip](https://pip.pypa.io/en/stable/)
- [The latest version of CARLA](https://github.com/carla-simulator/carla/blob/master/Docs/download.md)

### Installing

1. Clone the repository to your local machine
2. Change directory into the cloned repository
3. Create a virtual environment in the cloned directory. Example: `python3 -m venv carla_exploration_venv`
4. Activate the virtual environment. Example: `carla_exploration_venv\scripts\activate` on Windows
5. Install the required packages from requirements.txt. Example: `pip install -r requirements.txt`

## Contents of this repository
- [Exploring the capabilities of the lidar raycast sensor](#lidar)
- [Exploring the capabilities of other sensors](#other-sensors)
- [Building a pedestrian detector from RGB camera data](#pedestrian-detection)
- [Attempting to build a self driving agent using reinforcement learning](#building-a-self-driving-agent)

### Lidar
The [lidar raycast sensor](https://carla.readthedocs.io/en/stable/cameras_and_sensors/#ray-cast-based-lidar]) in CARLA implements a rotating lidar using ray-casting. My goal was to attach a lidar sensor to a vehicle and create a point cloud animation of it passing another vehicle. Here's what I ended up with:

![Point cloud animation gif of one car passing another](sensor_output/passing_animation.gif)

Since the lidar raycasts bounce off of the collision detector for each agent it interacts with rather than the visual texture, vehicles seen through lidar have significantly simplified models. In addition, I [ran into issues](https://github.com/carla-simulator/carla/issues/2842) using the [SpringArm attachment type](https://docs.unrealengine.com/en-US/Gameplay/HowTo/UsingCameras/SpringArmComponents/index.html) to attach the lidar sensor to the vehicle in CARLA 0.9.9. These issues will hopefully be fixed in the future.

### Other Sensors
Carla has many [other sensors](https://carla.readthedocs.io/en/stable/cameras_and_sensors/) including collision detectors, GNSS, IMU, lane inversion detectors, obstacle detectors, and radar. In addition, Carla offers RGB, depth, and semantic segmentation cameras. I was able to implement all of these sensors successfully and the documentation provided for these sensors is more than sufficient.

### Pedestrian detection

I attempted pedestrian detection using the [pretrained default person detector HOG model from OpenCV](https://docs.opencv.org/2.4/modules/gpu/doc/object_detection.html?highlight=peopledetect#gpu-hogdescriptor-getdefaultpeopledetector) on RGB sensor data. I found that this model trained on real people was able to detect walkers in CARLA with *relative accuracy*. I tracked the distance from the camera to the pedestrian to determine the distance the sensor was able to start detecting true positive bounding boxes.

![Pedestrian detection gif straight on](sensor_output/pedestrian_detection_straight_on.gif)

With the camera sensor going straight at the pedestrian, the model is able to safely produce true positive bounding boxes at around 12.2 meters. In order to test that the initial bounding boxes drawn around 25 - 30 meters were false positives, I moved the pedestrian a bit to the left.

![Pedestrian detection gif from the side](sensor_output/pedestrian_detection.gif)

Sure enough, the bounding box gets drawn anyways in the same area of the image and the model even draws two bounding boxes once it sees the real pedestrian. How exciting! Spending some time fine tuning the model would be beneficial to its accuracy, but this was just meant as an initial exploration. The default person detector model from OpenCV was able to detect artificial walkers in CARLA.

### Building a Self Driving Agent

Turns out, reinforcement learning is hard. *Who knew?*

Unfortunately, my laptop ended up being a limiting factor in creating a self driving agent using reinforcement learning because it kept overheating and crashing. [Disabling rendering](https://carla.readthedocs.io/en/latest/adv_rendering_options/) may have been beneficial to performance. I was able to train an agent using deep Q learning to drive straight forward at 50kmh for 10 seconds. I used code from [sentdex on pythonprogramming.net](https://pythonprogramming.net/introduction-self-driving-autonomous-cars-carla-python/) and I'd recommend checking out his tutorial if you're interested in learning more. The one thing to note is that he trains his model using multi-threading, and [I was only able to get multi-threaded training working with Keras 2.2.5 and TensorFlow 1.14](https://github.com/keras-team/keras/issues/13353). This is the behavior of the model I trained to drive straight forward starting from various spawn points.

![Self driving model test gif](sensor_output/self_driving_test.gif)

CARLA is clearly meant for autonomous driving research and I'm sure it is possible to train a proper self driving agent in this simulation. Access to varied environments, a satisfactory amount of sensors to use for reward and punishment, and the ability to control multiple vehicles at once make CARLA an ideal simulation for autonomous driving research with the right hardware.

## Built with 
- [CARLA](https://carla.org/) - Autonomous vehicle simulation
- [TensorFlow](https://www.tensorflow.org/) - Machine learning platform
- [OpenCV](https://opencv.org/) - Computer vision library

## Authors
- Ryan Hopkins - *The creator of this wonderful mess* - Research Assistant, [Michigan Tech Research Institute](https://www.mtu.edu/mtri/)
- Joseph Paki, Ph.D. - *Who provided amazing direction and guidance* - Research Scientist, [Michigan Tech Research Institute](https://www.mtu.edu/mtri/)

## Acknowledgements
- Point cloud animation created in [Blender](https://www.blender.org/) with the [Stop-motion-OBJ](https://github.com/neverhood311/Stop-motion-OBJ) add on
- I wrote a [script to convert a directory of images to a gif](https://github.com/RyanHopkins7/images_to_gif) that I used frequently in this project with the help of [Matt Bierner and Almar on Stack Overflow](https://stackoverflow.com/questions/753190/programmatically-generate-video-or-animated-gif-in-python)
- Pedestrian detection code from [Adrian Rosebrock on pyimagesearch](https://www.pyimagesearch.com/2015/11/09/pedestrian-detection-opencv/)
- Reinforcement learning code from [sentdex on pythonprogramming.net](https://pythonprogramming.net/introduction-self-driving-autonomous-cars-carla-python/)
- Writing distance to pedestrian on each camera frame code from [Vinay Jain on haptik.ai](https://haptik.ai/tech/putting-text-on-image-using-python/)