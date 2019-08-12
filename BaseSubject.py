"""
Module to create a new subject for an experiment.

"""

from abc import ABCMeta

# import statements
import socket

import viz
import vizact
import vizconnect
import vizinfo
import vizshape
import viztask
import vizproximity

import steamvr

from resources.trackers.lsl_lib import StreamInfo, StreamOutlet, local_clock


class BaseSubject(object):
    """
    Instances of the class subject contain general information about the subject, such as age and handedness.
    Furthermore the class contains functionality to choose and load a certain control mechanism for the subject
    to interact with the virtual environment.

    """
    __metaclass__ = ABCMeta

    # def __init__(self, id, sex, age, handedness, vision, cap_size, neck_size, labelscheme, control_style):
    def __init__(self, control_style):
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
        self.hand_tracker_id = None
        # self._sex = sex
        # self._age = age
        # self._handedness = handedness
        # self._vision = vision
        # self._cap_size = cap_size
        # self._neck_size = neck_size
        # self._labelscheme = labelscheme
        
        # register button press events
        self.BUTTON_A_EVENT = viz.getEventID('A')
        self.BUTTON_B_EVENT = viz.getEventID('B')

        if control_style == 'steamvr without PS':
            self.sphere_radius = 0.01
            self.right_hand_sphere = vizshape.addSphere(radius=self.sphere_radius)
            self.right_hand_sphere_target = vizproximity.Target(self.right_hand_sphere)
            self.right_hand_sphere.alpha(0)
            self.right_hand_sphere.collideSphere()
            self.right_hand_sphere.disable(viz.DYNAMICS)

            self.head_sphere = vizshape.addSphere(radius=self.sphere_radius)
            self.head_sphere_target = vizproximity.Target(self.head_sphere)
            self.head_sphere.alpha(0)
            self.head_sphere.collideSphere()
            self.head_sphere.disable(viz.DYNAMICS)

            # manifest and define control_style
            #self.steamvr_setup_vm2(self.right_hand_sphere, self.head_sphere)

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
        items = ['steamvr without PS']  # 'mouse and keyboard', 'joystick', 'dk2 head only', 'dk2 head wiimote',
        drop_control_style.addItems(items)

        # Add name and ID fields of maze configurations
        drop_maze_config = participant_info.addLabelItem('Choose maze configuration', viz.addDropList())
        # items2 = ['baseline', 'auto', 'training', 'I', 'L', 'Z', 'U', '+']#, 'T', ]  # Add a list of items.
        items2 = ['all', 'I', 'L', 'Z', 'U', 'S']  # , 'T', ]  # Add a list of items.
        drop_maze_config.addItems(items2)

        # Add name and ID fields of experimental condition
        drop_maze_run = participant_info.addLabelItem('Choose maze run', viz.addDropList())
        items2 = ['all', '2', '3']
        drop_maze_run.addItems(items2)

        # participant_info.addSeparator(padding=(10, 10))
        #
        textbox_id = participant_info.addLabelItem('ID', viz.addTextbox())
        # textbox_age = participant_info.addLabelItem('Age', viz.addTextbox())
        # textbox_handedness = participant_info.addLabelItem('Handedness', viz.addTextbox())
        # textbox_vision = participant_info.addLabelItem('Vision', viz.addTextbox())
        # textbox_cap_size = participant_info.addLabelItem('Cap size', viz.addTextbox())
        # textbox_neck_size = participant_info.addLabelItem('Neck size', viz.addTextbox())
        # textbox_labelscheme = participant_info.addLabelItem('Electrode Labelscheme', viz.addTextbox())
        #
        # participant_info.addSeparator(padding=(10, 10))
        #
        # # Add gender and age fields
        # radiobutton_male = participant_info.addLabelItem('Male', viz.addRadioButton(2))
        # radiobutton_female = participant_info.addLabelItem('Female', viz.addRadioButton(2))
        #
        # participant_info.addSeparator(padding=(10, 10))

        # Add submit button aligned to the right and wait until it's pressed
        submit_button = participant_info.addItem(viz.addButtonLabel('Submit'), align=viz.ALIGN_CENTER)
        yield viztask.waitButtonUp(submit_button)

        # Collect participant data
        data = viz.Data()
        data.id = textbox_id.get()
        # data.age = textbox_age.get()
        # data.handedness = textbox_handedness.get()
        # data.vision = textbox_vision.get()
        # data.cap_size = textbox_cap_size.get()
        # data.neck_size = textbox_neck_size.get()
        # data.labelscheme = textbox_labelscheme.get()

        # if radiobutton_male.get() == viz.DOWN:
        #     data.sex = 'male'
        # else:
        #     data.sex = 'female'

        # Find the index of the current selection. Find the selection itself.
        data.control_style = drop_control_style.getItems()[drop_control_style.getSelection()]
        data.maze_config = drop_maze_config.getItems()[drop_maze_config.getSelection()]
        data.maze_run = drop_maze_run.getItems()[drop_maze_run.getSelection()]

        participant_info.remove()

        # Return participant data
        viztask.returnValue(data)

    def steamvr_setup_vm2(self, right_hand_object, head_object):

        hmd = steamvr.HMD()
        if not hmd.getSensor():
            sys.exit('SteamVR HMD not detected')
        viz.link(hmd.getSensor(), viz.MainView)

        # create LSL stream for MoBIlab pos and ori analysis --> ori should be in quaternions
        hmd_stream = self.create_non_phasespace_rigid_body_stream('headRigid', 0)
        # stream 6dof of HMD as pos (x,y,z) and ori(x,y,z,w) --> quaternion
        vizact.onupdate(18, self.update_and_push_rigid_body, viz.MainView, head_object, hmd_stream)

        #  connecting present controllers
        trackers = steamvr.getTrackerList()
        self.controller = steamvr.getControllerList()[0]
        tracker_names = ['handRigid', 'torsoRigid']

        for i in range(len(trackers)):
            # create LSL stream for MoBIlab pos and ori analysis --> ori should be in quaternions
            tracker_stream = self.create_non_phasespace_rigid_body_stream(tracker_names[i], 0)
            # stream 6dof as pos (x,y,z) and ori(x,y,z,w) --> quaternion

            print(trackers[i].getData())
            print(trackers[i].getPosition())

            if i == 0:
                vizact.onupdate(19, self.update_and_push_rigid_body, trackers[i], right_hand_object, tracker_stream)
            else:
                vizact.onupdate(19, self.update_and_push_rigid_body, trackers[i], None, tracker_stream)

    def create_non_phasespace_rigid_body_stream(self, name, srate):
        """

        Args:
            name:
            ps_heading:

        Returns:

        """

        # create LSL stream for MoBIlab pos and ori analysis --> ori should be in quaternions
        # beware the streamname (must contain the word "rigid") and type (must be Mocap)
        # self defined LSL streamtype, not officially supported
        stream_type = 'rigidBody'

        num_channels = 7  # pos + ori in quaternion + acquisition time

        sampling_rate = srate  # regular rate, one sample per HTC Vive frame
        data_type = 'float32'
        uuid = socket.gethostname()  # PC name as uuid

        vizard_rigid = StreamInfo(name, stream_type, num_channels, sampling_rate, data_type, uuid)
        vizard_rigid.desc().append_child('synchronization').append_child_value('can_drop_samples', 'true')

        # define LSL stream meta-data
        setup = vizard_rigid.desc().append_child("setup")
        setup.append_child_value("name", name)

        # channels with position and orientation in quaternions
        objs = setup.append_child("objects")
        obj = objs.append_child("object")
        obj.append_child_value("label", "Rigid" + str(name))
        obj.append_child_value("id", str(name))
        obj.append_child_value("type", "Mocap")

        channels = vizard_rigid.desc().append_child("channels")
        chan = channels.append_child("channel")
        chan.append_child_value("label", "Rigid_" + str(name) + "_X")
        chan.append_child_value("object", "Rigid_" + str(name))
        chan.append_child_value("type", "PositionX")
        chan.append_child_value("unit", "meters")

        chan = channels.append_child("channel")
        chan.append_child_value("label", "Rigid_" + str(name) + "_Y")
        chan.append_child_value("object", "Rigid_" + str(name))
        chan.append_child_value("type", "PositionY")
        chan.append_child_value("unit", "meters")

        chan = channels.append_child("channel")
        chan.append_child_value("label", "Rigid_" + str(name) + "_Z")
        chan.append_child_value("object", "Rigid_" + str(name))
        chan.append_child_value("type", "PositionZ")
        chan.append_child_value("unit", "meters")

        chan = channels.append_child("channel")
        chan.append_child_value("label", "Rigid_" + str(name) + "_quat_X")
        chan.append_child_value("object", "Rigid_" + str(name))
        chan.append_child_value("type", "OrientationX")
        chan.append_child_value("unit", "quaternion")

        chan = channels.append_child("channel")
        chan.append_child_value("label", "Rigid_" + str(name) + "_quat_Y")
        chan.append_child_value("object", "Rigid_" + str(name))
        chan.append_child_value("type", "OrientationY")
        chan.append_child_value("unit", "quaternion")

        chan = channels.append_child("channel")
        chan.append_child_value("label", "Rigid_" + str(name) + "_quat_Z")
        chan.append_child_value("object", "Rigid_" + str(name))
        chan.append_child_value("type", "OrientationZ")
        chan.append_child_value("unit", "quaternion")

        chan = channels.append_child("channel")
        chan.append_child_value("label", "Rigid_" + str(name) + "_quat_W")
        chan.append_child_value("object", "Rigid_" + str(name))
        chan.append_child_value("type", "OrientationW")
        chan.append_child_value("unit", "quaternion")

        vizard_rigid_outlet = StreamOutlet(vizard_rigid)

        return vizard_rigid_outlet

    def update_and_push_rigid_body(self, tracker_data_source, object_to_update, markerstream):
        """

        :param tracker_data_source:
        :param object_to_update:
        :param markerstream:
        :return:
        """

        pos = tracker_data_source.getPosition()
        ori_quat = tracker_data_source.getQuat()

        if object_to_update is not None:
            object_to_update.setPosition(pos)
            object_to_update.setQuat(ori_quat)

        if markerstream is not None:
            acquisition_time = local_clock()
            markerstream.push_sample([pos[0], pos[1], pos[2], ori_quat[0], ori_quat[1], ori_quat[2], ori_quat[3]], acquisition_time)

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
