import matplotlib.pyplot as plt
import pathlib
import dill as pickle
import tikzplotlib
import time
from typer import Argument, Option, run

from nonlinear_mor.models import ReducedSpacetimeModel

from load_model import load_full_order_model


def main(filepath: str = Argument(..., help='Path to the folder containing the reduction results'),
         num_test_parameters: int = Option(50, help='Number of test parameters'),
         sampling_mode: str = Option('uniform', help='Sampling mode for sampling the training parameters'),
         max_reduced_basis_size: int = Option(50, help='Maximum dimension of reduced basis for vector fields')):

    with open(f'{filepath}/full_order_model/model.pickle', 'rb') as fom_file:
        fom_dictionary = pickle.load(fom_file)
    fom = load_full_order_model(**fom_dictionary)

    parameters = fom.parameter_space.sample(num_test_parameters, sampling_mode)
    basis_sizes = range(1, max_reduced_basis_size + 1)
    timestr = time.strftime("%Y%m%d-%H%M%S")

    for basis_size in basis_sizes:
        results_filepath = f'{filepath}/test_results_{timestr}/basis_size_{basis_size}'
        pathlib.Path(results_filepath).mkdir(parents=True, exist_ok=True)
        pathlib.Path(results_filepath + '/figures_tex').mkdir(parents=True, exist_ok=True)

        reduced_model_filepath = f'{filepath}/reduced_models/basis_size_{basis_size}/model.pickle'
        with open(reduced_model_filepath, 'rb') as model_file:
            model_dictionary = pickle.load(model_file)

        rom = ReducedSpacetimeModel.load_model(model_dictionary)
        for mu in parameters:
            tic = time.perf_counter()
            u_red = rom.solve(mu, filepath_prefix=results_filepath)
            time_rom = time.perf_counter() - tic
            u_red.save(f'{results_filepath}/result_mu_{str(mu).replace(".", "_")}.png',
                       title=f"Reduced solution for mu={mu}")
            u_red.plot()
            tikzplotlib.save(f'{results_filepath}/figures_tex/result_mu_{str(mu).replace(".", "_")}.tex')
            plt.close()

            tic = time.perf_counter()
            u_full = fom.solve(mu)
            time_fom = time.perf_counter() - tic
            u_full.save(f'{results_filepath}/full_solution_mu_{str(mu).replace(".", "_")}.png',
                        title=f"Full solution for mu={mu}")
            u_full.plot()
            tikzplotlib.save(f'{results_filepath}/figures_tex/full_solution_mu_{str(mu).replace(".", "_")}.tex')
            plt.close()
            (u_red - u_full).save(f'{results_filepath}/difference_mu_{str(mu).replace(".", "_")}.png',
                                  title=f"Difference for mu={mu}")
            (u_red - u_full).plot()
            tikzplotlib.save(f'{results_filepath}/figures_tex/difference_mu_{str(mu).replace(".", "_")}.tex')
            plt.close()

            with open(f'{results_filepath}/relative_errors.txt', 'a') as errors_file:
                errors_file.write(f"{mu}\t{(u_red - u_full).norm / u_full.norm}\t{time_fom}\t{time_rom}\n")


if __name__ == "__main__":
    run(main)
