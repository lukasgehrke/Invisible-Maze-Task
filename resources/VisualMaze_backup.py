"""
Exemplary instance of the BaseExperiment main class showing the usage of the Worlviz Vizard VR framework at BeMoBIL.

"""

import math
import random
import socket

import viz
import vizact
import vizproximity
import viztask

from BaseExperiment import BaseExperiment
from BaseSubject import BaseSubject
from VisualMazeScene import VisualMazeScene
from resources.trackers.lsl_lib import pylsl as lsl


# todo for experiment checklist:
# - markers (enter/exit, maze units, HED, experiment procedure)
# - add instructions and learn and test trial logic according to sccn/klaus document

# - participant info am anfang pimpen, sachen rausnehmen
# - labrecorder config file

# - rb ids of hands are 1, 2 (0 being the head) hence have to be measured as 1,2 rb in PS master software
# - problem still when entering one wall, entering the second at a corner, leaving the first one while still in the second one, and then reentering the first wall again

class VisualMaze(BaseExperiment):

    def __init__(self, participant, maze_type):

        # call constructor of superclass
        super(VisualMaze, self).__init__(participant)
        self.scene = VisualMazeScene(maze_type, self.subject)

        self.triallist = []

        # todo instruktionen schreiben
        self.visual_maze_instruktionen = {
            'baseline start': 'Zu Beginn wird eine Zusatzmessung aufgenommen.\n'
                              'In fuenf Sekunden geht es automatisch weiter...',
            'baseline end': 'Danke, bitte melden Sie sich jetzt beim Versuchsleiter!',
            'baseline standing': 'Bitte bleiben Sie nun fuer 3 Minuten auf der Stelle stehen.\n'
                                 'Halten Sie Ihre Augen offen und entspannen sich soweit wie moeglich.\n'
                                 'Starten Sie die Messung durch druecken der Taste A.\n'
                                 'Nach Ablauf der Zeit wird eine neue Instruktion erscheinen.',
            'baseline standing end': 'Vielen Dank. Es geht in 5 Sekunden weiter...',
            'drawing end': 'Ihre Zeichnung wurde gespeichert.\n'
                           'In 5 Sekunden geht es weiter...'
        }
        
        self.left_hand_sphere_prox_target = vizproximity.Target(self.subject.left_hand_sphere)

        # add mainview head as proximity target to all proximity managers (corners, maze unit, center spot)
        for prox_manager in self.scene.prox_manager_list:
            prox_manager.addTarget(viz.MainView)
            prox_manager.onEnter(None, self.enter_maze_unit)  # todo test if valid and necessary for all managers
            prox_manager.onExit(None, self.exit_maze_unit)
        
        self.left_hand_sphere_prox_target = vizproximity.Target(self.subject.left_hand_sphere)
        self.scene.convex_corner_proximity_manager.addTarget(self.left_hand_sphere_prox_target)
        self.scene.concave_corner_proximity_manager.addTarget(self.left_hand_sphere_prox_target)
        
        self.right_hand_sphere_prox_target = vizproximity.Target(self.subject.right_hand_sphere)
        self.scene.convex_corner_proximity_manager.addTarget(self.right_hand_sphere_prox_target)
        self.scene.concave_corner_proximity_manager.addTarget(self.right_hand_sphere_prox_target)

        # keys for video recording
        vizact.onkeydown('b', viz.window.startRecording, 'visual_maze_video.avi')
        vizact.onkeydown('e', viz.window.stopRecording)

        # objects handling current state of visual maze experiment
        # wall enter and exit collision events
        self.collide_begin = None
        self.collide_end = None

        # collision event objects
        self.which_wall_enter = None
        self.which_wall_exit = None
        self.which_tracker_enter = None

        # Handling wall events for experiment maze behavior
        # determine in which wall sensor currently collided with, if any
        self.first_wall_left = None
        self.first_collide_event_left = None
        self.second_wall_left = None
        self.second_collide_event_left = None

        self.first_wall_right = None
        self.first_collide_event_right = None
        self.second_wall_right = None
        self.second_collide_event_right = None

        self.axis_diff_first_wall = None
        self.axis_diff_second_wall = None

        # tracker placeholders
        self.left_hand_tracker = None
        self.right_hand_tracker = None
        self.current_wall_head = None

        # placeholders for visual feedback functions
        self.feedback_function_left = None
        self.feedback_function_right = None
        self.feedback_function_head = None

        # fadeout if feedback longer than 2 seconds
        self.feedback_function_left_start_time = 0
        self.feedback_function_right_start_time = 0
        self.elapsed_left_hand = 0
        self.elapsed_right_hand = 0

        # value between 0 and 1 depending on if 30 cm in wall or not
        self.feedback_intensity = None

        # -----------------------------------------------------
        # Bookkeeping variables for behavioral data collection
        # current trial parameters
        # enter times and durations
        self.total_maze_duration = 0  # start_end marker, todo necessary if predefined learn time?
        self.exp_start_time = lsl.local_clock()  # start_end marker
        self.current_maze = None
        self.current_trial_run = None

        # maze unit bookkeeping parameters
        self.current_maze_unit = None
        self.current_maze_unit_enter_time = 0
        self.current_maze_unit_enter_count = 0
        self.duration_maze_unit = 0
        self.visited_maze_units_list = []
        self.maze_unit_progression = 0

        # wall touch bookkeeping parameters
        self.enter_or_exit = ''
        self.corner = ''
        self.total_time_in_wall = 0

        # left hand
        self.enter_wall_time_left_hand = 0
        self.exit_wall_time_left_hand = 0
        self.left_hand_wall_touch_count = 0
        self.left_hand_wall_touch_time_in_wall = 0
        self.left_hand_total_time_in_wall = 0
        self.left_hand_enter_X = 0
        self.left_hand_enter_Y = 0
        self.left_hand_enter_Z = 0
        self.left_hand_exit_X = 0
        self.left_hand_exit_Y = 0
        self.left_hand_exit_Z = 0

        # right hand
        self.enter_wall_time_right_hand = 0
        self.exit_wall_time_right_hand = 0
        self.right_hand_wall_touch_count = 0
        self.right_hand_wall_touch_time_in_wall = 0
        self.right_hand_total_time_in_wall = 0
        self.right_hand_enter_X = 0
        self.right_hand_enter_Y = 0
        self.right_hand_enter_Z = 0
        self.right_hand_exit_X = 0
        self.right_hand_exit_Y = 0
        self.right_hand_exit_Z = 0

        # head
        self.enter_wall_time_head = 0
        self.exit_wall_time_head = 0
        self.head_wall_touch_count = 0
        self.head_wall_touch_time_in_wall = 0
        self.head_total_time_in_wall = 0
        self.head_enter_X = 0
        self.head_enter_Y = 0
        self.head_enter_Z = 0
        self.head_exit_X = 0
        self.head_exit_Y = 0
        self.head_exit_Z = 0

        # remark self.markerstream already exists in super class and is instatiated, use with self.markerstream
        # LSL Stream declaration for begin and end marker
        self.maze_start_end_info = lsl.StreamInfo('MazeStartEnd', 'Markers', 5, 0, 'float32', socket.gethostname())
        self.maze_start_end = lsl.StreamOutlet(self.maze_start_end_info)

        # LSL stream maze unit markers
        self.maze_unit_marker_info = lsl.StreamInfo('MazeUnits', 'MazeBehavior', 1, 0, 'string', socket.gethostname())
        self.maze_unit_marker = lsl.StreamOutlet(self.maze_unit_marker_info)

    def lsl_start_end(self, start=False):
        """

        :param start
        :return:
        """

        if start is True:
            marker = 'start'
        else:
            marker = 'end'

        acquisition_time = lsl.local_clock()
        data = marker, self.current_maze, self.current_trial_run, self.exp_start_time, self.total_maze_duration
        self.maze_start_end.push_sample([data], acquisition_time)

    def lsl_maze_behavior(self, tracker, enter=True):
        """

        :param tracker:
        :param enter:
        :return:
        """
        
        # todo stream online or calculate offline
        #feedback_intensity = 'feedback_intensity:'+self.feedback_intensity+','

        # handle with metadata for channels or define once and then use class instance attributes?
        acquisition_time = lsl.local_clock()

        # create long data string with factor:value pairs and add ',' for string separation
        exp_start = 'exp_start:'+str(self.exp_start_time)+','
        current_maze = 'current_maze:'+str(self.current_maze)+','
        current_trial_run = 'current_trial_run:'+str(self.current_trial_run)+','

        corner = 'corner:'+str(self.corner)+','

        current_wall_enter = 'current_wall:'+str(self.which_wall_enter)+','
        current_wall_exit = 'current_wall:' + str(self.which_wall_exit) + ','
        
        # default values
#        exit_wall_time = 0
#        wall_touch_time_in_wall = 0
#        total_time_in_wall = 0
#        exit_X = 0
#        exit_Y = 0
#        exit_Z = 0

        if tracker == 'left':

            tracker = 'tracker:left,'

            if enter is True:
                enter_exit = 'enter_exit:enter,'
                enter_wall_time = 'enter_wall_time_left_hand:' + str(self.enter_wall_time_left_hand) + ','
                wall_touch_count = 'left_hand_wall_touch_count:' + str(self.left_hand_wall_touch_count) + ','
                enter_X = 'enter_X:'+str(self.left_hand_enter_X)+','
                enter_Y = 'enter_Y:' + str(self.left_hand_enter_Y) + ','
                enter_Z = 'enter_Z:' + str(self.left_hand_enter_Z) + ','

            elif enter is False:
                enter_exit = 'enter_exit:exit,'
                exit_wall_time = 'exit_wall_time_left_hand:'+str(self.exit_wall_time_left_hand)+','
                wall_touch_time_in_wall = 'left_hand_wall_touch_time_in_wall:'+str(self.left_hand_wall_touch_time_in_wall)+','
                total_time_in_wall = 'left_hand_total_time_in_wall:'+str(self.left_hand_total_time_in_wall)+','
                exit_X = 'exit_X:'+str(self.left_hand_exit_X)+','
                exit_Y = 'exit_Y:' + str(self.left_hand_exit_Y) + ','
                exit_Z = 'exit_Z:' + str(self.left_hand_exit_Z) + ','

        elif tracker == 'right':

            tracker = 'tracker:right,'

            if enter is True:
                enter_exit = 'enter_exit:enter,'
                enter_wall_time = 'enter_wall_time_right_hand:' + str(self.enter_wall_time_right_hand) + ','
                wall_touch_count = 'right_hand_wall_touch_count:' + str(self.right_hand_wall_touch_count) + ','
                enter_X = 'enter_X:'+str(self.right_hand_enter_X)+','
                enter_Y = 'enter_Y:' + str(self.right_hand_enter_Y) + ','
                enter_Z = 'enter_Z:' + str(self.right_hand_enter_Z) + ','

            elif enter is False:
                enter_exit = 'enter_exit:exit,'
                exit_wall_time = 'exit_wall_time_right_hand:'+str(self.exit_wall_time_right_hand)+','
                wall_touch_time_in_wall = 'right_hand_wall_touch_time_in_wall:'+str(self.right_hand_wall_touch_time_in_wall)+','
                total_time_in_wall = 'right_hand_total_time_in_wall:'+str(self.right_hand_total_time_in_wall)+','
                exit_X = 'exit_X:'+str(self.right_hand_exit_X)+','
                exit_Y = 'exit_Y:' + str(self.right_hand_exit_Y) + ','
                exit_Z = 'exit_Z:' + str(self.right_hand_exit_Z) + ','
        
        elif tracker == 'head':

            tracker = 'tracker:head,'

            if enter is True:
                
                enter_exit = 'enter_exit:enter,'
                enter_wall_time = 'enter_wall_time_head:'+str(self.enter_wall_time_head)+','
                wall_touch_count = 'head_wall_touch_count:' + str(self.head_wall_touch_count) + ','
                enter_X = 'enter_X:'+str(self.head_enter_X)+','
                enter_Y = 'enter_Y:' + str(self.head_enter_Y) + ','
                enter_Z = 'enter_Z:' + str(self.head_enter_Z) + ','

            elif enter is False:
                
                enter_exit = 'enter_exit:exit,'
                exit_wall_time = 'exit_wall_time_head:'+str(self.exit_wall_time_head)+','
                wall_touch_time_in_wall = 'head_wall_touch_time_in_wall:'+str(self.head_wall_touch_time_in_wall)+','
                total_time_in_wall = 'head_total_time_in_wall:'+str(self.head_total_time_in_wall)+','
                exit_X = 'exit_X:'+str(self.head_exit_X)+','
                exit_Y = 'exit_Y:' + str(self.head_exit_Y) + ','
                exit_Z = 'exit_Z:' + str(self.head_exit_Z) + ','

        if enter is True:
            data_string_enter = exp_start+current_maze+current_trial_run+current_wall_enter+corner+tracker+enter_exit+enter_wall_time+wall_touch_count+enter_X+enter_Y+enter_Z
            self.markerstream.push_sample([data_string_enter], acquisition_time)
        elif enter is False:
            data_string_exit = exp_start+current_maze+current_trial_run+current_wall_exit+corner+tracker+enter_exit+exit_wall_time+wall_touch_time_in_wall+total_time_in_wall+exit_X+exit_Y+exit_Z
            self.markerstream.push_sample([data_string_exit], acquisition_time)

    def generate_list_of_controlled_randomized_trials(self, triallist, mazes, trial_runs):
        """

        :param mazes:
        :param trial_runs:
        :return:
        """

        # maybe shuffle mazes before adding trial_runs 1:3
        random.shuffle(mazes)

        for maze in mazes:
            triallist.append((maze, trial_runs[0]))

        random.shuffle(mazes)
        for maze in mazes:
            triallist.append((maze, trial_runs[1]))

        random.shuffle(mazes)
        for maze in mazes:
            triallist.append((maze, trial_runs[2]))

        # for maze in mazes:
        #     for run in trial_runs:
        #             triallist.append((maze, run))

        print triallist
        return triallist

    def draw_maze_task(self, draw_device, maze, run):
        """

        :param draw_device:
        :return:
        """

        # first remove collide events and feedback opacity so subjects do not get any feedback at the hands
        try:
            self.feedback_function_left.remove()
            self.feedback_function_right.remove()
            self.feedback_function_head.remove()
        except:
            print 'feedback functions do not exist!'
        
        # remove collide events, todo must be enabled again for next trial
        self.collide_begin.setEnabled(False)
        self.collide_end.setEnabled(False)
        self.scene.feedback_sphere_left.alpha(0)
        self.scene.feedback_sphere_right.alpha(0)

        # direct subjects to the center of the room
        self.scene.move_to_center(self.scene.poi_manager)

        self.scene.change_instruction("Please draw the maze using your right arm.\n"
                                      "Click and hold left mousebutton to draw.\n"
                                      "Click right mousebutton to erase drawing.\n"
                                      "Click middle mousebutton to save the drawing when finished.\n\n"
                                      "Press left mousebutton once to start!")

        # todo wie soll man malen -> instruktion:
        # - arm ausgestreckt
        # - evtl. roten Kasten hinmalen?
        # - beim foto machen probanden instruieren das gemalt im Blick zu haben
        self.scene.change_instruction("")

        yield viztask.waitMouseDown(viz.MOUSEBUTTON_LEFT)
        self.scene.hide_instruction()

        # enable drawing functionality
        self.subject.right_hand_sphere.alpha(1)
        self.subject.right_hand_sphere.color(viz.RED)
        viz.link(self.subject.right_hand_sphere, self.scene.draw_tool)

        # drawing update function called every frame and handling states of input device
        self.scene.draw_tool.setUpdateFunction(self.draw)

        # wait until drawing is saved and continue with the experiment
        yield viztask.waitMouseDown(viz.MOUSEBUTTON_MIDDLE)
        filename = 'sketchmap_' + str(self.current_maze) + '_' + str(self.current_trial_run)
        viz.window.screenCapture(filename + '.bmp')

        self.scene.change_instruction("")
        yield viztask.waitTime(5)

        # remove drawing and draw_tool
        self.scene.draw_tool.clear()

    @staticmethod
    def draw(draw_tool):
        """
        update code for pencil

        :param draw_tool:
        :param maze: name of maze learned in the current trial
        :param run: current run of this maze
        :return:
        """

        state = viz.mouse.getState()
        if state & viz.MOUSEBUTTON_LEFT:
            draw_tool.draw()
        if state & viz.MOUSEBUTTON_RIGHT:
            draw_tool.clear()

    def on_enter_wall(self, collide_event):
        """

        :param collide_event:
        :return:
        """

        enter_wall_time = lsl.local_clock()
        self.which_tracker_enter = collide_event.obj2
        self.which_wall_enter = collide_event.obj1

        # todo add to marker stream test if collide_event.obj1.name works
        #print self.which_wall_enter.name
        self.enter_or_exit = 'enter'

        # design decision to handle conflicts at dual walls at convex and concave corners of the maze.
        # each tracker (hand(s) and head) can only be in 1 wall at the time
        # to make sure only 1 event is further handled the walls have a slight offset at positions where they overlap
        if self.which_tracker_enter is self.subject.left_hand_sphere:

            print 'left hand'
            self.left_hand_tracker = self.which_tracker_enter

            # Wenn vor Eintritt noch in keiner Wand gewesen, rufe feedback function an der wand auf mit der collision
            # wenn aktuell nicht in einer ecke dann ist die erste wand immer die aktuelle
            if self.first_wall_left is None:
                print 'one wall'

                # update bookkeeping variables 1 wall enter left hand
                # codiere ecken mit no / convex / concave:
                self.corner = 'no'
                self.left_hand_wall_touch_count += 1
                self.enter_wall_time_left_hand = enter_wall_time
                self.left_hand_enter_X = collide_event.pos[0]
                self.left_hand_enter_Y = collide_event.pos[1]
                self.left_hand_enter_Z = collide_event.pos[2]

                # params for feedback
                self.first_wall_left = self.which_wall_enter
                self.first_collide_event_left = collide_event

                # call feedback function NOT in corner mode
                self.feedback_function_left_start_time = viz.tick()
                self.feedback_function_left = vizact.onupdate(0, self.wall_touch, None, self.left_hand_tracker,
                                                              self.first_wall_left, None,
                                                              self.first_collide_event_left.pos, None)#markerstream
            else:

                print 'second wall'
                print self.scene.concave_corner_proximity_manager.getActiveTargets()
                print len(self.scene.concave_corner_proximity_manager.getActiveTargets())
                print self.scene.convex_corner_proximity_manager.getActiveTargets()
                print len(self.scene.convex_corner_proximity_manager.getActiveTargets())
                
                # design decision:
                # wenn neue wand dazu kommt -> pruefe ob convexe ecke oder concave ecke -> rufe entsprechende feedback function
                # onupdate auf die entweder den groesseren beider werte nimmt (convex) oder die neue wand ignoriert (concave)
                # 1. convex corner: use bigger value (axis_diff computation on both walls) of both walls touched
                if len(self.scene.concave_corner_proximity_manager.getActiveTargets()) > 0:
                    # ignore concave corners
                    # update bookkeeping variables concave corner enter left hand
                    self.corner = 'concave'
                    print 'concave'
                    
                elif len(self.scene.convex_corner_proximity_manager.getActiveTargets()) > 0:
                    print 'convex'
                    self.second_wall_left = self.which_wall_enter
                    self.second_collide_event_left = collide_event

                    # remove function self.feedback_function_left and create new with corner mode
                    self.feedback_function_left.remove()

                    # call feedback function in 'corner' mode
                    self.feedback_function_left_start_time = viz.tick()
                    self.feedback_function_left = vizact.onupdate(0, self.wall_touch, 'convex',
                                                                  self.left_hand_tracker,
                                                                  self.first_wall_left,
                                                                  self.second_wall_left,
                                                                  self.first_collide_event_left.pos,
                                                                  self.second_collide_event_left.pos)#markerstream

                    # update bookkeeping variables 1 wall enter left hand
                    self.corner = 'convex'

            self.lsl_maze_behavior('left', enter=True)

        elif self.which_tracker_enter is self.subject.right_hand_sphere:
            
            print 'right hand'
            self.right_hand_tracker = self.which_tracker_enter

            if self.first_wall_right is None:
                
                print 'first wall'

                # update bookkeeping variables 1 wall enter right hand
                # codiere ecken mit no / convex / concave:
                self.corner = 'no'
                self.right_hand_wall_touch_count += 1
                self.enter_wall_time_right_hand = enter_wall_time
                self.right_hand_enter_X = collide_event.pos[0]
                self.right_hand_enter_Y = collide_event.pos[1]
                self.right_hand_enter_Z = collide_event.pos[2]

                # feedback params
                self.first_wall_right = self.which_wall_enter
                self.first_collide_event_right = collide_event

                # call feedback function not in corner mode
                self.feedback_function_right_start_time = viz.tick()
                self.feedback_function_right = vizact.onupdate(0, self.wall_touch, None, self.right_hand_tracker,
                                                              self.first_wall_right, None,
                                                              self.first_collide_event_right.pos, None)
            else:

                print 'second wall'
                # design decision:
                # wenn neue wand dazu kommt -> pruefe ob convexe ecke oder concave ecke -> rufe entsprechende feedback function
                # onupdate auf die entweder den groesseren beider werte nimmt (convex) oder die neue wand ignoriert (concave)
                # 1. convex corner: use bigger value (axis_diff computation on both walls) of both walls touched
                if len(self.scene.concave_corner_proximity_manager.getActiveTargets()) > 0:
                    # ignore concave corners
                    # update bookkeeping variables concave corner enter left hand
                    print 'concave'
                    self.corner = 'concave'

                elif len(self.scene.convex_corner_proximity_manager.getActiveTargets()) > 0:
                    self.second_wall_right = self.which_wall_enter
                    self.second_collide_event_right = collide_event

                    self.enter_concave_corner_time_right_hand = enter_wall_time

                    # remove function self.feedback_function_left and create new with corner mode
                    self.feedback_function_right.remove()

                    # call feedback function in 'corner' mode
                    self.feedback_function_right_start_time = viz.tick()
                    self.feedback_function_right = vizact.onupdate(0, self.wall_touch, 'convex',
                                                                  self.right_hand_tracker,
                                                                  self.first_wall_right,
                                                                  self.second_wall_right,
                                                                  self.first_collide_event_right.pos,
                                                                  self.second_collide_event_right.pos)

                    # update bookkeeping variables 1 wall enter left hand
                    self.corner = 'convex'
                    print 'convex'

            self.lsl_maze_behavior('right', enter=True)

        elif self.which_tracker_enter is self.subject.head_sphere:

            if self.current_wall_head is None:

                # update bookkeeping variables 1 wall enter right hand
                # codiere ecken mit no / convex / concave:
                self.corner = 'no'
                self.head_wall_touch_count += 1
                self.enter_wall_time_head = enter_wall_time
                self.head_enter_X = collide_event.pos[0]
                self.head_enter_Y = collide_event.pos[1]
                self.head_enter_Z = collide_event.pos[2]

                self.current_wall_head = self.which_wall_enter
                self.feedback_function_head = vizact.onupdate(0, self.wall_touch, None, self.which_tracker_enter,
                                                            self.which_wall_enter, None, collide_event.pos, None)
            else:
                return

            self.lsl_maze_behavior('head', enter=True)

        # ein LSL data stream push am ende des onEnter der alle aktuellen und geupdateten parameter pushed, so muss
        # nur sichergestellt werden, dass ALLE Klassenparameter geupdatet werden
        # durch die aktuellen zustaende der klassenvariablen lassen sich auch einfach online Masse (zB critical slope
        # Abnahme der wall touches und zunahme der velocity) berechnen

    def on_exit_wall(self, collide_event):
        """

        :param collide_event:
        :return:
        """

        exit_wall_time = lsl.local_clock()
        self.which_wall_exit = collide_event.obj1
        which_tracker_exited = collide_event.obj2

        self.enter_or_exit = 'exit'

        # design decision to allow a tracker to be in only 1 wall at the time
        # delete feedback onupdate function and set feedback to be invisible
        # test if exists, then remove. May not exist in the beginning of experiment when subjects enter from outside
        if which_tracker_exited is self.subject.left_hand_sphere:

            # variable needed to compute fade out values if feedback_duration exceeds 2 seconds
            self.elapsed_left_hand = None

            # if only 1 wall is touched and subsequently exited
            if self.which_wall_exit is self.first_wall_left:

                # destroy feedback if only one wall was touched
                self.first_wall_left = None
                try:
                    self.feedback_function_left.remove()
                except:
                    print 'feedback function does not exist'
                self.scene.feedback_sphere_left.color(viz.WHITE)
                self.scene.feedback_sphere_left.alpha(0)

                # continue with feedback along second wall if first wall was exited = convex corner case
                if self.second_wall_left is not None:

                    # feedback function an zweiter wand wird fortgesetzt bzw. neu aufgerufen mit werten aus enter event
                    # zweite wand wird zu erster wand
                    self.feedback_function_left = vizact.onupdate(0, self.wall_touch, None, self.left_hand_tracker,
                                                                  self.second_wall_left, None,
                                                                  self.second_collide_event_left.pos, None)
                    self.first_wall_left = self.second_wall_left
                    self.second_wall_left = None
            if self.which_wall_exit is self.second_wall_left:

                self.second_wall_left = None
                try:
                    self.feedback_function_left.remove()
                except:
                    print 'feedback function does not exist'
                self.scene.feedback_sphere_left.color(viz.WHITE)
                self.scene.feedback_sphere_left.alpha(0)

                # continue with feedback along first wall if second wall was exited
                if self.first_wall_left is not None:
                    # feedback function an zweiter wand wird fortgesetzt bzw. neu aufgerufen mit werten aus enter event
                    self.feedback_function_left = vizact.onupdate(0, self.wall_touch, None, self.left_hand_tracker,
                                                                  self.first_wall_left, None,
                                                                  self.first_collide_event_left.pos, None)

            # update bookkeeping variables
            # update exit markers only if hand is currently not in a wall, hence an actual wall exit occured
            if self.first_wall_left is None and self.second_wall_left is None:

                self.exit_wall_time_left_hand = exit_wall_time
                self.left_hand_wall_touch_time_in_wall = self.exit_wall_time_left_hand - self.enter_wall_time_left_hand
                self.left_hand_total_time_in_wall += self.left_hand_wall_touch_time_in_wall
                self.total_time_in_wall += self.left_hand_wall_touch_time_in_wall
                self.left_hand_exit_X = collide_event.obj2.getPosition()[0]
                self.left_hand_exit_Y = collide_event.obj2.getPosition()[1]
                self.left_hand_exit_Z = collide_event.obj2.getPosition()[2]

            self.lsl_maze_behavior('left', enter=False)

        elif which_tracker_exited is self.subject.right_hand_sphere:

            self.elapsed_right_hand = None

            # Checking the convex corner cases
            # if only 1 wall is touched and subsequently exited
            if self.which_wall_exit is self.first_wall_right:

                # destroy feedback if only one wall was touched
                self.first_wall_right = None
                try:
                    self.feedback_function_right.remove()
                except:
                    print 'feedback function does not exist'
                self.scene.feedback_sphere_right.color(viz.WHITE)
                self.scene.feedback_sphere_right.alpha(0)

                # continue with feedback along second wall if first wall was exited
                if self.second_wall_right is not None:
                    # feedback function an zweiter wand wird fortgesetzt bzw. neu aufgerufen mit werten aus enter event
                    self.feedback_function_right = vizact.onupdate(0, self.wall_touch, None, self.right_hand_tracker,
                                                                  self.second_wall_right, None,
                                                                  self.second_collide_event_right.pos, None)
                    self.first_wall_right = self.second_wall_right
                    self.second_wall_right = None
            if self.which_wall_exit is self.second_wall_right:

                self.second_wall_right = None
                try:
                    self.feedback_function_right.remove()
                except:
                    print 'feedback function does not exist'
                self.scene.feedback_sphere_right.color(viz.WHITE)
                self.scene.feedback_sphere_right.alpha(0)

                # continue with feedback along first wall if second wall was exited
                if self.first_wall_right is not None:
                    # feedback function an zweiter wand wird fortgesetzt bzw. neu aufgerufen mit werten aus enter event
                    self.feedback_function_right = vizact.onupdate(0, self.wall_touch, None, self.right_hand_tracker,
                                                                  self.first_wall_right, None,
                                                                  self.first_collide_event_right.pos, None)

            # update bookkeeping variables
            # update exit markers only if hand is currently not in a wall, hence an actual wall exit occured
            if self.first_wall_right is None and self.second_wall_right is None:
                self.exit_wall_time_right_hand = exit_wall_time
                self.right_hand_wall_touch_time_in_wall = self.exit_wall_time_right_hand - self.enter_wall_time_right_hand
                self.right_hand_total_time_in_wall += self.right_hand_wall_touch_time_in_wall
                self.total_time_in_wall += self.right_hand_wall_touch_time_in_wall
                self.right_hand_exit_X = collide_event.obj2.getPosition()[0]
                self.right_hand_exit_Y = collide_event.obj2.getPosition()[1]
                self.right_hand_exit_Z = collide_event.obj2.getPosition()[2]

            self.lsl_maze_behavior('right', enter=False)

        elif which_tracker_exited is self.subject.head_sphere:
            self.current_wall_head = None
            try:
                self.feedback_function_head.remove()
            except:
                print 'feedback function does not exist'
            self.scene.warning.visible(viz.OFF)
            self.scene.hide_instruction()

            # update bookkeeping variables
            # update exit markers only if hand is currently not in a wall, hence an actual wall exit occured
            self.exit_wall_time_head = exit_wall_time
            self.head_wall_touch_time_in_wall = self.exit_wall_time_head - self.enter_wall_time_head
            self.head_total_time_in_wall += self.head_wall_touch_time_in_wall
            self.total_time_in_wall += self.head_wall_touch_time_in_wall
            self.head_exit_X = collide_event.obj2.getPosition()[0]
            self.head_exit_Y = collide_event.obj2.getPosition()[1]
            self.head_exit_Z = collide_event.obj2.getPosition()[2]

        self.lsl_maze_behavior('head', enter=False)

    def wall_touch(self, corner_type, tracker, wall1, wall2, collide_event_pos1, collide_event_pos2):
        """

        :param tracker:
        :param wall:
        :param collide_event_pos:
        :param markerstream:
        :return:
        """

        # 1. set position of visual feedback to the position of the tracker
        tracker_pos = tracker.getPosition()

        # 2. set visual properties based on difference between tracker position and wall collision point
        # either in x or z direction depending on orientation of the collided-with wall
        if wall1.orientation == 'z':
            axis_diff = tracker_pos[2] - collide_event_pos1[2]
        elif wall1.orientation == 'x':
            axis_diff = tracker_pos[0] - collide_event_pos1[0]
        else:
            print 'Wall orientation unknown'
        axis_diff = math.fabs(axis_diff)
        self.axis_diff_first_wall = axis_diff

        # 2.1. if currently in a convex corner, calculate feedback values for both walls and proceed with bigger value
        if corner_type == 'convex':

            # second wall only exists when in convex corners
            if wall2.orientation == 'z':
                axis_diff = tracker_pos[2] - collide_event_pos2[2]
            elif wall2.orientation == 'x':
                axis_diff = tracker_pos[0] - collide_event_pos2[0]
            else:
                print 'Wall orientation unknown'
            self.axis_diff_second_wall = math.fabs(axis_diff)

            # both values exist, since collision with both walls only occurs in corners
            if self.axis_diff_first_wall > self.axis_diff_second_wall:
                axis_diff = self.axis_diff_first_wall
            else:
                axis_diff = self.axis_diff_second_wall

        # 3.1 change opacity and scale if hand entered a wall
        if tracker is self.subject.left_hand_sphere:

            self.scene.feedback_sphere_left.setPosition(tracker_pos)
            self.scene.feedback_sphere_left.color(viz.WHITE)

            if axis_diff < 0.3:
                self.scene.feedback_sphere_left.alpha(axis_diff / 0.3)
                self.scene.feedback_sphere_left.setScale([axis_diff * 5, axis_diff * 5, axis_diff * 5])
            else:
                # change color to red if larger than 0.3
                self.scene.feedback_sphere_left.color(viz.RED)
                self.scene.feedback_sphere_left.alpha(1)
                self.scene.feedback_sphere_left.setScale([1.5, 1.5, 1.5])

            feedback_duration = viz.tick() - self.feedback_function_left_start_time
            if feedback_duration > 3:
                self.scene.feedback_sphere_left.alpha(0)
                self.elapsed_left_hand = None
            
            elif feedback_duration > 2:

                self.scene.feedback_sphere_left.setPosition(tracker_pos)
                self.scene.feedback_sphere_left.color(viz.BLUE)
                
                if self.elapsed_left_hand is None:
                    self.elapsed_left_hand = viz.getFrameNumber()

                # calculate elapsed parameter and set alpha of sphere to elaps
                increasing_val = (viz.getFrameNumber()+1) - self.elapsed_left_hand
                decreasing_alpha = 1.0 / float(increasing_val)
                self.scene.feedback_sphere_left.alpha(decreasing_alpha)

            return axis_diff

        elif tracker is self.subject.right_hand_sphere:

            self.scene.feedback_sphere_right.setPosition(tracker_pos)
            self.scene.feedback_sphere_right.color(viz.WHITE)

            if axis_diff < 0.3:
                self.scene.feedback_sphere_right.alpha(axis_diff / 0.3)
                self.scene.feedback_sphere_right.setScale([axis_diff * 5, axis_diff * 5, axis_diff * 5])
            else:
                self.scene.feedback_sphere_right.color(viz.RED)
                self.scene.feedback_sphere_right.alpha(1)
                self.scene.feedback_sphere_right.setScale([1.5, 1.5, 1.5])

            feedback_duration = viz.tick() - self.feedback_function_right_start_time
            if feedback_duration > 3:
                self.scene.feedback_sphere_right.alpha(0)
                self.elapsed_right_hand = None
            
            elif feedback_duration > 2:

                self.scene.feedback_sphere_right.setPosition(tracker_pos)
                self.scene.feedback_sphere_right.color(viz.BLUE)
                
                if self.elapsed_right_hand is None:
                    self.elapsed_right_hand = viz.getFrameNumber()

                # calculate elapsed parameter and set alpha of sphere to elaps
                increasing_val = (viz.getFrameNumber()+1) - self.elapsed_right_hand
                decreasing_alpha = 1.0 / float(increasing_val)
                self.scene.feedback_sphere_right.alpha(decreasing_alpha)
                    
            return axis_diff

        # 3.2 turn on a red warning and show an instruction to move back
        elif tracker is self.subject.head_sphere:

            self.scene.warning.visible(viz.ON)
            self.scene.warning.setScale([axis_diff*10, axis_diff*10, axis_diff*10])
            self.scene.change_instruction('You are leaving the maze!\nPlease take a step back until this message disappears!')

    def enter_maze_unit(self, proximity_event):
        """
        Function for bookkeeping of subjects maze trajectory

        """

        acquisition_time = lsl.local_clock()

        if proximity_event.manager is self.scene.maze_unit_proximity_manager:
            for elem in self.scene.maze.maze_units_list:
                if elem.ground is proximity_event.sensor:

                    # 1. lsl push maze markers
                    self.current_maze_unit = elem.name
                    self.current_maze_unit_enter_count += 1
                    self.current_maze_unit_enter_time = lsl.local_clock()
                    self.duration_maze_unit = None

                    current_state = 'current_state:entered,'
                    current_maze = 'current_maze:' + str(self.current_maze) + ','
                    current_trial_run = 'current_trial_run:' + str(self.current_trial_run) + ','
                    current_maze_unit = 'current_maze_unit:' + str(self.current_maze_unit) + ','
                    current_maze_unit_enter_count = 'current_maze_unit_enter_count:' + str(self.current_maze_unit_enter_count) + ','
                    current_maze_unit_enter_time = 'current_maze_unit_enter_time:' + str(self.current_maze_unit_enter_time) + ','
                    duration_maze_unit = 'duration_maze_unit:' + str(self.duration_maze_unit) + ','

                    data = current_state+current_maze+current_trial_run+current_maze_unit+current_maze_unit_enter_count+current_maze_unit_enter_time+duration_maze_unit
                    self.maze_unit_marker.push_sample([data], acquisition_time)

                    # 2. check if maze elem already in list of visited elem -> new maze unit decovered
                    if elem.name not in self.visited_maze_units_list:
                        self.visited_maze_units_list.append(elem.name)

        # 3. maze unit prox manager calculate maze progression if all sensors have been active at least once
        # maybe quantify maze progression in % of maze units activated for a given maze layout
        self.maze_unit_progression = len(self.visited_maze_units_list) / self.scene.maze.path_length

    def exit_maze_unit(self, collision_event):
        """
        Function for bookkeeping of subjects maze trajectory

        """

        acquisition_time = lsl.local_clock()

        for elem in self.scene.maze.maze_units_list:
            if elem.ground is collision_event.sensor:

                # 1. lsl push maze markers
                self.current_maze_unit = elem.name
                current_maze_unit_exit_time = lsl.local_clock()
                self.duration_maze_unit = current_maze_unit_exit_time - self.current_maze_unit_enter_time

                current_state = 'current_state:exited,'
                current_maze = 'current_maze:' + str(self.current_maze) + ','
                current_trial_run = 'current_trial_run:' + str(self.current_trial_run) + ','
                current_maze_unit = 'current_maze_unit:' + str(self.current_maze_unit) + ','
                current_maze_unit_enter_count = 'current_maze_unit_enter_count:' + str(
                    self.current_maze_unit_enter_count) + ','
                current_maze_unit_exit_time = 'current_maze_unit_exit_time:' + str(current_maze_unit_exit_time) + ','
                duration_maze_unit = 'duration_maze_unit:' + str(self.duration_maze_unit) + ','

                visited_maze_units = 'visited_maze_units:' + str(len(self.visited_maze_units_list)) + ','
                maze_unit_progression = 'maze_unit_progression' + str(self.maze_unit_progression) + ','

                data = current_state+current_maze+current_trial_run+current_maze_unit+current_maze_unit_enter_count+current_maze_unit_exit_time+duration_maze_unit+visited_maze_units+maze_unit_progression
                self.maze_unit_marker.push_sample([data], acquisition_time)

    def calculate_reward(self):
        pass

    def baseline_measurement(self, markerstream, duration=None):
        """
        Standing baseline measurement for BeMoBIL experiments.

        :param markerstream: LSL markerstream for experimental procedure markers.
        :param duration: Baseline duration, default 3 minutes
        :return:
        """

        self.scene.change_instruction(self.visual_maze_instruktionen['baseline start'])
        self.markerstream.push_sample([str(self.HED_tag_dictionary['instruction on'])])
        yield viztask.waitTime(10)

        self.scene.change_instruction(self.visual_maze_instruktionen['baseline standing'])
        self.markerstream.push_sample([str(self.HED_tag_dictionary['instruction on'])])
        yield viztask.waitTime(20)
        self.scene.hide_instruction()
        self.markerstream.push_sample([str(self.HED_tag_dictionary['instruction off'])])
        self.markerstream.push_sample([str(self.HED_tag_dictionary['standing baseline start'])])

        if duration is not None:
            yield viztask.waitTime(duration)
        else:
            yield viztask.waitTime(180)

        self.markerstream.push_sample([str(self.HED_tag_dictionary['standing baseline end'])])
        self.scene.change_instruction(self.visual_maze_instruktionen['baseline standing end'])
        self.markerstream.push_sample([str(self.HED_tag_dictionary['instruction on'])])

        yield viztask.waitTime(10)
        self.scene.hide_instruction()
        self.markerstream.push_sample([str(self.HED_tag_dictionary['instruction off'])])

    def learn_trial(self):
        """
        To make familiar with wall feedback, present a wall in front of subject to try out the touch feedback as well
        as the drawing functionality

        :return:
        """
        
        self.scene.change_instruction("Um mit dem Lerndurchgang zu beginnen,\n"
                                      "werden Sie nun zu der gelben Kugel gef?hrt.")
                                        

        # 1. bring subject to center of the room (phasespace [0, 0, 0]) facing to the wall next to vive lab
        self.scene.poi_manager.addSensor(self.scene.center_sensor)
        self.scene.poi_manager.addTarget(viz.MainView)
        self.scene.center_sphere.visible(viz.ON)

        # wait until subjects enter proximity sensor
        if self.scene.center_sensor not in self.scene.poi_manager.getActiveSensors():
            yield vizproximity.waitEnter(self.scene.center_sensor)
            self.scene.center_sphere.visible(viz.OFF)

        # setup things for learn session
        self.scene.poi_manager.addTarget(self.subject.left_hand_sphere)
        self.scene.poi_manager.addTarget(self.subject.right_hand_sphere)

        from Wall import Wall
        learn_wall = Wall('learn_wall', wall_length=4, wall_height=4, wall_depth=1, orientation='z', position=[0, 2, 1],
                          visible=False)

        learn_wall.wall_object.alpha(1)
        learn_wall.wall_object.color(viz.RED)

        self.scene.change_instruction("Ca. 1m vor Ihnen befindet sich nun eine Wand.\n"
                                      "Schauen Sie sich diese Wand einmal an.\n"
                                      "Diese Wand wird ausgeblendet nachdem Sie Ruecksprache\n"
                                      "mit dem Experimentator gehalten haben.\n\n"
                                      "Bitte sagen Sie dem Experimentator, dass Sie fortfahren moechten!")

        # experimenter continues with button press after talking to subject
        yield viztask.waitMouseDown(viz.MOUSEBUTTON_LEFT)
        self.scene.hide_instruction()
        learn_wall.wall_object.alpha(0)
        
        # register collide events to training wall
        # node3d collision callback handling
        self.collide_begin = vizact.addCallback(viz.COLLIDE_BEGIN_EVENT, self.on_enter_wall)
        self.collide_end = vizact.addCallback(viz.COLLIDE_END_EVENT, self.on_exit_wall)

        # wall touch feedback training
        first_wall_touch = self.scene.add_sphere('first_wall_touch', 0.05, viz.YELLOW, [0,1.6, 0.8], viz.ON, True, 1)
        self.scene.poi_manager.addSensor(first_wall_touch.sensor)

        self.scene.change_instruction("Sie sehen nun vor Ihnen eine gelbe Kugel.\n\n"
                                      "Warten Sie bis diese Nachricht ausgeblendet ist und\n"
                                      "beruehren die Kugel mit Ihrer rechten Hand!")
        yield viztask.waitTime(10)
        self.scene.hide_instruction()

        # wait until subjects enter proximity sensor
        yield vizproximity.waitEnter(first_wall_touch.sensor, self.subject.right_hand_sphere)
        self.scene.change_instruction("Bei Naeherung an die verdeckte Wand erscheint\n"
                                      "eine weisse Kugel an der Stelle Ihrer Hand!\n"
                                      "Diese weisse Kugel wird groesser und sichtbarer\n"
                                      "je naeher Sie der Wand kommen.")
        yield viztask.waitTime(10)
        self.scene.change_instruction("Nach 2 Sekunden verschwindet die weisse Kugel.\n"
                                      "Dann sind Sie gefordert erneut nach der Wand zu tasten!\n"
                                      "Beruehren Sie die Kugel nun mit Ihrer linken Hand\n"
                                      "nachdem diese Nachricht ausgeblendet ist!")
        yield viztask.waitTime(10)
        yield vizproximity.waitEnter(first_wall_touch.sensor, self.subject.left_hand_sphere)
        first_wall_touch.visible(viz.OFF)

        # maximunm wall depth collision training
        max_wall_depth = self.scene.add_sphere('max_wall_depth', 0.1, viz.YELLOW, [0, 1.6, 1], viz.ON, True, 1)
        self.scene.poi_manager.addSensor(max_wall_depth.sensor)
        self.scene.change_instruction("Eine neue gelbe Kugel ist eingeblendet.\n"
                                      "Versuchen Sie diese Kugel nun mit beiden Haend zu beruehren,\n"
                                      "nachdem diese Nachricht ausgeblendet ist!")
        viztask.waitTime(10)
        self.scene.hide_instruction()

        # wait until subjects enter proximity sensor
        yield vizproximity.waitEnter(max_wall_depth.sensor, self.subject.left_hand_sphere)
        self.scene.change_instruction("Wenn Sie durch die Wand durchgreifen wird die weisse Kugel rot.\n"
                                      "Bitte versuchen Sie dies zu vermeiden.")
        viztask.waitTime(10)
        max_wall_depth.visible(viz.OFF)

        # head collision feedback training
        head_test = self.scene.add_sphere('head_test', 0.1, viz.YELLOW, [0, 1.6, 1], viz.ON, True, 1)
        self.scene.poi_manager.addSensor(head_test.sensor)
        self.scene.change_instruction("Eine neue gelbe Kugel ist eingeblendet.\n"
                                      "Bitte laufen Sie nun einmal zu der gelben Kugel\n"
                                      "und beruehren sie mit Ihrem Kopf,\n"
                                      "nachdem diese Nachrich ausgblendet ist!")
        yield viztask.waitTime(10)
        self.scene.hide_instruction()
        
        # wait until subjects enter proximity sensor
        yield vizproximity.waitEnter(head_test.sensor, self.subject.left_hand_sphere)
        head_test.visible(viz.OFF)
        
        self.scene.change_instruction("Wenn Sie mit Ihrem Kopf in die Wand geraten\n"
                                      "wird eine rote Kugel direkt in Ihrem Sichtfeld eingeblendet.\n"
                                      "Diese Kugel wird groesser je weiter Sie in die Wand geraten.\n"
                                      "Sie werden zus?tzlich aufgefordert zurueck zu gehen!")

        yield viztask.waitTime(10)
        self.scene.change_instruction("Sie haben dieses Training abgeschlossen.\n"
                                      "Zum Ueben haben Sie nun 30 Sekunden Zeit\n"
                                      "die vor Ihnen liegende Wand etwas zu ertasten!")
        yield viztask.waitTime(10)
        self.scene.hide_instruction()
        yield viztask.waitTime(30)

        # 1. move to center_spot # and todo get a reward (ball sphere linked to head or play sound)


        # 2 minute Time to learn wall touch simulation
        yield viztask.waitTime(120)

    def test_trial(self, maze, run):
        """

        :param maze:
        :param run:
        :return:
        """

        # todo add to trial logic in test trials
        # gamification with start/end point

        # 1. disorient subject in lab space
        # 2. have subject move to start marker of this maze

        # wait until subjects enter proximity sensor
        #if self.scene.maze.maze_start_position.ground not in self.scene.poi_manager.getActiveSensors():
         #   yield vizproximity.waitEnter(self.scene.maze.maze_start_position.ground)

        # node3d collision callback handling
        self.collide_begin = vizact.addCallback(viz.COLLIDE_BEGIN_EVENT, self.on_enter_wall)
        self.collide_end = vizact.addCallback(viz.COLLIDE_END_EVENT, self.on_exit_wall)

#        if run == 1:
#            yield viztask.waitTime(480)
#        elif run == 2:
#            yield viztask.waitTime(300)
#        elif run == 3:
#            yield viztask.waitTime(180)

        yield self.draw_maze_task(self.subject.right_hand_sphere, maze, run)

    def experiment_procedure(self, experiment_block):
        """
        overwrites abstractmethod of base class BaseExperiment

        :return:
        """

        self.markerstream.push_sample([str(self.HED_tag_dictionary['experiment setup'])])
        self.markerstream.push_sample([str(self.HED_tag_dictionary['initial context'])])
        self.markerstream.push_sample([str(self.HED_tag_dictionary['experiment start'])])
        self.generate_list_of_controlled_randomized_trials(self.triallist, ['I', 'L', 'U', 'Z', 'T', '+'], [1, 2, 3])

        # procedural experiment logic:
        if experiment_block == 'training':
            #yield self.baseline_measurement(self.markerstream)
            yield self.learn_trial()

        #test phase
        else:
            # for elem in self.triallist:
            yield self.test_trial('I', 1)


# setup and schedule vizard main loop. Run this program in Worldviz Vizard IDE.
def create_experiment():
    """
    Creates and sets up the experiment instance

    """

    # start with asking the participant some informations -> use info to create a new instance of class "Subject"
    participant = yield BaseSubject.participant_info()
    
    # creates the instance of the experiment
    experiment = VisualMaze(participant, participant.maze_config)

    # starts experimental procedure, i.e. procedural logic of the experiment
    viztask.schedule(experiment.experiment_procedure(participant.maze_config))

# start vizard main loop and create experiment instance
viz.go()
viz.setMultiSample(4)
viz.phys.enable()
viztask.schedule(create_experiment)