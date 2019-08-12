import viz

class Landmark(object):
	
	def __init__(self, resourcePath, position, scale, scope):
		"""
		Args:
			resourcePath: string with path to the resource model
			position: position (depending on scope)
			scale: scale[float x, float y, float z] of the object
			scope: string, can be "local" oder "global"
		"""
		self.resource = resourcePath
		self.position = position
		self.scale = scale
		self.scope = scope
		
		self.start()
		
	
	def start(self):
		viz.add(self.resource)
		self.visible(viz.OFF)
		self.setScale(self.scale[0], self.scale[1], self.scale[2])
		
		if self.scope == 'global':
			self.setPosition(self.position, viz.ABS_GLOBAL)
		elif self.scope == 'local':
			self.setPosition(self.position, viz.ABS_LOCAL)
		else:
			print("ERROR: Could not set position of landmark object because of undefined scope '" + str(scope) + "'. Scope must be 'local' or 'global'.")