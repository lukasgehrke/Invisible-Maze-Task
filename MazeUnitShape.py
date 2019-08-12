import vizproximity


class MazeUnitShape(object):
    """

    """

    def __init__(self, name, vertices, proximity_manager):
        """

            Args:
                name:
                edge_length:
                position:
                proximity_manager:

        """

        self.name = name
        self.proximity_manager = proximity_manager

        # create ground wall proximity sensor / 0.6 added due to wall thickness
        self.ground = vizproximity.Sensor(vizproximity.PolygonArea(vertices), None)

        # and add to vizard proximity manager
        proximity_manager.addSensor(self.ground)