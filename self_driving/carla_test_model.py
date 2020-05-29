import random
from collections import deque
import numpy as np
import cv2
import time
import tensorflow as tf
import keras.backend.tensorflow_backend as backend
from keras.models import load_model

"""
Tests the model trained from self_driving.py by loading the model from the disk, randomly spawning a 
vehicle, attaching a camera to the vehicle, and letting the model have a go at controling the vehicle.

Developed for CARLA 0.9.9 on Windows 10

Usage: 
    Run CarlaUE4.exe to start server, then run python3 self_driving/test_model.py to run script.
        Be patient as it takes some time to start up (and ignore the warnings-- it's fine! :)
        After some time, an OpenCV window will appear where you can see the car's camera sensor output

Outputs: 
    input frames fed into the model into self_driving/camera_RGB

Sources:
https://pythonprogramming.net/introduction-self-driving-autonomous-cars-carla-python
"""

from carla_train_model import CarEnv, MEMORY_FRACTION

MODEL_PATH = 'self_driving/models/Xception____-2.00max__-42.60avg_-203.00min__1589853479.model'

if __name__ == '__main__':

    frame_count = 0

    # Memory fraction
    gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=MEMORY_FRACTION)
    backend.set_session(tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(gpu_options=gpu_options)))

    # Load the model
    model = load_model(MODEL_PATH)

    # Create environment
    env = CarEnv()

    # For agent speed measurements - keeps last 60 frametimes
    fps_counter = deque(maxlen=60)

    # Initialize predictions - first prediction takes longer as of initialization that has to be done
    # It's better to do a first prediction then before we start iterating over episode steps
    model.predict(np.ones((1, env.im_height, env.im_width, 3)))

    # Loop over episodes
    while True:

        print('Restarting episode')

        # Reset environment and get initial state
        current_state = env.reset()
        env.collision_hist = []

        done = False

        # Loop over steps
        while True:

            # For FPS counter
            step_start = time.time()

            # Show current frame
            cv2.imshow(f'Agent - preview', current_state)

            # Write current frame
            cv2.imwrite(f'self_driving/camera_RGB/{frame_count}.png', current_state)
            frame_count += 1

            cv2.waitKey(1)

            # Predict an action based on current observation space
            qs = model.predict(np.array(current_state).reshape(-1, *current_state.shape)/255)[0]
            action = np.argmax(qs)

            # Step environment (additional flag informs environment to not break an episode by time limit)
            new_state, reward, done, _ = env.step(action)

            # Set current step for next loop iteration
            current_state = new_state

            # If done - agent crashed, break an episode
            if done:
                break

            # Measure step time, append to a deque, then print mean FPS for last 60 frames, q values and taken action
            frame_time = time.time() - step_start
            fps_counter.append(frame_time)
            print(f'Agent: {len(fps_counter)/sum(fps_counter):>4.1f} FPS | Action: [{qs[0]:>5.2f}, {qs[1]:>5.2f}, {qs[2]:>5.2f}] {action}')

        # Destroy an actor at end of episode
        for actor in env.actor_list:
            actor.destroy()