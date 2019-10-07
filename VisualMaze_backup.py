import math
import socket
import os
import numpy
import steamvr
import random

import viz
import vizact
import vizproximity
import vizshape
import viztask
import vizfx

from BaseExperiment import BaseExperiment
from BaseSubject import BaseSubject
from VisualMazeScene import VisualMazeScene
from resources.trackers.lsl_lib import pylsl as lsl

from Maze import Maze

class VisualMaze(BaseExperiment):

    def __init__(self, participant):

        self.visual_maze_instruktionen = {
            'baseline_start': 'Zu Beginn wird eine Zusatzmessung aufgenommen.\n'
                              'Es geht gleich automatisch weiter...',
            'baseline_standing': 'Halten Sie Ihre Augen offen und\n'
                                 'entspannen sich.\n'
                                 'Mit einem Klick,\n'
                                 'beginnt die Messung',
            'baseline_thrusting':'Halten Sie Ihre Augen offen und\n'
                                 'tasten wiederholt nach vorne.\n'
                                 'Mit einem Klick,\n'
                                 'beginnt die Messung.',
            'baseline_end': 'Bitte beim Versuchsleiter melden.'
        }

        # call constructor of superclass
        super(VisualMaze, self).__init__(participant)

        #ground = viz.add('tut_ground.wrl')  # Add ground

        # create scene of the experiment
        self.subject_id = participant.id
        self.scene = VisualMazeScene(participant.maze_config, self.subject)
        self.maze = None
        self.light = vizfx.addDirectionalLight(euler=(0, 90, 0), color=viz.WHITE)
        self.hand_tracker_id = None
        self.arm_tracker_id = None
        self.torso_tracker_id = None

        # permuted list of all 4 trial mazes L Z U S, with 24 subjects 1 permutation cycle is complete
        self.trial_list_all = [
            ['Z', 'L', 'U', 'S'],
            ['L', 'Z', 'U', 'S'],
            ['U', 'L', 'Z', 'S'],
            ['L', 'U', 'Z', 'S'],
            ['Z', 'U', 'L', 'S'],
            ['U', 'Z', 'L', 'S'],
            ['U', 'Z', 'S', 'L'],
            ['Z', 'U', 'S', 'L'],
            ['S', 'U', 'Z', 'L'],
            ['U', 'S', 'Z', 'L'],
            ['Z', 'S', 'U', 'L'],
            ['S', 'Z', 'U', 'L'],
            ['S', 'L', 'U', 'Z'],
            ['L', 'S', 'U', 'Z'],
            ['U', 'S', 'L', 'Z'],
            ['S', 'U', 'L', 'Z'],
            ['L', 'U', 'S', 'Z'],
            ['U', 'L', 'S', 'Z'],
            ['Z', 'L', 'S', 'U'],
            ['L', 'Z', 'S', 'U'],
            ['S', 'Z', 'L', 'U'],
            ['Z', 'S', 'L', 'U'],
            ['L', 'S', 'Z', 'U'],
            ['S', 'L', 'Z', 'U']
        ]
        # permuted list of all 3 objects to test in rvd task (G = Global Landmark, L = Local, S = Start) with 24 subjects 4 permutation cycles are complete
        self.rvd_list_all = [
            ['G', 'L', 'S'],
            ['L', 'G', 'S'],
            ['S', 'G', 'L'],
            ['G', 'S', 'L'],
            ['L', 'S', 'G'],
            ['S', 'L', 'G'],
            ['G', 'L', 'S'],
            ['L', 'G', 'S'],
            ['S', 'G', 'L'],
            ['G', 'S', 'L'],
            ['L', 'S', 'G'],
            ['S', 'L', 'G'],
            ['G', 'L', 'S'],
            ['L', 'G', 'S'],
            ['S', 'G', 'L'],
            ['G', 'S', 'L'],
            ['L', 'S', 'G'],
            ['S', 'L', 'G'],
            ['G', 'L', 'S'],
            ['L', 'G', 'S'],
            ['S', 'G', 'L'],
            ['G', 'S', 'L'],
            ['L', 'S', 'G'],
            ['S', 'L', 'G']
        ]

        # # keys for video recording
        # vidname = str(participant.id) + '_' + str(participant.control_style) + '.avi'
        # viz.setOption('viz.AVIRecorder.fps','25')
        # viz.setOption('viz.AVIRecorder.maxWidth','1280')
        # viz.setOption('viz.AVIRecorder.maxHeight', '720')
        # vizact.onkeydown('b', viz.window.startRecording, vidname)
        # vizact.onkeydown('e', viz.window.stopRecording)

        # ---- collision event params ---- #
        # objects handling current state of visual maze experiment
        # wall enter and exit collision event callbacks
        self.hand_in_wall = False
        self.head_in_wall = False

        # placeholders for visual feedback functions
        self.feedback_hand = None
        self.feedback_start_time = 0
        self.feedback_duration = 0
        self.new_touch_allowed = True
        self.feedback = vizact.sequence(vizact.waittime(0.5),vizact.fadeTo(0,time=.2)) # event is 700 ms
        self.help_sphere = vizshape.addSphere(.1)
        self.help_sphere.color(viz.GREEN)
        self.help_sphere.visible(viz.OFF)

        # ---- Bookkeeping variables for behavioral data collection ---- #
        self.current_maze = None
        self.current_trial_run = None

        # ---- Reward tracking variables ---- #
        self.hand_hits = 0
        self.head_hits = 0
        self.local_landmark_hits = 0
        self.duration = 0
        self.start_return = 0

        # pointing task
        self.pointing_task_on = False

        # RVD task objects
        self.rvd_task_on = False
        self.in_rvd_table = False
        self.rvd_table = vizshape.addCube(1)
        self.rvd_table.alpha(0.3)  # make surface barely visible
        self.rvd_table.visible(viz.OFF)
        self.start_sign = viz.add('resources/start.dae')
        self.start_sign.setScale(.02, .02, .02)
        self.start_sign.visible(viz.OFF)

    def push_marker(self, markerstream, marker):
        # push marker LSL

        markerstream.push_sample([marker])

    def log_exp_progress(self, event):

        maze = 'maze:' + self.current_maze + ';'
        trial_run = 'trial_run:' + str(self.current_trial_run) + ';'

        data = event + maze + trial_run
        self.push_marker(self.markerstream, data)

        #print data

    def log_wall_touches(self, hand_tracker, collision_position):
        # visual event: something in the vis input changes on enter and on exit
        # acquisition_time = lsl.local_clock()

        if hand_tracker:
            event = 'wall_touch;'
            self.hand_hits += 1
            hit = 'num_wall_touch:' + str(self.hand_hits) + ';'
        else:
            event = 'head_collision;'
            self.head_hits += 1
            hit = 'num_head_collision:' + str(self.head_hits) + ';'

        event = 'type:' + event
        trial_run = 'trial_run:' + str(self.current_trial_run) + ';'
        maze = 'maze:' + self.current_maze + ';'
        data = event + trial_run + maze

        x = 'x:' + str(collision_position[0]) + ';'
        y = 'y:' + str(collision_position[1]) + ';'
        z = 'z:' + str(collision_position[2]) + ';'
        pos = hit + x + y + z

        data = data + pos
        self.push_marker(self.markerstream, data)

        #print data

    def hide_inst_continue_left_mouse(self):

        yield viztask.waitMouseDown(viz.MOUSEBUTTON_LEFT)
        self.scene.hide_instruction()

    def hide_inst_continue_trigger(self):

        yield viztask.waitSensorDown(self.controller, steamvr.BUTTON_TRIGGER)
        self.scene.hide_instruction()

    def baseline_measurement(self, instruction, duration):
        """
        Standing baseline measurement for BeMoBIL experiments.

        :param markerstream: LSL markerstream for experimental procedure markers.
        :param duration: Baseline duration, default 1 minute
        :return:
        """

        self.scene.change_instruction(self.visual_maze_instruktionen[instruction])
        yield self.hide_inst_continue_left_mouse()

        # baseline start marker
        event = 'type:'+instruction+'_start;'
        self.log_exp_progress(event)
        if duration is not None:
            yield viztask.waitTime(duration)
        else:
            yield viztask.waitTime(60)
        # baseline end marker
        event = 'type:'+instruction+'_end;'
        self.log_exp_progress(event)

    def change_experiment_scene(self, maze_type):

        # remove old maze
        if self.maze is not None:
            # self.remove_old_scene(self.maze)
            # clear instance of class Maze
            del self.maze

            # reset logging vars
            self.hand_hits = 0
            self.head_hits = 0
            self.local_landmark_hits = 0
            self.duration = 0
            self.start_return = 0

        self.maze = Maze(maze_type, self.scene.poi_manager)

        self.maze.walls.collideMesh()
        self.maze.walls.disable(viz.DYNAMICS)
        self.maze.walls.disable(viz.RENDERING)
        self.maze.walls.disable(viz.DEPTH_WRITE)

    def remove_old_scene(self, maze):

        # remove 3D objects of previous maze
        maze.walls.remove()
        maze.global_landmark.remove()

        # reset logging vars
        self.hand_hits = 0
        self.head_hits = 0
        self.local_landmark_hits = 0
        self.duration = 0
        self.start_return = 0

    def draw(self, draw_tool):
        """
        update code for pencil

        :param draw_tool:
        :return:
        """

        state = viz.mouse.getState()
        
#        if state & viz. MOUSEBUTTON_LEFT:
#            draw_tool.draw()

        if self.controller.getTrigger() > 0.0:
            draw_tool.draw()
        if state & viz.MOUSEBUTTON_RIGHT:
            draw_tool.clear()

    def draw_maze_task(self):

        # remove collide events
        viz.phys.disable()

        # position frame in front of subject after reorienting
        pos = self.subject.head_sphere.getPosition()
        self.scene.drawing_frame.setPosition([pos[0]-.2, pos[1]-.5, pos[2]+.6])
        self.scene.drawing_frame.visible(viz.ON)

        self.scene.change_instruction("Bitte zeichnen Sie den Raum in den Rahmen ein.\nStart mit Klick.")
        print '!!! DRAWING TASK, TRIGGER TO START !!!'
        yield self.hide_inst_continue_trigger()
        print '!!! DRAWING STARTED, MOUSECLICK TO SAVE !!!'

        # enable drawing functionality
        self.subject.right_hand_sphere.alpha(1)
        self.subject.right_hand_sphere.setScale(2, 2, 2)
        self.subject.right_hand_sphere.color(viz.WHITE)
        draw_link = viz.link(self.subject.right_hand_sphere, self.scene.draw_tool)

        # drawing update function called every frame and handling states of input device
        self.scene.draw_tool.setUpdateFunction(self.draw)

        # send drawing task start marker
        self.log_exp_progress('type:drawing_start;')
        start = viz.tick()

        # wait until drawing is saved and continue with the experiment
        yield self.hide_inst_continue_left_mouse()
        print '!!! DRAWING SAVED !!!'

        # send drawing task end marker
        duration_drawing = viz.tick() - start
        self.log_exp_progress('type:drawing_end;duration_drawing:' + str(round(duration_drawing,2)) + ';')

        # save screenshot of drawing
        filename = 'subject_' + str(self.subject_id) + '_sketchmap_' + str(self.current_maze)
        viz.window.screenCapture(filename + '.bmp')
        yield viztask.waitTime(0.5)

        # remove drawing and draw_tool
        self.scene.drawing_frame.visible(viz.OFF)
        draw_link.remove()
        self.scene.draw_tool.clear()
        self.subject.right_hand_sphere.alpha(0)
        self.subject.right_hand_sphere.setScale(1, 1, 1)

    def reorient(self):

        # put arrow in direction of start and ask participants to turn around
        self.scene.arrow.setEuler([180, 0, 0])
        self.scene.arrow.setPosition(self.maze.start_pos[0], self.maze.start_pos[1] - .5, self.maze.start_pos[2] - 1.5)
        self.scene.arrow.visible(viz.ON)
        self.scene.change_instruction('Bitte umdrehen!')

        # remove after 2s
        yield viztask.waitTime(2)
        self.scene.arrow.visible(viz.OFF)
        self.scene.hide_instruction()

    def pointing(self, trial_start_time):
        duration_outward = viz.tick() - trial_start_time
        self.log_exp_progress(
            'type:enter_local_landmark;num_local_landmark:' + str(self.local_landmark_hits) + \
            ';duration_outward:' + str(round(duration_outward, 2)) + ';')
        self.scene.change_instruction("Bitte zeigen Sie zum Startpunkt.")
        self.pointing_task_on = True
        self.subject.right_hand_sphere.alpha(1)
        yield self.hide_inst_continue_trigger()
        self.log_exp_progress('type:pointing;')
        self.subject.right_hand_sphere.alpha(0)
        self.start_return = viz.tick()
        self.pointing_task_on = False

    def rvd_task(self):

        # make 3D surface to put object on / like a table in front of participant
        self.rvd_table.setPosition([self.maze.start_pos[0], .5, self.maze.start_pos[2]+.5]) # move a bit away
        self.rvd_table.visible(viz.ON)

        sc = .03 # manually set scale factor of 3D objects
        self.maze.global_landmark.setScale(.03*sc, .03*sc, .03*sc)
        self.maze.maze_end_ground.setScale(sc, sc, sc) # make a bit bigger
        self.maze.maze_start_ground.setScale(sc, sc, sc) # make a bit bigger
        self.maze.maze_start_ground.color(viz.YELLOW)        

        # set start position as anchor
        y_offset = 1.0
        z_offset = .4
        scale_factor = 20

        s_scaled = [x / scale_factor for x in self.maze.maze_start_ground.getPosition()]
        l_scaled = [x / scale_factor for x in self.maze.maze_end_ground.getPosition()]
        g_scaled = [x / scale_factor for x in self.maze.global_landmark.getPosition()]

        # get difference to correct the offset of to the start position ground
        abs_x_diff = abs(self.maze.maze_start_ground.getPosition()[0]) - abs(s_scaled[0])
        # add/subtract offset in x direction
        if self.maze.maze_start_ground.getPosition()[0] < 0:
            s_scaled[0] = s_scaled[0] - abs_x_diff
            l_scaled[0] = l_scaled[0] - abs_x_diff
            g_scaled[0] = g_scaled[0] - abs_x_diff
        else:
            s_scaled[0] = s_scaled[0] + abs_x_diff
            l_scaled[0] = l_scaled[0] + abs_x_diff
            g_scaled[0] = g_scaled[0] + abs_x_diff

        # subtract z to table location and add offset on z direction
        combined_offset = self.maze.maze_start_ground.getPosition()[2] + z_offset
        s_scaled[2] = s_scaled[2] + combined_offset
        l_scaled[2] = l_scaled[2] + combined_offset
        g_scaled[2] = g_scaled[2] + combined_offset

        # add height of table in y direction
        s_scaled[1] = s_scaled[1] + y_offset
        l_scaled[1] = l_scaled[1] + y_offset
        g_scaled[1] = g_scaled[1] + y_offset

        # set position of objects
        self.maze.maze_start_ground.setPosition(s_scaled)
        self.maze.maze_end_ground.setPosition(l_scaled)
        self.maze.global_landmark.setPosition(g_scaled)

        # # compute scaled, z_offseted (moved a bit forward) triangle of objects once and then make objects visible or not
        # scale_factor = 30
        #
        # # set start position as anchor
        # z_offset = .2
        #
        # self.maze.maze_start_ground.setPosition(self.maze.start_pos[0], 1.0, self.maze.start_pos[2] + z_offset)
        #
        # # set position of global landmark: only differs in z dimension from start position
        # z_dist_landmark_start = abs(self.maze.global_landmark.getPosition()[2] - self.maze.maze_start_ground.getPosition()[2]) / scale_factor
        # self.maze.global_landmark.setPosition([self.maze.maze_start_ground.getPosition()[0],
        #                                        self.maze.maze_start_ground.getPosition()[1],
        #                                        self.maze.maze_start_ground.getPosition()[2] + z_dist_landmark_start])
        #
        # # set position of local landmark: differs in x and z dimensions from start position
        # x_dist_local_start = abs(self.maze.maze_end_ground.getPosition()[0] - self.maze.maze_start_ground.getPosition()[0]) / scale_factor
        # z_dist_local_start = (self.maze.maze_end_ground.getPosition()[2] - self.maze.maze_start_ground.getPosition()[2]) / scale_factor
        #
        # if self.maze.maze_end_ground.getPosition()[0] < 0:
        #     self.maze.maze_end_ground.setPosition([self.maze.maze_start_ground.getPosition()[0] - x_dist_local_start,
        #                                            self.maze.maze_start_ground.getPosition()[1],
        #                                            self.maze.maze_start_ground.getPosition()[2] + z_dist_local_start])
        # else:
        #     self.maze.maze_end_ground.setPosition([self.maze.maze_start_ground.getPosition()[0] + x_dist_local_start,
        #                                            self.maze.maze_start_ground.getPosition()[1],
        #                                            self.maze.maze_start_ground.getPosition()[2] + z_dist_local_start])

        # send positions of all target objects
        if self.current_trial_run is 1:
            event = 'type:rvd_triangle;S:' + str(self.maze.maze_start_ground.getPosition()) + \
                ';L:' + str(self.maze.maze_end_ground.getPosition()) + \
                ';G:' + str(self.maze.global_landmark.getPosition()) + ';'
            self.log_exp_progress(event)

        # make different objects visible and guess third object
        object_to_guess = self.rvd_list_all[int(self.subject_id)-1]
        object_to_guess = object_to_guess[int(self.current_trial_run)-1]
        marker_object_to_guess = object_to_guess

        if object_to_guess is 'G':
            object_to_guess = self.maze.global_landmark
        elif object_to_guess is 'L':
            object_to_guess = self.maze.maze_end_ground
        elif object_to_guess is 'S':
            object_to_guess = self.maze.maze_start_ground

        # move somewhere out of sight before making visible so not to indicate correct solution for 1 frame
        object_to_guess.setPosition([0,0,-10])
        self.maze.maze_end_ground.visible(viz.ON)
        self.maze.maze_start_ground.visible(viz.ON)
        self.maze.global_landmark.visible(viz.ON)

        # start tracking with mouseclick
        self.scene.change_instruction("Platzieren Sie das fehlende Objekt.")
        print '!!! EXPERIMENTER CLICK MOUSE TO START RVD TASK THEN PARTICIPANTS HAS TO CONFIRM PLACEMENT WITH TRIGGER!!!'
        yield self.hide_inst_continue_left_mouse()
        self.log_exp_progress("event:rvd_start;")

        # track object
        self.rvd_feedback = vizact.onupdate(0, self.track_rvd, object_to_guess)

        # place target with button
        yield self.hide_inst_continue_trigger()
        print '!!! OBJECT PLACED !!!'
        self.log_exp_progress("event:rvd_target_placed;object_location:"+\
                              str(object_to_guess.getPosition())+';'+\
                              'object:'+marker_object_to_guess +';')
        self.rvd_feedback.remove()
        self.scene.change_instruction("Danke! Einen Moment...")

        # keep in view for 2 seconds
        yield viztask.waitTime(3)
        self.log_exp_progress("event:rvd_end;")
        self.rvd_task_on = False

        # hide objects
        self.rvd_table.visible(viz.OFF)
        self.maze.maze_start_ground.color(viz.WHITE)
        self.maze.maze_start_ground.visible(viz.OFF)
        self.maze.global_landmark.visible(viz.OFF)
        self.maze.maze_end_ground.visible(viz.OFF)

    def track_rvd(self, object):
        object.setPosition([self.subject.right_hand_sphere.getPosition()[0], 1, self.subject.right_hand_sphere.getPosition()[2]])

    def walk_maze_task(self):
        """
        Writes a start and end marker of walking phase.

        :param markerstream:
        :return:
        """

        print '!!! HIT TRIGGER TO START REWALKING MAZE !!!'
        self.scene.change_instruction("Finden Sie das Ende des Pfades!\n"
                                      "Zum Starten und bestaetigen, Klick!")
        yield self.hide_inst_continue_trigger()
        # send walking phase start marker
        start_walk = viz.tick()
        self.log_exp_progress('type:rewalking_start;')
        # end walking phase
        yield self.hide_inst_continue_trigger()
        print '!!! REWALKING TASK: ESTIMATED END LOGGED !!!'

        # send walking phase end marker
        duration_walk = viz.tick() - start_walk
        self.log_exp_progress('type:rewalking_end;duration_walk:' + str(round(duration_walk,2)) + ';')

    def on_enter_wall(self, tracker, pos, dir):

        # hand wall enter
        # allow only one collision and reactivate after the next collision (enter, then exit first, then enter again)
        if tracker is self.subject.right_hand_sphere and not self.hand_in_wall:
            self.hand_in_wall = True
            # only do wall touch when no collision of the head is present
            if not self.head_in_wall and not self.pointing_task_on:
                # only allow if previous touch was completed
                if self.new_touch_allowed is True:
                    # start time of wall touch
                    self.feedback_start_time = viz.tick()
                    # display feedback along the wall, flips axis based on normal vector
                    if round(dir[0]) == 1.0 or round(dir[0]) == -1.0 :
                        self.scene.feedback_sphere_right.setEuler([90, 0, 0])
                    else:
                        self.scene.feedback_sphere_right.setEuler([0, 0, 0])
                    # set feedback sphere color, alpha, scale and position:
                    self.scene.feedback_sphere_right.alpha(1)
                    self.scene.feedback_sphere_right.setPosition(pos)

                    # add action to display and fade out
                    self.scene.feedback_sphere_right.add(self.feedback)
                    self.new_touch_allowed = False
                    self.log_wall_touches(True, pos)

                    # check how long hand left in wall
                    self.feedback_hand = vizact.onupdate(0, self.check_hand_in_wall)

        # hand wall exit
        elif tracker is self.subject.right_hand_sphere and self.hand_in_wall:
            self.hand_in_wall = False
            self.scene.hide_instruction()

        # head wall collision
        elif tracker is self.subject.head_sphere and not self.head_in_wall:
            self.head_in_wall = True

            # place arrow orthogonal to crossed wall
            self.scene.change_instruction('Bitte zurueck treten!')

            if round(dir[0]) == 1.0:
                self.scene.arrow.setEuler([-90,0,0])
                self.scene.arrow.setPosition(pos[0] - 1, pos[1] - .5, pos[2])
                self.help_sphere.setPosition(pos[0] + .5, pos[1] - .5, pos[2])
            elif round(dir[0],1) == -1.0:
                self.scene.arrow.setEuler([90, 0, 0])
                self.scene.arrow.setPosition(pos[0] + 1, pos[1] - .5, pos[2])
                self.help_sphere.setPosition(pos[0] - .5, pos[1] - .5, pos[2])
            elif round(dir[2],1) == 1.0:
                self.scene.arrow.setEuler([180, 0, 0])
                self.scene.arrow.setPosition(pos[0], pos[1] - .5, pos[2] - 1)
                self.help_sphere.setPosition(pos[0], pos[1] - .5, pos[2] + .5)
            elif round(dir[2],1) == -1.0:
                self.scene.arrow.setEuler([0, 0, 0])
                self.scene.arrow.setPosition(pos[0], pos[1] - .5, pos[2] + 1)
                self.help_sphere.setPosition(pos[0], pos[1] - .5, pos[2] - .5 )
            self.scene.arrow.visible(viz.ON)
            self.help_sphere.visible(viz.ON)

            # log the head collision
            self.log_wall_touches(False, pos)

        elif tracker is self.subject.head_sphere and self.head_in_wall:
            self.head_in_wall = False
            self.scene.arrow.visible(viz.OFF)
            self.help_sphere.visible(viz.OFF)
            self.scene.hide_instruction()

    def check_hand_in_wall(self):
        """
        wall touch (for hand collision only!) simulated by a flat sphere at the position of the wall
        
        """

        # current feedback duration
        self.feedback_duration = viz.tick() - self.feedback_start_time

        if self.hand_in_wall:
            if self.feedback_duration > 2:
                self.scene.change_instruction('Hand zurueck ziehen!')

        if not self.hand_in_wall and self.feedback_duration > .7:
            self.new_touch_allowed = True
            self.feedback_hand.remove()
            self.feedback_start_time = 0

    def reset_touching(self):
        self.feedback_hand.remove()
        self.scene.hide_instruction()
        self.hand_in_wall = False
        self.head_in_wall = False
        self.feedback_start_time = 0
        self.feedback_duration = 0
        self.new_touch_allowed = True

    def check_node_intersection(self, tracker, walls):

        tracker_t2_pos = tracker.getPosition()

        if tracker is self.subject.right_hand_sphere:
            intersect_info = walls.intersect(tracker_t2_pos, self.hand_t1_pos)
            self.hand_t1_pos = tracker_t2_pos

            # when intersection across wall object
            if intersect_info.intersected:
                self.on_enter_wall(self.subject.right_hand_sphere, intersect_info.point, intersect_info.normal)

        elif tracker is self.subject.head_sphere:
            intersect_info = walls.intersect(tracker_t2_pos, self.head_t1_pos)
            self.head_t1_pos = tracker_t2_pos

            # when intersection across wall object trigger warning for to step back into maze
            if intersect_info.intersected:
                self.on_enter_wall(self.subject.head_sphere, intersect_info.point, intersect_info.normal)

    def enter_local_landmark(self, proximity_event):
        """
        Flash screen and fade out

        :param flash_time:
        :param markerstream:
        :return:
        """

        self.scene.flash_quad.flash()

        if proximity_event.sensor is self.maze.maze_start_position.ground:
            self.maze.maze_start_ground.visible(viz.ON)
        else:
            self.maze.maze_end_ground.visible(viz.ON)

        self.local_landmark_hits += 1
        self.log_exp_progress('type:enter_local_landmark;num_local_landmark:' + str(self.local_landmark_hits) + ';')

    def exit_local_landmark(self, proximity_event):

        if proximity_event.sensor is self.maze.maze_start_position.ground:
            self.maze.maze_start_ground.visible(viz.OFF)
        else:
            self.maze.maze_end_ground.visible(viz.OFF)
        self.log_exp_progress('type:exit_local_landmark;')

    def baseline(self):
        # set num_sphere positions of spheres randomly, spheres have to be touched then next sphere appears
        # baselines:
        # 1. spectrum (averaging 90% best 1s windows of the baseline period, has touches and walking but no 'task')
        # 2. ersp/connectivity: reaches without meaning but different visual feedback

        # set height of spheres to head - 20cm
        z_range = 3 # lab restrictions
        x_range = 2 # lab restrictions
        height = self.subject.head_sphere.getPosition()[1] - .2

        # number of spheres to touch
        num_sphere = 7

        self.log_exp_progress('type:baseline_start;')
        self.scene.poi_manager.addTarget(self.subject.right_hand_sphere_target)

        # spawn num_sphere balls and touch them consecutively
        for i in range(num_sphere):

            z_pos = random.randrange(0, 2*z_range+1) - z_range
            x_pos = random.randrange(0, 2*x_range+1) - x_range
            pos = [x_pos, height, z_pos]

            # make a sphere at a random position in the plusminus z and x range
            sphere = vizshape.addSphere(.1)
            sphere.color(viz.YELLOW)
            sphere.setPosition(pos)
            sphere_sensor = vizproximity.addBoundingSphereSensor(sphere)
            self.scene.poi_manager.addSensor(sphere_sensor)

            # yield wait enter hand sphere
            yield vizproximity.waitEnter(sphere_sensor)
            self.log_exp_progress('type:baseline_touch;number:'+str(i+1)+';')
            self.scene.poi_manager.removeSensor(sphere_sensor)
            sphere.remove()

        self.scene.poi_manager.removeTarget(self.subject.right_hand_sphere_target)
        self.log_exp_progress('type:baseline_end;')

    def generate_list_of_controlled_randomized_trials(self, maze, p_id, run):

        #simply update self.trial_list by remaining trials
        self.trial_list = self.trial_list_all[int(p_id)-1]
        if maze == 'all':
            self.trial_list.insert(0, 'I') # add baseline trial
            ix=0
        elif maze == 'I':
            self.trial_list = ['I']
        elif maze == 'L':
            ix = self.trial_list.index('L')
        elif maze == 'Z':
            ix = self.trial_list.index('Z')
        elif maze == 'U':
            ix = self.trial_list.index('U')
        elif maze == 'S':
            ix = self.trial_list.index('S')
    
        self.trial_list = self.trial_list[ix:]
        print self.trial_list			

        if run == 'all':
            self.run_list = [1, 2, 3]
        elif run == '2':
            self.run_list = [2, 3]
        elif run == '3':
            self.run_list = [3]

    def assign_trackers(self, trackers):
        
        # problem is I do not know which is which here, I only know there are 3 trackers differing in z dimension when starting experiment
        tracker0_z = trackers[0].getPosition()[2]
        tracker1_z = trackers[1].getPosition()[2]
        tracker2_z = trackers[2].getPosition()[2]
        
        # get the minimum value in list of all z value of the trackers
        trackers = [tracker0_z, tracker1_z, tracker2_z]
        
        # hand is highest in z dimension (most forward in direction facing right wall when entering into lab)
        self.hand_tracker_id = trackers.index(max(trackers))
        
        # torso is lowest in z dimension (most back)
        self.torso_tracker_id = trackers.index(min(trackers))
        
        # arm is median in z dimension
        self.arm_tracker_id = trackers.index(numpy.median(trackers))

    def start_vr(self):
        hmd = steamvr.HMD()
        if not hmd.getSensor():
            sys.exit('SteamVR HMD not detected')
        viz.link(hmd.getSensor(), viz.MainView)

        # create LSL stream for MoBIlab pos and ori analysis --> ori should be in quaternions
        hmd_stream = self.subject.create_non_phasespace_rigid_body_stream('headRigid', 0)
        # stream 6dof of HMD as pos (x,y,z) and ori(x,y,z,w) --> quaternion
        vizact.onupdate(0, self.subject.update_and_push_rigid_body, viz.MainView, self.subject.head_sphere, hmd_stream)

        #  connecting present controllers
        trackers = steamvr.getTrackerList()
        self.controller = steamvr.getControllerList()[0]
        print self.controller
        tracker_names = ['handRigid', 'armRigid', 'torsoRigid']

        find_out_tracker = vizact.onupdate(0, self.assign_trackers, trackers)
        yield viztask.waitTime(5) # wait two seconds to figure out which tracker is more to the front in z direction = hand tracker
        find_out_tracker.remove()
        
        # create LSL stream for MoBIlab pos and ori analysis --> ori should be in quaternions
        # stream 6dof as pos (x,y,z) and ori(x,y,z,w) --> quaternion
        hand_stream = self.subject.create_non_phasespace_rigid_body_stream(tracker_names[self.hand_tracker_id], 0)
        vizact.onupdate(0, self.subject.update_and_push_rigid_body, trackers[self.hand_tracker_id], self.subject.right_hand_sphere, hand_stream)
        
        # create LSL stream for MoBIlab pos and ori analysis --> ori should be in quaternions
        arm_stream = self.subject.create_non_phasespace_rigid_body_stream(tracker_names[self.arm_tracker_id], 0)
        vizact.onupdate(0, self.subject.update_and_push_rigid_body, trackers[self.arm_tracker_id], None, arm_stream)

        # create LSL stream for MoBIlab pos and ori analysis --> ori should be in quaternions
        torso_stream = self.subject.create_non_phasespace_rigid_body_stream(tracker_names[self.torso_tracker_id], 0)
        vizact.onupdate(0, self.subject.update_and_push_rigid_body, trackers[self.torso_tracker_id], None, torso_stream)

    def trial(self):

        # trial start marker with landmark positions
        start_pos = 'start_pos:' + str(self.maze.start_pos) + ';'
        end_pos = 'end_pos:' + str(self.maze.end_pos) + ';'
        global_pos = 'global_pos:' + str(self.maze.global_landmark.getPosition()) + ';'
        self.log_exp_progress('type:trial_start;' + start_pos + end_pos + global_pos)

        # baseline
        print '!!! BASELINE START !!!'
        yield self.baseline()
        print '!!! BASELINE END -> FIND START !!!'

        # show start of maze and let participant go there
        self.maze.maze_start_sphere.visible(viz.ON)
        self.maze.start_arrow.visible(viz.ON)
        self.maze.maze_start_ground.visible(viz.ON)

        # add to proximity manager
        self.scene.poi_manager.addSensor(self.maze.maze_start_sphere_sensor)
        self.scene.poi_manager.addTarget(self.subject.right_hand_sphere_target)

        # yield wait enter hand sphere
        yield vizproximity.waitEnter(self.maze.maze_start_sphere_sensor)
        self.log_exp_progress('type:arrived_at_start_position;')
        self.maze.maze_start_sphere.visible(viz.OFF)
        self.maze.start_arrow.visible(viz.OFF)
        self.maze.maze_start_ground.visible(viz.OFF)

        # remove from proximity manager
        self.scene.poi_manager.removeSensor(self.maze.maze_start_sphere_sensor)
        self.scene.poi_manager.removeTarget(self.subject.right_hand_sphere_target)

        # wait for experimenter to click window once via remote to start trial
        print '!!! CLICK MOUSE TO START EXPLORATION !!!'
        yield self.hide_inst_continue_left_mouse()
        yield self.scene.countdown(5)  # countdown to start

        ### Trial Procedure Start ###
        self.log_exp_progress('type:navigation_start;')
        start = viz.tick()

        # enable collision
        viz.phys.enable()

        # start intersection check for both head and hand against the maze walls
        self.hand_t1_pos = self.subject.right_hand_sphere.getPosition()
        self.head_t1_pos = self.subject.head_sphere.getPosition()
        hand_feedback = vizact.onupdate(0, self.check_node_intersection, self.subject.right_hand_sphere, self.maze.walls)
        head_feedback = vizact.onupdate(0, self.check_node_intersection, self.subject.head_sphere, self.maze.walls)

        # add head sphere to proximity manager and register callbacks for end and start ground
        self.scene.poi_manager.addTarget(self.subject.head_sphere_target)
        self.scene.poi_manager.addSensor(self.maze.maze_start_position.ground)
        self.scene.poi_manager.addSensor(self.maze.maze_end_position.ground)
        head_landmark_enter = self.scene.poi_manager.onEnter(None, self.enter_local_landmark)
        head_landmark_exit = self.scene.poi_manager.onExit(None, self.exit_local_landmark)

        # [BPA 2019-04-29] make global landmark visible
        self.maze.global_landmark.visible(viz.ON)

        # now wait until subjects found the end of the maze
        yield vizproximity.waitEnter(self.maze.maze_end_position.ground)
        print '!!! END REACHED: POINTING TASK, PARTICIPANT NEEDS TO POINT AND CLICK WITH CONTROLLER !!!'

        # temporarily remove proximity target head while doing the pointing task when sensor is first entered
        self.scene.poi_manager.clearTargets()
        yield self.pointing(start)
        print '!!! POINTED BACK TO START NOW EXPLORE BACK TO START!!!'
        self.scene.poi_manager.addTarget(self.subject.head_sphere_target)

        # then wait till subjects returned to the start position
        yield vizproximity.waitEnter(self.maze.maze_start_position.ground)
        print '!!! START REACHED: RVD & REWALKING TASK COMING UP... PARTICIPANTS NEEDS TO CLICK TRIGGER TO START!!!'
        
        # performance measures for reward and analysis
        end = viz.tick()
        self.duration = end - start
        duration_return = end - self.start_return
        performance = 'type:navigation_end;duration:' + str(round(self.duration, 2)) + \
                      ';total_touches:' + str(self.hand_hits) + \
                      ';duration_return:' + str(round(duration_return, 2)) + ';'
        self.log_exp_progress(performance)

        # remove all the proximity sensors and the target and unregister the callbacks
        self.scene.poi_manager.clearTargets()
        self.scene.poi_manager.clearSensors()
        head_landmark_enter.remove()
        head_landmark_exit.remove()

        # remove wall collisions
        hand_feedback.remove()
        head_feedback.remove()
        
        # reset wall touches
        if self.feedback_hand is not None:
            self.reset_touching()
                
        # [BPA 2019-04-29] remove landmark
        self.scene.toggle_global_landmark(self.maze, "off")

        # show reward for 5 seconds
        self.log_exp_progress('type:reward_start;')
        yield self.scene.reward_feedback(self.head_hits, self.duration, 3)
        self.log_exp_progress('type:reward_end;')

        # start testaufgaben
        self.scene.change_instruction("Es folgen die Testaufgaben.\n"
                                      "weiter durch Klick!")
        yield self.hide_inst_continue_trigger()

        # start spatial tasks with turning around
        print '!!! REORIENTING... !!!'
        yield self.reorient()

        # RVD Task
        yield self.rvd_task()

        # walk maze task
        yield self.walk_maze_task()

        # trial end marker
        self.log_exp_progress('type:trial_end;')
        print '!!! TRIAL END !!!'
        ### Trial Procedure End ###

        if not self.current_maze is 'I' and self.current_trial_run < 3:
            # Beginn next trial mit Baseline
            print '!!! START NEXT RUN WITH N KEY !!!'
            self.scene.change_instruction("Bitte beim Versuchsleiter melden!")
            yield viztask.waitKeyDown('n')
            self.scene.hide_instruction()

    def pause(self):

        if self.current_maze is 'I':
            self.scene.change_instruction("Noch fragen?")
            print '!!! GIBT ES NOCH UNKLARHEITEN? WEITER MIT TASTE W !!!'
        else:
            self.scene.change_instruction("Pause machen?")
            print '!!! PAUSE? START NEXT MAZE WITH W KEY !!!'
        yield viztask.waitKeyDown('w')
        self.scene.hide_instruction()

    def experiment_procedure(self, maze, id, run):

        # figure out which tracker is which to start recording data
        print '!!! WAIT ... !!!'
        yield self.start_vr()

        print '!!! START LABRECORDER DATA COLLECTION AND THEN CLICK MOUSE TO START EXPERIMENT !!!'
        yield self.hide_inst_continue_left_mouse()
        print '!!! EXPERIMENT NOW RUNNING !!!'

        # wait for experimenter to click window once via remote to start trial
        self.push_marker(self.markerstream, 'type:experiment_start')

        # generate trial and run list (still hardcoded but whatever...)
        self.generate_list_of_controlled_randomized_trials(maze, id, run)

        for maze in self.trial_list:
            if maze is 'I': # do only once for I as training
                self.change_experiment_scene(maze)
                self.current_maze = maze
                self.current_trial_run = 1
                yield self.trial()
            else:
                for current_run in self.run_list:
                    self.change_experiment_scene(maze)
                    self.current_maze = maze
                    self.current_trial_run = current_run
                    yield self.trial()

            # after all runs in run_list
            # draw_maze_task after each maze only once; task disables collisions
            yield self.draw_maze_task()
            yield self.pause()

        # end marker
        self.scene.change_instruction("Vielen Dank!\nSie haben den Versuch abgeschlossen.\nBitte melden Sie sich beim Versuchsleiter.")
        self.push_marker(self.markerstream, 'type:experiment_end')
        print '!!! END LABRECORDER DATA COLLECTION !!!'


# setup and schedule vizard main loop. Run this program in Worldviz Vizard IDE.
def create_experiment():
    """
    Creates and sets up the experiment instance

    """

    # start with asking the participant some informations -> use info to create a new instance of class "Subject"
    participant = yield BaseSubject.participant_info()

    # creates the instance of the experiment
    experiment = VisualMaze(participant)

    # starts experimental procedure, i.e. procedural logic of the experiment
    # serves as a fall back in case subject screw up a trial and we must manually restart
    yield experiment.experiment_procedure(participant.maze_config, participant.id, participant.maze_run)

# start vizard main loop and create experiment
viz.go()
viztask.schedule(create_experiment)