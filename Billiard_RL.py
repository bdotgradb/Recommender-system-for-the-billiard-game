
import pygame
import sys
from math import *
import random
import numpy as np
import time


class Ball:
	def __init__(self, x, y,speed, color, angle):
		self.x = x + radius
		self.y = y + radius
		self.color = color
		self.angle = angle
		self.speed = speed

	def draw(self):
		pygame.draw.ellipse(display, self.color, (self.x - radius, self.y - radius, radius*2, radius*2))


	def move(self):
		self.speed -= friction
		if self.speed <= 0:
			self.speed = 0

		self.x = self.x + self.speed*cos(radians(self.angle))
		self.y = self.y + self.speed*sin(radians(self.angle))

		if (self.x >= width + margin - radius):
			self.x = width + margin - radius
			self.angle = 180 - self.angle
		if (radius + margin >= self.x):
			self.x = radius + margin
			self.angle = 180 - self.angle
		if (self.y >= height + margin - radius):
			self.y = height + margin - radius
			self.angle = 360 - self.angle
		if (radius + margin >= self.y):
			self.y = radius + margin
			self.angle = 360 - self.angle

 
#Detection de collision
def collision(ball1, ball2):
	dist = ((ball1.x - ball2.x)**2 + (ball1.y - ball2.y)**2)**0.5
	if dist < radius*2:
		return True
	else:
		return False

# Physique simplifiée pour des premiers résultats (à améliorer)
def checkCollision(balls):
    for i in range(len(balls)):
        for j in range(len(balls) - 1, i, -1):
            if collision(balls[i], balls[j]):
            	if balls[i].x == balls[j].x: #A changer
            		angleIncl = 180
            	else:
	                u1 = balls[i].speed
	                u2 = balls[j].speed
	                

	                balls[i].speed = ((u1*cos(radians(balls[i].angle)))**2 + (u2*sin(radians(balls[j].angle)))**2)**0.5
	                balls[j].speed = ((u2*cos(radians(balls[j].angle)))**2 + (u1*sin(radians(balls[i].angle)))**2)**0.5

	                tangent = degrees((atan((balls[i].y - balls[j].y)/(balls[i].x - balls[j].x)))) + 90
	                angle = tangent + 90
	                    
	                balls[i].angle = (2*tangent - balls[i].angle)
	                balls[j].angle = (2*tangent - balls[j].angle)

	                balls[i].x += (balls[i].speed)*sin(radians(angle))
	                balls[i].y -= (balls[i].speed)*cos(radians(angle))
	                balls[j].x -= (balls[j].speed)*sin(radians(angle))
	                balls[j].y += (balls[j].speed)*cos(radians(angle))

def border():
    pygame.draw.rect(display, green, (0, 0, width + 2*margin, margin))
    pygame.draw.rect(display, green, (0, 0, margin, height + 2*margin))
    pygame.draw.rect(display, green, (width + margin, 0, margin, height + 2*margin))
    pygame.draw.rect(display, green, (0, height + margin, width + 2*margin, margin))

def close():
	pygame.quit()
	sys.exit()
# RL
def build_q_table(actions):
    table = np.zeros((1, len(actions)))
    return table
def update_qtable(qmatrix, action_index, R, currentState, nextState):
	q_predicted = qmatrix[currentState	,action_index]
	q_target = R + GAMMA*np.amax(qmatrix[nextState,:])
	qmatrix[currentState,action_index] += ALPHA * (q_target - q_predicted)
	return qmatrix
	
# Comments for epsilon varying over time and reward = -1 for bad moves 
def choose_action(qmatrix, nextState):
	# EPSILON = (time.time() - start_time)/120
	# print(EPSILON)
	if (np.random.uniform() > EPSILON) or (np.count_nonzero(qmatrix[nextState]) == 0):
		action_index = int(np.random.choice(len(qmatrix[0,:]),1))
		# if qmatrix[nextState, action_index] == -1:
		# 	print("denied action")
		# 	action_index = choose_action(qmatrix, nextState)
		print("random")
	else:
		action_index = qmatrix[nextState].argmax()
	return action_index

def poolTable(qmatrix, actions, action_index, State, State_index, Sindex, ball_pos, episode):
	loop = True
	yellowb_pos = (0.3*(width + 2*margin) - radius, 0.5*(height + 2*margin) - radius)	
	whiteb_pos = (0.3*(width + 2*margin) - radius, 0.65*(height + 2*margin) - radius)	
	redb_pos = (0.8*(width + 2*margin) - radius, 0.5*(height + 2*margin) - radius)
	init_ball_pos = [yellowb_pos, whiteb_pos, redb_pos]
	noBalls = 3
	balls = []

	# for i in range(noBalls):
	# 	newBall = Ball(random.randrange(0, width - 2*radius), random.randrange(0, height - 2*radius), 10, white, random.randrange(-180, 180))
	# 	balls.append(newBall)

	white_speed = actions[action_index][0]
	white_angle = actions[action_index][1]

	yellowb = Ball(ball_pos[0][0], ball_pos[0][1], 0, yellow, 0)	
	whiteb = Ball(ball_pos[1][0], ball_pos[1][1], white_speed, white, white_angle)	
	redb = Ball(ball_pos[2][0], ball_pos[2][1], 0, red, 0)	
	balls.append(yellowb)
	balls.append(whiteb)
	balls.append(redb)

	collWY = False
	collWR = False	

	nb_first_ep = 3
	nb_fast_ep = 60

	if (nb_first_ep < episode < nb_fast_ep):
		pygame.display.set_caption("Episode %d - Fast learning simulation until episode %d to see improvements" % (episode, nb_fast_ep))
	else: 
		pygame.display.set_caption("Episode %d" % (episode))
	while loop:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				close()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q: # => IN qwerty so press A to quit
					close()		
				if event.key == pygame.K_r:
					poolTable(qmatrix, actions, 0, State, State_index, Sindex, ball_pos, episode)
		if (whiteb.speed == 0 and redb.speed == 0 and yellowb.speed == 0):
			R = 0
			nextState = 0
			if (collWR == True and  collWY == True):
				R = 1
				ball_pos = [(yellowb.x - radius,yellowb.y - radius),(whiteb.x - radius,whiteb.y - radius),(redb.x - radius,redb.y - radius)]
				if State_index[State,action_index] == 0:
					newState = np.zeros((1,len(actions)))
					qmatrix = np.concatenate((qmatrix,newState))
					State_index[State,action_index] = Sindex
					Sindex += 1
					nextState = int(State_index[State,action_index])
				else:
					nextState = int(State_index[State,action_index])

			if R == 1:
				qmatrix = update_qtable(qmatrix, action_index, R, State, nextState)
				action_index = choose_action(qmatrix, nextState)
				print("Chosen action : %d"%(action_index))
				print(qmatrix)
				poolTable(qmatrix,actions, action_index, nextState, State_index, Sindex, ball_pos, episode)
			else:
				# qmatrix[State, action_index] = -1
				action_index = choose_action(qmatrix, nextState)
				print("Chosen action : %d"%(action_index))
				print(qmatrix)
				episode += 1
				poolTable(qmatrix,actions, action_index, nextState, State_index, Sindex, init_ball_pos, episode)

		display.fill(background)
		for i in range(noBalls):
			balls[i].draw()

		for i in range(noBalls):
			balls[i].move()

		if (collision(whiteb, redb)):
			collWR = True
		if (collision(whiteb, yellowb)):
			collWY = True
		checkCollision(balls)	
		border()


		pygame.display.update()
		if (nb_first_ep < episode < nb_fast_ep):
			clock.tick(1000000) # Increase FPS to simulate faster
		else:
			clock.tick(60)
		
start_time = time.time()
pygame.init()
width = 284*2
height = 142*2
margin = 10

display = pygame.display.set_mode((width + 2*margin, height + 2*margin))
clock = pygame.time.Clock() 
background = (20, 140, 59) #green
white = (236, 240, 241)
yellow = (244, 208, 63)
red = (203, 67, 53)
green = (40, 180, 99)
EPSILON = 0.9  # greedy police > 1 - pourcentage de chance de choisir une action aléatoire 
ALPHA = 0.1     # learning rate
GAMMA = 0.9    # discount factor

radius = 10
friction = 0.01

actions = []
for i in range(1,11):
	for j in range(-180,180,5):
		actions.append((i,j))
# actions = [(10,20),(5,25),(7,30)] good example to understand
episode = 1
qmatrix = build_q_table(actions)
action_index = action_index = int(np.random.choice(len(qmatrix[0,:]),1))
print("Initial random first action: %d" %(action_index))
State = 0
State_index = np.zeros((1000,len(actions)))
Sindex = 1
yellowb_pos = (0.3*(width + 2*margin) - radius, 0.5*(height + 2*margin) - radius)	
whiteb_pos = (0.3*(width + 2*margin) - radius, 0.65*(height + 2*margin) - radius)	
redb_pos = (0.8*(width + 2*margin) - radius, 0.5*(height + 2*margin) - radius)
init_ball_pos = [yellowb_pos, whiteb_pos, redb_pos]
poolTable(qmatrix, actions, action_index, State, State_index, Sindex, init_ball_pos, episode)


