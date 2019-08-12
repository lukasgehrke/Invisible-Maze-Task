# # values should be class variables such as self.maze_duration and then send markers function taking current
# # values of bookkeeping variables and pushes them through lsl
# # init behavioral markers of interest, key:value pair ;
# self.marker_dict = {'maze_duration': 0,
#                     'left_hand_wall_touch_count': 0,
#                     'left_hand_wall_touch_time_in_wall': 0,
#                     'left_hand_total_time_in_wall': 0,
#
#                     'right_hand_wall_touch_count': 0,
#                     'right_hand_wall_touch_time_in_wall': 0,
#                     'right_hand_total_time_in_wall': 0,
#
#                     'head_wall_touch_count': 0,
#                     'head_wall_touch_time_in_wall': 0,
#                     'head_total_time_in_wall': 0,
#                     'total_time_in_wall': 0,
#
#                     'head_to_left_hand_vector_X': 0,
#                     'head_to_left_hand_vector_Y': 0,
#                     'head_to_left_hand_vector_Z': 0,
#                     'head_to_right_hand_vector_X': 0,
#                     'head_to_right_hand_vector_Y': 0,
#                     'head_to_right_hand_vector_Z': 0,
#
#                     'current_maze_unit_id': 0,
#                     'current_wall_id': 0
#                     }




# todo birds eye view camera, remove later for experiment
BirdEyeWindow = viz.addWindow()
BirdEyeWindow.fov(60)
BirdEyeView = viz.addView()
BirdEyeWindow.setView(BirdEyeView)
BirdEyeView.setPosition([0, 10, 0])
BirdEyeView.setEuler([0, 90, 0])


def send_markers(self, wall, target, marker_dictionary, lsl_stream, exit):
    """

    :param wall:
    :param target:
    :param marker_dictionary:
    :param lsl_stream:
    :param exit:
    :return:
    """

    acquisition_time = lsl.local_clock()

    if exit is True:
        time_in_wall = self.exit_wall_time - self.enter_wall_time
        marker_dictionary['total_time_in_wall'] += time_in_wall
        #            print 'time in wall', time_in_wall

    current_maze_duration = acquisition_time - self.exp_start_time
    marker_dictionary['maze_duration'] = current_maze_duration
    #        print 'current maze duration', current_maze_duration

    # todo test with actual trackers
    marker_dictionary['current_maze_unit'] = self.scene.wall_proximity_manager.getActiveSensors(target)
    #        print 'maze unit', marker_dictionary['current_maze_unit']

    marker_dictionary['current_wall_id'] = wall
    #        print 'wall id', marker_dictionary['current_wall_id']

    lsl_stream.push_sample([marker_dictionary['maze_duration'],
                            marker_dictionary['left_hand_wall_touch_count'],
                            marker_dictionary['left_hand_wall_touch_time_in_wall'],
                            marker_dictionary['left_hand_total_time_in_wall'],
                            marker_dictionary['right_hand_wall_touch_count'],
                            marker_dictionary['right_hand_wall_touch_time_in_wall'],
                            marker_dictionary['right_hand_total_time_in_wall'],
                            marker_dictionary['head_wall_touch_count'],
                            marker_dictionary['head_wall_touch_time_in_wall'],
                            marker_dictionary['head_total_time_in_wall'],
                            marker_dictionary['total_time_in_wall'],
                            marker_dictionary['head_to_left_hand_vector_X'],
                            marker_dictionary['head_to_left_hand_vector_Y'],
                            marker_dictionary['head_to_left_hand_vector_Z'],
                            marker_dictionary['head_to_right_hand_vector_X'],
                            marker_dictionary['head_to_right_hand_vector_Y'],
                            marker_dictionary['head_to_right_hand_vector_Z'],
                            marker_dictionary['current_maze_unit_id'],
                            marker_dictionary['current_wall_id']],
                           acquisition_time)


def lsl_maze_progression(self, lsl_stream):
    """

    :return:
    """

    acquisition_time = lsl.local_clock()

    # create long data string with factor:value pairs and add ',' for string separation
    exp_start = 'exp_start:' + str(self.exp_start_time) + ','
    current_maze = 'current_maze:' + str(self.current_maze) + ','
    current_trial_run = 'current_trial_run:' + str(self.current_trial_run) + ','
    current_maze_unit = 'current_maze_unit:' + str(self.current_maze_unit) + ','
    current_maze_unit_enter_time = 'current_maze_unit_enter_time:' + str(self.current_maze_unit_enter_time) + ','
    current_maze_unit_enter_count = 'current_maze_unit_enter_count:' + str(self.current_maze_unit_enter_count) + ','
    duration_maze_unit = 'duration_maze_unit:' + str(self.duration_maze_unit) + ','
    visited_maze_units = 'visited_maze_units:' + str(len(self.visited_maze_units_list)) + ','
    maze_unit_progression = 'maze_unit_progression' + str(self.maze_unit_progression) + ','

    data = exp_start + current_maze + current_trial_run + current_trial_run + current_maze_unit + current_maze_unit_enter_time + current_maze_unit_enter_count + duration_maze_unit + visited_maze_units + maze_unit_progression

    lsl_stream.push_sample([data], acquisition_time)


 def enter_maze_unit(self, proximity_event):

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