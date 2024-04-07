from time import time
from typing import Iterator, List, Tuple
import numpy as np
import pandas as pd

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
    
    
    def run_prog_dyn(self, debit_total, niveau_amont, active_turbines_bool) -> pd.DataFrame:
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
        result = progDyn.dynamicProgrammingAlgorithm(active_turbines_bool)
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

            bb = TestBlackBox(debit_total, niveau_amont, active_turbines, self.df.iloc[0], 200)
            time, puissances = bb.run()
            self.results["BB"]["time_data"].append(time)
            df_result = bb.df_result
            df_result = df_result.rename(index={'Computed': 'Computed BB'})
            if "ProgDyn" in self.simulationTypes:

                df_resultDyn = self.run_prog_dyn(debit_total, niveau_amont, active_turbines)
                row = df_resultDyn.loc[['Computed']].rename(index={'Computed': 'Computed ProgDyn'})
                df_result = pd.concat([df_result, row])

            return df_result
                    

    def calcul_exemple(self, debit_total: float, niveau_amont: float, active_turbines) -> pd.DataFrame:
        
        self.df = self.default_panda_return()
        bb = TestBlackBox(debit_total, niveau_amont, active_turbines, self.df.iloc[0], 200)
        time, puissances = bb.run()
        self.results["BB"]["time_data"].append(time)
        df_result = bb.df_result
        df_result = df_result.rename(index={'Computed': 'Computed BB'})
        if "ProgDyn" in self.simulationTypes:

            df_resultDyn = self.run_prog_dyn(debit_total, niveau_amont, active_turbines)
            row = df_resultDyn.loc[['Computed']].rename(index={'Computed': 'Computed ProgDyn'})
            df_result = pd.concat([df_result, row])

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
    