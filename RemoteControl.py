"""
Send to and receive information from the VR rendering machine (backtop).

Can send information to the client running the experiment and receive and
visualize information about the orientation and position as well as
EEG data and current state of the experiment.

"""

import socket

import viz

from resources.trackers.lsl_lib import StreamInfo, StreamOutlet


class RemoteControl(object):
    """
    Handles interaction between experiment instance on VR render machine and control room PC.

    """

    def __init__(self):

        # create simple GUI window with buttons for: pause, continue and a window to print strings
        self.pause_button = viz.addButtonLabel('pause Experiment')
        self.pause_button.setPosition(.5, .7)
        self.pause_button.setScale(2, 2)

        self.continue_button = viz.addButtonLabel('continue Experiment')
        self.continue_button.setPosition(.5, .5)
        self.continue_button.setScale(2, 2)

        self.text_screen = viz.addText('current marker:', viz.SCREEN)
        self.text_screen.setPosition(.25, .3)

        self.marker_field = viz.addButtonLabel('markers')
        self.marker_field.setPosition(.5, .2)
        self.marker_field.setScale(2, 2)

        # register callbacks for GUI to either pause or continue function
        viz.callback(viz.BUTTON_EVENT, self.on_button_press)

        # create network outlet
        self.connection_to_vr_machine = viz.addNetwork('BPN-C043')

        # register callback for network event handling
        viz.callback(viz.NETWORK_EVENT, self.write)

        # send behavioral to LSL stream (saved extra for faster testing of behavioral data)
        # create and start LSL marker stream
        self.behavior_stream_info = StreamInfo('BehavioralMarkerStream', 'Markers', 1, 0, 'string', socket.gethostname())
        self.behavior_stream = StreamOutlet(self.behavior_stream_info)

    def on_button_press(self, button, state):
        """
        Handles button pressed events to pause and continue the experiment.

        Args:
            button: the button object
            state: the state of the button object

        """

        if button == self.pause_button:
            if state == viz.DOWN:
                self.pause()
        elif button == self.continue_button:
            if state == viz.DOWN:
                self.continue_exp()
        else:
            print 'This is not a button :)'

    def pause(self):
        """
        Sends pause command to the experimental procedure.

        """

        self.connection_to_vr_machine.send(command='pause')
        self.marker_field.message('pause')
        self.behavior_stream.push_sample(['pauseRC'])

    def continue_exp(self):
        """
        Sends continue command to the experiment.

        """

        self.connection_to_vr_machine.send(command='continue')
        self.marker_field.message('continue')
        self.behavior_stream.push_sample(['continueRC'])

    def write(self, marker_event):
        """
        Prints a received message to the text window of the GUI

        Args:
            marker_event: text message/marker received from the experiment instance on VR machine.

        """

        self.marker_field.message(marker_event.marker)
        self.behavior_stream.push_sample([marker_event.marker])

# Start the vizard main loop and create an instance of the RemoteControl class
viz.go()
rc = RemoteControl()