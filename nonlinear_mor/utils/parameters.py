import numpy as np

from nonlinear_mor.utils.logger import getLogger


class ParameterSpace:
    def __init__(self):
        pass


class CubicParameterSpace(ParameterSpace):
    def __init__(self, extends):
        super().__init__()
        self.extends = np.array(extends)
        self.dim = len(self.extends)

        self.logger = getLogger('nonlinear_mor.CubicParameterSpace')

    def sample(self, num_samples=1, mode='uniform'):
        assert mode in ['uniform']
        assert isinstance(num_samples, int) and num_samples >= 1

        if mode == 'uniform':
            number_of_parameters_per_dimension = int(np.ceil(num_samples**(1/self.dim)))
            self.logger.info(f"Sampling {number_of_parameters_per_dimension**self.dim} parameters uniformly ...")
            linspace_list = [np.linspace(p_min, p_max, number_of_parameters_per_dimension)
                             for p_min, p_max in self.extends]
            temp = np.meshgrid(*linspace_list)
            parameters = np.stack([temp_.T for temp_ in temp], axis=-1).reshape(-1, self.dim)
            assert parameters.shape == (number_of_parameters_per_dimension**self.dim, self.dim)

        return parameters.squeeze()