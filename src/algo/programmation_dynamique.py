import copy
from typing import Dict, Iterator, List, Union
from time import time
import numpy as np
import pandas as pd
# from plotFunctions import plot_differences, plot_time
MIN_DEBIT = 0
# MAX_DEBIT = 160
PAS_DEBIT = 5

# debit_total = 0
niveau_amont = 0

# Paramètres

# L’élévation avale en fonction du débit total
# f(x) = p1*x^2 + p2*x + p3	

COEFFICIENTS_ELEV_AVAL = [-1.453*10**(-6), 0.007022, 99.9812] # [p1, p2, p3] 

# puissance turbine 1 = 1.1018 − 0.0487x − 0.0319y + 0.0022x2 + 0.0033xy
# puissance turbine 2 = 0.6987 − 0.1750x − 0.0201y + 0.0036x2 + 0.0042xy − 1.6988 × 10−5x3 + 3.5401 × 10−5x2y
# puissance turbine 3 = 0.7799 + 0.1995x − 0.0226y − 0.0017xy + 0.0001x2y 
# puissance turbine 4 = 0.2212 − 0.0487x − 0.0319y + 0.0022x2 + 0.0033xy

# La puissance produite en fonction de la hauteur de chute nette et du débit turbiné
# f(x,y) = p00 + p10*x + p01*y + p20*x^2 + p11*x*y + p02*y^2 + p30*x^3 + p21*x^2*y + p12*x*y^2 + p03*y^3 + p40*x^4 + p31*x^3*y + p22*x^2*y^2 + p13*x*y^3 + p04*y^4

# x : debit
# y : Chute nette

# turbine 1            p00   |    x    |    y    |   x^2   |
#                      x*y   |   y^2   |   x^3   |   x^2*y |         
puissance_turbine_1 = [1.1018, -0.04866, -0.03187, 0.002182, 
                       0.003308, 0, -1.2771e-05, 3.683e-05]

# turbine 2             p00   |    x    |    y    |   x^2   |
#                       x*y   |   y^2   |   x^3   |   x^2*y |
puissance_turbine_2 = [0.6987, -0.175, -0.02011, 0.003632, 
                       0.004154, 0, -1.6988e-05, 3.5401e-05]

# turbine 3             p00   |    x    |    y    |   x^2   |
#                       x*y   |   y^2   |   x^3   |   x^2*y |
puissance_turbine_3 = [0.7799,  0.1995 , -0.02261, -3.519e-05 , 
                       -0.001695, 0, -9.338e-06, 7.235e-05]

# turbine 4             p00   |    x    |    y    |   x^2   |
#                       x*y   |   y^2   |   x^3   |   x^2*y |
puissance_turbine_4 = [20.2212 , -0.4586, -0.5777, 0.004886, 
                       0.01151, 0, -1.882e-05,   1.379e-05]

# turbine 5             p00   |    x    |    y    |   x^2   |
#                       x*y   |   y^2   |   x^3   |   x^2*y |
puissance_turbine_5 = [1.9786, 0.004009, -0.05699, 0.001064, 
                       0.005456, 0,  -8.162e-06,   2.849e-05]
		

ARRAY_COEFFICIENTS_TURBINES = [puissance_turbine_1, puissance_turbine_2, 
                               puissance_turbine_3, puissance_turbine_4, 
                               puissance_turbine_5]


def getChuteNette(debit_turbine: Union[int,float]) -> Union[int,float]:
  # Vérifier si le débit est dans la plage admissible
  # if debit_turbine < MIN_DEBIT or debit_turbine > MAX_DEBIT:
  #   raise ValueError(f"Le débit doit être compris entre {MIN_DEBIT} et {MAX_DEBIT} m³/s. now is more {debit_turbine}")
  # Déterminer l'élévation avale en fonction du débit total
  elevation_avale = COEFFICIENTS_ELEV_AVAL[0] * DEBIT_TOTAL**2 + \
                    COEFFICIENTS_ELEV_AVAL[1] * DEBIT_TOTAL + \
                    COEFFICIENTS_ELEV_AVAL[2]

  # Calculer la chute nette
  chute_nette = niveau_amont - elevation_avale \
  - (0.5 * (10**-5) * (debit_turbine**2))

  return chute_nette

def get_chute_nette_for_turbine_result(df_result: pd.DataFrame,
                                       list_debit_turbine_dyn: List[float],
                                       list_debit_turbine_nomad: List[float],
                                       list_debit_turbine_original : List[float]=None) -> pd.DataFrame:
  for i in range(0,5):
    dyn_chutte = getChuteNette(debit_turbine=list_debit_turbine_dyn[i])
    nomad_chutte = getChuteNette(debit_turbine=list_debit_turbine_nomad[i])
    original_chutte = 0
    if list_debit_turbine_original:
      original_chutte = getChuteNette(debit_turbine=list_debit_turbine_original[i])
    df_result[f'Chute Nette T{i+1}'] = [original_chutte,dyn_chutte,nomad_chutte]
  

  return df_result

def getStates(turbines: list, max_debit_turbine: List[float]) -> Dict[int,List[int]]:
  """
  return A dictionnary containing a list of every state possible for each
  available turbine
  """
  nb_turbines = len(turbines)
  result: Dict[int, List[int]] = {}
  result[turbines[0]] = [DEBIT_TOTAL]
  for i, turbine in enumerate(turbines[1:]):
    # print(f"turbine : {turbine}")
    debit_restant = max_debit_turbine[turbine-1:]
    debit_avant = max_debit_turbine[:turbine-1]

    # print(f"debit restant  : {debit_restant} => {np.sum(debit_restant)}")
    # print(f"debit avant  : {debit_avant} => {(DEBIT_TOTAL - np.sum(debit_avant))} ")

    # Débit max restant: Max débit * nb turbines restantes 
    # ou QTot si Max débit * nb turbines restantes > Qtot
    if np.sum(debit_restant) < DEBIT_TOTAL:
      debit_restant_max = np.sum(debit_restant)
    else:
      debit_restant_max = DEBIT_TOTAL
    # print(f"debit max : {debit_restant_max}")
    # print(f"debit ")
    debit_restant_max = find_nearest_number(reference_list=REF,number=debit_restant_max, is_max=True)
    debit_restant_max = round(debit_restant_max,2)

    # Débit min restant: Débit total - DébitMax * Nb turbines avant (ou 0)

    if (DEBIT_TOTAL - np.sum(debit_avant)) > 0:
      debit_restant_min = DEBIT_TOTAL - np.sum(debit_avant)
    else:
      debit_restant_min = 0
    debit_restant_min = find_nearest_number(reference_list=REF,number=debit_restant_min, is_max=False)
    debit_restant_min = round(debit_restant_min,2)

    debit_restant = list(np.arange(debit_restant_min,
                                   debit_restant_max,
                                   PAS_DEBIT))
    if debit_restant == []:
      debit_restant = [debit_restant_max]

    debit_restant = round_list(debit_restant)
    
    if not (debit_restant[-1] == debit_restant_max):
      debit_restant.append(debit_restant_max)

    
    
    result[turbine] = debit_restant
  return result
  

def getPossibleValues(turbines_working : List[bool], 
                      max_debit_list : List[Union[float,int]]) -> List[List[float]]:
  """
  return All the values that a step can take
  """
  debit_turbine_possible = [[] for _ in range(len(turbines_working))]

  for i, debit_max in enumerate(max_debit_list):
    max_for_turbine = DEBIT_TOTAL if debit_max > DEBIT_TOTAL else debit_max
    list_debit_turbine = list(np.arange(MIN_DEBIT, max_for_turbine + PAS_DEBIT,
                                  PAS_DEBIT))
    if turbines_working[i]:
      list_debit_turbine[-1] = max_for_turbine
      list_debit_turbine = round_list(list_debit_turbine)
    else:
      list_debit_turbine = [MIN_DEBIT]
    
    debit_turbine_possible[i] = list_debit_turbine
  
  # max_for_turbine = DEBIT_TOTAL if MAX_DEBIT > DEBIT_TOTAL else MAX_DEBIT
  # debit_turbine = list(np.arange(MIN_DEBIT, max_for_turbine + PAS_DEBIT,
  #                                 PAS_DEBIT))
  # debit_turbine[-1] = max_for_turbine
  # debit_turbine = round_list(debit_turbine)

  return debit_turbine_possible


def getOptimalSolution(stage: pd.DataFrame, turbineID: int) -> pd.DataFrame:
  xn = f"X{turbineID}"
  fn = f"F{turbineID}"

  for debit_restant in stage.index:
    # Filter out non-numeric values and convert to float
    numeric_values = stage.loc[debit_restant, 
                               stage.columns.difference([fn, xn])]
    numeric_values = numeric_values.apply(pd.to_numeric, errors='coerce')
    numeric_values = numeric_values.dropna()  # Drop NaN values

    if not numeric_values.empty:
      max_value = numeric_values.max()
      max_column = numeric_values.idxmax()
      stage.at[debit_restant, fn] = max_value
      stage.at[debit_restant, xn] = max_column
  
  return stage

def max_on_all_turbine(max_debit_turbines, turbines_working: List[bool]):
  turbines = [index for index, value in enumerate(turbines_working, start=1) if value]
  # print(turbines)
  loopForwardPass
  listeEtats = {}
  debits_possible = [[],[],[],[],[]]
  for i, max_debit_turbine in enumerate(max_debit_turbines):
    listeEtats[i] = [np.sum(max_debit_turbines[i:])]
    debits_possible[i] = [max_debit_turbine]
  emptyStages = createStages(turbines=turbines,
                       listeEtats=listeEtats,
                       debits_possible=debits_possible)

  # print(listeEtats)
  # print(debits_possible)

  for turbineID in emptyStages:
    print(f"{turbineID}")
    print("====")
    print(f"{emptyStages[turbineID]}")
    print("------")
    # xn, fn = addOptimalResultCols(stage[turbineID], turbineID)

  filledStages = backwardPass(turbines, emptyStages,max_debit_turbine)
  # print(stage[turbineID])





def createStages(turbines: list,
                 listeEtats: Dict[int,List[int]],
                 debits_possible: List[List[float]]):
  
  result = {}
  for i in turbines[:-1]:
    df = pd.DataFrame(index = listeEtats.get(i), columns = debits_possible[i-1])
    result[i] = df
  # La dernière turbine n'a pas de colonnes car on utilise tout le débit possible
  result[turbines[-1]] = pd.DataFrame(index = listeEtats.get(turbines[-1]), 
                                      columns = [])
  return result

def addOptimalResultCols(stage: pd.DataFrame, turbineID: int):
  xn = f"X{turbineID}"
  fn = f"F{turbineID}"
  stage[xn] = None
  stage[fn] = None
  return xn, fn

def powerFunction(debit_turbine: Union[int,float],
                  chute_nette: Union[int,float],
                  coefficients: list):
  return coefficients[0] + \
         coefficients[1] * debit_turbine +\
         coefficients[2] * chute_nette + \
         coefficients[3] * debit_turbine**2 +\
         coefficients[4] * debit_turbine * chute_nette +\
         coefficients[5] * chute_nette**2 +\
         coefficients[6] * debit_turbine**3 +\
         coefficients[7] * debit_turbine**2*chute_nette

def fillLastStage(stage: pd.DataFrame,
                  fonctionPuissance: list,
                  turbineID: int) -> pd.DataFrame: 
  xn, fn = addOptimalResultCols(stage, turbineID)
  for debit_restant in stage.index:
    debit_turbine = debit_restant
    stage.loc[debit_restant, xn] = debit_restant
    
    chute_nette = getChuteNette(debit_turbine)
    puissance = powerFunction(debit_turbine, chute_nette, fonctionPuissance)
    stage.loc[debit_restant, fn] = puissance
  return stage



def fillPreviousStages(stage: pd.DataFrame,
                       previousStage: pd.DataFrame,
                       fonctionPuissance: list,
                       turbineID: int,
                       previousTurbineID: int,
                       turbineIndex: int,
                       nb_turbines: int,
                       max_debit_turbine : List[float]
                       ) -> pd.DataFrame: 
  
  
  if np.sum(max_debit_turbine[turbineID:]) < DEBIT_TOTAL:
    debit_restant_max_for_turbine_after = np.sum(max_debit_turbine[turbineID:]) 
  else:
    debit_restant_max_for_turbine_after = DEBIT_TOTAL

  
  debit_turbine_columns = stage.columns
  addOptimalResultCols(stage, turbineID)
  
  # print(previousStage.columns)

  for debit_restant in stage.index:
    for debit_turbine in debit_turbine_columns:
      chute_nette = getChuteNette(debit_turbine)
      

      debit_for_turbine_after = round(debit_restant - debit_turbine,2)
      # print(f"debit total : {debit_restant_max_for_turbine_after} ",end=" ")
      # print(f"debit_restant {debit_restant} / debit_turbine {debit_turbine} => {debit_for_turbine_after}")
      
      if debit_for_turbine_after < 0 \
      or  debit_for_turbine_after > debit_restant_max_for_turbine_after \
      or  debit_for_turbine_after not in previousStage.index :
        # print(f"{(debit_for_turbine_after < 0)} or {(debit_for_turbine_after > debit_restant_max_for_turbine_after)} or {(debit_for_turbine_after not in previousStage.index)}")

        stage.loc[debit_restant, debit_turbine] = "-"
        debit_for_turbine_after = None

      if debit_for_turbine_after != None:
        # print("dif")
        # print(f"[{debit_for_turbine_after}, F{previousTurbineID}]")
        puissance_add = previousStage.loc[debit_for_turbine_after, f"F{previousTurbineID}"]
        puissance = 0
        if puissance_add != None:
          puissance = puissance_add + powerFunction(debit_turbine, chute_nette, 
                                                  fonctionPuissance)   
            
        stage.loc[debit_restant, debit_turbine] = puissance

    stage = getOptimalSolution(stage, turbineID)
    
  return stage

def backwardPass(turbines: list, emptyStages, max_debit_turbine):
  nb_turbines = len(turbines)
  filledStages = {}
  for i, turbineID in enumerate(turbines[::-1]):
    # print(turbineID)
    if turbineID == turbines[-1]:
      # print("first")
      filledStages[turbineID] = fillLastStage(copy.copy(emptyStages[turbineID]),
                                  ARRAY_COEFFICIENTS_TURBINES[turbineID - 1],
                                  turbineID)
    else:
      filledStages[turbineID] = fillPreviousStages(copy.copy(emptyStages[turbineID]),
                                  copy.copy(filledStages[prevStage]),
                                  ARRAY_COEFFICIENTS_TURBINES[turbineID - 1],
                                  turbineID,
                                  prevStage,
                                  nb_turbines - i,
                                  nb_turbines,
                                  max_debit_turbine)
    prevStage = turbineID
  return filledStages

def forward_pass(stage : pd.DataFrame,
                 df_tableau_turbine_after :pd.DataFrame,
                 prevStageID: int) -> pd.DataFrame:
  debit_restant = stage.index[0]
  debit_choose = stage.loc[debit_restant,f"X{prevStageID}"]
  # print(prevStageID)
  # print(f"{debit_restant} / {debit_choose}")
  # print(stage)

  debit_restant_after = debit_restant - debit_choose
  debit_restant_after = round(debit_restant_after,2)

  final_df = df_tableau_turbine_after.loc[[debit_restant_after]]
  return final_df

def loopForwardPass(turbines, filledStages):
    dfs_choose = {}
    prevStage = turbines[0]
    dfs_choose[prevStage] = copy.copy(filledStages[prevStage])
    for i in turbines[1:]:
      # print(i)
      dfs_choose[i] = forward_pass(stage = copy.copy(dfs_choose[prevStage]),
                                 df_tableau_turbine_after = copy.copy(filledStages[i]),
                                 prevStageID = prevStage)
      prevStage = i
    return dfs_choose

def dynamicProgrammingAlgorithm(turbines_working, 
                                max_debit_turbine : List[float]):
  
  turbines = [index for index, value in enumerate(turbines_working, start=1) if value]
  # print(turbines)
  listeEtats = getStates(turbines, max_debit_turbine)
  # print(" ==== LIST ETATS ==== ")
  # print(f" 1 : {listeEtats[1]}")
  # # print(f" 2 : {listeEtats[2]}")
  # print(f" 3 : {listeEtats[3]}")
  # print(f" 4 : {listeEtats[4]}")
  # print(f" 5 : {listeEtats[5]}")
  debits_possible = getPossibleValues(turbines_working=turbines_working, 
                                      max_debit_list=max_debit_turbine)
  # print("==== DEBIT POSSIBLE ====")
  # print(debits_possible)
  
  
  emptyStages = createStages(turbines, listeEtats, debits_possible)
  # print("==== EMPTY STAGE ===")
  # print(emptyStages)
  # print("=================")
  filledStages = backwardPass(turbines, emptyStages,max_debit_turbine)
  # print(filledStages)
  # print("=======")
  dfs_choose = loopForwardPass(turbines, filledStages)
  return dfs_choose

def initResultDf():
  dfResult = pd.DataFrame(index=["Original", "Computed"], columns = ["Débit disponible", "Puissance totale"])
  dfResult.loc[:, "Puissance totale"] = 0
  return dfResult

def extractResults(dfResult, actives_turbines, result):
    for i, IDturbine in enumerate(actives_turbines):
      colNameDebit = "Débit T" + str(IDturbine)
      colNamePuissance = "Puissance T" + str(IDturbine)
      if (i < len(actives_turbines) - 1):
        nextTurbine = actives_turbines[i+1]
        # print(f'{IDturbine}/ {result[IDturbine]} => {nextTurbine}/{result[nextTurbine]}')


        currentPuissance = result[IDturbine][f"F{IDturbine}"].values[0] - result[nextTurbine][f'F{nextTurbine}'].values[0]
      else:
        currentPuissance = result[IDturbine]['F' + str(IDturbine)].values[0]
      currentDebit = result[IDturbine]['X'+str(IDturbine)].values[0]
      dfResult.loc["Computed", colNameDebit] = currentDebit
      dfResult.loc["Computed", colNamePuissance] = currentPuissance
      dfResult.loc["Computed", "Puissance totale"] += currentPuissance


def get_active_turbines(df_file: pd.DataFrame, excel_line_index: int) -> List[bool]:
    active_turbines = [True if df_file.loc[excel_line_index, f"P{i} (MW)"] else False for i in range(1, 6)]
    return active_turbines

def initialize_result_df(debit_total: float, debit_total_computed: float, df_file_row: pd.Series) -> pd.DataFrame:
    df_result = initResultDf()

    df_result.at["Original", "Débit disponible"] = debit_total
    df_result.at["Computed", "Débit disponible"] = debit_total_computed
    
    puissance_totale = 0
    for i in range(1, 5+1, 1):
        df_result.loc["Original", f"Débit T{i}"] = df_file_row[f"Q{i} (m3/s)"]
        df_result.loc["Original", f"Puissance T{i}"] = df_file_row[f"P{i} (MW)"]
        df_result.loc["Computed", f"Débit T{i}"] = 0
        df_result.loc["Computed", f"Puissance T{i}"] = 0
        puissance_totale += df_file_row[f"P{i} (MW)"]

    df_result.at["Original", "Puissance totale"] = puissance_totale
    
    return df_result

def find_nearest_number(reference_list, number, is_max=True):
    if is_max:
        closest = max(filter(lambda x: x <= number, reference_list))
    else:
        closest = min(filter(lambda x: x >= number, reference_list))
    return closest


def round_list(numbers, decimals=2):
    """
    Arrondit tous les nombres dans la liste 'numbers' à 'decimals' décimales.
    """
    return [round(number, decimals) for number in numbers]


def read_excel_yield(filename, starting_row, end_row) -> Iterator[pd.DataFrame]:
    yield pd.read_excel(filename, skiprows=starting_row , nrows=end_row+1)









