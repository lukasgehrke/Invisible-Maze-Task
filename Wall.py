import viz


class Wall(object):
    """

    """

    def __init__(self, name, wall_length, wall_height, wall_depth, orientation, feedback_dir, position, visible=False):
        """

            Args:
                name:
                wall_length:
                wall_height:
                wall_depth
                position:
                orientation:
                visible:

        """

        # create collision wall object
        self.wall_object = viz.add('box.wrl', scale=[wall_length, wall_height, wall_depth])
        self.wall_object.collideBox()
        self.wall_object.disable(viz.DYNAMICS)
        self.wall_object.enable(viz.COLLIDE_NOTIFY)

        self.wall_object.name = name
        self.wall_object.wall_length = wall_length
        self.wall_object.wall_height = wall_height
        self.wall_object.wall_depth = wall_depth
        self.wall_object.orientation = orientation

        # feedback direction parameter: can be + or - on an axis or 0 if no problem as is
        self.wall_object.feedback_dir = feedback_dir

        self.wall_object.position = position

        # make wall invisible
        if visible:
            self.wall_object.alpha(1)
        else:
            self.wall_object.alpha(0)

        if orientation == 'x':
            ori = [90, 0, 0]
            self.wall_object.color(viz.BLUE) # change color of x walls if visible
        elif orientation == 'z':
            ori = [0, 0, 0]

        self.wall_object.setPosition(position)
        self.wall_object.setEuler(ori)