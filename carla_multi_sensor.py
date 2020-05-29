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

"""
This script generates one vehicle in CARLA and attaches an RGB camera, a semantic segmentation camera, 
a depth camera, a GNSS sensor, a radar sensor, and an IMU sensor to it. It then drives the car forward while
recording all appropriate data. Data from each camera is saved to the disk.

Developed for CARLA 0.9.9 on Windows 10

Usage: 
    Run CarlaUE4.exe to start server, then run python3 carla_multi_sensor.py to run script

Outputs:
    .png files from frames of camera capture in sensor_output/camera_depth, 
        sensor_output/camera_RGB, and sensor_output/camera_SS respectively

Sources:
https://carla.readthedocs.io/en/stable/cameras_and_sensors/
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

        # Vehicle being tested is the Telsa model 3 :)
        vehicle_bp = blueprint_library.filter('vehicle.tesla.model3')[0]

        # Get spawn points for vehicle
        world_map = world.get_map()
        transform = world_map.get_spawn_points()[0]

        # Spawn vehicle
        vehicle = world.spawn_actor(vehicle_bp, transform)

        # Need to append actors to actor list to delete when script finishes
        actor_list.append(vehicle)
        print('created %s' % vehicle.type_id)

        # Add sensors
        # Offset
        sensor_location = carla.Location(0, 0, 2)
        sensor_rotation = carla.Rotation(0, 0, 0)
        sensor_transform = carla.Transform(sensor_location, sensor_rotation)

        # RGB camera
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_rgb = world.spawn_actor(
            camera_bp, sensor_transform, attach_to=vehicle)
        actor_list.append(camera_rgb)
        camera_rgb.listen(lambda image: image.save_to_disk(
            'sensor_output/camera_RGB/%06d.png' % image.frame))

        # Depth camera
        camera_bp = blueprint_library.find('sensor.camera.depth')
        camera_depth = world.spawn_actor(
            camera_bp, sensor_transform, attach_to=vehicle)
        actor_list.append(camera_depth)
        camera_depth.listen(lambda image: image.save_to_disk(
            'sensor_output/camera_depth/%06d.png' % image.frame, carla.ColorConverter.LogarithmicDepth))

        # Semantic segmentation camera
        camera_bp = blueprint_library.find(
            'sensor.camera.semantic_segmentation')
        camera_SS = world.spawn_actor(
            camera_bp, sensor_transform, attach_to=vehicle)
        actor_list.append(camera_SS)
        camera_SS.listen(lambda image: image.save_to_disk(
            'sensor_output/camera_SS/%06d.png' % image.frame, carla.ColorConverter.CityScapesPalette))

        # GNSS
        gnss_bp = blueprint_library.find('sensor.other.gnss')
        gnss_bp.set_attribute("sensor_tick", str(3.0))
        gnss = world.spawn_actor(
            gnss_bp, sensor_transform, attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
        actor_list.append(gnss)

        def gnss_callback(output):
            print("GNSS measure:\n"+str(output)+'\n')
        gnss.listen(lambda output: gnss_callback(output))

        # IMU
        imu_bp = blueprint_library.find('sensor.other.imu')
        imu_bp.set_attribute("sensor_tick", str(3.0))
        imu = world.spawn_actor(
            imu_bp, sensor_transform, attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
        actor_list.append(imu)

        def imu_callback(output):
            print("IMU measure:\n"+str(output)+'\n')
        imu.listen(lambda output: imu_callback(output))

        # Radar
        rad_bp = blueprint_library.find('sensor.other.radar')
        radar = world.spawn_actor(rad_bp, sensor_transform, attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
        actor_list.append(radar)

        def rad_callback(radar_data):
            velocity_range = 7.5  # m/s
            current_rot = radar_data.transform.rotation
            for detect in radar_data:
                azi = math.degrees(detect.azimuth)
                alt = math.degrees(detect.altitude)
                # The 0.25 adjusts a bit the distance so the dots can
                # be properly seen
                fw_vec = carla.Vector3D(x=detect.depth - 0.25)
                carla.Transform(
                    carla.Location(),
                    carla.Rotation(
                        pitch=current_rot.pitch + alt,
                        yaw=current_rot.yaw + azi,
                        roll=current_rot.roll)).transform(fw_vec)

                def clamp(min_v, max_v, value):
                    return max(min_v, min(value, max_v))

                norm_velocity = detect.velocity / velocity_range  # range [-1, 1]
                r = int(clamp(0.0, 1.0, 1.0 - norm_velocity) * 255.0)
                g = int(clamp(0.0, 1.0, 1.0 - abs(norm_velocity)) * 255.0)
                b = int(abs(clamp(- 1.0, 0.0, - 1.0 - norm_velocity)) * 255.0)
                world.debug.draw_point(
                    radar_data.transform.location + fw_vec,
                    size=0.075,
                    life_time=0.06,
                    persistent_lines=False,
                    color=carla.Color(r, g, b))

        radar.listen(lambda radar_data: rad_callback(radar_data))

        # Hardcoded vehicle control
        # Forward
        vehicle.apply_control(carla.VehicleControl(throttle=0.6))
        time.sleep(10)


    finally:
        print('destroying actors')
        for actor in actor_list:
            actor.destroy()
        print('done.')


if __name__ == '__main__':

    main()
