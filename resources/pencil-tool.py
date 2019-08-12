# idea: attach pencil to feed while walking around

"""  
Right mouse button clears the drawing.  
Middle mouse button changes color.  
Mouse movements control viewpoint orientation.  
Arrow Keys control viewpoint position.  
""" 

import viz
import vizshape
import vizinfo
vizinfo.InfoPanel(align=viz.ALIGN_LEFT_BOTTOM)

viz.setMultiSample(4)
viz.fov(60)
viz.go()

piazza = viz.add('piazza.osgb')
arrow = vizshape.addArrow(length=0.2, color = viz.RED)

from tools import pencil
tool = pencil.Pencil()

# update code for pencil
def update(tool):

	state = viz.mouse.getState()
	if state & viz.MOUSEBUTTON_RIGHT:
		tool.clear()
		vizfx.postprocess.removeEffect(effect)
	elif state & viz.MOUSEBUTTON_MIDDLE:
		tool.cycleColor()
	elif state & viz.MOUSEBUTTON_LEFT:
		tool.draw()
		vizfx.postprocess.addEffect(effect)

tool.setUpdateFunction(update)

#Link the pencil tool to an arrow  
#Then move the arrow in the reference frame of the viewpoint
from vizconnect.util import virtual_trackers
mouseTracker = virtual_trackers.ScrollWheel(followMouse = True)
mouseTracker.distance = 1
arrowLink = viz.link(mouseTracker,arrow)
arrowLink.postMultLinkable(viz.MainView)
viz.link(arrowLink,tool)

import vizcam
vizcam.FlyNavigate()

#Hide the mouse cursor
viz.mouse.setVisible(viz.OFF)

import vizfx.postprocess
from vizfx.postprocess.distort import BulgeEffect
effect = BulgeEffect(0.5)
