import viz, vizproximity, vizshape, vizact, viztask
from tools import pencil

import math, random
from BaseScene import BaseScene


class ProbingNavigationScene(BaseScene):
    """
    Scene of the Spot Rotation Experiment.

    Contains graphical models of the 3D environment. Makes use of BaseClass Scene to set some behavior and
    visual for the scene.

    """
    def __init__(self):

        super(ProbingNavigationScene, self).__init__()

        self.world = viz.add('ground.osgb')

        self.walls = []
        self.wall_names = ['left', 'right', 'front', 'back']
        self.wall_sizes = []
        self.wall_positions = [['']]
        self.wall_orientations = []

        # create pencil
        self.drawing_tool = pencil.Pencil()
        self.drawing_tool.setUpdateFunction(self.update_pencil(self.drawing_tool))

        for wall in range(4):

            wall = super(ProbingNavigationScene, self).add_wall(self.wall_names[wall], [4, 4, 4], )
            self.walls.append(wall)

            # todos
            # create drawing tool and pencil 3D object for drawing and link the two
            # self.draw_tool = super(SpotRotationScene, self).add_pencil()
            # self.pen = vizshape.addArrow(length=0.2, color=viz.RED)

            # for testing: create virtual tracker object
            # from vizconnect.util import virtual_trackers
            # mouseTracker = virtual_trackers.ScrollWheel(followMouse=True)
            # mouseTracker.distance = 1

            # link the trackers and the pen
            # super(SpotRotationScene, self).link_pencil(self.pen, mouseTracker, self.draw_tool)

            # when drawing: call update function
            # self.scene.draw_tool.setUpdateFunction(self.scene.update_pencil)

    @staticmethod
    def add_pencil():
        """

        Returns:

        """

        from tools import pencil
        draw_tool = pencil.Pencil()

        return draw_tool

    @staticmethod
    def link_pencil(pencil_3d_object, tracker, tool):
        """

        Args:
            pencil_3d_object:
            tracker:
            tool:

        Returns:

        """

        draw_link = viz.link(tracker, pencil_3d_object)
        draw_link.postMultLinkable(viz.MainView)

        viz.link(draw_link, tool)

    @staticmethod
    def update_pencil(tool):
        """

        Args:
            tool:

        Returns:

        """

        state = viz.mouse.getState()
        if state & viz.MOUSEBUTTON_LEFT:
            tool.draw()
        if state & viz.MOUSEBUTTON_RIGHT:
            tool.project()
        if state & viz.MOUSEBUTTON_MIDDLE:
            tool.cycleColor()

    @staticmethod
    def add_wall(name, size_xy, position, orientation, vis, proximity, scale):
        """
        Adds a maze wall object and returns it. Optionally equipped with a bounding proximity sensor.

        Args:
            name: name of the wall object
            size_xy: length of the wall object in x, y direction
            position: x, y, z position of the wall object
            orientation: Orientation values to set "pointing" direction of wall, i.e. vizshape.AXIS_X / Y / Z
            [Euler orientation values to set "pointing" direction of wall]
            vis: viz.ON or viz.OFF
            proximity: if True create PathArea proximity sensor
            [if True create BoundingBoxSensor proximity sensor around the wall]
            scale: scale factor or radius of PathArea sensor
            [scale factor or size of BoundingBoxSensor]

        Returns: a wall 3D object with optional BoundingBoxSensor proximity sensor.

        """

        wall = vizshape.addPlane(size=size_xy, axis=orientation)
        wall.name = name
        wall.setPosition(position)
        wall.visible(vis)
        wall.cullFace(True)

        wall.collideMesh()
        wall.disable(viz.DYNAMICS)

        # works only for 90 degree orientation steps, otherwise rotation of pre-created walls would be necessary
        # (-> programmers can't decide)

        normal_vector = [0, 0, 0]
        normal_vector[abs(orientation) - 1] = orientation / abs(orientation)

        if proximity:
            # wall.sensor = vizproximity.addBoundingBoxSensor(wall, scale=scale)
            wall.sensor = vizproximity.sensor(vizproximity.PathArea((wall[0], 0), radius=scale), None)

        return [wall, normal_vector]

        # register callbacks: manager.onEnter(sensor, enter_sphere, sphere, color)
        # --> see vizard demo experiment

    @staticmethod
    def read_maze_config(file_to_read):
        """

        wallSizes = [(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3)]
        wallDirections = [-vizshape.AXIS_Z,-vizshape.AXIS_Z,-vizshape.AXIS_X,-vizshape.AXIS_X,vizshape.AXIS_Z,vizshape.AXIS_Z,vizshape.AXIS_X,vizshape.AXIS_X]
        wallPositions = [(2.5,1.5,1),(-2.5,1.5,1),(1,1.5,2.5),(1,1.5,-2.5),(2.5,1.5,-1),(-2.5,1.5,-1),(-1,1.5,-2.5),(-1,1.5,2.5)]

        """

        try:
            from configparser import ConfigParser
        except ImportError:
            from ConfigParser import ConfigParser  # ver. < 3.0

        # instantiate
        config = ConfigParser()

        # parse existing file
        config.read(file_to_read)

        # read values from a section
        wall_sizes = config.get('section_a', 'wall_size')
        wall_directions = config.get('section_a', 'wall_directions')
        wall_positions = config.get('section_a', 'wall_positions')

        wall_sizes = wall_sizes.split(',')
        wall_directions = wall_directions.split(',')
        wall_positions = wall_positions.split(',')

        maze = [wall_sizes, wall_directions, wall_positions]

        return maze

    @staticmethod
    def create_maze(wall_sizes, wall_directions, wall_positions):
        """


        Args:
            wall_sizes:
            wall_directions:
            wall_positions:

        Returns:

        """

        maze_walls = []
        number_of_walls = len(wall_positions)

        for wall in range(number_of_walls):
            next_wall = BaseScene.add_wall('wall_number' + str(wall), wall_sizes(wall), wall_positions(wall),
                                           viz.ON, True, scale=0.25)
            maze_walls.append(next_wall)

        return maze_walls

    @staticmethod
    def play_bounce_vid(video_position, video_name, video_length):
        """
        Plays a video at a given position in the 3D world for an indicated length.

        Example:
            bounceVid = viz.add('testPNGtoRAW_multi.avi',loop=0,play=0)
            bounceVid.setRate(myRate)
            self.collisionPoint = [iSectX,iSectY,iSectZ]
            viztask.schedule(play_bounce_vid(self.collisionPoint, bounceVid))

        Args:
            video_position: [x, y, z] position where the video should be displayed in the world
            video_name: name of the video file to play (.avi works, others not tested)
            video_length: duration of the video to play

        """

        video_position[2] = video_position[2] - .05

        quad = viz.addTexQuad(texture=video_name, pos=video_position)
        # quad.zoffset(-15)
        video_name.play()

        yield viztask.waitTime(video_length)
        quad.remove()

    @staticmethod
    def on_wall_collision(info):
        """
        This event is generated when the viewpoint collides with an object.
        Viewpoint collision must be enabled for the event to be generated.

        Example:
            viz.callback(viz.COLLISION_EVENT, on_wall_collision)

        Args:
            info: An intersect info object containing details of the collision.

        Returns: [[x,y,z] position of collision, [x,y,z] normal vector of collision point]

        """

        print('collided with object ', info.object)

        return [info.point, info.normal]

class VisualFeedback(viz.ActionClass):
    """
    Visual Feedback of the probing navigation.

    Class inherits from Vizard ActionClass.
    """

    def begin(self):
        pass

    def update(self):
        pass

    def end(self):
        pass