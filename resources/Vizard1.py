viz.go()
viz.add('ground.osgb')

def reward():
	progress = 10
	max_progress = 15

	nr_long_touch = 10
	nr_head_touch = 5
	time = 250
	new_progress = progress/float(max_progress)

	start_reward = 200

	# calculate reward/penalty
	penalty_long_touch = 2
	penalty_head_touch = 5
	touch_penalty = (nr_long_touch*penalty_long_touch)+(nr_head_touch*penalty_head_touch)
	tmp_reward = start_reward - touch_penalty

	if time < 300:
		tmp_reward += 50

	reward = int((tmp_reward * new_progress)*0.1)

	m_long_touch = 'nr_long_touch:' + str(nr_long_touch) + ','
	m_head_touch = 'nr_head_touch:' + str(nr_head_touch) + ','
	m_progress = 'progress:' + str(progress) + ','
	m_time = 'time' + str(time) + ','
	data = m_long_touch + m_head_touch + m_progress + m_time
	#markerstream.push_sample(data)

	for elem in range(reward):
		new_y = elem/float(100) - 0.15	
		coin = viz.add('model.dae', cache=viz.CACHE_CLONE)
		coin_link = viz.link(viz.MainView, coin)
		coin_link.preTrans([0, new_y, 0.5])

vizact.onkeydown(' ', reward)

def off(obj):
	obj.visible(viz.OFF)

vizact.onkeydown('a', off, coin)