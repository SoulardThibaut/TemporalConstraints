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

    path = f"./0.Data/{type_ent}/"
    gt_pd = pd.read_csv(f"{path}valid.gt", names=["GT_value"])
    
    vt = 0.9
    gt = 5
    strat = "R"

    ### Symb VS ML
    with open(f"{path}Running_Time_Symb_VS_Ml.csv", "w", 1, encoding="UTF-8") as f_time:
        with open(f"{path}Results_Symb_VS_ML.csv", "w", encoding="UTF-8")  as file_res:

            file_res.write("Rule_strat, GT, ET, Strat, #CorrectPred, #Pred\n")
            
            os.chdir("./1.DataGeneration")

            print("Key Discovery")
            start = time.time()
            cmd = f"python3 ./5.RuleDiscovery.py {type_ent} {gt} {vt}"
            check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
            end = time.time()
            f_time.write(f"_,{gt},{vt},{strat},Key_Disccovery,{end-start}\n")
            
            os.chdir("./..")

            os.chdir("./2.Symbolic")

            print("Symbolic")
            start = time.time()
            cmd = f"python3 ./1.Tester.py {type_ent} Rules_{strat}_{gt}_{vt}.tsv valid.quintuplet {vt} 20"
            check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
            end = time.time()
            f_time.write(f"{strat},{gt},{vt},Remove,Symbolic,{end-start}\n")
            os.chdir("./../")

            os.chdir("./3.MachineLearning")
            print("\tRemove")
            start = time.time()
            cmd = f"python3 ./1.0.RulesWeightsTrain.py {type_ent} Rules_{strat}_{gt}_{vt}.tsv train_ML.quintuplet 20"
            check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
            end = time.time()
            f_time.write(f"{strat},{gt},{vt},Remove,1,{end-start}\n")

            start = time.time()
            cmd = f"python3 ./1.1.RulesWeightsTester.py {type_ent} Rules_{strat}_{gt}_{vt}.tsv valid.quintuplet 20"
            check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
            end = time.time()
            f_time.write(f"{strat},{gt},{vt},Remove,2,{end-start}\n")

            start = time.time()
            cmd = f"python3 ./2.0.TreeRemoveUnknown.py {type_ent} ML_train_ML.quintuplet_Rules_{strat}_{gt}_{vt}.tsv train_ML.gt ML_valid.quintuplet_Rules_{strat}_{gt}_{vt}.tsv valid.gt"
            check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
            end = time.time()
            f_time.write(f"{strat},{gt},{vt},Remove,3,{end-start}\n")
            
            os.chdir("./..")

            symbolic_basic = pd.read_csv(f"{path}Symbolic_valid.quintuplet_Rules_{strat}_{gt}_{vt}.tsv",\
                                                    index_col=0, sep="\t",\
                                                    names=["Pred", "Comment", "Confidence", "Support"])
            symbolic_basic_merged = pd.merge(symbolic_basic, gt_pd, left_index=True, right_index=True)
            symbolic_basic_merged_prediction_made = symbolic_basic_merged[\
                            symbolic_basic_merged["Pred"].map(\
                                lambda x : x in [0,1])]
            nb_correct_pred = sum(symbolic_basic_merged_prediction_made[["Pred", "GT_value"]].apply(\
                                lambda x: (not bool(x["Pred"])) == x["GT_value"], \
                                axis=1))
            nb_pred = len(symbolic_basic_merged_prediction_made)
            output_results(file_res, strat, gt, vt,"Symbolic",nb_correct_pred, nb_pred)


            with open(f"{path}Weights_ML_train_ML.quintuplet_Rules_{strat}_{gt}_{vt}.tsv_ML_valid.quintuplet_Rules_{strat}_{gt}_{vt}.tsv.txt", "r") \
                    as f_r:

                line = f_r.readline()[:-1]
                nb_correct_pred, nb_pred = line.split(" / ")
                output_results(file_res, strat, gt, vt, "ML", nb_correct_pred, nb_pred)

    ### Types Constraint
    with open(f"{path}Running_Time_R_VS_RxV.csv", "w", 1, encoding="UTF-8") as f_time:
        with open(f"{path}Results_R_VS_RxV.csv", "w", encoding="UTF-8")  as file_res:

            for strat in ["R", "RxV"]:

                os.chdir("./3.MachineLearning")

                start = time.time()
                cmd = f"python3 ./1.0.RulesWeightsTrain.py {type_ent} Rules_{strat}_{gt}_{vt}.tsv train_ML.quintuplet 20"
                check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
                end = time.time()
                f_time.write(f"{strat},{gt},{vt},Remove,1,{end-start}\n")

                start = time.time()
                cmd = f"python3 ./1.1.RulesWeightsTester.py {type_ent} Rules_{strat}_{gt}_{vt}.tsv valid.quintuplet 20"
                check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
                end = time.time()
                f_time.write(f"{strat},{gt},{vt},Remove,2,{end-start}\n")

                start = time.time()
                cmd = f"python3 ./2.0.TreeRemoveUnknown.py {type_ent} ML_train_ML.quintuplet_Rules_{strat}_{gt}_{vt}.tsv train_ML.gt ML_valid.quintuplet_Rules_{strat}_{gt}_{vt}.tsv valid.gt"
                check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
                end = time.time()
                f_time.write(f"{strat},{gt},{vt},Remove,3,{end-start}\n")
                os.chdir("./../")

                with open(f"{path}Weights_ML_train_ML.quintuplet_Rules_{strat}_{gt}_{vt}.tsv_ML_valid.quintuplet_Rules_{strat}_{gt}_{vt}.tsv.txt", "r") \
                            as f_r:

                        line = f_r.readline()[:-1]
                        nb_correct_pred, nb_pred = line.split(" / ")
                        output_results(file_res, strat, gt, vt, "ML", nb_correct_pred, nb_pred)

    ### Types Constraint
    with open(f"{path}Running_Time_Naive_VS_Remove.csv", "w", 1, encoding="UTF-8") as f_time:
        with open(f"{path}Results_Naive_VS_Remove.csv", "w", encoding="UTF-8")  as file_res:

            os.chdir("./3.MachineLearning")

            start = time.time()
            cmd = f"python3 ./1.0.RulesWeightsTrain.py {type_ent} Rules_{strat}_{gt}_{vt}.tsv train_ML.quintuplet 20"
            check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
            end = time.time()
            f_time.write(f"{strat},{gt},{vt},Naive,1,{end-start}\n")

            start = time.time()
            cmd = f"python3 ./1.1.RulesWeightsTester.py {type_ent} Rules_{strat}_{gt}_{vt}.tsv valid.quintuplet 20"
            check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
            end = time.time()
            f_time.write(f"{strat},{gt},{vt},Naive,2,{end-start}\n")

            start = time.time()
            cmd = f"python3 ./2.0.TreeRemoveUnknown.py {type_ent} ML_train_ML.quintuplet_Rules_{strat}_{gt}_{vt}.tsv train_ML.gt ML_valid.quintuplet_Rules_{strat}_{gt}_{vt}.tsv valid.gt"
            check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
            end = time.time()
            f_time.write(f"{strat},{gt},{vt},Naive,3,{end-start}\n")

            start = time.time()
            cmd = f"python3 ./1.2.RulesWeightsTrainRemove.py {type_ent} Rules_{strat}_{gt}_{vt}.tsv train_ML.quintuplet 20"
            check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
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

            with open(f"{path}Weights_ML_train_ML.quintuplet_Rules_{strat}_{gt}_{vt}.tsv_ML_valid.quintuplet_Rules_{strat}_{gt}_{vt}.tsv.txt", "r") \
                        as f_r:

                    line = f_r.readline()[:-1]
                    nb_correct_pred, nb_pred = line.split(" / ")
                    output_results(file_res, strat, gt, vt, "Naive", nb_correct_pred, nb_pred)

            with open(f"{path}Weights_ML_train_ML.quintuplet_Rules_{strat}_{gt}_{vt}.tsv_strat_Remove_ML_valid.quintuplet_Rules_{strat}_{gt}_{vt}.tsv_strat_Remove.txt", "r") \
                        as f_r:

                    line = f_r.readline()[:-1]
                    nb_correct_pred, nb_pred = line.split(" / ")
                    output_results(file_res, strat, gt, vt, "Rmove", nb_correct_pred, nb_pred)

    ### Types Constraint
    with open(f"{path}Running_Time_ETGT.csv", "w", 1, encoding="UTF-8") as f_time:
        with open(f"{path}Results_ETGT.csv", "w", encoding="UTF-8")  as file_res:
            for vt in [0.9, 0.95]:
                for gt in [2,5]:
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
                    check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
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
