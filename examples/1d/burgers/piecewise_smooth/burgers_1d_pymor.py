from nonlinear_mor.models import WrappedpyMORModel
from nonlinear_mor.utils.parameters import CubicParameterSpace

from pymor.analyticalproblems.elliptic import StationaryProblem
from pymor.analyticalproblems.domaindescriptions import LineDomain, CircleDomain
from pymor.analyticalproblems.instationary import InstationaryProblem
from pymor.analyticalproblems.functions import ConstantFunction, ExpressionFunction
from pymor.discretizers.builtin import discretize_instationary_fv


def burgers_problem(parameter_ranges, circle=False):
    """One-dimensional Burgers-type problem.

    The problem is to solve ::
        ∂_t u(x, t, μ)  +  ∂_x (v * u(x, t, μ)^μ) = 0
                                       u(x, 0, μ) = u_0(x)
    for u with t in [0, 0.3] and x in [0, 2].

    Parameters
    ----------
    circle
        If `True`, impose periodic boundary conditions. Otherwise Dirichlet left,
        outflow right.
    parameter_range
        The interval in which μ is allowed to vary.
    """

    initial_data = ExpressionFunction('(2. + 0.1*sin(4*pi*x[0]*3)) * (x[0] <= .25)'
                                      '+ (1. + 0.1*sin(8*pi*x[0]*3)) * (.25 < x[0]) * (x[0] <= .5)'
                                      '+ (0.1*sin(2*pi*x[0]*3)) * (x[0] > .5)', 1)
    dirichlet_data = ConstantFunction(dim_domain=1, value=2.)

    return InstationaryProblem(
        StationaryProblem(
            domain=CircleDomain([0, 1]) if circle else LineDomain([0, 1], right=None),
            dirichlet_data=dirichlet_data,
            rhs=None,
            nonlinear_advection=ExpressionFunction('mu1[0] * x**2 / 2.',
                                                   1, {'mu1': 1}),
            nonlinear_advection_derivative=ExpressionFunction('mu1[0] * x',
                                                              1, {'mu1': 1}),
        ),
        T=1.,
        initial_data=initial_data,
        parameter_ranges={'mu1': parameter_ranges[0]},
        name=f"burgers_problem({circle})"
    )


def create_model(spatial_shape, num_time_steps):
    assert len(spatial_shape) == 1
    parameter_ranges = [(.25, 1.5)]
    problem = burgers_problem(parameter_ranges)
    model, _ = discretize_instationary_fv(
        problem,
        diameter=1 / spatial_shape[0],
        num_flux='engquist_osher',
        nt=num_time_steps
    )
    parameter_space = CubicParameterSpace(parameter_ranges)
    return WrappedpyMORModel(spatial_shape, num_time_steps, parameter_space, model)
