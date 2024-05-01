import argparse
from subprocess import DEVNULL, STDOUT, check_call
import time
import os 

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--relation',
        default = 'P31',
        type=str
    )
    parser.add_argument(
        '-type',
        type=str
    )
    parser.add_argument(
        '--hdt_querier',
        default = './../../../../../sharewithserver/QueryHDT/SparqlHomemade2.jar',
        type=str
    )
    parser.add_argument(
        '--hdt_file',
        default = './../../../../../Graphs_HDT/Wikidata/Wikidata_final.hdt',
        type=str
    )
    args = parser.parse_args()
    relation = args.relation
    type_ent = args.type
    hdtsparql_file = args.hdt_querier
    hdt_file = args.hdt_file
    
                    ##### DATA GENERATION
    print("Data Generation")

    os.chdir("./1.DataGeneration")

    cmd = f"python3 ./1.QueryGenerator.py {relation} {type_ent}"
    check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)

    cmd = f"python3 ./2.QueryLauncher.py {type_ent} {hdtsparql_file} {hdt_file}"
    check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
    
    cmd = f"python3 ./3.GenerateData.py {type_ent}"
    check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)

    cmd = f"python3 ./4.SpliterRel.py {type_ent}"
    check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)

    os.chdir("./../")

    f_time = open(f"./0.Data/{type_ent}/RunningTime.csv", "w", 1, encoding="UTF-8")

    # Validy Threshold (vt) = 1 - Error Threshold (et)
    for vt in [.95, .9, .8]:
        for gt in [10, 5, 2]:

            os.chdir("./1.DataGeneration")

            print("Key Discovery")
            start = time.time()
            cmd = f"python3 ./5.RuleDiscovery.py {type_ent} {gt} {vt}"
            check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
            end = time.time()
            f_time.write(f"_,{gt},{vt},_,Key_Disccovery,{end-start}\n")
            
            os.chdir("./..")

            for strat in ["R", "RxV"]:

                os.chdir("./2.Symbolic")

                print("Symbolic")
                start = time.time()
                cmd = f"python3 ./1.Tester.py {type_ent} Rules_{strat}_{gt}_{vt}.tsv valid.quintuplet {vt} 20"
                check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
                end = time.time()
                f_time.write(f"{strat},{gt},{vt},Basic,Symbolic,{end-start}\n")

                start = time.time()
                cmd = f"python3 ./1.TesterRemoveOverlap.py {type_ent} Rules_{strat}_{gt}_{vt}.tsv valid.quintuplet {vt} 20"
                check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
                end = time.time()
                f_time.write(f"{strat},{gt},{vt},Remove,Symbolic,{end-start}\n")

                os.chdir("./../")

                os.chdir("./3.MachineLearning/")

                print("ML")
                print("\t Naive")
                start = time.time()
                cmd = f"python3 ./1.0.RulesWeightsTrain.py {type_ent} Rules_{strat}_{gt}_{vt}.tsv train_ML.quintuplet 20"
                check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
                end = time.time()
                f_time.write(f"{strat},{gt},{vt},Basic,1,{end-start}\n")

                start = time.time()
                cmd = f"python3 ./1.1.RulesWeightsTester.py {type_ent} Rules_{strat}_{gt}_{vt}.tsv valid.quintuplet 20"
                check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
                end = time.time()
                f_time.write(f"{strat},{gt},{vt},Basic,2,{end-start}\n")

                start = time.time()
                cmd = f"python3 ./2.0.TreeRemoveUnknown.py {type_ent} ML_train_ML.quintuplet_Rules_{strat}_{gt}_{vt}.tsv train_ML.gt ML_valid.quintuplet_Rules_{strat}_{gt}_{vt}.tsv valid.gt"
                check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
                end = time.time()
                f_time.write(f"{strat},{gt},{vt},Basic,3,{end-start}\n")

                start = time.time()
                print("\tRemove")
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
                cmd = f"python3 ./2.0.TreeRemoveUnknown.py {type_ent} ML_train_ML.quintuplet_Rules_{strat}_{gt}_{vt}.tsv_strat_Remove train_ML.gt ML_valid.quintuplet_Rules_{strat}_{gt}_{vt}.tsv_strat_Remove valid.gt"
                check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
                end = time.time()
                f_time.write(f"{strat},{gt},{vt},Remove,3,{end-start}\n")

                os.chdir("./../")