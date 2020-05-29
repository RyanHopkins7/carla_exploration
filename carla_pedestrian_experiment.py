import glob
import os
import sys
import numpy as np
import math

# Update this with the path to your CARLA egg file
path_to_carla_egg = 'C:/Users/ryana/Documents/GitHub/carla0.9.9/PythonAPI/carla/dist'

try:
    sys.path.append(glob.glob('%s/carla-*%d.%d-%s.egg' % (
        path_to_carla_egg,
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import random
import time
from PIL import Image, ImageDraw, ImageFont

"""
This script generates one vehicle in CARLA and attaches an RGB camera to it. It then generates one 
pedestrian 30 meters in front of and 3 meters to the left of the vehicle. The vehicle slowly moves towards
the pedestrian with the camera pointed at the pedestrian. Each frame from the camera has the distance
from the camera to the pedestrian written on it and is saved to the disk.

After running this script, run detect_pedestrians.py to draw bounding boxes around the pedestrian and
images_to_gif.py to turn the .png files into a .gif file.

Developed for CARLA 0.9.9 on Windows 10

Usage: 
    Run CarlaUE4.exe to start server, then run python3 carla_pedestrian_experiment.py to run script

Outputs:
    .png files from frames of camera capture with distance from camera sensor to pedestrian written on them
        in sensor_output/pedestrian_pictures

Sources:
https://carla.readthedocs.io/en/stable/cameras_and_sensors/
https://haptik.ai/tech/putting-text-on-image-using-python/
"""

def main():
    actor_list = []

    try:
        # Start server on localhost, look for Unreal client for 2 seconds
        client = carla.Client('127.0.0.1', 2000)
        client.set_timeout(2.0)

        # Get the map / world
        world = client.get_world()

        # Load blueprints
        blueprint_library = world.get_blueprint_library()

        # Vehicle being tested is the Telsa model 3
        vehicle_bp = blueprint_library.filter('vehicle.tesla.model3')[0]

        # Get spawn points for vehicle
        world_map = world.get_map()
        vehicle_transform = world_map.get_spawn_points()[0]

        # Spawn vehicles
        vehicle = world.spawn_actor(vehicle_bp, vehicle_transform)

        # Need to append actors to actor list to delete when script finishes
        actor_list.append(vehicle)
        print('created %s' % vehicle.type_id)

        # Spawn pedestrian
        ped_blueprint = world.get_blueprint_library().filter("walker.*")[0]
        ped_transform = carla.Transform(vehicle_transform.transform(carla.Location(x=30.0, y=-3.0)), 
            carla.Rotation(yaw=270))
        pedestrian = world.try_spawn_actor(ped_blueprint, ped_transform)
        actor_list.append(pedestrian)

        # Add sensors
        # Offset
        sensor_location = carla.Location(0, 0, 2)
        sensor_rotation = carla.Rotation(0, 0, 0)
        sensor_transform = carla.Transform(sensor_location, sensor_rotation)

        # RGB camera
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_rgb = world.spawn_actor(
            camera_bp, sensor_transform, attach_to=vehicle)

        def save_frame_with_distance(image):
            distance_to_ped = image.transform.location.distance(ped_transform.location)
            pil_image = Image.frombytes('RGBA', (image.width, image.height), image.raw_data.tobytes(), 'raw')

            # Draw distance_to_ped on image
            draw = ImageDraw.Draw(pil_image)
            font = ImageFont.truetype('sensor_output/Roboto-Bold.ttf', size=45)
            draw.text((50, 50), f'Distance: {distance_to_ped:.2f}', fill='rgb(255,0,0)', font=font)

            pil_image.save(f'./sensor_output/pedestrian_pictures/{image.frame}.png')

        camera_rgb.listen(save_frame_with_distance)

        actor_list.append(camera_rgb)

        # Hardcoded vehicle control
        # Forward
        vehicle.apply_control(carla.VehicleControl(throttle=.3))
        time.sleep(13)


    finally:

        print('destroying actors')
        for actor in actor_list:
            actor.destroy()
        print('done.')


if __name__ == '__main__':

    main()
