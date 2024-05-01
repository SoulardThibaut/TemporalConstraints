import sys 
import numpy as np
import copy 
import multiprocessing as mp
from subprocess import DEVNULL, STDOUT, check_call

sys.path.append("./../../..")
import TimePackage as tp

temporal_granularity = "D"
today = np.datetime64("2023-12-31", temporal_granularity)

def to_common_uri(uri_relation):
    namespace_common = "http://www.wikidata.org/prop/P"
    namespace_direct = "http://www.wikidata.org/prop/direct/P"
    if uri_relation[:len(namespace_direct)] == namespace_direct:
        return namespace_common+uri_relation[len(namespace_direct):]
    else:
        return uri_relation

def processing_date_unknown_allowed(date_raw) -> np.datetime64:
    if date_raw == "None":
        return None
    else:
        return np.datetime64(date_raw, temporal_granularity)

def function_subprocess(id, works, entities, rules) :
    print(id)
    with open(f"./{path}{files_test}_{rules_to_use}_{id}", "w", encoding="UTF-8") as f:
        try: 
            while(True):
                if works.qsize() %1000 == 0:
                    print(works.qsize())

                i, (true_triple, false_triple) = works.get(timeout=10)

                for j, triple in enumerate([true_triple, false_triple]):
                    decision_per_rule = []
                    # 0 -> Followed
                    # 1 -> Refuted
                    # 2 -> Rule not on the sequence
                    # 3 -> Multi
                    # 4 -> No data on R
                    # 5 -> The triple added overlaps on the R level
                    # 6 -> The triple added overlaps on the RxV level

                    if not triple.head in entities:
                        decision_per_rule = [4]*len(rules)
                    else:
                        entity = entities[triple.head]
                        entity.remove_triple(true_triple)

                        entity.add_triple(triple)
                        entity.update_lifespan()
                        
                        for rule in rules:
                            
                            if len({triple.relation, (triple.relation, triple.value)}.intersection({rule.get_a(), rule.get_b()})) == 0:
                                decision_per_rule.append(2)
                            else:

                                ts_a = tp.TimeSequence(tp.ordered_time_sequence_first_start_with_rxv(entity, rule.get_a()))
                                ts_b = tp.TimeSequence(tp.ordered_time_sequence_first_start_with_rxv(entity, rule.get_b()))
                                if (not ts_a.multi_valuation_temporal) and (not ts_b.multi_valuation_temporal):
                                    if (len(ts_a.intervals) != 0) and (len(ts_b.intervals) != 0):
                                        tsr = tp.TimeSequenceRelation(rule.get_a(), rule.get_b(), ts_a, ts_b)
                                        if (str(rule.get_a()) == tsr.name_relation_A):
                                            if rule.get_r() in tsr.A_o_B:
                                                decision_per_rule.append(0)
                                            else:
                                                decision_per_rule.append(1)
                                        else:
                                            if rule.get_r() in tsr.B_o_A:
                                                decision_per_rule.append(0)
                                            else:
                                                decision_per_rule.append(1)
                                    else:
                                        decision_per_rule.append(4)
                                else:
                                    decision_per_rule.append(3)

                        entity.remove_triple(triple)
                        entity.add_triple(true_triple)
                        entity.update_lifespan()
                    
                    f.write(f"{i+j},{','.join([str(d) for d in decision_per_rule])}\n")
        except Exception as error:
            import traceback
            print(traceback.print_stack())
            print(f"{id} : OVER")
            print(error)

if __name__ == '__main__':
    
    type_ent = sys.argv[1]
    path = f"./../0.Data/{type_ent}/"
    rules_to_use = sys.argv[2]
    files_test = sys.argv[3]

    nb_process = int(sys.argv[4])

    entities = {}

    print("Load knowledge")
    with open(f"{path}train_cst_knowledge.quintuplet", "r", encoding="UTF-8") as f_read:
        for line in f_read.readlines():
            head, relation, value, start, end = line[:-1].split("\t")

            relation = to_common_uri(relation)

            if not head in entities:
                entities[head] = tp.Entity(head, today, temporal_granularity) 

            entities[head].add_triple(tp.Triple(head, relation, value,\
                                    tp.Interval(processing_date_unknown_allowed(start),\
                                                processing_date_unknown_allowed(end))))
    
    print("Load rules")
    rules = []
    with open(f"{path}{rules_to_use}", "r", encoding="UTF-8") as f:
        for line in f.readlines():
            rule = tp.TemporalRule.load_a_rule(line)
            rules.append(rule)

    print("Load facts to test")
    facts_to_try = []
    with open(f"{path}{files_test}", "r", encoding="UTF-8") as f:
        line = f.readline()
        cpt = 0
        while line!="":
        
            if line[-1] == "\n":
                line = line[:-1]
            entity, relation, value, start, end = line.split("\t")

            start = processing_date_unknown_allowed(start)
            end = processing_date_unknown_allowed(end)

            true_triple = tp.Triple(entity, relation, value, tp.Interval(start, end))

            line = f.readline()
            if line[-1] == "\n":
                line = line[:-1]
            entity, relation, value, start, end = line.split("\t")

            start = processing_date_unknown_allowed(start)
            end = processing_date_unknown_allowed(end)

            false_triple = tp.Triple(entity, relation, value, tp.Interval(start, end))

            facts_to_try.append((cpt, (true_triple, false_triple)))
            line = f.readline()
            cpt+=2
    
    print("Verify facts")
    with mp.Manager() as manager:

        works = mp.Queue()
        for i, fact in facts_to_try:
            works.put((i, fact))

        print(works.qsize())
        processes = []
        for id in range(nb_process):
            p = mp.Process(target=function_subprocess, args=(id,\
                                                            works,\
                                                            copy.deepcopy(entities),\
                                                            rules))
            processes.append(p)
            p.start()

        for j in range(len(processes)):
            processes[j].join()

        cmd = "cat "
        for id in range(nb_process):
            cmd += f"{path}{files_test}_{rules_to_use}_{id} "
        cmd += f"> {path}ML_{files_test}_{rules_to_use}"
        check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)

        for id in range(nb_process):
            cmd = f"rm {path}{files_test}_{rules_to_use}_{id} "
            check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)


                
