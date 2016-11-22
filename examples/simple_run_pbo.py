import numpy as np

from ifqi import envs
from ifqi.evaluation import evaluation
from ifqi.algorithms.pbo.PBO import PBO

mdp = envs.LQG1D()
state_dim, action_dim, reward_dim = envs.get_space_info(mdp)
reward_idx = state_dim + action_dim
discrete_actions = np.array([-8, -7, -6, -5, -4, -3, -2.5, -2, -1.5, -1, -.75,
                             -.5, -.25, 0, .25, .5, .75, 1, 1.5, 2, 2.5, 3, 4,
                             5, 6, 7, 8])
dataset = evaluation.collect_episodes(mdp, n_episodes=200)
sast = np.append(dataset[:, :reward_idx],
                 dataset[:, reward_idx + reward_dim:-1],
                 axis=1)
r = dataset[:, reward_idx]


class LQG_Q():
    def __init__(self, theta):
        self.theta = theta

    def predict(self, sa, **opt_pars):
        if 'f_rho' in opt_pars:
            k, b = opt_pars['f_rho']
        else:
            k, b = self.theta
        return b - (sa[:, 1] - k * sa[:, 0]) ** 2

theta = np.array([1., 0.])
regressor = LQG_Q(theta)

pbo = PBO(estimator=regressor,
          state_dim=state_dim,
          action_dim=action_dim,
          discrete_actions=discrete_actions,
          gamma=mdp.gamma,
          horizon=mdp.horizon,
          scaled=False,
          features=None,
          verbose=True)

epsilon = 1e-5
delta = np.inf

rho, score = pbo.fit(sast, r)
while delta > epsilon:
    rho, score = pbo.fit()
    old_theta = pbo.theta
    pbo.theta = pbo.f(rho)
    delta = np.sum(pbo.theta - old_theta) ** 2

    print(delta)

print(pbo.theta)
