"""
Base scene module contains general functionality to build and manipulate the experimental scene.

"""

from abc import ABCMeta, abstractmethod

import random

import viz, viztask, vizshape, vizproximity, vizact, vizinfo


class BaseScene(object):
    """
    Creates an instruction window and contains several functions to build and change objects in the virtual environment.
    Furthermore has the functionality to create and feed a proximity manager.

    Recommendation: implement an inheriting class 'YourExperimentScene' extending BaseScene and put the code
    specific to the look and feel of your experimental scene there. Make use of the functions in the class BaseScene
    where possible.

    """

    __metaclass__ = ABCMeta

    def __init__(self, background_noise):
        """
        Initializes a BaseScene instance which loads vizconnect configuration.

        Args:
            background_noise: if enabled plays a background white noise on repeat

        """

        if background_noise:
            noise = self.add_and_play_background_noise(volume=0.1)

        # todo test
        vizact.onkeydown('s', self.noise.play, viz.TOGGLE)

        self.instruction = self.instruction_canvas_vr(40)
        # Press 'i' to toggle instruction visibility
        vizact.onkeydown('i', self.instruction.visible, viz.TOGGLE)
        vizact.onmousedown(viz.MOUSEBUTTON_RIGHT, self.instruction.visible, viz.TOGGLE)

        # Hit the 's' key for a screen capture. Save that file as 'screenshot_experiment.bmp'.
        #vizact.onkeydown('s', viz.window.screenCapture, 'screenshot_experiment.bmp')

    def instruction_canvas_vr(self, fov_canvas):
        """
        Sets up a canvas for showing instructions in VR.

        Args:
            fov_canvas: field of view that the canvas should overlay

        """

        self.canvas = viz.addGUICanvas()

        # Reduce canvas FOV from default 50 to 40 ; fov ist wichtig, distance scheint nichts zu tun.
        self.canvas.setRenderWorldOverlay([1280, 720], fov_canvas, distance=10.0)
        viz.MainWindow.setDefaultGUICanvas(self.canvas)
        instruction_window = vizinfo.InfoPanel(text='Bitte warten...', title='Instruktionen', key=None, icon=False,
                                               align=viz.ALIGN_CENTER, fontSize=30, parent=self.canvas)

        return instruction_window

    def hide_instruction(self):
        """
        Hides the infopanel "info".

        """

        self.instruction.visible(viz.OFF)
    
    def show_instruction(self):
        """
        Shows the infopanel "info".

        """
        
        self.instruction.visible(viz.ON)

    def change_instruction(self, string):
        """
        Changes the message of the infopanel "info" and makes it visible.

        Args:
            string: message to be shown to the participant

        """
        
        self.instruction.setText(string)
        self.show_instruction()

    def countdown(self, seconds):
        """
        A countdown timer.

        Counts down by 1 digit in 1 second and displays the new value after each second.

        Args:
            seconds: Start value to count down from.

        """
        
        for second in range(seconds):

            while seconds != 0:
                self.change_instruction(str(seconds))
                seconds = seconds - 1
                yield viztask.waitTime(1)

        self.change_instruction('Los!')
        yield viztask.waitTime(1)
        self.hide_instruction()
        print '!!! EXPLORATION STARTED !!!'

    @staticmethod
    def add_light(euler):
        """
        Creates and returns a light object.

        Args:
            euler: degree relating to the x, y plane from which the light shines.

        Returns: A Vizard light object instance.

        """

        light = viz.addLight()
        light.setEuler(0,euler,0)

        return light

    @staticmethod
    def fade_in(object_to_fadein, duration, markerstream):
        """
        Plays a fade in animation for a given 3D object.

        Args:
            object_to_fadein: 3D object
            duration: time it takes to fade in the object from 0 to 100% opacity
            markerstream: LSL markerstream to push start of object rotation

        """

        fadein = vizact.fadeTo(1, time=duration)
        object_to_fadein.addAction(fadein)
        markerstream.push_sample(['object_fadein, duration:' + str(duration)])

    @staticmethod
    def fade_out(object_to_fadeout, duration, markerstream):
        """
        Plays a fade out animation for a given 3D object.

        Args:
            object_to_fadeout: 3D object
            duration: duration: time it takes to fade out the object from 0 to 100% opacity
            markerstream: LSL markerstream to push start of object rotation

        """

        fadeout = vizact.fadeTo(0, time=duration)
        object_to_fadeout.addAction(fadeout)
        markerstream.push_sample(['object_fadeout, duration:' + str(duration)])

    @staticmethod
    def rotate(object_to_rotate, duration, markerstream):
        """
        Rotates a 3d object by a randomly chosen angle between 1 and 360 degree.

        Args:
            object_to_rotate: any 3d node object
            duration: duration of the rotation in seconds
            markerstream: LSL markerstream to push rotate value

        Returns:

        """

        rotate_val = random.randint(1, 360)
        markerstream.push_sample(['ground_rotate'])
        markerstream.push_sample(['ground_rotate_angle,' + str(rotate_val)])
        spinto = vizact.spinTo(euler=(rotate_val, 0, 0), time=0, mode=viz.REL_GLOBAL)
        fadeout = vizact.fadeTo(0, time=duration)
        fadein = vizact.fadeTo(1, time=duration)

        fadeinout = vizact.sequence(fadeout, spinto, fadein)
        object_to_rotate.addAction(fadeinout)
        markerstream.push_sample(['object_fadeInOut, duration:' + str(duration)])

    @staticmethod
    def add_sphere(name, rad, col, position, vis, proximity, scale):
        """
        Adds a sphere object and returns it. Optionally adds a proximity sensor around the sphere.

        Args:
            name: name of the sphere object
            rad: radius of the sphere, e.g. 1.0
            col: color of the sphere, e.g. "viz.RED"
            position: specified position by [x, y, z]
            vis: visibility of the sphere, i.e. "viz.ON" or "viz.OFF"
            proximity: if True create a BoundingSphereSensor proximity sensor around the sphere
            scale: scale factor or size of BoundingSphereSensor

        Returns: A Vizard sphere object with the optionality of creating a proximity sensor around the sphere.

        """

        sphere = vizshape.addSphere(radius=rad, color=col)
        sphere.name = name
        sphere.setPosition(position)
        sphere.visible(vis)

        if proximity:
            sphere.sensor = vizproximity.addBoundingSphereSensor(sphere, scale=scale)

        return sphere

    def add_and_play_background_noise(self, volume):
        """
        background noise for noise cancellation

        Args:
            volume: volume of background noise

        Returns: an audio object.

        """

        self.noise = viz.addAudio('white-noise_192k.wav')
        self.noise.loop(viz.ON)
        self.noise.volume(volume)
        self.noise.play()

        return self.noise

    @staticmethod
    def create_proximity_manager():
        """
        Create a proximity manager and returns it.

        Returns: proximity manager

        """

        manager = vizproximity.Manager()
        manager.setDebug(viz.OFF)
        #vizact.onkeydown('v', manager.setDebug, viz.TOGGLE)

        return manager

    @staticmethod
    def proximity_target(proximity_manager, target):
        """
        Creates and adds a target to the proximity manager.

        Args:
            proximity_manager:
            target:

        Returns:

        """

        target = vizproximity.Target(target)
        proximity_manager.addTarget(target)

        return target

    @staticmethod
    def proximity_sensor(proximity_manager, sensor):
        """
        Adds a sensor to a proximity manager.

        Args:
            proximity_manager: Vizard proximity manager
            sensor: Vizard proximity sensor object

        """

        proximity_manager.addSensor(sensor)

    @staticmethod
    def enter_proximity_sensor(e):
        """
        Elicit event when target enters proximity sensor.

        Args:
            e:

        Returns:

        """

        # sphere.runAction(vizact.fadeTo(viz.BLUE, time=1))
        # register callback: manager.onEnter(sensor, enter_sphere, sphere, color)
        # print("a proximity sensor in the proximity manager was just entered")
        print(e.sensor, "entered by proximity target")

    @staticmethod
    def exit_proximity_sensor(e):
        """
        Elicit event when target exits proximity sensor.

        Args:
            e:

        Returns:

        """

        # sphere.runAction(vizact.fadeTo(viz.WHITE, time=1))
        # register callback: manager.onExit(sensor, exit_sphere, sphere, color)
        # print("a proximity sensor in the proximity manager was just left")
        print(e.sensor, "left by proximity target")