from gurobipy import *
import pandas as pd
import numpy as np
from pathlib import Path

# set variables
data_path = Path(__file__).parent.parent.resolve().joinpath("input_data", "base_dados.xlsx")
df = pd.read_excel(data_path, index_col="Date")
df_returns = df.pct_change().dropna()
R = df_returns.mean()
Sigma = df_returns.cov()
n_features = df_returns.shape[1]


def solve_for_alpha(alpha):
    # create model
    opt_mod = Model(name="linear program")
    opt_mod.setParam("NonConvex", 2)
    opt_mod.setParam("OutputFlag", 0)

    # Add decision variable
    w = [opt_mod.addVar(name=str(i), vtype=GRB.CONTINUOUS, lb=0.0) for i in range(n_features)]

    # define objective function
    function = alpha * -np.linalg.multi_dot([R, w]) + (1 - alpha) * np.linalg.multi_dot([w, Sigma, w])
    opt_mod.setObjective(function, GRB.MINIMIZE)

    # add constraints
    opt_mod.addConstr(sum(w) == 1, name="full investment")

    # solve the model
    opt_mod.optimize()
    w_opt = [v.x for v in opt_mod.getVars()]
    Re = 100 * np.linalg.multi_dot([R, w_opt])
    Ri = 100 * np.sqrt(np.linalg.multi_dot([w_opt, Sigma, w_opt]))
    print("---------------------------")
    print(f"solution alpha {alpha} = ")
    print("Objective Function Value", opt_mod.objVal)
    print(f'R: {Re}%')
    print(f'Risco: {Ri} %')
    print(f"Sharpe: {Re / Ri}")
    return w_opt, np.linalg.multi_dot([R, w_opt]), np.sqrt(np.linalg.multi_dot([w_opt, Sigma, w_opt]))


def save_result_image(solutions):
    import matplotlib.pyplot as plt

    solutions = pd.DataFrame(solutions)
    plt.plot(solutions[1], solutions[0])
    plt.title("fronteira eficiente")
    plt.xlabel("risco")
    plt.ylabel("retorno")
    plt.gca().invert_yaxis()
    image_path = Path(__file__).parent.parent.resolve().joinpath("images", "fronteira_eficiente.png")
    plt.savefig(image_path)


alphas = np.linspace(start=0, stop=1, num=100)

solutions = []
for alpha in alphas:
    w_opt, asset_return, asset_risk = solve_for_alpha(alpha)
    solutions.append([asset_return, asset_risk])

save_result_image(solutions)
