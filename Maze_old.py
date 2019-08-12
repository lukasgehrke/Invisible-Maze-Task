"""
Mazes in different dimensions.

"""

import vizshape, viz, vizproximity

from Wall import Wall
from MazeUnit import MazeUnit
from MazeUnitShape import MazeUnitShape


class Maze(object):

    def __init__(self, maze_type, poi_prox_manager, unit_prox_manager, convex_corner_prox_manager, concave_corner_prox_manager,
                 crit_corner_prox_manager):

        # if maze_type == 'training':
        #
        #     self.maze_units = []
        #     self.maze_walls = []
        #     self.maze_convex_corners = []
        #     self.maze_concave_corners = []
        #     self.maze_crit_corners = []
        #     self.crit_positions = []

        if maze_type == 'I' or maze_type == 'training':

            # small version
            # # introduce maze units (for unit events) and maze walls (for collisions)
            # self.maze_units = [[0, 0, -2], [0, 0, -1], [0, 0, 0], [0, 0, 1], [0, 0, 2]]
            # self.maze_walls = [[3, 4, 1, 'z', [0, 2, 3]],
            #                    [3, 4, 1, 'z', [0, 2, -3]],
            #                    [7, 4, 1, 'x', [1, 2, 0]],
            #                    [7, 4, 1, 'x', [-1, 2, 0]]]
            #
            # # position of 1x1 m prox sensors
            # self.maze_convex_corners = [[-1, 0, -3], [-1, 0, 3], [1, 0, 3], [1, 0, -3]]

            # introduce maze units (for unit events) and maze walls (for collisions)
            # start_pos = [0, 1.5, -2]

            # self.maze_units = [[0, 0, -2], [0, 0, -1], [0, 0, 0], [0, 0, 1], [0, 0, 2]]

            self.maze_units = [[0, 0, -4.5], [0, 0, -3.5], [0, 0, -2.5], [0, 0, -1.5], [0, 0, -0.5],
                               [0, 0, 4.5], [0, 0, 3.5], [0, 0, 2.5], [0, 0, 1.5], [0, 0, 0.5]]

# original larger layout
#            self.maze_walls = [[3, 4, 1, 'z', '+', [0, 2, 5.5]],
#                               [3, 4, 1, 'z', '-', [0, 2, -5.5]],
#                               [12, 4, 1, 'x', '+', [1, 2, 0]],
#                               [12, 4, 1, 'x', '-', [-1, 2, 0]]]
#
#            self.head_walls = [[3, 4, 1, 'z', '+', [0, 2, 5.8]],
#                               [3, 4, 1, 'z', '-', [0, 2, -5.8]],
#                               [12, 4, 1, 'x', '+', [1.3, 2, 0]],
#                               [12, 4, 1, 'x', '-', [-1.3, 2, 0]]]

# fat walls
            self.maze_walls = [[5, 4, 3, 'z', '+', [0, 2, 6.5]],
                               [5, 4, 3, 'z', '-', [0, 2, -6.5]],
                               [15, 4, 3, 'x', '+', [2, 2, 0]],
                               [15, 4, 3, 'x', '-', [-2, 2, 0]]]
                               
            self.head_walls = [[5, 4, 3, 'z', '+', [0, 2, 6.8]],
                               [5, 4, 3, 'z', '-', [0, 2, -6.8]],
                               [15, 4, 3, 'x', '+', [2.3, 2, 0]],
                               [15, 4, 3, 'x', '-', [-2.3, 2, 0]]]

            # position of 1x1 m prox sensors
            self.maze_convex_corners = [[-1, 0, -5.5], [-1, 0, 5.5], [1, 0, 5.5], [1, 0, -5.5]]
            self.maze_concave_corners = []
            self.concave_corner_size = 0
            
            self.maze_crit_corners = []
            start_pos = [0, 1.5, -4.5]

            self.start_sphere = vizshape.addSphere(0.2)
            self.start_sphere.setPosition(start_pos)
            self.start_sphere.visible(viz.OFF)
            self.maze_start_position = MazeUnit('start_pos_maze:I', edge_length=0.9, position=start_pos,
                                                crit_pos=None, proximity_manager=poi_prox_manager)
            self.path_length = len(self.maze_units)

        elif maze_type == 'L':

            # small version
            # # introduce maze units (for unit events) and maze walls (for collisions)
            # self.maze_units = [[0, 0, 2], [0, 0, 1], [0, 0, 0], [0, 0, -1], [0, 0, -2], [1, 0, -2], [2, 0, -2]]
            # self.maze_walls = [[3, 4, 1, 'z', [0, 2, 3]],
            #                    [5, 4, 1, 'x', [0.98, 2, 1]],
            #                    [7, 4, 1, 'x', [-1, 2, 0]],
            #                    [3, 4, 1, 'z', [2, 2, -1.02]],
            #                    [3, 4, 1, 'x', [3, 2, -2]],
            #                    [5, 4, 1, 'z', [1, 2, -3]]]
            #
            # # position of 1,01 x 1,01 m prox sensors
            # self.maze_convex_corners = [[-1, 0, -3], [-1, 0, 3], [1, 0, 3], [3, 0, -1], [3, 0, -3]]
            # self.maze_concave_corners = [[1, 0, -1]]
            #
            # start_pos = [0, 1.5, 2]

            # introduce maze units (for unit events) and maze walls (for collisions)
            self.maze_units = [[-2, 0, -3], [-2, 0, -2], [-2, 0, -1], [-2, 0, 0], [-2, 0, 1], [-2, 0, 2],
                               [-1, 0, 2], [0, 0, 2], [1, 0, 2], [2, 0, 2]]

# original layout
#            self.maze_walls = [[3, 4, 1, 'z', '-', [-2, 2, -4]],
#                               [8, 4, 1, 'x', '-', [-3, 2, -0.5]],
#                               [7, 4, 1, 'z', '+', [0, 2, 3]],
#                               [3, 4, 1, 'x', '+', [3, 2, 2]],
#                               [4.95, 4, 1, 'z', '-', [1, 2, 1]],
#                               #[6, 4, 1, 'z', '-', [1.5, 2, 1]],
#                               [5.95, 4, 1, 'x', '+', [-1, 2, -1.5]]]
#                               #[5, 4, 1, 'x', '+', [-1, 2, -2]]]
#                               #[7, 4, 1, 'x', '+', [-1, 2, -2]]]
#
#            self.head_walls = [[3, 4, 1, 'z', '-', [-2, 2, -4.3]],
#                               [8, 4, 1, 'x', '-', [-3.3, 2, -0.5]],
#                               [7, 4, 1, 'z', '+', [0, 2, 3.3]],
#                               [3, 4, 1, 'x', '+', [3.3, 2, 2]],
#                               [4.3, 4, 1, 'z', '-', [1, 2, 0.7]],
#                               #[6, 4, 1, 'z', '-', [1.5, 2, 1]],
#                               [5.3, 4, 1, 'x', '+', [-0.7, 2, -1.5]]]
#                               #[5, 4, 1, 'x', '+', [-1, 2, -2]]]
#                               #[7, 4, 1, 'x', '+', [-1, 2, -2]]]

# fat walls
            self.maze_walls = [[3, 4, 3, 'z', '-', [-2, 2, -5]],
                               [8, 4, 3, 'x', '-', [-4, 2, -0.5]],
                               [7, 4, 3, 'z', '+', [0, 2, 4]],
                               [3, 4, 3, 'x', '+', [4, 2, 2]],
                               #[4.97, 4, 3, 'z', '-', [1, 2, 0]],
                               [5, 4, 3, 'z', '-', [1, 2, 0]],
                               #[6, 4, 1, 'z', '-', [1.5, 2, 1]],
                               #[5.97, 4, 3, 'x', '+', [0, 2, -1.5]]]
                               [6, 4, 3, 'x', '+', [0, 2, -1.5]]]
                               #[5, 4, 1, 'x', '+', [-1, 2, -2]]]
                               #[7, 4, 1, 'x', '+', [-1, 2, -2]]]

            self.head_walls = [[3, 4, 3, 'z', '-', [-2, 2, -5.3]],
                               [8, 4, 3, 'x', '-', [-4.3, 2, -0.5]],
                               [7, 4, 3, 'z', '+', [0, 2, 4.3]],
                               [3, 4, 3, 'x', '+', [4.3, 2, 2]],
                               [4.3, 4, 3, 'z', '-', [1, 2, -0.3]],
                               #[6, 4, 1, 'z', '-', [1.5, 2, 1]],
                               [5.3, 4, 3, 'x', '+', [0.3, 2, -1.5]]]
                               #[5, 4, 1, 'x', '+', [-1, 2, -2]]]
                               #[7, 4, 1, 'x', '+', [-1, 2, -2]]]

            # position of 1,01 x 1,01 m prox sensors
            self.maze_convex_corners = [[-3, 0, -4], [-1, 0, -4], [-3, 0, 3], [3, 0, 3], [3, 0, 1]]

            # original layout
            # self.maze_concave_corners = [[-1, 0, 1]]
            #self.maze_concave_corners = [[0, 0, 0]]
            #self.concave_corner_size = 3.1

            # new concave corners with path shapes (29.05.2017)
            #self.maze_concave_corners = [[[-1.6, 1.6], [1.6, -1.6], [-1.6, -1.6]],
            #                             [[-1.6, 1.6], [1.6, -1.6], [1.6, 1.6]]]

            # updates 30.05.2017
            self.maze_concave_corners = [[[-1.6, 1.6], [-1.5, 1.5], [-1.15, 1.5], [-1.15, 1.15], [1.6, -1.6], [-1.6, -1.6]],
                                         [[-1.6, 1.6], [-1.5, 1.5], [-1.5, 1.15], [-1.15, 1.15], [1.6, -1.6], [1.6, 1.6]]]

            self.walls_to_ignore_idx = [[4], [5]]

            self.maze_crit_corners = [[-1.36, 0, 1.36]]
            self.crit_positions = [[-1.2, 0, 1.2]]

            start_pos = [-2, 1.5, -3]

            self.start_sphere = vizshape.addSphere(0.2)
            self.start_sphere.setPosition(start_pos)
            self.start_sphere.visible(viz.OFF)
            self.maze_start_position = MazeUnit('start_pos_maze:L', edge_length=0.9, position=start_pos, crit_pos=None,
                                                proximity_manager=poi_prox_manager)
            self.path_length = len(self.maze_units)

        elif maze_type == 'Z':

            # small version
            # # introduce maze units (for unit events) and maze walls (for collisions)
            # self.maze_units = [[2, 0, -2], [1, 0, -2], [0, 0, -2], [0, 0, -1], [0, 0, 0], [0, 0, 1], [0, 0, 2],
            #                    [-1, 0, 2], [-2, 0, 2]]
            #
            # self.maze_walls = [[5, 4, 1, 'z', [-1, 2, 3]],
            #                    [5, 4, 1, 'x', [0.98, 2, 1]],
            #                    [3, 4, 1, 'z', [2, 2, -1.02]],
            #                    [3, 4, 1, 'x', [3, 2, -2]],
            #                    [5, 4, 1, 'z', [1, 2, -3]],
            #                    [5, 4, 1, 'x', [-0.98, 2, -1]],
            #                    [3, 4, 1, 'z', [-2, 2, 1.02]],
            #                    [3, 4, 1, 'x', [-3, 2, 2]]
            #                    ]
            #
            # # position of 1,01 x 1,01 m prox sensors
            # self.maze_convex_corners = [[-3, 0, 1], [-3, 0, 3], [1, 0, 3], [-1, 0, -3], [3, 0, -1], [3, 0, -3]]
            # self.maze_concave_corners = [[1, 0, -1], [-1, 0, 1]]
            #
            # start_pos = [2, 1.5, -2]

            self.maze_units = [[1.5, 0, -3], [1.5, 0, -2], [1.5, 0, -1], [1.5, 0, 0], [0.5, 0, 0], [-0.5, 0, 0],
                               [-1.5, 0, 0], [-1.5, 0, 1], [-1.5, 0, 2], [-1.5, 0, 3]]

# original layout
#            self.maze_walls = [[3, 4, 1, 'z', '-', [1.5, 2, -4]],
#                               [3.95, 4, 1, 'x', '-', [0.5, 2, -2.5]],
#                               #[4, 4, 1, 'x', '-', [0.5, 2, -2.8]],
#                               [3.95, 4, 1, 'z', '-', [-1, 2, -1]],
#                               #[4, 4, 1, 'z', '-', [-1.3, 2, -1]],
#                               [6, 4, 1, 'x', '-', [-2.5, 2, 1.5]],
#                               [3, 4, 1, 'z', '+', [-1.5, 2, 4]],
#                               [3.95, 4, 1, 'x', '+', [-0.5, 2, 2.5]],
#                               #[4, 4, 1, 'x', '+', [-0.5, 2, 2.8]],
#                               [3.95, 4, 1, 'z', '+', [1, 2, 1]],
#                               #[4, 4, 1, 'z', '+', [1.3, 2, 1]],
#                               [6, 4, 1, 'x', '+', [2.5, 2, -1.5]]
#                               ]
#
#            self.head_walls = [[3, 4, 1, 'z', '-', [1.5, 2, -4.3]],
#                               [3.3, 4, 1, 'x', '-', [0.2, 2, -2.5]],
#                               #[4, 4, 1, 'x', '-', [0.5, 2, -2.8]],
#                               [3.3, 4, 1, 'z', '-', [-1, 2, -1.3]],
#                               #[4, 4, 1, 'z', '-', [-1.3, 2, -1]],
#                               [6, 4, 1, 'x', '-', [-2.8, 2, 1.5]],
#                               [3, 4, 1, 'z', '+', [-1.5, 2, 4.3]],
#                               [3.3, 4, 1, 'x', '+', [-0.2, 2, 2.5]],
#                               #[4, 4, 1, 'x', '+', [-0.5, 2, 2.8]],
#                               [3.3, 4, 1, 'z', '+', [1, 2, 1.3]],
#                               #[4, 4, 1, 'z', '+', [1.3, 2, 1]],
#                               [6, 4, 1, 'x', '+', [2.8, 2, -1.5]]
#                               ]

            self.maze_walls = [[3, 4, 3, 'z', '-', [1.5, 2, -5]],
                               #[3.97, 4, 2, 'x', '-', [0, 2, -2.5]],
                               [4, 4, 2, 'x', '-', [0, 2, -2.5]],
                               #[4, 4, 1, 'x', '-', [0.5, 2, -2.8]],
                               #[3.97, 4, 2, 'z', '-', [-1, 2, -1.5]],
                               [4, 4, 2, 'z', '-', [-1, 2, -1.5]],
                               #[4, 4, 1, 'z', '-', [-1.3, 2, -1]],
                               [6, 4, 3, 'x', '-', [-3.5, 2, 1.5]],
                               [3, 4, 3, 'z', '+', [-1.5, 2, 5]],
                               #[3.97, 4, 2, 'x', '+', [0, 2, 2.5]],
                               [4, 4, 2, 'x', '+', [0, 2, 2.5]],
                               #[4, 4, 1, 'x', '+', [-0.5, 2, 2.8]],
                               #[3.97, 4, 2, 'z', '+', [1, 2, 1.5]],
                               [4, 4, 2, 'z', '+', [1, 2, 1.5]],
                               #[4, 4, 1, 'z', '+', [1.3, 2, 1]],
                               [6, 4, 3, 'x', '+', [3.5, 2, -1.5]]
                               ]

            self.head_walls = [[3, 4, 3, 'z', '-', [1.5, 2, -5.3]],
                               [3.3, 4, 3, 'x', '-', [-0.8, 2, -2.5]],
                               #[4, 4, 1, 'x', '-', [0.5, 2, -2.8]],
                               [3.3, 4, 3, 'z', '-', [-1, 2, -2.3]],
                               #[4, 4, 1, 'z', '-', [-1.3, 2, -1]],
                               [6, 4, 3, 'x', '-', [-3.8, 2, 1.5]],
                               [3, 4, 3, 'z', '+', [-1.5, 2, 5.3]],
                               [3.3, 4, 3, 'x', '+', [0.8, 2, 2.5]],
                               #[4, 4, 1, 'x', '+', [-0.5, 2, 2.8]],
                               [3.3, 4, 3, 'z', '+', [1, 2, 2.3]],
                               #[4, 4, 3, 'z', '+', [1.3, 2, 1]],
                               [6, 4, 3, 'x', '+', [3.8, 2, -1.5]]
                               ]

            # position of 1,01 x 1,01 m prox sensors
            self.maze_convex_corners = [[0.5, 0, -4], [2.5, 0, -4], [-2.5, 0, -1], [-2.5, 0, 4], [-0.5, 0, 4],
                                        [2.5, 0, 1]]
            #self.maze_concave_corners = [[-0.5, 0, 1], [0.5, 0, -1]]
            #self.maze_concave_corners = [[0, 0, 1.5], [0, 0, -1.5]]
            #self.concave_corner_size = 2.1

            # new implementation 29.05.2017
            # updated 30.05.2017
            # self.maze_concave_corners = [[[-1.1, 0.4], [-1.1, 2.6], [1.1, 2.6]],
            #                              [[1.1, 2.6], [-1.1, 0.4], [1.1, 0.4]],
            #                              [[1.1, -0.4], [1.1, -2.6], [-1.1, -2.6]],
            #                              [[1.1, -0.4], [-1.1, -0.4], [-1.1, -2.6]]]

            self.maze_concave_corners = [[[1.1, 2.6], [-0.65, 0.85], [-0.65, 0.5], [-1, 0.5], [-1.1, 0.4], [-1.1, 2.6]],
                                         [[1.1, 2.6], [-0.65, 0.85], [-1, 0.85], [-1, 0.5], [-1.1, 0.4], [1.1, 0.4]],
                                         [[1.1, -0.4], [1, -0.5], [0.65, -0.5], [0.65, -0.85], [-1.1, -2.6], [1.1, -2.6]],
                                         [[1.1, -0.4], [1, -0.5], [1, -0.85], [0.65, -0.85], [-1.1, -2.6], [-1.1, -0.4]]]

            self.walls_to_ignore_idx = [[6], [5], [2], [1]]

            self.maze_crit_corners = [[-0.85, 0, 0.65], [0.85, 0, -0.65]]
            self.crit_positions = [[-0.7, 0, 0.8], [0.7, 0, -0.8]]

            start_pos = [1.5, 1.5, -3]
            self.start_sphere = vizshape.addSphere(0.2)
            self.start_sphere.setPosition(start_pos)
            self.start_sphere.visible(viz.OFF)
            self.maze_start_position = MazeUnit('start_pos_maze:Z', edge_length=0.9, position=start_pos, crit_pos=None,
                                                proximity_manager=poi_prox_manager)
            self.path_length = len(self.maze_units)

        elif maze_type == 'U':

            # small version
            # # introduce maze units (for unit events) and maze walls (for collisions)
            # self.maze_units = [[-2, 0, 2], [-2, 0, 1], [-2, 0, 0], [-2, 0, -1], [-1, 0, -1], [0, 0, -1], [1, 0, -1],
            #                    [2, 0, -1], [2, 0, 0], [2, 0, 1], [2, 0, 2]]
            # self.maze_walls = [[6, 4, 1, 'x', [-3, 2, 0.5]],
            #                    [3, 4, 1, 'z', [-2, 2, 3]],
            #                    [4, 4, 1, 'x', [-1.02, 2, 1.5]],
            #                    [3, 4, 1, 'z', [0, 2, -0.02]],
            #                    [4, 4, 1, 'x', [1.02, 2, 1.5]],
            #                    [3, 4, 1, 'z', [2, 2, 3]],
            #                    [6, 4, 1, 'x', [3, 2, 0.5]],
            #                    [7, 4, 1, 'z', [0, 2, -2]]
            #                    ]
            #
            # # position of 1,01 x 1,01 m prox sensors
            # self.maze_convex_corners = [[-3, 0, 3], [-1, 0, 3], [-3, 0, -2], [3, 0, 3], [1, 0, 3], [3, 0, -2]]
            # self.maze_concave_corners = [[-1, 0, 0], [1, 0, 0]]
            #
            # start_pos = [-2, 1.5, 2]

            # introduce maze units (for unit events) and maze walls (for collisions)
            self.maze_units = [[-1.5, 0, -1.5], [-1.5, 0, -0.5], [-1.5, 0, 0.5], [-1.5, 0, 1.5], [-0.5, 0, 1.5],
                               [0.5, 0, 1.5], [1.5, 0, 1.5], [1.5, 0, 0.5], [1.5, 0, -0.5], [1.5, 0, -1.5]]

# original layout
#            self.maze_walls = [[3, 4, 1, 'z', '-', [1.5, 2, -2.5]],
#                               [3.95, 4, 1, 'x', '-', [0.5, 2, -1]],
#                               [1.95, 4, 1, 'z', '-', [0, 2, 0.5]],
#                               [3.95, 4, 1, 'x', '+', [-0.5, 2, -1]],
#                               #[4, 4, 1, 'x', '-', [0.5, 2, -1.3]],
#                               #[1.4, 4, 1, 'z', '-', [0, 2, 0.5]],
#                               #[4, 4, 1, 'x', '+', [-0.5, 2, -1.3]],
#                               [3, 4, 1, 'z', '-', [-1.5, 2, -2.5]],
#                               [6, 4, 1, 'x', '-', [-2.5, 2, 0]],
#                               [6, 4, 1, 'z', '+', [0, 2, 2.5]],
#                               [6, 4, 1, 'x', '+', [2.5, 2, 0]]
#                               ]
#
#            self.head_walls = [[3, 4, 1, 'z', '-', [1.5, 2, -2.8]],
#                               [3.95, 4, 1, 'x', '-', [0.2, 2, -1]],
#                               [1, 4, 1, 'z', '-', [0, 2, 0.2]],
#                               [3.95, 4, 1, 'x', '+', [-0.2, 2, -1]],
#                               #[4, 4, 1, 'x', '-', [0.5, 2, -1.3]],
#                               #[1.4, 4, 1, 'z', '-', [0, 2, 0.5]],
#                               #[4, 4, 1, 'x', '+', [-0.5, 2, -1.3]],
#                               [3, 4, 1, 'z', '-', [-1.5, 2, -2.8]],
#                               [6, 4, 1, 'x', '-', [-2.8, 2, 0]],
#                               [6, 4, 1, 'z', '+', [0, 2, 2.8]],
#                               [6, 4, 1, 'x', '+', [2.8, 2, 0]]
#                               ]

            self.maze_walls = [[3, 4, 3, 'z', '-', [1.5, 2, -3.5]],
                               [3.97, 4, 1, 'x', '-', [0.5, 2, -1]],
                               [1.97, 4, 1, 'z', '-', [0, 2, 0.5]],
                               [3.97, 4, 1, 'x', '+', [-0.5, 2, -1]],
                               #[4, 4, 1, 'x', '-', [0.5, 2, -1.3]],
                               #[1.4, 4, 1, 'z', '-', [0, 2, 0.5]],
                               #[4, 4, 1, 'x', '+', [-0.5, 2, -1.3]],
                               [3, 4, 3, 'z', '-', [-1.5, 2, -3.5]],
                               [6, 4, 3, 'x', '-', [-3.5, 2, 0]],
                               [6, 4, 3, 'z', '+', [0, 2, 3.5]],
                               [6, 4, 3, 'x', '+', [3.5, 2, 0]]
                               ]

            self.head_walls = [[3, 4, 3, 'z', '-', [1.5, 2, -3.8]],
                               [3.97, 4, 1, 'x', '-', [0.2, 2, -1]],
                               [1, 4, 1, 'z', '-', [0, 2, 0.2]],
                               [3.97, 4, 1, 'x', '+', [-0.2, 2, -1]],
                               #[4, 4, 1, 'x', '-', [0.5, 2, -1.3]],
                               #[1.4, 4, 1, 'z', '-', [0, 2, 0.5]],
                               #[4, 4, 1, 'x', '+', [-0.5, 2, -1.3]],
                               [3, 4, 3, 'z', '-', [-1.5, 2, -3.8]],
                               [6, 4, 3, 'x', '-', [-3.8, 2, 0]],
                               [6, 4, 3, 'z', '+', [0, 2, 3.8]],
                               [6, 4, 3, 'x', '+', [3.8, 2, 0]]
                               ]                               

            # position of 1,01 x 1,01 m prox sensors
            self.maze_convex_corners = [[-2.5, 0, 2.5], [2.5, 0, 2.5], [-2.5, 0, -2.5], [2.5, 0, -2.5],
                                        [0.5, 0, -2.5], [-0.5, 0, -2.5]]

            #self.maze_concave_corners = [[-0.5, 0, 0.5], [0.5, 0, 0.5]]
            #self.concave_corner_size = 1.1

            # new implementation 29.05.2017
            self.maze_concave_corners = [[[1.1, -0.1], [1.1, 1.1], [1, 1], [0.65, 1], [0.65, 0.65], [-0.1, -0.1]],
                                         [[-1.1, -0.1], [-1.1, 1.1], [-1, 1], [-0.65, 1], [-0.65, 0.65], [0.1, -0.1]],
                                         [[0, 0], [0.65, 0.65], [1, 0.65], [1, 1], [1.1, 1.1], [-1.1, 1.1], [-1, 1], [-1, 0.65], [-0.65, 0.65]]]


            # achtung mehrere walls to ignore in U shape
            self.walls_to_ignore_idx = [[2], [2], [1, 3]]

            self.maze_crit_corners = [[0.85, 0, 0.85], [-0.85, 0, 0.85]]
            self.crit_positions = [[0.7, 0, 0.7], [-0.7, 0, 0.7]]

            start_pos = [-1.5, 1.5, -1.5]

            self.start_sphere = vizshape.addSphere(0.2)
            self.start_sphere.setPosition(start_pos)
            self.start_sphere.visible(viz.OFF)
            self.maze_start_position = MazeUnit('start_pos_maze:U', edge_length=0.9, position=start_pos, crit_pos=None,
                                                proximity_manager=poi_prox_manager)
            self.path_length = len(self.maze_units)

        # currently unused, keep for later changes in maze configurations
        # elif maze_type == 'T':
        #
        #     # introduce maze units (for unit events) and maze walls (for collisions)
        #     self.maze_units = [[0, 0, 2], [0, 0, 1], [0, 0, 0], [0, 0, -1], [0, 0, -2], [1, 0, -2], [2, 0, -2],
        #                        [-1, 0, -2], [-2, 0, -2]]
        #
        #     self.maze_walls = [[5, 4, 1, 'x', [-0.99, 2, 1]],
        #                        [3, 4, 1, 'z', [0, 2, 3]],
        #                        [5, 4, 1, 'x', [0.99, 2, 1]],
        #                        [3, 4, 1, 'z', [2, 2, -1.02]],
        #                        [3, 4, 1, 'x', [3, 2, -2]],
        #                        [7, 4, 1, 'z', [0, 2, -3]],
        #                        [3, 4, 1, 'x', [-3, 2, -2]],
        #                        [3, 4, 1, 'z', [-2, 2, -1.02]]
        #                        ]
        #
        #     # position of 1,01 x 1,01 m prox sensors
        #     self.maze_convex_corners = [[-1, 0, 3], [1, 0, 3], [3, 0, -1], [3, 0, -3], [-3, 0, -1], [-3, 0, -3]]
        #     self.maze_concave_corners = [[-1, 0, -1], [1, 0, -1]]
        #
        #     start_pos = [0, 1.5, 2]
        #
        #     self.start_sphere = vizshape.addSphere(0.2)
        #     self.start_sphere.setPosition(start_pos)
        #     self.start_sphere.visible(viz.OFF)
        #     self.maze_start_position = MazeUnit('start_pos_maze:T', edge_length=0.5, position=start_pos,
        #                                         proximity_manager=poi_prox_manager)
        #     self.path_length = len(self.maze_units)
        #
        # elif maze_type == '+':
        #
        #     self.maze_units = [[0, 0, -2], [0, 0, -1], [0, 0, 0], [0, 0, 1], [0, 0, 2], [-2, 0, 0], [-1, 0, 0],
        #                        [1, 0, 0], [2, 0, 0]]
        #
        #     self.maze_walls = [[3, 4, 1, 'z', [0, 2, 3]],
        #                        [3, 4, 1, 'x', [-1, 2, 2]],
        #                        [3, 4, 1, 'x', [1, 2, 2]],
        #                        [3, 4, 1, 'x', [3, 2, 0]],
        #                        [3, 4, 1, 'z', [2, 2, 1]],
        #                        [3, 4, 1, 'z', [2, 2, -1]],
        #                        [3, 4, 1, 'z', [0, 2, -3]],
        #                        [3, 4, 1, 'x', [-1, 2, -2]],
        #                        [3, 4, 1, 'x', [1, 2, -2]],
        #                        [3, 4, 1, 'x', [-3, 2, 0]],
        #                        [3, 4, 1, 'z', [-2, 2, 1]],
        #                        [3, 4, 1, 'z', [-2, 2, -1]],
        #                        ]
        #
        #     # position of 1,01 x 1,01 m prox sensors
        #     self.maze_convex_corners = [[-1, 0, -3], [-1, 0, 3], [1, 0, 3], [1, 0, -3], [-3, 0, 1], [-3, 0, -1],
        #                                 [3, 0, 1], [3, 0, -1]]
        #     self.maze_concave_corners = [[1, 0, 1], [-1, 0, 1], [-1, 0, -1], [1, 0, -1]]
        #
        #     start_pos = [0, 1.5, 2]
        #     self.start_sphere = vizshape.addSphere(0.2)
        #     self.start_sphere.setPosition(start_pos)
        #     self.start_sphere.visible(viz.OFF)
        #     self.maze_start_position = MazeUnit('start_pos_maze:U', edge_length=0.5, position=start_pos,
        #                                         proximity_manager=poi_prox_manager)
        #     self.path_length = len(self.maze_units)

        # create list for maze walls
        self.maze_walls_list = []
        # create maze walls and add to list
        for wall in self.maze_walls:
            new_wall = Wall('wall_id:'+str(wall), wall_length=wall[0], wall_height=wall[1], wall_depth=wall[2],
                            orientation=wall[3], feedback_dir=wall[4], position=wall[5], visible=False)
            self.maze_walls_list.append(new_wall)

        # create head walls and add to list
        self.maze_head_wall_list = []
        for wall in self.head_walls:
            new_wall = Wall('head_wall', wall_length=wall[0], wall_height=wall[1], wall_depth=wall[2],
                            orientation=wall[3], feedback_dir=wall[4], position=wall[5], visible=False)
            self.maze_head_wall_list.append(new_wall)

        self.maze_units_list = []
        for maze_unit in self.maze_units:
            new_maze_unit = MazeUnit('maze_unit_id:' + str(maze_unit), edge_length=1, position=maze_unit,
                                     crit_pos=None, proximity_manager=unit_prox_manager)
            self.maze_units_list.append(new_maze_unit)

        self.maze_convex_corners_list = []
        for convex_corner in self.maze_convex_corners:
            new_convex_corner = MazeUnit('convex_corner_id:' + str(convex_corner), edge_length=1.1,
                                         position=convex_corner, crit_pos=None, proximity_manager=convex_corner_prox_manager)
            self.maze_convex_corners_list.append(new_convex_corner)

        self.maze_concave_corners_list = []
        for concave_corner in self.maze_concave_corners:
        # original layout
        #            new_concave_corner = MazeUnit('concave_corner_id:' + str(concave_corner), edge_length=1.1,
        #                                         position=concave_corner, crit_pos=None, proximity_manager=concave_corner_prox_manager)

#             new_concave_corner = MazeUnit('concave_corner_id:' + str(concave_corner), edge_length=self.concave_corner_size,
#                                          position=concave_corner, crit_pos=None, proximity_manager=concave_corner_prox_manager)
#             self.maze_concave_corners_list.append(new_concave_corner)

            # todo sensor erstellung polygon area

            new_concave_corner = MazeUnitShape('concave_corner_id:'+str(concave_corner), concave_corner, concave_corner_prox_manager)
            # #verts = [[0, 0], [1, 1], [0, 1.5], [-2, 2], [-1, 1], [-2, 0.5]]
            # sensor = vizproximity.Sensor(vizproximity.PolygonArea(concave_corner), None)
            # # and add to vizard proximity manager
            # concave_corner_prox_manager.addSensor(sensor)
            self.maze_concave_corners_list.append(new_concave_corner)

        self.maze_crit_corners_list = []
        i = 0
        for crit_corner in self.maze_crit_corners:
            print self.crit_positions[i]
            new_crit_corner = MazeUnit('crit_corner_id:' + str(crit_corner), edge_length=0.33,
                                       position=crit_corner, crit_pos=self.crit_positions[i],
                                       proximity_manager=crit_corner_prox_manager)
            self.maze_crit_corners_list.append(new_crit_corner)
            i = i + 1
