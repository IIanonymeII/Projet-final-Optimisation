import pandas as pd
import subprocess
import re
from time import time
import os
from typing import Union, List, Tuple
from dotenv import dotenv_values


MIN_DEBIT = 0
MAX_DEBIT = 160

COEFFICIENTS_ELEV_AVAL = [-1.453*10**(-6), 0.007022, 99.9812]

puissance_turbine_1 = [1.1018, -0.04866, -0.03187, 0.002182, 
                       0.003308, 0, -1.2771e-05, 3.683e-05]

puissance_turbine_2 = [0.6987, -0.175, -0.02011, 0.003632, 
                       0.004154, 0, -1.6988e-05, 3.5401e-05]

puissance_turbine_3 = [0.7799,  0.1995 , -0.02261, -3.519e-05 , 
                       -0.001695, 0, -9.338e-06, 7.235e-05]

puissance_turbine_4 = [20.2212 , -0.4586, -0.5777, 0.004886, 
                       0.01151, 0, -1.882e-05,   1.379e-05]

puissance_turbine_5 = [1.9786, 0.004009, -0.05699, 0.001064, 
                       0.005456, 0,  -8.162e-06,   2.849e-05]
		

ARRAY_COEFFICIENTS_TURBINES = [puissance_turbine_1, puissance_turbine_2, 
                               puissance_turbine_3, puissance_turbine_4, 
                               puissance_turbine_5]


class TestBlackBox:

    def __init__(self, 
                 debit_total: float, 
                 niveau_amont: float, 
                 active_turbines: List[bool], 
                 max_debit: List[float],
                 df_file_row: pd.Series,
                 nb_iterations: int) -> None:
        self.debit_total = debit_total
        self.niveau_amont = niveau_amont
        self.active_turbines = active_turbines
        self.nb_iterations = nb_iterations
        self.max_debit = max_debit
        self.prepareParamFile()
        self.initialize_result_df(df_file_row)
        self.read_nomad_path_from_env()



    def read_nomad_path_from_env(self):
        env_vars = dotenv_values('.env')  # Load variables from .env file
        self.nomad_path = env_vars.get('NOMAD_PATH',"src\\")  # Get NOMAD_PATH value from loaded variables

    def getChuteNette(self, 
                      debit_turbine: Union[int,float]) -> Union[int,float]:
        # Vérifier si le débit est dans la plage admissible
        # if debit_turbine < MIN_DEBIT or debit_turbine > MAX_DEBIT:
        #     raise ValueError(f"Le débit doit être compris entre {MIN_DEBIT} et {MAX_DEBIT} m³/s. now is more {debit_turbine}")
        # Déterminer l'élévation avale en fonction du débit total
        elevation_avale = COEFFICIENTS_ELEV_AVAL[0] * self.debit_total**2 + \
                            COEFFICIENTS_ELEV_AVAL[1] * self.debit_total + \
                            COEFFICIENTS_ELEV_AVAL[2]
        
        # Calculer la chute nette
        chute_nette = self.niveau_amont - elevation_avale \
        - (0.5 * (10**-5) * (debit_turbine**2))

        return chute_nette

    def powerFunction(self, 
                      debit_turbine: Union[int,float], 
                      chute_nette: float,
                      coefficients: list):
        return coefficients[0] + \
            coefficients[1] * debit_turbine +\
            coefficients[2] * chute_nette + \
            coefficients[3] * debit_turbine**2 +\
            coefficients[4] * debit_turbine * chute_nette +\
            coefficients[5] * chute_nette**2 +\
            coefficients[6] * debit_turbine**3 +\
            coefficients[7] * debit_turbine**2*chute_nette

    def initResultDf(self) -> pd.DataFrame:
        dfResult = pd.DataFrame(index=["Original", "Computed"], columns = ["Débit disponible", "Puissance totale"])
        dfResult.loc[:, "Puissance totale"] = 0
        return dfResult
    
    def getSteps(self, output: str):
        pattern_end_line = re.compile(r"-\d+\.\d+", re.MULTILINE)
        pattern_start_line = re.compile(r"^\s*\d+", re.MULTILINE)
        puissances_str = pattern_end_line.findall(output)
        iteration_numbers_str = pattern_start_line.findall(output)
        iteration_numbers = [int(x.strip()) for x in iteration_numbers_str]
        puissances = [float(puissances_str[0])]
        curr_it = 1
        for i in range(2,self.nb_iterations+1):
            if curr_it >= len(puissances_str):
                puissances.append(puissances[-1])
            elif iteration_numbers[curr_it] == i:
                puissances.append(float(puissances_str[curr_it]))
                curr_it += 1
            else:
                puissances.append(puissances[-1])
        return puissances
    
    def getSolutionsFromOutput(self, 
                               output: str):
        match = re.search(r'best feasible solution.*', output, re.DOTALL)
        if match:
            numbers = re.findall(r'-?\d+\.?\d*', match.group(0))
            return numbers
        else:
            return None
        
    def runNomad(self) -> Tuple[float, list[float]]:
        cmd = [self.nomad_path + 'nomad.exe', 'src\\param.txt']
        start = time()
        try:
            output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
        except:
            print("nomad.exe not found. Make sure it's in the PATH ")
            exit(1) 
        ttl_time = time() - start
        output = output.decode("utf-8")
        numbers = self.getSolutionsFromOutput(output)
        puissances = self.getSteps(output)
        return ttl_time, numbers, puissances
    
    def initialize_result_df(self, df_file_row: pd.Series) -> None:
        self.df_result = self.initResultDf()

        self.df_result.at["Original", "Débit disponible"] = self.debit_total
        self.df_result.at["Computed", "Débit disponible"] = self.debit_total
        
        puissance_totale = 0
        for i in range(1, 5+1, 1):
            self.df_result.loc["Original", f"Débit T{i}"] = df_file_row[f"Q{i} (m3/s)"]
            self.df_result.loc["Original", f"Puissance T{i}"] = df_file_row[f"P{i} (MW)"]
            self.df_result.loc["Computed", f"Débit T{i}"] = 0
            self.df_result.loc["Computed", f"Puissance T{i}"] = 0
            puissance_totale += df_file_row[f"P{i} (MW)"]

        self.df_result.at["Original", "Puissance totale"] = puissance_totale

    def prepareParamFile(self, exe_path: str = "src/main.exe", 
                         file_name: str = "src/param.txt") -> None:
        abs_path_exe = os.path.abspath(exe_path)
        with open(file_name,'r',encoding='utf-8') as file:
            data = file.readlines()
        data[2] = f"BB_EXE         \"${abs_path_exe} ${self.debit_total} ${self.niveau_amont}\"\n"
        data[23] = f"MAX_BB_EVAL    {self.nb_iterations}\n"
        str_max_debit = "UPPER_BOUND\t( "
        i = 0
        for turbine in self.active_turbines:
            if turbine:
                if self.max_debit[i] == None:
                    str_max_debit += "160 "
                else:
                    str_max_debit += str(int(self.max_debit[i])) + " "
            else:
                str_max_debit += "0 "
            i += 1
        str_max_debit += ")\n"
        data[21] = str_max_debit
        with open(file_name, 'w', encoding='utf-8') as file:
            file.writelines(data)

    def processResults(self, results: list[float]) -> None:
        for i in range(5):
            colNameDebit = "Débit T" + str(i+1)
            colNamePuissance = "Puissance T" + str(i+1)
            debit_turbine = float(results[i])
            if debit_turbine == 0:
                currentPuissance = 0
            else:
                currentPuissance = self.powerFunction(debit_turbine, 
                                                      self.getChuteNette(debit_turbine), 
                                                ARRAY_COEFFICIENTS_TURBINES[i])
            self.df_result.loc["Computed", colNameDebit] = debit_turbine
            self.df_result.loc["Computed", colNamePuissance] = currentPuissance
            self.df_result.loc["Computed", "Puissance totale"] = - float(results[-1])

    def run(self) -> float:
        result = self.runNomad()
        self.processResults(result[1])
        return result[0], result[2]
    
