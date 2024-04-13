from time import time
from typing import Iterator, List, Tuple
import numpy as np
import pandas as pd
import src.algo.programmation_black_box as progBB
from src.algo.programmation_black_box import TestBlackBox
import src.algo.programmation_dynamique as progDyn

class Simulations:

    def __init__(self, file_name: str, simulationTypes: List[str]) -> None:
        """
        Initialise la classe Simulations.
        
        Args:
            file_name (str): Le nom du fichier.
            simulationTypes (List[str]): Les types de simulation.
        """
        self.df_filename = file_name
        self.simulationTypes = simulationTypes
        self.df = None
        self.results = {key: {
            "sumDifferences": 0,
            "nbImprovements": 0,
            "time_data": [],
            "diff_ttl_puissance_data": [],
            "diff_puissance_puissance_per_turbine_data": [[], [], [], [], []]
        } for key in simulationTypes}


    @staticmethod
    def read_excel_yield(filename: str, starting_row: int, end_row: int) -> Iterator[pd.DataFrame]:
        """
        Lit un fichier Excel et renvoie les données en itérant sur chaque DataFrame.

        Args:
            filename (str): Le nom du fichier.
            starting_row (int): La ligne de départ.
            end_row (int): La ligne de fin.

        Yields:
            Iterator[pd.DataFrame]: Un itérateur de DataFrame.
        """
        header = ['Unnamed: 0', 'Elav (m)', 'Qtot (m3/s)', 'Qturb  (m3/s)','Qvan  (m3/s)', 'Niv Amont (m)',
                  'Q1 (m3/s)', 'P1 (MW)', 'Q2 (m3/s)', 'P2 (MW)', 'Q3 (m3/s)', 'P3 (MW)', 'Q4 (m3/s)',
                  'P4 (MW)', 'Q5 (m3/s)', 'P5 (MW)', 'Perte 1 (m)', 'Perte 2 (m)', 'Perte 3 (m)', 'Perte 4 (m)',
                  'Perte 5 (m)', 'Hauteur nette 1', 'Hauteur nette 2', 'Hauteur nette 3', 'Hauteur nette 4',
                  'Hauteur nette 5']
        yield pd.read_excel(filename, skiprows=end_row, nrows=1, names=header)

    @staticmethod
    def default_panda_return():
        data = {
            'Unnamed: 0': [0],
            'Elav (m)': [0],
            'Qtot (m3/s)': [0],
            'Qturb (m3/s)': [0],
            'Qvan (m3/s)': [0],
            'Niv Amont (m)': [0],
            'Q1 (m3/s)': [0],
            'P1 (MW)': [0],
            'Q2 (m3/s)': [0],
            'P2 (MW)': [0],
            'Q3 (m3/s)': [0],
            'P3 (MW)': [0],
            'Q4 (m3/s)': [0],
            'P4 (MW)': [0],
            'Q5 (m3/s)': [0],
            'P5 (MW)': [0],
            'Perte 1 (m)': [0],
            'Perte 2 (m)': [0],
            'Perte 3 (m)': [0],
            'Perte 4 (m)': [0],
            'Perte 5 (m)': [0],
            'Hauteur nette 1': [0],
            'Hauteur nette 2': [0],
            'Hauteur nette 3': [0],
            'Hauteur nette 4': [0],
            'Hauteur nette 5': [0]
        }
        return pd.DataFrame(data)


    def get_data_from_excel(self) -> Tuple[float, float, list[bool]]:
        """
        Récupère les données nécessaires depuis le DataFrame.

        Returns:
            Tuple[float, float, List[bool]]: Débit total, niveau amont et turbines actives.
        """
        debit_total = self.df.loc[0, "Qtot (m3/s)"]
        niveau_amont = self.df.loc[0, "Niv Amont (m)"]
        active_turbines = [bool(self.df[f'P{i} (MW)'][0]) for i in range(1, 6)]
        return debit_total, niveau_amont, active_turbines
    
    def createBypassResult(self, active_turbines_bool, max_debit_turbine):
        resultDict = {}
        index = 0
        sumPuissance = 0
        for i, is_active in enumerate(active_turbines_bool[::-1]):
            if is_active:
                numTurbine = len(active_turbines_bool) - i
                debit = max_debit_turbine[numTurbine - 1]
                coefficients = progDyn.ARRAY_COEFFICIENTS_TURBINES[numTurbine - 1]
                chuteNette = progDyn.getChuteNette(debit)
                puissance = progDyn.powerFunction(debit, chuteNette, 
                                                  coefficients)
                sumPuissance += puissance
                df = pd.DataFrame(columns=[f"X{numTurbine}", f"F{numTurbine}"])
                new_row = {f"X{numTurbine}": debit, f"F{numTurbine}": 0}
                df.loc[index] = new_row
                df[f"F{numTurbine}"] = df[f"F{numTurbine}"] + sumPuissance
                resultDict[numTurbine] = df
                index += 1
        return resultDict
    
    def run_prog_dyn(self, debit_total, niveau_amont, active_turbines_bool, max_debit_turbine) -> pd.DataFrame:
        """
        Exécute le programme dynamique et retourne les résultats sous forme de DataFrame.

        Args:
            debit_total (float): Le débit total.
            niveau_amont (float): Le niveau amont.
            active_turbines_bool (List[bool]): Les turbines actives.

        Returns:
            pd.DataFrame: Les résultats du programme dynamique.
        """
        debit_total_computed = round(debit_total, 2)
        progDyn.DEBIT_TOTAL = debit_total_computed
        progDyn.niveau_amont = niveau_amont
        ref = np.arange(progDyn.DEBIT_TOTAL, progDyn.MIN_DEBIT - progDyn.PAS_DEBIT, -progDyn.PAS_DEBIT)
        progDyn.REF = [round(number, 2) for number in ref if number >= 0]
        df_result = progDyn.initialize_result_df(debit_total, debit_total_computed, self.df.iloc[0])
        actives_turbines = [index for index, value in enumerate(active_turbines_bool, start=1) if value]
        start = time()
        result = None
        
        if np.sum(max_debit_turbine) <= progDyn.DEBIT_TOTAL:
            ttl_time = 0
            result = self.createBypassResult(active_turbines_bool, max_debit_turbine)


        else:
            result = progDyn.dynamicProgrammingAlgorithm(active_turbines_bool, 
                                                     max_debit_turbine=max_debit_turbine)
        ttl_time = time() - start
        self.results["ProgDyn"]["time_data"].append(ttl_time)
        progDyn.extractResults(df_result, actives_turbines, result)
        return df_result

           
    def calcul_row(self, row_columns_index: int, row_to_calculate: int) -> pd.DataFrame:
        """
        Calcule une ligne de données.

        Args:
            row_columns_index (int): L'index de la ligne.
            row_to_calculate (int): La ligne à calculer.

        Returns:
            pd.DataFrame: Le DataFrame résultant.
        """
        with open(self.df_filename, 'rb') as f:
            rows = self.read_excel_yield(f, row_columns_index, row_to_calculate)
            self.df = next(rows)
            
            debit_total, niveau_amont, active_turbines = self.get_data_from_excel()

            bb = TestBlackBox(debit_total, niveau_amont, active_turbines, [160, 160, 160, 160, 160], self.df.iloc[0], 200)
            time, puissances = bb.run()
            self.results["BB"]["time_data"].append(time)
            df_result = bb.df_result
            df_result = df_result.rename(index={'Computed': 'Computed BB'})
            if "ProgDyn" in self.simulationTypes:

                df_resultDyn = self.run_prog_dyn(debit_total, niveau_amont, active_turbines, max_debit_turbine=[160, 160, 160, 160, 160])
                row = df_resultDyn.loc[['Computed']].rename(index={'Computed': 'Computed ProgDyn'})
                df_result = pd.concat([df_result, row])
            # print(df_result)
            df_result = progDyn.get_chute_nette_for_turbine_result(df_result=df_result,
                                                               list_debit_turbine_dyn=[df_result.at["Computed ProgDyn","Débit T1"],
                                                                                       df_result.at["Computed ProgDyn","Débit T2"],
                                                                                       df_result.at["Computed ProgDyn","Débit T3"],
                                                                                       df_result.at["Computed ProgDyn","Débit T4"],
                                                                                       df_result.at["Computed ProgDyn","Débit T5"]],
                                                                list_debit_turbine_nomad=[df_result.at["Computed BB","Débit T1"],
                                                                                          df_result.at["Computed BB","Débit T2"],
                                                                                          df_result.at["Computed BB","Débit T3"],
                                                                                          df_result.at["Computed BB","Débit T4"],
                                                                                          df_result.at["Computed BB","Débit T5"]],
                                                                list_debit_turbine_original=[df_result.at["Original","Débit T1"],
                                                                                             df_result.at["Original","Débit T2"],
                                                                                             df_result.at["Original","Débit T3"],
                                                                                             df_result.at["Original","Débit T4"],
                                                                                             df_result.at["Original","Débit T5"]],                          )

            return df_result
                    
    def createBypassBbox(self, active_turbines, max_debit, 
                         debit_total, niveau_amont, bb: TestBlackBox):
        df = pd.DataFrame(index=["Original", "Computed"])
        df["Débit disponible"] = debit_total
        puissance_totale = 0
        new_row = pd.Series([0] * len(df.columns), index=df.columns)
        for i, is_active in enumerate(active_turbines):
            if is_active:
                chuteNette = bb.getChuteNette(max_debit[i])
                puissance = bb.powerFunction(max_debit[i],chuteNette,
                                             progBB.ARRAY_COEFFICIENTS_TURBINES[i])
                puissance_totale += puissance
                df.at["Computed", f"Débit T{i+1}"] = max_debit[i]
                df.at["Original", f"Débit T{i+1}"] = 0
                df.at["Computed", f"Puissance T{i+1}"] = puissance
                df.at["Original", f"Puissance T{i+1}"] = 0
                
        df["Puissance totale"] = puissance_totale
        df.at["Original", f"Puissance totale"] = 0
        return df

    def calcul_exemple(self, debit_total: float, niveau_amont: float, active_turbines, max_debit) -> pd.DataFrame:
        self.df = self.default_panda_return()
        bb = TestBlackBox(debit_total, niveau_amont, active_turbines, 
                          max_debit, self.df.iloc[0], 200)
        if np.sum(max_debit) <= debit_total:
            time = 0
            df_result = self.createBypassBbox(active_turbines, max_debit, 
                                              debit_total, niveau_amont, bb)
        else:
            time, puissances = bb.run()
            df_result = bb.df_result
        self.results["BB"]["time_data"].append(time)
        df_result = df_result.rename(index={'Computed': 'Computed BB'})
        if "ProgDyn" in self.simulationTypes:

            df_resultDyn = self.run_prog_dyn(debit_total, niveau_amont, 
                                             active_turbines, max_debit)
            # print(df_resultDyn)
            row = df_resultDyn.loc[['Computed']].rename(index={'Computed': 'Computed ProgDyn'})
            df_result = pd.concat([df_result, row])
        print(df_result)
        df_result = progDyn.get_chute_nette_for_turbine_result(df_result=df_result,
                                                               list_debit_turbine_dyn=[df_result.at["Computed ProgDyn","Débit T1"],
                                                                                       df_result.at["Computed ProgDyn","Débit T2"],
                                                                                       df_result.at["Computed ProgDyn","Débit T3"],
                                                                                       df_result.at["Computed ProgDyn","Débit T4"],
                                                                                       df_result.at["Computed ProgDyn","Débit T5"]],
                                                                list_debit_turbine_nomad=[df_result.at["Computed BB","Débit T1"],
                                                                                          df_result.at["Computed BB","Débit T2"],
                                                                                          df_result.at["Computed BB","Débit T3"],
                                                                                          df_result.at["Computed BB","Débit T4"],
                                                                                          df_result.at["Computed BB","Débit T5"]])

        return df_result








if __name__ == "__main__":
    FILENAME = "data/DataProjet2024.xlsx"
    STARTING_ROW = 2
    ROW_COUNT = 3

    multi_sim = Simulations(FILENAME, ["ProgDyn"])
    # ===============
    #      EXCEL
    # ===============

    # for row_index in range(STARTING_ROW, ROW_COUNT+1,1):
    #     df_dyn_result = multi_sim.calcul_row(row_columns_index=STARTING_ROW, row_to_calculate=row_index)
    #     print(df_dyn_result)
    #     puissance_total = df_dyn_result.at["Computed","Puissance totale"]
    #     puissance_turbine_1 = df_dyn_result.at["Computed","Puissance T1"]
    #     puissance_turbine_2 = df_dyn_result.at["Computed","Puissance T2"]
    #     puissance_turbine_3 = df_dyn_result.at["Computed","Puissance T3"]
    #     puissance_turbine_4 = df_dyn_result.at["Computed","Puissance T4"]
    #     puissance_turbine_5 = df_dyn_result.at["Computed","Puissance T5"]



    #     debit_total = df_dyn_result.at["Computed","Débit disponible"]
    #     debit_turbine_1 = df_dyn_result.at["Computed","Débit T1"]
    #     debit_turbine_2 = df_dyn_result.at["Computed","Débit T2"]
    #     debit_turbine_3 = df_dyn_result.at["Computed","Débit T3"]
    #     debit_turbine_4 = df_dyn_result.at["Computed","Débit T4"]        
    #     debit_turbine_5 = df_dyn_result.at["Computed","Débit T5"]
    
        
    # ===============
    #      Manual
    # ===============
    debit_total = 580.2
    niveau_amont = 137.2
    active_turbines = [True, True, True, True, False]

    multi_sim.calcul_exemple(debit_total=debit_total,niveau_amont=niveau_amont,active_turbines=active_turbines)
    