from manim import *
from scipy.integrate import odeint

N_ = 80  # Number of fireflies
w = np.pi/1.5  # Intrinsic frequency of fireflies

end = 50
t = np.linspace(0, end, 15*end)

U = 4
L = 4
POS = np.array([[np.random.uniform(-L, L),
                 np.random.uniform(-U, U), 0] for i in range(N_)])  # Initializing random position

K = 2  # Coupling Constant

Omegas = w*np.ones(N_) # initializing intrinsic frequency omega = 1 for all fireflies
iTheta = np.random.uniform(0, 2*np.pi, N_)  # initializing thetas - random values between 0 and 2pi


'''def adjacency(POS):
    P = np.broadcast_to(POS, (N_, N_, 3))
    PT = np.transpose(P, axes=[1, 0, 2])
    A = np.linalg.norm(P - PT, axis=2) < Influence
    return np.array(A, dtype=int)'''


def Kuramoto(Thetas, t):
    #A = adjacency(POS)
    Theta_ij = np.tile(Thetas, (N_, 1))
    S = np.sin(Theta_ij-Theta_ij.T)
    d_dt = Omegas + (K/N_)*np.sum(S, axis=1)
    return d_dt


def gauss(x):
    return np.exp(-5*(np.sin(x)**2))  # tune to coefficient of sinx to for the width of flash spike


sol = odeint(Kuramoto, iTheta, t).T
vel = (sol[:,:-1]-sol[:,1:])


class Fireflies:
    def __init__(self, i, Thetas, step = 0.15) -> None:
        self.i = i
        self.theta = Thetas
        self.n = 0
        self.t = 0
        self.step = step

    def update(self, Mobject, dt):
        self.n += 1
        self.t += dt
        s = int(self.t/self.step)
        alp = gauss(self.theta[s])
        Mobject.set_opacity(alp)

class Syncronize(Scene):
    def construct(self):
        opacity = gauss(iTheta)
        bees = [Dot(POS[i], radius=0.03, color = YELLOW, fill_opacity=opacity[i]) for i in range(N_)]
        for i in range(N_):
            bees[i].add_updater(Fireflies(i, sol[i]).update)
            self.add(bees[i])
        self.wait(15)
