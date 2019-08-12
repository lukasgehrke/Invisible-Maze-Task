"""
Mazes in different dimensions.

"""

import vizshape, viz, vizproximity

from Wall import Wall
from MazeUnit import MazeUnit
from MazeUnitShape import MazeUnitShape
from Landmark import Landmark


class Maze(object):

    def __init__(self, maze_type, poi_prox_manager):

        if maze_type == 'I' or maze_type == 'training':

            # adapt to lab specifics at BeMoBIL
            x_offset = 1
            z_offset = 5
            y_offset = .5

            self.walls = viz.add('resources/mazes/I.osgb')
            pos = self.walls.getPosition()
            self.walls.setPosition([pos[0]-x_offset, pos[1]+y_offset, pos[2]-z_offset])
            self.start_pos = [1.5-x_offset, 0, .5-z_offset]
            self.end_pos = [1.5-x_offset, 0, 9.5-z_offset]

        elif maze_type == 'L':

            # adapt to lab specifics at BeMoBIL
            x_offset = 3
            z_offset = 3
            y_offset = .5

            self.walls = viz.add('resources/mazes/L.osgb')
            pos = self.walls.getPosition()
            self.walls.setPosition([pos[0]-x_offset, pos[1]+y_offset, pos[2]-z_offset])
            self.start_pos = [1.5-x_offset, 0, .5-z_offset]
            self.end_pos = [6.5-x_offset, 0, 4.5-z_offset]

        elif maze_type == 'Z':

            # adapt to lab specifics at BeMoBIL
            x_offset = 3.5
            z_offset = 3
            y_offset = .5

            self.walls = viz.add('resources/mazes/Z.osgb')
            pos = self.walls.getPosition()
            self.walls.setPosition([pos[0]-x_offset, pos[1]+y_offset, pos[2]-z_offset])
            self.start_pos = [4.5-x_offset, 0, .5-z_offset]
            self.end_pos = [1.5-x_offset, 0, 6.5-z_offset]

        elif maze_type == 'U':

            # adapt to lab specifics at BeMoBIL
            x_offset = 3
            z_offset = 3
            y_offset = .5

            self.walls = viz.add('resources/mazes/U.osgb')
            pos = self.walls.getPosition()
            self.walls.setPosition([pos[0]-x_offset, pos[1]+y_offset, pos[2]-z_offset])
            self.start_pos = [1.5-x_offset, 0, .5-z_offset]
            self.end_pos = [4.5-x_offset, 0, .5-z_offset]

        elif maze_type == 'S':

            # adapt to lab specifics at BeMoBIL
            x_offset = 2
            z_offset = 3
            y_offset = .5

            self.walls = viz.add('resources/mazes/Z4.osgb')
            pos = self.walls.getPosition()
            self.walls.setPosition([pos[0]-x_offset, pos[1]+y_offset, pos[2]-z_offset])
            self.start_pos = [3.5-x_offset, 0, .5-z_offset]
            self.end_pos = [3.5-x_offset, 0, 5.5-z_offset]

        # add sensor for start position
        self.maze_start_position = MazeUnit('start_pos', edge_length=1, position=self.start_pos,
                                            proximity_manager=poi_prox_manager)
        self.maze_end_position = MazeUnit('end_pos', edge_length=1, position=self.end_pos,
                                            proximity_manager=poi_prox_manager)

        self.maze_start_sphere = vizshape.addSphere(.05)
        self.maze_start_sphere.setPosition([self.start_pos[0], 1.5, self.start_pos[2]])
        self.maze_start_sphere.color(viz.YELLOW)
        self.maze_start_sphere.visible(viz.OFF)
        self.maze_start_sphere_sensor = vizproximity.addBoundingSphereSensor(self.maze_start_sphere)

        self.maze_start_ground = vizshape.addPlane([1,1])
        self.maze_start_ground.setPosition(self.start_pos)
        self.maze_start_ground.visible(viz.OFF)

        # start arrow on the ground pointing in direction of start
        self.start_arrow = viz.add('resources/arrow.dae')
        self.start_arrow.visible(viz.OFF)
        self.start_arrow.setScale(2, 2, 2)
        self.start_arrow.color(viz.RED)
        self.start_arrow.setPosition([self.start_pos[0]+.12, 0, self.start_pos[2]+.25])
        self.start_arrow.setEuler([180,0,0])

        self.maze_end_ground = vizshape.addPlane([1,1])
        self.maze_end_ground.setPosition(self.end_pos)
        self.maze_end_ground.visible(viz.OFF)

        # add landmark
        #[BPA 2019-04-29] using the new landmark class now:
        ##### configuration:
        self.landmarkOffsetPosition = 10    #units straight ahead from start position
        self.landmarkResource = 'resources/lighthouse.dae'
        self.landmarkScale = [.03, .03, .03]
        #self.landmarkPosition = [self.start_pos[0], 0, self.start_pos[2]+self.landmarkOffsetPosition]
        self.landmarkPosition = [0.5, 0, self.start_pos[2]+self.landmarkOffsetPosition]
        self.global_landmark = viz.add(self.landmarkResource)

        self.global_landmark.visible(viz.OFF)
        self.global_landmark.setScale(self.landmarkScale[0], self.landmarkScale[1], self.landmarkScale[2])
        self.global_landmark.setPosition(self.landmarkPosition)