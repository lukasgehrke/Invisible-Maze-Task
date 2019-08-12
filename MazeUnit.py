import vizproximity


class MazeUnit(object):
    """

    """

    def __init__(self, name, edge_length, position, proximity_manager):
        """

            Args:
                name:
                edge_length:
                position:
                proximity_manager:

        """

        self.name = name
        self.edge_length = edge_length
        self.proximity_manager = proximity_manager
        self.position = position

        # remove y position for proximity sensor which continues indefinitely along y axis
        self.pos_xz = self.position[0], self.position[2]

        # create ground wall proximity sensor / 0.6 added due to wall thickness
        self.ground = vizproximity.Sensor(vizproximity.RectangleArea([edge_length, edge_length],
                                                                     center=self.pos_xz), None)

        # and add to vizard proximity manager
        #proximity_manager.addSensor(self.ground)