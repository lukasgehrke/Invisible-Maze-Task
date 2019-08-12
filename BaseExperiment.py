"""
Experiment class defining standard experimental procedures using the Worldviz Vizard Bemobil Framework.

"""

import random
import socket
from abc import ABCMeta

import viz

from BaseSubject import BaseSubject
from Chaperone import Chaperone
from resources.trackers.lsl_lib import StreamInfo, StreamOutlet


class BaseExperiment(object):
    """
    Control the procedure of the whole experiment.

    Initializes a LSL markerstream called "markerstream" that should be fed with behavioral information throughout the
    experiment (usage: markerstream.push_sample(['behavioral information'])). The markerstream is attached with the
    meta data obtained from the initial on screen questionnaire.
    Any instance of BaseExperiment furthermore opens a network connection that sends each marker to the 'RemoteControl'
    class. Vice versa BaseExperiment handles the commands 'pause' and 'continue' which may be send from the remote
    control.

    BaseExperiment contains 2 abstractmethod that must be implemented by any inheriting class.
    1. generate_list_of_controlled_randomized_trials makes sure that experimenters handle pseudo randomization of trials
    2. experiment_procedure is a pointer to implement a neat progression through each step in the experimental pipeline

    Lastly, BaseExperiment contains a python dictionary with HED Tags (http://www.hedtags.org/) that apply to most
    experiments at BeMoBIL and are therefore of general usage.

    """
    __metaclass__ = ABCMeta

    def __init__(self, subject):
        """
        Initialize all necessary classes to run the experiment.

        """

        # standard BeMoBIL settings start
        # self.subject = BaseSubject(subject.id, subject.sex, subject.age, subject.handedness, subject.vision,
        #                            subject.cap_size, subject.neck_size, subject.labelscheme, subject.control_style)
        self.subject = BaseSubject(subject.control_style)

        # Test if Boundaries can still be approached, otherwise deactivate
        #self.chaperone = Chaperone(None, 0.1, 0.2, True, None)

        # create irregular sampled LSL marker stream for button/experimental events in the experimental procedure
        print socket.gethostname()
        self.markerstream_info = StreamInfo('vizardMarkers', 'Markers', 1, 0, 'string', socket.gethostname())
        # start LSL marker stream
        # To send a marker through the stream to the recording unit use the LSL push_sample method
        self.markerstream = StreamOutlet(self.markerstream_info)

        # HED Tag BeMoBIL dictionary
        # self.HED_tag_dictionary = {
        #     'experiment start': ('/Event/Category/Experiment control/Sequence/Experiment',
        #                          '/Event/Label/exp_start',
        #                          '/Event/Description/Experimental condition started',
        #                          '/Attribute/Onset'),
        #     'experiment end': ('/Event/Category/Experiment control/Sequence/Experiment',
        #                        '/Event/Label/exp_end',
        #                        '/Event/Description/Experimental condition finished',
        #                        '/Attribute/Offset'),
        #     'experiment setup': ('/Event/Category/Experiment control/Setup/Parameters',
        #                          '/Event/Label/exp_language/',
        #                          '/Event/Description/Experiment language is german',
        #                          '/Attribute/Language/Family/Latin/German',
        #                          '/Experiment context/Standing',
        #                          '/Experiment context/Virtual world/Rift DK2',
        #                          '/Participant/ID/#'),
        #     'initial context': '/Event/Category/Initial context/VR (visual maze) experiment at BeMoBIL',
        #     'instruction on': ('/Event/Category/Experimental stimulus/Instruction/Read/',
        #                         '/Event/Label/inst_read',
        #                         '/Event/Description/Text instruction to understand experiment presented to the subject',
        #                         '/Item/Symbolic/Character/Letter/Unicode',
        #                         '/Attribute/Onset',
        #                         '/Attribute/Location/Screen/Center',
        #                         '/Attribute/Visual/Color/White',
        #                         '/Attribute/Visual/Foreground',
        #                         '/Attribute/Visual/Background/Color/Black with grassy ground',
        #                         '/Attribute/Language/Unit/Sentence/Full',
        #                         '/Attribute/Language/Family/Latin/German',
        #                         '/Sensory presentation/Visual/Rendering type/Screen/3D/Rift DK2',
        #                         '/Participant/Effect/Cognitive/Meaningful',
        #                         '/Participant/Effect/Visual/Foveal'),
        #     'instruction off': ('/Event/Category/Experimental stimulus/Instruction/Read/',
        #                         '/Event/Label/inst_read',
        #                         '/Event/Description/Text instruction to understand experiment presented to the subject',
        #                         '/Item/Symbolic/Character/Letter/Unicode',
        #                         '/Attribute/Offset',
        #                         '/Attribute/Location/Screen/Center',
        #                         '/Attribute/Visual/Color/White',
        #                         '/Attribute/Visual/Foreground',
        #                         '/Attribute/Visual/Background/Color/Black with grassy ground',
        #                         '/Attribute/Language/Unit/Sentence/Full',
        #                         '/Attribute/Language/Family/Latin/German',
        #                         '/Sensory presentation/Visual/Rendering type/Screen/3D/Rift DK2',
        #                         '/Participant/Effect/Cognitive/Meaningful',
        #                         '/Participant/Effect/Visual/Foveal'),
        #     'walk around on': ('/Event/Category/Experimental procedure',
        #                         '/Event/Label/base_walk',
        #                         '/Event/Description/Baseline measurement with subjects freely walking and exploring the VR space',
        #                         '/Item/Natural scene/',
        #                         '/Attribute/Onset',
        #                         '/Attribute/Visual/Background/Color/Black with grassy ground',
        #                         '/Sensory presentation/Visual/Rendering type/Screen/3D/Rift DK2',
        #                         '/Action/Type/Walk',
        #                         '/Participant/Effect/Body part/Whole Body',
        #                         '/Participant/Effect/Vestibular',
        #                         '/Participant/Effect/Cognitive/Not meaningful',
        #                         '/Participant/Effect/Cognitive/novel'),
        #     'walk around off': ('/Event/Category/Experimental procedure',
        #                         '/Event/Label/base_walk',
        #                         '/Event/Description/Baseline measurement with subjects freely walking and exploring the VR space',
        #                         '/Item/Natural scene/',
        #                         '/Attribute/Offset',
        #                         '/Attribute/Visual/Background/Color/Black with grassy ground',
        #                         '/Sensory presentation/Visual/Rendering type/Screen/3D/Rift DK2',
        #                         '/Action/Type/Walk',
        #                         '/Participant/Effect/Body part/Whole Body',
        #                         '/Participant/Effect/Vestibular',
        #                         '/Participant/Effect/Cognitive/Not meaningful',
        #                         '/Participant/Effect/Cognitive/novel'),
        #     'button press': ('/Event/Category/Participant response',
        #                             '/Event/Label/wii_button',
        #                             '/Event/Description/Button press with the right index finger (devices include Wiimote/Joystick/Mouse)',
        #                             '/Action/Type/Button press/Joystick',
        #                             '/Participant/Effect/Tactile',
        #                             '/Participant/Effect/Body part/Arm/Hand/Finger/Index',
        #                             '/Attribute/Object side/Left'),
        #     'target color change': ('/Event/Category/Experimental stimulus/Instruction/Attend/',
        #                         '/Event/Label/targ_color_change',
        #                         '/Event/Description/A spherical target object changed color',
        #                         '/Item/3D Shape/Sphere',
        #                         '/Attribute/Onset',
        #                         '/Attribute/Visual/Color/Blue',
        #                         '/Attribute/Location/Screen/Center',
        #                         '/Attribute/Visual/Foreground',
        #                         '/Attribute/Visual/Background/Color/Black',
        #                         '/Sensory presentation/Visual/Rendering type/Screen/3D/Rift DK2',
        #                         '/Participant/Effect/Cognitive/Meaningful',
        #                         '/Participant/Effect/Visual/Foveal'),
        #     'feedback on': ('/Event/Category/Experimental stimulus/Instruction/Attend/',
        #                             '/Event/Label/targ_color_change',
        #                             '/Event/Description/A target sphere appeared at the position of the hand when a subject touched a wall',
        #                             '/Item/3D Shape/Sphere',
        #                             '/Attribute/Onset',
        #                             '/Attribute/Visual/Color/White',
        #                             '/Attribute/Location/Screen/Center',
        #                             '/Attribute/Visual/Foreground',
        #                             '/Attribute/Visual/Background/Color/Black',
        #                             '/Sensory presentation/Visual/Rendering type/Screen/3D/Rift DK2',
        #                             '/Participant/Effect/Cognitive/Meaningful',
        #                             '/Participant/Effect/Visual/Foveal'),
        #     'feedback off': ('/Event/Category/Experimental stimulus/Instruction/Attend/',
        #                             '/Event/Label/targ_color_change',
        #                             '/Event/Description/A target sphere disappeared at the position of the hand when a subject touched a wall',
        #                             '/Item/3D Shape/Sphere',
        #                             '/Attribute/Offset',
        #                             '/Attribute/Visual/Color/White',
        #                             '/Attribute/Location/Screen/Center',
        #                             '/Attribute/Visual/Foreground',
        #                             '/Attribute/Visual/Background/Color/Black',
        #                             '/Sensory presentation/Visual/Rendering type/Screen/3D/Rift DK2',
        #                             '/Participant/Effect/Cognitive/Meaningful',
        #                             '/Participant/Effect/Visual/Foveal'),
        #     'standing baseline start': ('/Event/Category/Baseline measurement',
        #                                 'Attribute/Onset'),
        #     'standing baseline end': ('/Event/Category/Baseline measurement',
        #                               'Attribute/Offset'),
        # }

    def generate_list_of_controlled_randomized_trials(self, factor1, factor2, factorN):
        """Returns a list of randomized trials consisting of strings with values determined by factorial design.

        This abstractmethod serves as a reminder to properly implement the controlled randomization of trials
        in an experiment. Since it is abstract it has to be implemented by inheriting classes! The code below
        provides a head start to implement randomization of trials in a multi-factorial design.

        Args:
            factor1: [Array] of levels of first factor in study design, e.g. ['clockwise','counterclockwise']
            factor2: [Array] of levels of second factor in study design, e.g. ['fast','slow']
            factorN: [Array] of levels of Nth factor in study design, e.g. ['control','treatment']

        Returns: A list of randomized trials.

        """

        list_of_trials = []

        for level_factor1 in factor1:
            for level_factor2 in factor2:
                for level_factorN in factorN:
                    list_of_trials.append((level_factor1, level_factor1, level_factorN))

        random.shuffle(list_of_trials)

        return list_of_trials

    def experiment_procedure(self):
        """
        Logic of the general procedure of the experiment. To be added to the viztask scheduler, when experiment is run.

        This abstractmethod must clarify and define the procedural logic of the experiment. An example simple procedure would
        consist of a control block (baseline measurements) followed by a training session which is in turn followed by
        the test session.

        """