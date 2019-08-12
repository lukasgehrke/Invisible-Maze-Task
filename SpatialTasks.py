def sop_task(self, pointing_target):
    """
    pointing task: point to landmarks/dead-ends, records vector of hand-head
    1. Instruktion: Bitte zeigen Sie nun in die Richtung, in der Sie das Ende des Labyrinths vermuten.
    2. Hide Message
    mouse click
    3. Instruktion: Bitte zeigen Sie nun in die Richtung, in der Sie die Landmarke vermuten.
    2. Hide Message
    mouse click

    :param head:
    :param hand:
    :param start:
    :param pointing_target:
    :param markerstream:
    :return:
    """

    self.subject.right_hand_sphere.alpha(0)

    # todo align with tracker, might need some pre transformation, pointing_hand.visible(viz.ON)
    # rotate tracker on the handle to match arrow direction of hand
    pointing_hand = viz.add('resources/arrow.dae')
    pointing = vizact.onupdate(0, self.subject.update_and_push_rigid_body, self.subject.right_hand_sphere,
                               pointing_hand, None)

    self.scene.change_instruction(
        "Zeigen Sie bitte auf: " + pointing_target + "!\nzum Starten, linke Maustaste druecken.\nBestaetigen Sie Ihre Antwort durch\nerneutes druecken der linken Maustaste")
    yield self.hide_inst_continue_left_mouse()

    # send pointing task start marker
    event = 'sop:start'
    target = 'target:' + pointing_target + ';'
    maze = 'maze:' + str(self.current_maze) + ';'
    trial_run = 'trial_run:' + str(self.current_trial_run) + ';'
    marker = event + target + maze + trial_run
    self.push_marker(self.markerstream, [marker], True)

    # mouseclick to indicate answer
    # todo later, use glove with mouse attached for responses
    yield viztask.waitMouseDown(viz.MOUSEBUTTON_LEFT)

    # send pointing task start marker
    event = 'sop:end'
    marker = event + target + maze + trial_run
    self.push_marker(self.markerstream, [marker], True)

    # delete hand object and link to update pos/ori from tracker
    pointing.remove()
    pointing_hand.remove()

def rvd_task(self, number_of_landmarks, markerstream):

    self.scene.change_instruction("Bitte platzieren Sie aus der Vogelperspektive,\nIhre Startposition, das Ende (Blitz), sowie den Leuchtturm!\nBitte einmal linke Maustaste druecken.")
    yield self.hide_inst_continue_left_mouse()
    self.scene.change_instruction("Platzieren Sie jedes einzelne Element\ndurch druecken der linken Maustaste.\nzum Starten, linke Maustaste druecken.")
    yield self.hide_inst_continue_left_mouse()
    self.push_marker(markerstream, ["spatial_task:rvd;when:start"], False)

    # place three different shapes in three different colors, representing current position, landmark1, landmark2, landmarkn
    for i in range(number_of_landmarks):
        if i==0:
            self.scene.start_sign.visible(viz.ON)
            start_track = vizact.onupdate(0, self.subject.update_and_push_rigid_body, self.subject.right_hand_sphere, self.scene.start_sign, None)
        elif i==1:
            self.scene.end_sign.visible(viz.ON)
            end_track = vizact.onupdate(0, self.subject.update_and_push_rigid_body, self.subject.right_hand_sphere, self.scene.end_sign, None)
        elif i==2:
            #self.scene.global_landmark.setScale(.002, .002, .002)
            #self.scene.global_landmark.visible(viz.ON)
            #landmark_track = vizact.onupdate(0, self.subject.update_and_push_rigid_body, self.subject.right_hand_sphere, self.scene.global_landmark, None)

            #[BPA 2019-04-29] updated for new landmark class:
            self.maze.global_landmark.setScale(.002, .002, .002)
            self.scene.toggle_global_landmark(self.maze, "on")
            landmark_track = vizact.onupdate(0, self.subject.update_and_push_rigid_body, self.subject.right_hand_sphere, self.maze.global_landmark, None)


        yield viztask.waitMouseDown(viz.MOUSEBUTTON_LEFT)
        self.push_marker(self.markerstream, ["object:" + str(i) + ";what:placed"], False)
        # post hoc analysis of RT with 0,1,2 meaning start, end, landmark

        # unlink object tracking
        if i==0:
            start_track.remove()
        elif i==1:
            end_track.remove()
        elif i==2:
            landmark_track.remove()

    yield viztask.waitTime(3)

    # LG: todo test with viewpoint (view) function in matlab
    self.push_marker(markerstream, ["spatial_task:rvd;when:end"
                                    + ";pos_start_object:" + str(self.scene.start_sign.getPosition(1))
                                    + ";pos_end_object:" + str(self.scene.end_sign.getPosition(1))
                                    #+ ";pos_landmark:" + str(self.scene.global_landmark.getPosition(1))
                                    + ";pos_landmark:" + str(self.maze.global_landmark.getPosition(1))
                                    + ";viewpoint:" + str(viz.MainView.getPosition(1))], False)

    # make invisible again
    self.scene.start_sign.visible(viz.OFF)
    self.scene.end_sign.visible(viz.OFF)
    #self.scene.global_landmark.visible(viz.OFF)
    self.maze.global_landmark.visible(viz.OFF)