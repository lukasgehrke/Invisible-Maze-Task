import viz
import vizact
import vizproximity
import viztask
import vizinfo
import vizshape
from tools import pencil

import screen_flash

from BaseScene import BaseScene
# from Maze import Maze


class VisualMazeScene(BaseScene):
    """
    Scene of the Spot Rotation Experiment.

    Contains graphical models of the 3D environment. Makes use of BaseClass Scene to set some behavior and
    visual for the scene.

    """

    def __init__(self, maze_type, subject, show_avatar_hands=False):

        # call constructor of superclass
        super(VisualMazeScene, self).__init__(background_noise=True)

        if not maze_type == 'baseline':

            # create proximity manager for maze ground units and corner types
            self.poi_manager = super(VisualMazeScene, self).create_proximity_manager()
            vizact.onkeydown('p', self.poi_manager.setDebug, viz.TOGGLE)

            # init drawing tool
            self.draw_tool = pencil.Pencil()
            self.draw_sphere = VisualMazeScene.add_sphere('draw_sphere', 0.1, viz.RED, [0,0,0], viz.OFF, False, None)

            # arrow for warning when head is leaving the maze path
            self.arrow = viz.add('resources/arrow.dae')
            self.arrow.visible(viz.OFF)
            self.arrow.setScale(2, 2, 2)
            self.arrow.color(viz.RED)

            # add draw frame 3D model
            self.drawing_frame = viz.add('resources/frame_model.osgb')
            self.drawing_frame.setScale(1.5, 1.5, 1.5)
            self.drawing_frame.visible(viz.OFF)

            # add local landmark (flash)
            self.flash_quad = screen_flash.Flasher(color=viz.WHITE)

            # reward feedback
            self.coin = viz.add('resources/model2.dae')
            self.coin.setScale(1, 1, 1)
            self.coin.visible(viz.OFF)

            # tracked 3D object for hand collision
            self.feedback_sphere_right = VisualMazeScene.add_sphere('wall_touch', 0.001, viz.WHITE, [0, 0, 0], viz.ON, False, None)
            self.feedback_sphere_right.setScale([0.29 * 350, 0.29 * 350, 0.01])
            self.feedback_sphere_right.alpha(0)
    
    def toggle_global_landmark(self, maze, on_off):
        """
        show or hide landmark
        
        :param maze: the maze object containing the landmark object
        :param on_off
        """

        if on_off == "on":
            maze.global_landmark.visible(viz.ON)
        else:
            maze.global_landmark.visible(viz.OFF)

    def reward_feedback(self, head_hits, duration, show_duration):

        self.coin.visible(viz.ON)
        completed = viz.link(viz.MainView, self.coin)
        completed.preTrans([-.3, 0, 2])
		reward = 1/3

        if duration <= 300:
            dur_coin = self.coin.copy()
            fast = viz.link(viz.MainView, dur_coin)
            fast.preTrans([.2, 0, 2])
			reward += 1/3

        if head_hits <= 10:
            head_coin = self.coin.copy()
            precise = viz.link(viz.MainView, head_coin)
            precise.preTrans([.7, 0, 2])
			reward += 1/3

		print round(reward,2)
        yield viztask.waitTime(show_duration)

        self.coin.visible(viz.OFF)
        completed.remove()
        if duration <= 300:
            dur_coin.visible(viz.OFF)
            fast.remove()
        if head_hits <= 10:
            head_coin.visible(viz.OFF)
            precise.remove()
