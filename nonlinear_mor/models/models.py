import numpy as np
from functools import partial

from geodesic_shooting.core import ScalarFunction

from nonlinear_mor.utils.logger import getLogger


class SpacetimeModel:
    def __init__(self, grid_operator, transformation, n_x=100, n_t=100, name='SpacetimeModel'):
        self.grid_operator = grid_operator
        self.transformation = transformation

        assert isinstance(n_x, int) and n_x > 0
        assert isinstance(n_t, int) and n_t > 0
        self.n_x = n_x
        self.n_t = n_t

        self.name = name

    def __str__(self):
        return self.name


    def solve(self, mu):
        logger = getLogger('nonlinear_mor.SpacetimeModel')

        logger.info(f"Reparametrizing flux functions for mu={mu} ...")
        self._reparametrize_flux_functions(mu)

        with logger.block("Running `solve`-method of grid operator ..."):
            u = self.grid_operator.solve()

        return u.sample_function_uniformly(self.transformation, n_x=self.n_x, n_t=self.n_t)

    def _reparametrize_flux_functions(self, mu):
        self.grid_operator.time_stepper.discretization.numerical_flux.flux = partial(
            self.grid_operator.time_stepper.discretization.numerical_flux.flux, mu=mu)
        self.grid_operator.time_stepper.discretization.numerical_flux.flux_derivative = partial(
            self.grid_operator.time_stepper.discretization.numerical_flux.flux_derivative, mu=mu)
        self.grid_operator.time_stepper.discretization.inverse_transformation = partial(
            self.grid_operator.time_stepper.discretization.inverse_transformation, mu=mu)

        self.transformation = partial(self.transformation, mu=mu)


class AnalyticalModel:
    def __init__(self, exact_solution, n_x=100, n_t=100, x_min=0., x_max=1., t_min=0., t_max=1.,
                 name='AnalyticalModel'):
        self.exact_solution = exact_solution

        assert isinstance(n_x, int) and n_x > 0
        assert isinstance(n_t, int) and n_t > 0
        self.n_x = n_x
        self.n_t = n_t

        self.x_min = x_min
        self.x_max = x_max
        self.t_min = t_min
        self.t_max = t_max

        self.name = name

    def __str__(self):
        return self.name

    def solve(self, mu):
        logger = getLogger('nonlinear_mor.AnalyticalModel')

        XX, YY = np.meshgrid(np.linspace(self.x_min, self.x_max, self.n_x),
                             np.linspace(self.t_min, self.t_max, self.n_t))
        XY = np.stack([XX.T, YY.T], axis=-1)

        with logger.block(f"Sampling analytical solution for mu={mu} ..."):
            result = self.exact_solution(XY, mu=mu)

        return result


class WrappedpyMORModel:
    def __init__(self, model, spatial_shape=(100, ), name='WrappedpyMORModel'):
        self.model = model

        self.spatial_shape = spatial_shape

        self.name = name

    def __str__(self):
        return self.name

    def solve(self, mu):
        logger = getLogger('nonlinear_mor.WrappedpyMORModel')

        with logger.block(f"Calling pyMOR to solve for mu={mu} ..."):
            u = self.model.solve(mu).to_numpy()

        u = u.reshape((u.shape[0], *self.spatial_shape))

        return ScalarFunction(data=u)

    def visualize(self, u):
        u = u.to_numpy()
        U = self.model.operator.range.from_numpy(u.reshape(u.shape[0], -1))
        self.model.visualize(U)
