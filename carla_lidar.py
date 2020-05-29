import glob
import os
import sys
import numpy as np

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
This script generates two vehicles in CARLA, attaches a raycast lidar to vehicle_2,
and has vehicle_2 pass vehicle_1 using hardcoded vehicle controls. The passing is recorded
using the lidar sensor and the resulting .ply files are saved to the disk. I suggest using 
Blender and Stop-motion-OBJ to visualize the resulting pointcloud animation.

Developed for CARLA 0.9.9 on Windows 10

Usage: 
    Run CarlaUE4.exe to start server, then run python3 carla_lidar.py to run script

Outputs:
    .ply files representing frames of lidar output in ./sensor_output/lidar/

Sources:
https://github.com/neverhood311/Stop-motion-OBJ
https://carla.readthedocs.io/en/stable/cameras_and_sensors/#ray-cast-based-lidar
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

        # Vehicles being tested
        vehicle_bp1 = blueprint_library.filter('vehicle.tesla.model3')[0]
        vehicle_bp2 = blueprint_library.filter('vehicle.*.*')[0]

        # Get spawn points for both vehicles
        world_map = world.get_map()
        transform1 = world_map.get_spawn_points()[0]
        # Spawn vehicle2 10m behind vehicle1
        transform2 = carla.Transform(transform1.transform(
            carla.Location(x=-10.0)), transform1.rotation)

        # Spawn vehicles
        vehicle1, vehicle2 = world.spawn_actor(
            vehicle_bp1, transform1), world.spawn_actor(vehicle_bp2, transform2)

        # Need to append actors to actor list to delete when script finishes
        actor_list.extend([vehicle1, vehicle2])
        print('created %s' % vehicle1.type_id)
        print('created %s' % vehicle2.type_id)

        # --------------
        # Add a new LIDAR sensor
        # --------------
        lidar_cam = None
        lidar_bp = world.get_blueprint_library().find('sensor.lidar.ray_cast')
        lidar_bp.set_attribute('channels',str(32))
        lidar_bp.set_attribute('points_per_second',str(300000))
        lidar_bp.set_attribute('rotation_frequency',str(120))
        lidar_bp.set_attribute('range',str(20))
        lidar_bp.set_attribute('lower_fov',str(-40))

        lidar_location = carla.Location(0,0,2)
        lidar_rotation = carla.Rotation(0,0,0)
        lidar_transform = carla.Transform(lidar_location,lidar_rotation)

        # Attach lidar sensor to vehicle 2
        # For some reason, using AttachmentType.SpringArm results in weirdness so Rigid is used instead
        lidar_sen = world.spawn_actor(lidar_bp,lidar_transform,attach_to=vehicle2,attachment_type=carla.AttachmentType.Rigid)
        lidar_sen.listen(lambda point_cloud: point_cloud.save_to_disk('sensor_output/lidar/f%.6d.ply' % point_cloud.frame))
        actor_list.append(lidar_sen)

        # Hardcoded vehicle control -- vehicle2 passes vehicle1
        # Forward
        vehicle1.apply_control(carla.VehicleControl(throttle=0.6))
        vehicle2.apply_control(carla.VehicleControl(throttle=0.8))
        time.sleep(4)

        # Get in left lane
        vehicle2.apply_control(carla.VehicleControl(throttle=0.8, steer=-0.1))
        time.sleep(1)

        vehicle2.apply_control(carla.VehicleControl(throttle=0.8))
        time.sleep(1)

        vehicle2.apply_control(carla.VehicleControl(throttle=0.8, steer=0.1))
        time.sleep(1)

        # Pass vehicle 1
        vehicle2.apply_control(carla.VehicleControl(throttle=0.8))
        time.sleep(1.5)

        # Get back in right lane
        vehicle2.apply_control(carla.VehicleControl(throttle=0.8, steer=0.1))
        time.sleep(1)

        vehicle2.apply_control(carla.VehicleControl(throttle=0.8))
        time.sleep(1)

        vehicle2.apply_control(carla.VehicleControl(throttle=0.8, steer=-0.1))
        time.sleep(1)


    finally:

        print('destroying actors')
        for actor in actor_list:
            actor.destroy()
        print('done.')


if __name__ == '__main__':

    main()
