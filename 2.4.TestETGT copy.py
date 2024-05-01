import argparse
from subprocess import DEVNULL, STDOUT, check_call
import time
import os 
import pandas as pd

def output_results(file, strat_rule_local, gt_local, et_local, strat_local, nb_correct_pred_local, nb_pred_local):
    file.write(f"{strat_rule_local},{gt_local},{et_local},{strat_local},{nb_correct_pred_local},{nb_pred_local}\n")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-type',
        type=str
    )
    args = parser.parse_args()
    type_ent = args.type
    
                    ##### DATA GENERATION
    path = f"./0.Data/{type_ent}/"
    f_time = open(f"{path}RunningTimeETGT2.csv", "w", 1, encoding="UTF-8")

    file_res = open(f"{path}Results_ETGT2.csv", "w", encoding="UTF-8") 
    file_res.write("Rule_strat, GT, ET, Strat, #CorrectPred, #Pred\n")

    gt_pd = pd.read_csv(f"{path}valid.gt", names=["GT_value"])

    # Validy Threshold (vt) = 1 - Error Threshold (et)
    # vt = 0.95
    # gt = 5
    strat = "RxV"


    for (vt, gt) in [(0.9, 5)]:#, (0.95,2), (0.95,5)]:
        os.chdir("./1.DataGeneration")

        print("Key Discovery")
        start = time.time()
        cmd = f"python3 ./5.RuleDiscovery.py {type_ent} {gt} {vt}"
        check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
        end = time.time()
        f_time.write(f"_,{gt},{vt},_,Key_Disccovery,{end-start}\n")
        
        os.chdir("./..")

        os.chdir("./3.MachineLearning")

        start = time.time()
        cmd = f"python3 ./1.2.RulesWeightsTrainRemove.py {type_ent} Rules_{strat}_{gt}_{vt}.tsv train_ML.quintuplet 20"
        #check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
        end = time.time()
        f_time.write(f"{strat},{gt},{vt},Remove,1,{end-start}\n")

        start = time.time()
        cmd = f"python3 ./1.3.RulesWeightsTesterRemove.py {type_ent} Rules_{strat}_{gt}_{vt}.tsv valid.quintuplet 20"
        check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
        end = time.time()
        f_time.write(f"{strat},{gt},{vt},Remove,2,{end-start}\n")

        start = time.time()
        cmd = f"python3 ./2.0.TreeRemoveUnknown.py {type_ent} ML_train_ML.quintuplet_Rules_{strat}_{gt}_{vt}.tsv train_ML.gt ML_valid.quintuplet_Rules_{strat}_{gt}_{vt}.tsv valid.gt"
        check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
        end = time.time()
        f_time.write(f"{strat},{gt},{vt},Remove,3,{end-start}\n")
        os.chdir("./../")

        with open(f"{path}Weights_ML_train_ML.quintuplet_Rules_{strat}_{gt}_{vt}.tsv_strat_Remove_ML_valid.quintuplet_Rules_{strat}_{gt}_{vt}.tsv_strat_Remove.txt", "r") \
                    as f_r:

            line = f_r.readline()[:-1]
            nb_correct_pred, nb_pred = line.split(" / ")
            output_results(file_res, strat, gt, vt, "Remove", nb_correct_pred, nb_pred)


f_time.close()
file_res.close()
    
