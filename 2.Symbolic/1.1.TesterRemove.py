import sys 
import numpy as np
import copy 
import multiprocessing as mp
from subprocess import DEVNULL, STDOUT, check_call

sys.path.append("./..")
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

def function_subprocess(id, works, entities, rule_indexed) :
    print(id)
    with open(f"./{path}{files_test}_{rules_to_use}_{id}", "w", encoding="UTF-8") as f:
        try: 
            while(True):
                if works.qsize() %1000 == 0:
                    print(works.qsize())

                i, triple = works.get(timeout=10)
                # print(id, i , triple)
                f.write(f"{i}\t")
                # for triple in facts_to_try:
                if not triple.head in entities:
                    f.write("2\tNo data on the head\t_\t_\n")
                else:
                    entity = entities[triple.head]

                    date_triple = triple.date

                    if date_triple.start == None:
                        date_triple.start = entity.get_lifespan().get_start()

                    if date_triple.end == None:
                        date_triple.end = today

                    ts_r = tp.ordered_time_sequence_first_start_with_rxv_return_triples(entity, triple.relation)
                    triples_to_add_back = set()
                    try:
                        for t in ts_r:
                            date_t = copy.deepcopy(t.date)

                            if date_t.start == None:
                                date_t.start = entity.get_lifespan().get_start()

                            if date_t.end == None:
                                date_t.end = today

                            if date_triple.is_A_overlaps(date_t) or\
                                date_triple.is_A_during(date_t) or\
                                date_triple.is_A_starts(date_t) or\
                                date_triple.is_A_finishes(date_t) or\
                                date_triple.is_A_equal(date_t):
                                entity.remove_triple(t)
                                triples_to_add_back.add(t)
                    except:
                        print(t)
                        print(ts_r)
                        print(entity.triples_per_r[triple.relation])

                    # Should already been taken care by the previous part of code
                    ts_rxv = tp.ordered_time_sequence_first_start_with_rxv_return_triples(entity, (triple.relation, triple.value))
                    for t in ts_rxv:
                        date_t = copy.deepcopy(t.date)

                        if date_t.start == None:
                            date_t.start = entity.get_lifespan().get_start()

                        if date_t.end == None:
                            date_t.end = today

                        if date_triple.is_A_overlaps(date_t) or\
                            date_triple.is_A_during(date_t) or\
                            date_triple.is_A_starts(date_t) or\
                            date_triple.is_A_finishes(date_t) or\
                            date_triple.is_A_equal(date_t):
                            entity.remove_triple(t)
                            triples_to_add_back.add(t)
                        
                    entity.add_triple(triple)

                    entity.update_lifespan()

                    #Followed, not Followed, Unknown
                    count_rules = [0,0,0]

                    #Could work on 
                    sequences = [True, True]
                    
                    # ts = tp.TimeSequence(tp.ordered_time_sequence_first_start(entity, triple.relation))
                    
                    if triple.relation in rule_indexed:
                        for rule in rule_indexed[triple.relation]:
                            ts_a = tp.TimeSequence(tp.ordered_time_sequence_first_start(entity, rule.get_a()))
                            ts_b = tp.TimeSequence(tp.ordered_time_sequence_first_start(entity, rule.get_b()))
                            if (not ts_a.multi_valuation_temporal) and (not ts_b.multi_valuation_temporal):
                                if (len(ts_a.intervals) != 0) and (len(ts_b.intervals) != 0):
                                    tsr = tp.TimeSequenceRelation(rule.get_a(), rule.get_b(), ts_a, ts_b, rule)
                                    if tsr.verified:
                                        count_rules[0]+=1
                                    else:
                                        count_rules[1]+=1
                                    count_rules[2]+=1
                            else:
                                sequences[0] = False

                    # ts = tp.TimeSequence(tp.ordered_time_sequence_first_start_with_rxv(entity, (triple.relation,triple.value)))
                    if (triple.relation, triple.value) in rule_indexed:
                        # print("hEllo world")
                        for rule in rule_indexed[(triple.relation, triple.value)]:
                            ts_a = tp.TimeSequence(tp.ordered_time_sequence_first_start_with_rxv(entity, rule.get_a()))
                            ts_b = tp.TimeSequence(tp.ordered_time_sequence_first_start_with_rxv(entity, rule.get_b()))
                            if (not ts_a.multi_valuation_temporal) and (not ts_b.multi_valuation_temporal):
                                if (len(ts_a.intervals) != 0) and (len(ts_b.intervals) != 0):
                                    tsr = tp.TimeSequenceRelation(rule.get_a(), rule.get_b(), ts_a, ts_b, rule)
                                    if tsr.verified:
                                        count_rules[0]+=1
                                    else:
                                        count_rules[1]+=1
                                else:
                                    count_rules[2]+=1
                            else:
                                sequences[1] = False

                    if (not sequences[0]) & (not sequences[1]):
                        f.write(f"4\tBoth sequences were multi-valued\t_\t_\n")
                        
                    elif count_rules[0] + count_rules[1] == 0:
                        f.write(f"3\tNo rules could be used\t_\t_\n")

                    elif count_rules[0] / (count_rules[0]+count_rules[1]) > seuil :
                        f.write(f"0\tTrue\t{count_rules[0] / (count_rules[0]+count_rules[1])}\t{(count_rules[0]+count_rules[1])}\n")

                    # At least one rule has refuted the thing 
                    else :
                        f.write(f"1\tFalse\t{count_rules[0] / (count_rules[0]+count_rules[1])}\t{(count_rules[0]+count_rules[1])}\n")

                    entity.remove_triple(triple)

                    for t in triples_to_add_back:
                        entity.add_triple(t)

                    entity.update_lifespan()
        except:
#            print(works.qsize())
            print(f"{id} : OVER")

if __name__ == '__main__':
    
    type_ent = sys.argv[1]
    path = f"./../0.Data/{type_ent}/"
    rules_to_use = sys.argv[2]
    files_test = sys.argv[3]
    seuil = float(sys.argv[4])


    nb_process = int(sys.argv[5])

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
    rules = {}
    rule_indexed = {}
    with open(f"{path}{rules_to_use}", "r", encoding="UTF-8") as f:
        for line in f.readlines():
            # print(line)
            rule = tp.TemporalRule.load_a_rule(line)
            rules[rule] = rule

            a = rule.get_a()
            if not a in rule_indexed:
                rule_indexed[a] = set()
            rule_indexed[a].add(rule)

            b = rule.get_b()
            if not b in rule_indexed:
                rule_indexed[b] = set()
            rule_indexed[b].add(rule)
    # print(rule_indexed)

    print("Load facts to test")
    facts_to_try = []
    with open(f"./{path}{files_test}", "r", encoding="UTF-8") as f:
        for line in f.readlines():
            if line[-1] == "\n":
                line = line[:-1]
            entity, relation, value, start, end = line.split("\t")

            start = processing_date_unknown_allowed(start)
            end = processing_date_unknown_allowed(end)

            facts_to_try.append(tp.Triple(entity, relation, value, tp.Interval(start, end)))
    
    print("Verify facts")
    with mp.Manager() as manager:

        works = mp.Queue()
        for i, fact in enumerate(facts_to_try):
            # print(i, fact)
            works.put((i, fact))

        print(works.qsize())

        processes = []
        for id in range(nb_process):
            p = mp.Process(target=function_subprocess, args=(id,\
                                                            works,\
                                                            copy.deepcopy(entities),\
                                                            rule_indexed))
            processes.append(p)
            p.start()

        for j in range(len(processes)):
            processes[j].join()

        cmd = "cat "
        for id in range(nb_process):
            cmd += f"{path}{files_test}_{rules_to_use}_{id} "
        cmd += f"> {path}Symbolic_remove_overlap_{files_test}_{rules_to_use}"
        check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)

        for id in range(nb_process):
            cmd = f"rm {path}{files_test}_{rules_to_use}_{id} "
            check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)


                
