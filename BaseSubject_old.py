"""
Module to create a new subject for an experiment.

"""

import socket
from abc import ABCMeta

import viz
import vizact
import vizconnect
import vizinfo
import vizshape
import viztask

from resources.trackers.DK2_plus_left_right_hand_tracker_with_reset_and_drift_correction import HMD_Tracker
from resources.trackers.lsl_lib import StreamInfo, StreamOutlet


class BaseSubject(object):
    """
    Instances of the class subject contain general information about the subject, such as age and handedness.
    Furthermore the class contains functionality to choose and load a certain control mechanism for the subject
    to interact with the virtual environment.

    """
    __metaclass__ = ABCMeta

    def __init__(self, id, sex, age, handedness, vision, cap_size, neck_size, labelscheme, control_style):
        """
        Every instance of class subject should have at least a code.

        Args:
            id: subject Code determined on BeMoBIL subject questionnaire
            sex: male / female
            age: integer of subjects age
            handedness: left / right
            vision: impaired, corrected, corrected-to-normal
            cap_size: EEG cap size
            neck_size: EEG neck size
            labelscheme: EEG labeling scheme of the cap in use (e.g. MoBI, 10/20 etc.)
            control_style: subject interaction with VR
        """

        self._id = id
        self._sex = sex
        self._age = age
        self._handedness = handedness
        self._vision = vision
        self._cap_size = cap_size
        self._neck_size = neck_size
        self._labelscheme = labelscheme

        # manifest and define control_style
        self.control_style = control_style
        self.use_control(control_style)
        
        # register button press events
        self.BUTTON_A_EVENT = viz.getEventID('A')
        self.BUTTON_B_EVENT = viz.getEventID('B')

        # instatiate some class objects that may only be used in certain control_style settings to facilitate handling
        if control_style == 'dk2 head hands':

            self.tracker = None
            #self.left_hand_tracker = None
            self.right_hand_tracker = None

        elif self.control_style == 'joystick':
            self.joy = None

    @staticmethod
    def participant_info():
        """
        Query the participant for basic data.

        Questions to select experimental condition and control type of the experimental condition.

        Returns: the queried data as a viz.data object

        """

        participant_info = vizinfo.InfoPanel('', title='Participant Information', align=viz.ALIGN_CENTER, icon=False)

        # query control style droplist; Create a drop-down list
        drop_control_style = participant_info.addLabelItem('Choose control style', viz.addDropList())
        items = ['dk2 head & right hand', 'mouse and keyboard'] # 'mouse and keyboard', 'joystick', 'dk2 head only', 'dk2 head wiimote',
        drop_control_style.addItems(items)

        # Add name and ID fields of maze configurations
        drop_maze_config = participant_info.addLabelItem('Choose maze configuration', viz.addDropList())
        items2 = ['auto', 'baseline', 'training', 'I', 'L', 'Z', 'U']#, 'T', '+']  # Add a list of items.
        drop_maze_config.addItems(items2)

        # Add name and ID fields of experimental condition
        drop_maze_run = participant_info.addLabelItem('Choose maze run', viz.addDropList())
        items2 = ['auto', '1', '2', '3']
        drop_maze_run.addItems(items2)

        participant_info.addSeparator(padding=(10, 10))

        textbox_id = participant_info.addLabelItem('ID', viz.addTextbox())
        textbox_age = participant_info.addLabelItem('Age', viz.addTextbox())
        textbox_handedness = participant_info.addLabelItem('Handedness', viz.addTextbox())
        textbox_vision = participant_info.addLabelItem('Vision', viz.addTextbox())
        textbox_cap_size = participant_info.addLabelItem('Cap size', viz.addTextbox())
        textbox_neck_size = participant_info.addLabelItem('Neck size', viz.addTextbox())
        textbox_labelscheme = participant_info.addLabelItem('Electrode Labelscheme', viz.addTextbox())

        participant_info.addSeparator(padding=(10, 10))

        # Add gender and age fields
        radiobutton_male = participant_info.addLabelItem('Male', viz.addRadioButton(2))
        radiobutton_female = participant_info.addLabelItem('Female', viz.addRadioButton(2))

        participant_info.addSeparator(padding=(10, 10))

        # Add submit button aligned to the right and wait until it's pressed
        submit_button = participant_info.addItem(viz.addButtonLabel('Submit'), align=viz.ALIGN_CENTER)
        yield viztask.waitButtonUp(submit_button)

        # Collect participant data
        data = viz.Data()
        data.id = textbox_id.get()
        data.age = textbox_age.get()
        data.handedness = textbox_handedness.get()
        data.vision = textbox_vision.get()
        data.cap_size = textbox_cap_size.get()
        data.neck_size = textbox_neck_size.get()
        data.labelscheme = textbox_labelscheme.get()

        if radiobutton_male.get() == viz.DOWN:
            data.sex = 'male'
        else:
            data.sex = 'female'

        # Find the index of the current selection. Find the selection itself.
        data.control_style = drop_control_style.getItems()[drop_control_style.getSelection()]
        data.maze_config = drop_maze_config.getItems()[drop_maze_config.getSelection()]
        data.maze_run = drop_maze_run.getItems()[drop_maze_run.getSelection()]

        participant_info.remove()

        # Return participant data
        viztask.returnValue(data)
        
    def use_control(self, control_style):
        """
        Enable the control modality depending on the provided input modality.

        Different experimental setup make use of different ways to exert control over the experimental world.
        Use this function to define and setup the necessary things depending on the control modality to be used.

        Args:
            control_style: interaction possibilities between subject and VR world. Currently supports:
            'mouse and keyboard', 'joystick', 'wiimote with dk2 head', 'dk2 head only', 'dk2 head hands'

        """

        # control type for test purposes
        if control_style == 'mouse and keyboard': # control type for test purposes

            viz.mouse(viz.ON)
            vizact.onmousedown(viz.MOUSEBUTTON_LEFT, self.on_button_press, 'A')
            vizact.onmousedown(viz.MOUSEBUTTON_RIGHT, self.on_button_press, 'B')

            self.sphere_radius = 0.02
            self.right_hand_sphere = vizshape.addSphere(radius=self.sphere_radius)
            self.right_hand_sphere.color(viz.GREEN)
            self.right_hand_target = self.right_hand_sphere.collideSphere()
            self.right_hand_sphere.disable(viz.DYNAMICS)

            self.right_hand_sphere.alpha(1)

            self.head_sphere = vizshape.addSphere(radius=self.sphere_radius)
            self.head_sphere.color(viz.YELLOW)
            self.head_target = self.head_sphere.collideSphere()
            self.head_sphere.disable(viz.DYNAMICS)

            MOVE_SPEED = 0.025

            def move_hand():
                if viz.key.isDown(viz.KEY_UP):
                    self.right_hand_sphere.setPosition([self.right_hand_sphere.getPosition()[0], 1.6, self.right_hand_sphere.getPosition()[2]+MOVE_SPEED])
                elif viz.key.isDown(viz.KEY_DOWN):
                    self.right_hand_sphere.setPosition([self.right_hand_sphere.getPosition()[0], 1.6, self.right_hand_sphere.getPosition()[2]-MOVE_SPEED])
                elif viz.key.isDown(viz.KEY_LEFT):
                    self.right_hand_sphere.setPosition(self.right_hand_sphere.getPosition()[0]-MOVE_SPEED, 1.6, self.right_hand_sphere.getPosition()[2])
                elif viz.key.isDown(viz.KEY_RIGHT):
                    self.right_hand_sphere.setPosition(self.right_hand_sphere.getPosition()[0]+MOVE_SPEED, 1.6, self.right_hand_sphere.getPosition()[2])

            def move_head():
                if viz.key.isDown('w'):
                    self.head_sphere.setPosition([self.head_sphere.getPosition()[0], 1.6, self.head_sphere.getPosition()[2]+MOVE_SPEED])
                elif viz.key.isDown('s'):
                    self.head_sphere.setPosition([self.head_sphere.getPosition()[0], 1.6, self.head_sphere.getPosition()[2]-MOVE_SPEED])
                elif viz.key.isDown('a'):
                    self.head_sphere.setPosition(self.head_sphere.getPosition()[0]-MOVE_SPEED, 1.6, self.head_sphere.getPosition()[2])
                elif viz.key.isDown('d'):
                    self.head_sphere.setPosition(self.head_sphere.getPosition()[0]+MOVE_SPEED, 1.6, self.head_sphere.getPosition()[2])

            vizact.ontimer(0, move_hand)
            vizact.ontimer(0, move_head)

        elif control_style == 'joystick':

            # first load the oculus rift plugin and link sensor to viewpoint
            import oculus
            hmd = oculus.Rift()

            # loads the DirectInput plug-in and adds first available joystick
            dinput = viz.add('DirectInput.dle')
            self.joy = dinput.addJoystick()

            # Set dead zone threshold so small movements of joystick are ignored
            self.joy.setDeadZone(0.2)

            # add viewpoint at subject height
            eye_height = float(self._height) - 0.05

            joystick_node = viz.addGroup(pos=(0, eye_height, 0))
            viz.link(joystick_node, viz.MainView)

            # joystick control class with lsl streams of pos and ori as in the dk2 tracker class
            # stream pos and ori in joystick movement function which gets called with ontimer / onupdate
            # set lsl stream parameters
            lsl_streamName = 'vizard_hmd6dof_stateLog_joystick'
            lsl_streamType = 'sixFloat'  # no official lsl type (not recognized by eeglab or mobilab)
            lsl_numChannels = 6
            lsl_regularSPS = 75  # regular rate, one sample per DK2 frame
            lsl_dataType = 'float32'
            lsl_streamUuid = socket.gethostname()  # PC name as uuid

            # create stream
            lsl_hmd6dofStreamInfo = StreamInfo(lsl_streamName, lsl_streamType, lsl_numChannels, lsl_regularSPS,
                                                    lsl_dataType, lsl_streamUuid)
            lsl_hmd6dofStreamInfo.desc().append_child('synchronization').append_child_value('can_drop_samples',
                                                                                                 'true')
            lsl_hmd6dofOutlet = StreamOutlet(lsl_hmd6dofStreamInfo)

            viz.callback(viz.SENSOR_DOWN_EVENT, self.on_button_press)
            vizact.onupdate(0, self.update_joystick_movement, self.joy, joystick_node, 5, 90, lsl_hmd6dofOutlet)

        else:
            self.start_dk2_head_tracker(control_style)

    def start_dk2_head_tracker(self, control_style):
        """
        Initializes Ole Traupe's new Oculus Rift DK2 ("DK2") head tracker class with both heading reset and drift
        correction based on Phasespace ("PS") data.

        Args:
            control_style: interaction possibilities between subject and VR world. Currently supports:
            'mouse and keyboard', 'joystick', 'wiimote with dk2 head', 'dk2 head only', 'dk2 head hands'

        Returns: a Tracker object with automatic drift correction

        """

        # import OWLTK as otk
        # import OWL as _OWL

        ## get trackers ready by declaring some general settings
        # define tracker names
        hmdOri_trackerName = 'rift_ori'  # DK2 ori tracker
        rawHmdOri_trackerName = 'rawhmd_ori'  # group/dummy tracker for feeding the DK2 ori data to (and on which the drift correction is done)
        hmdGroundTruth6dof_trackerName = 'ps_groundtruth_6dof'  # group/dummy tracker for feeding the PS data to (let's the nose-tip pos offset be applied correctly)
        hmdMerged_trackerName = 'hmd_merged'  # merged tracker controlling the HMD (from rawHmdOri and hmdGroundTruth6dof)

        # hand trackers
        #left_hand_tracker_name = 'left_hand'
        right_hand_tracker_name = 'right_hand'

        # set some tracking properties
        smoothPositionData = 2  # 0: raw/single data positional tracking
        # 1: linear regression on the samples flushed per HMD frame
        # 2: mean of such flushed samples (the only effective PS jitter removal method)
        driftCorrectionDemoMode = False  # gives some input/output options (lets you create an offset via 'o')
        streamRenderStats = True  # stream render stats to LSL, such as updateTime, drawTime, cullTime etc.
        streamDriftStats = True  # stream drift stats to LSL: current offset, current correction increment, cumulative increment
        streamCompletePhasespaceData = True  # stream all Phasespace markers and rigids for logging purposes to LSL

        # set Phasespace properties
        psServer_ip = "130.149.173.155"  # PS server address
        #psServer_ip = "130.149.34.81"
        psServer_freq = 960  # slave can't set frequency, attempt to set only returns the actual freqency;
        # important for good head tracking: run PS profile with group=3 and interpolate=3
        psServer_slave = 1  # 'slave' is the first bit in the 'flags' parameter; 'master' is currently not supported here
        psServer_headingLeds = [4097,
                                4098]  # [4097,4098] are the IDs of the 2nd and 3rd marker of the 1st rigid body (the laterals used for heading reset)
        psServer_rigidBody = 0  # '0' is the 1st rigid body (the one used as comparator for the drift correction)

        if control_style == 'dk2 head wiimote':

            # Add wiimote extension and connect to first available wiimote
            wii = viz.add('wiimote.dle')
            self.wiimote = wii.addWiimote()

            # Register callback function to the wiimotes buttons
            vizact.onsensordown(self.wiimote, wii.BUTTON_A, self.on_button_press, 'A')
            vizact.onsensordown(self.wiimote, wii.BUTTON_B, self.on_button_press, 'B')

            # todos correct vizconnect file with steamVR controller
            vizconnect.go('resources/trackers/DK2_tracker_head_only_vizconnect.py')

            # instantiate the HMD tracker object (with ground truth reset and drift correction)
            self.tracker = HMD_Tracker(hmdOri_trackerName, rawHmdOri_trackerName, hmdGroundTruth6dof_trackerName, None,
                                       None, hmdMerged_trackerName, smoothPositionData, driftCorrectionDemoMode,
                                       streamRenderStats, streamDriftStats, streamCompletePhasespaceData,
                                       psServer_ip, psServer_freq, psServer_slave, psServer_headingLeds,
                                       psServer_rigidBody)

        elif control_style == 'dk2 head & right hand':

            vizconnect.go('resources/trackers/DK2_tracker_hands_vizconnect.py')

            # instantiate the HMD tracker object (with ground truth reset and drift correction)
            # None flag in case of left hand tracker
            self.tracker = HMD_Tracker(hmdOri_trackerName, rawHmdOri_trackerName, hmdGroundTruth6dof_trackerName,
                                       hmdMerged_trackerName, None, right_hand_tracker_name,
                                       smoothPositionData, driftCorrectionDemoMode, streamRenderStats, streamDriftStats,
                                       streamCompletePhasespaceData, psServer_ip, psServer_freq, psServer_slave,
                                       psServer_headingLeds, psServer_rigidBody)
                                       
            self.sphere_radius = 0.01
            self.right_hand_tracker = vizconnect.getTracker('right_hand').getNode3d()
            self.right_hand_sphere = vizshape.addSphere(radius=self.sphere_radius)
            self.right_hand_sphere.alpha(0)
            self.right_hand_target = self.right_hand_sphere.collideSphere()
            self.right_hand_sphere.disable(viz.DYNAMICS)
            right_hand_link = viz.link(self.right_hand_tracker, self.right_hand_sphere)
            # todos say somewhere that the collide sphere is defined here

            # self.left_hand_tracker = vizconnect.getTracker('left_hand').getNode3d()
            # self.left_hand_sphere = vizshape.addSphere(radius=0.02)
            # self.left_hand_sphere.alpha(0)
            # self.left_hand_target = self.left_hand_sphere.collideSphere()
            # self.left_hand_sphere.disable(viz.DYNAMICS)
            # left_hand_link = viz.link(self.left_hand_tracker, self.left_hand_sphere)
            
            self.head_tracker = vizconnect.getTracker('hmd_merged').getNode3d()
            self.head_sphere = vizshape.addSphere(radius=self.sphere_radius)
            self.head_sphere.alpha(0)
            self.head_target = self.head_sphere.collideSphere()
            self.head_sphere.disable(viz.DYNAMICS)
            head_link = viz.link(self.head_tracker, self.head_sphere)
            
#            if show_avatar_hands:
#
#                # link subjects hand trackers to proximity targets
#                right_hand = viz.add('resources/hand.cfg')
#                left_hand = viz.add('resources/hand_left.cfg')
#
#                right_hand_link = viz.link(subject.right_hand_tracker, right_hand)
#                left_hand_link = viz.link(subject.left_hand_tracker, left_hand)

#
#            elif subject.control_style == 'mouse and keyboard':
#
#                # add proximity target for test purposes using mouse and keyboard
#                self.head_target = viz.MainView            
#                
#                self.left_hand_tracker = vizconnect.getTracker('left_hand').getNode3d()
#                self.head_tracker = vizconnect.getTracker('hmd_merged').getNode3d()

        elif control_style == 'dk2 head only':

            vizconnect.go('resources/trackers/DK2_tracker_head_only_vizconnect.py')

            # instantiate the HMD tracker object (with ground truth reset and drift correction)
            self.tracker = HMD_Tracker(hmdOri_trackerName, rawHmdOri_trackerName, hmdGroundTruth6dof_trackerName,
                                       hmdMerged_trackerName, None, None, smoothPositionData, driftCorrectionDemoMode,
                                       streamRenderStats, streamDriftStats, streamCompletePhasespaceData, psServer_ip,
                                       psServer_freq, psServer_slave, psServer_headingLeds, psServer_rigidBody)

        else:
            print('Could not initialize HMD_Tracker')

    @staticmethod
    def update_joystick_movement(joystick, view_node, move_speed, turn_speed, lsl_stream):
        """
        Updates the viewpoint depending on joystick movements.

        Sends 6dof of viz.MainView via lsl.

        Args:
            joystick: joystick loaded with either vizconnect or directly as in 'use_control' function above
            view_node: Viewpoint node
            move_speed: move speed translated from joystick movement to viewpoint updating. Default value is 5.
            turn_speed: turn speed elicited by joystick twist in VR. Default value is 90.
            lsl_stream: stream to push 6dof sample

        """

        elapsed = viz.elapsed()

        # Get the joystick position
        x, y, z = joystick.getPosition()

        # Move the viewpoint based on xy-axis value
        view_node.setPosition([0, 0, y * move_speed * viz.getFrameElapsed()], viz.REL_LOCAL)

        # Turn the viewpoint left/right based on twist value
        view_node.setEuler([x * turn_speed * elapsed, 0, 0], viz.REL_LOCAL)

        # stream the HMD 6DOF
        pos = viz.MainView.getPosition()
        ori = viz.MainView.getEuler()
        lsl_stream.push_sample([pos[0], pos[1], pos[2], ori[0], ori[1], ori[2]])

    def get_current_6dof(self, control_style):
        """
        Returns the 6DOF of the Head/view depending on the control_style.

        """

        if control_style == 'mouse and keyboard' or control_style == 'joystick':

            pos = viz.MainView.getPosition()
            ori = viz.MainView.getEuler()

        else:

            pos = self.myHmdTracker.getCurrentPos()
            ori = self.myHmdTracker.getCurrentEuler()

    def on_button_press(self, sensor):
        """
        Callback function to handle button presses by external control devices.

        Args:
            sensor: reports button press by a connected devices

        """


        try:
            if sensor.button == 0:
                viz.sendEvent(self.BUTTON_A_EVENT)

            elif sensor.button == 18:
                viz.sendEvent(self.BUTTON_B_EVENT)
        except:
            pass

        if sensor == 'A':
            viz.sendEvent(self.BUTTON_A_EVENT)

        elif sensor == 'B':
            viz.sendEvent(self.BUTTON_B_EVENT)
