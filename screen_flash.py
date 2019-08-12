"""Simple module to flash the screen, works on Oculus"""

import viz
import vizact
import vizshape


class Flasher(object):
	"""Flasher class, requires a viz.VizWindow object be passed in"""
	def __init__(self, window=None, clientMask=viz.MASTER, color=viz.WHITE):
		if window is None:
			window = viz.MainWindow
		view = window.getView()
		self._color = color
		self._clientMask = clientMask
		# Add red quad to flash screen after falling
		self._flashSphere = vizshape.addSphere(10.0, flipFaces=True)
		link = viz.link(view, self._flashSphere)
		link.preTrans([0, 0, 10.1])
		self._flashSphere.color(self._color)
		self._flashSphere.visible(False)
		self._flashSphere.renderOnlyToWindows([window])

	def flash(self):
		"""Flashes screen red and animates blur effect"""
		with viz.cluster.MaskedContext(self._clientMask):
			self._flashSphere.visible(True)
			self._flashSphere.color(self._color)
			self._flashSphere.disable(viz.LIGHTING)
			self._flashSphere.disable(viz.SHADOWS)
			self._flashSphere.disable(viz.SHADOW_CASTING)
			self._flashSphere.enable(viz.BLEND)
			self._flashSphere.disable(viz.DEPTH_TEST)
			self._flashSphere.disable(viz.DEPTH_WRITE)
			self._flashSphere.alpha(0.5)
			self._flashSphere.drawOrder(101, bin=viz.BIN_TRANSPARENT)
		fade_out = vizact.fadeTo(0, begin=.3, time=1)
		self._flashSphere.runAction(vizact.sequence(fade_out, vizact.method.visible(False)))