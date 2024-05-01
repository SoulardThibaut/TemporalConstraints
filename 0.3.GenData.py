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
