import sys
import pandas as pd

def output_results(file, strat_rule_local, gt_local, et_local, strat_local, nb_correct_pred_local, nb_pred_local):
    file.write(f"{strat_rule_local},{gt_local},{et_local},{strat_local},{nb_correct_pred_local},{nb_pred_local}\n")

if __name__ == "__main__":
    
    ent = sys.argv[1]
    path = f"./0.Data/{ent}/"
    gt_pd = pd.read_csv(f"{path}valid.gt", names=["GT_value"])

    file_output = open(f"{path}final_results.csv", "w", encoding="UTF-8") 
    file_output.write("Rule_strat, GT, ET, Strat, #CorrectPred, #Pred\n")

    for strat in ["R", "RxV"]:
        for gt in [2, 5, 10]:
            for et in [0.80, 0.85, 0.9, 0.95]:
                
                # SYMBOLIC
                    # BASIC
                symbolic_basic = pd.read_csv(f"{path}Symbolic_valid.quintuplet_Rules_{strat}_{gt}_{et}.tsv",\
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
                output_results(file_output, strat, gt, et,"Symbolic_Basic",nb_correct_pred, nb_pred)

                    # REMOVE STRAT
                symbolic_remove = pd.read_csv(f"{path}Symbolic_remove_overlap_valid.quintuplet_Rules_{strat}_{gt}_{et}.tsv",\
                                                index_col=0, sep="\t",\
                                                names=["Pred", "Comment", "Confidence", "Support"])
                symbolic_remove_merged = pd.merge(symbolic_remove, gt_pd, left_index=True, right_index=True)
                symbolic_remove_merged_prediction_made = symbolic_remove_merged[\
                                symbolic_remove_merged["Pred"].map(\
                                    lambda x : x in [0,1])]
                nb_correct_pred = sum(symbolic_remove_merged_prediction_made[["Pred", "GT_value"]].apply(\
                                    lambda x: (not bool(x["Pred"])) == x["GT_value"], \
                                    axis=1))
                nb_pred = len(symbolic_remove_merged_prediction_made)
                output_results(file_output, strat, gt, et, "Symbolic_Remove", nb_correct_pred, nb_pred)

                # ML
                    # BASIC 
                with open(f"{path}Weights_ML_train_ML.quintuplet_Rules_{strat}_{gt}_{et}.tsv_ML_valid.quintuplet_Rules_{strat}_{gt}_{et}.tsv.txt", "r") \
                        as f_r:

                    line = f_r.readline()[:-1]
                    nb_correct_pred, nb_pred = line.split(" / ")
                    output_results(file_output, strat, gt, et, "ML_Basic", nb_correct_pred, nb_pred)

                    # REMOVE 
                with open(f"{path}Weights_ML_train_ML.quintuplet_Rules_{strat}_{gt}_{et}.tsv_strat_Remove_ML_valid.quintuplet_Rules_{strat}_{gt}_{et}.tsv_strat_Remove.txt", "r") \
                        as f_r:

                    line = f_r.readline()[:-1]
                    nb_correct_pred, nb_pred = line.split(" / ")
                    output_results(file_output, strat, gt, et, "ML_Remove", nb_correct_pred, nb_pred)

    file_output.close()