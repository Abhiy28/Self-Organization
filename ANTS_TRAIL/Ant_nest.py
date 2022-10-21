from manim import *

a = np.array([1, 0, 0])
def RandomVel():
    th = np.random.uniform(-3.14, 3.14)
    ROT3D = np.array([[np.cos(th), np.sin(th), 0], [-np.sin(th), np.cos(th), 0], [0, 0, 0]])
    vel = np.matmul(ROT3D, a)
    return vel



N = 70  # number of ants
'''We start with some initial pheromones'''
M = 10

sa = 0.05  # size of ants
speed = 2  # speed of ants
size = 0.2*sa  # size of the pheromone representation
T_e = 6  # Time of evaporation

'''------------Canvas Configuration-------------------'''
xl = -7.11111111
xr = 7.1037037
yu = 4
yd = -4
resx = int(1080/(sa*50))
resy = int(1920/(sa*50))
del_x = (xr-xl)/resx
del_y = (yu-yd)/resy
Env = np.zeros((resx, resy), dtype=int)    #Environment matrix that sort of keeps track of pheromone density

'''-----------------------------------------------'''

PoissonWandering = 0.03  # Exploratory part of ant motion. Ranges from 0 to 1
GaussVariance = 0.01
GaussMean = 0

# Defining the range of vision by R and Theta ... Detecting a pheromone particle

Theta = np.pi / 2 
R = 15 * sa
r = np.linspace(0, R, int(R * 50))
lam_r = 0.4*speed  # Pheromone deposition rate
lam_t = 1 # Trail recruitment rate

'''-------------------------------------------------'''
pheromones_time = np.zeros(M)


def ReturnIndex(pos):
    return [int((pos[0]-xl)/del_x)%resx, int((pos[1]-yd)/del_y)%resy]


def ReturnNeighbourCoords(angles, p):
    M = np.ravel(np.outer(r, np.cos(angles))) + p[0]
    N = np.ravel(np.outer(r, np.sin(angles))) + p[1]
    return zip(M, N)


def wondering(ANT):
    th = GaussVariance * np.random.randn() + GaussMean
    ROT3D = np.array([[np.cos(th), np.sin(th), 0], [-np.sin(th), np.cos(th), 0], [0, 0, 0]])
    ANT.vel = np.matmul(ANT.vel, ROT3D)
    return ANT


def Detecting_Walls(ANT):
    # dth = np.random.uniform(-np.pi/4, np.pi/4)
    v = np.array(ANT.pos < np.array([xl, yd, 0]), dtype=int) - np.array(np.array([xr, yu, 0]) < ANT.pos,
                                                                                  dtype=float)
    ANT.pos = np.array([xr*v[0], yu*v[1], 0])+np.array([ANT.pos[0]*(1-v[0]**2), ANT.pos[1]*(1-v[1]**2), 0])
        #ROT3D = np.array([[np.cos(dth), np.sin(dth), 0], [-np.sin(dth), np.cos(dth), 0], [0, 0, 0]])
        #ANT.vel = np.matmul(-ANT.vel, ROT3D)

    return ANT


def Trial_recruitment(ANT):
    distribution = ANT.neighbour()
    if any(distribution):
        idn = np.argmax(distribution)
        #distribution = distribution / np.sum(distribution)
        t = [-np.pi / 6, 0, np.pi / 6]
        th = t[idn]
        M = np.array([[np.cos(th), np.sin(th), 0], [-np.sin(th), np.cos(th), 0], [0, 0, 0]])
        ANT.vel = np.matmul(M, ANT.vel)
        return ANT


def Pheromone_deposition(Mobject, ANT):
    global pheromones_time
    pos = ANT.pos
    Mobject.add(Dot(pos, color=TEAL_A, radius=size))
    pheromones_time = np.append(pheromones_time, np.zeros(1))
    indx = ReturnIndex(pos)
    Env[indx[0], indx[1]] += 1

    return Mobject


def Update_pheromones(Mobject, dt):
    global pheromones_time
    s = len(Mobject)
    pheromones_time += dt
    rl = VGroup()
    t = np.nonzero(pheromones_time == 6)
    for i in t[0]:
        rl.add(Mobject[i])
    for r in rl:
        indx = ReturnIndex(r.get_center())
        Env[indx[0], indx[1]] -= 1
        Mobject -= r
    pheromones_time = np.delete(pheromones_time, np.nonzero(t))


    ind = np.random.uniform(0, 1, N)
    for i in np.nonzero(ind < lam_r)[0]:
        Pheromone_deposition(Mobject, ANTS_object[i])

'''Initialization of ants'''

POS = np.array([[np.random.uniform(xl, xr),
                 np.random.uniform(yd, yu), 0] for i in range(N)])  # Random initial position of ants
VEL = speed * np.array([RandomVel() for i in range(N)])  # Initial velocities of ants in random directions

'''Initialization of pheromones'''

PheromonePosition = np.array([[np.random.uniform(xl, xr), np.random.uniform(yd, yu), 0] for i in range(M)])

pheromones = VGroup()

pheromones.add_updater(Update_pheromones)

for i in range(M):
    pheromones.add(Dot(PheromonePosition[i], color=TEAL_A, radius=size))
    Env[ReturnIndex(PheromonePosition[i])[0], ReturnIndex(PheromonePosition[i])[1]] += 1


'''___'''


class Ant:
    def __init__(self, pos, vel, i):
        self.rep = Dot(pos, color=BLACK, radius=sa)
        self.pos = pos
        self.vel = vel
        self.label = i
        self.t = 0

    def neighbour(self):

        v = self.vel/speed
        p = self.pos
        if v[1] >= 0:
            phi = np.arccos(np.dot(v, [1, 0, 0]))
        else:
            phi = np.pi - np.arccos(np.dot(v, [1, 0, 0]))

        left_angle = np.linspace(phi + Theta / 3, phi + Theta, int(Theta * R * 20))
        middle_angle = np.linspace(phi - Theta / 3, phi + Theta / 3, int(Theta * R * 20))
        right_angle = np.linspace(phi - Theta, phi - Theta / 3, int(Theta * R * 20))
        middle_neighbour_indices = np.array([ReturnIndex(k)
                                             for k in np.array(list(ReturnNeighbourCoords(middle_angle, p)))])
        left_neighbour_indices = np.array([ReturnIndex(k)
                                           for k in np.array(list(ReturnNeighbourCoords(left_angle, p)))])
        right_neighbour_indices = np.array([ReturnIndex(k)
                                            for k in np.array(list(ReturnNeighbourCoords(right_angle, p)))])

        left_pher_num = np.sum(Env[left_neighbour_indices[:, 0], left_neighbour_indices[:, 1]])
        right_pher_num = np.sum(Env[right_neighbour_indices[:, 0], right_neighbour_indices[:, 1]])
        middle_pher_num = np.sum(Env[middle_neighbour_indices[:, 0], middle_neighbour_indices[:, 1]])

        return [left_pher_num, middle_pher_num, right_pher_num]

    def motion(self, Mobject, dt):
        self.pos += self.vel * dt
        self.t += dt

        if any(self.pos < np.array([xl, yd, 0])) or any(np.array([xr, yu, 0]) < self.pos):
            Detecting_Walls(self)

        a = np.random.uniform()
        if a < PoissonWandering:
            wondering(self)

        b = np.random.uniform()
        if b < lam_t:
            Trial_recruitment(self)
        Mobject.move_to(self.pos)


ANTS_object = [Ant(POS[i], VEL[i], i) for i in range(N)]

ANTS = VGroup()
for i in range(N):
    ANTS.add(ANTS_object[i].rep.add_updater(ANTS_object[i].motion))


'''____'''


class AntTrail(Scene):
    def construct(self):
        self.camera.background_color = DARK_BROWN
        self.add(pheromones)
        self.add(ANTS)
        self.wait(100)
