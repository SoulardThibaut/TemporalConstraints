import sys 
import numpy as np

sys.path.append("./..")
import TimePackage as tp

# INPUT :
#   Type

temporal_granularity = "D"
today = np.datetime64("2023-12-31", temporal_granularity)
root_data = "./../0.Data/"

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

# Find the relation that appears globally
def find_global_appiration(relation_seen, entities):

    first_appearance_of_r = {}
    ent_per_r = {}

    for r in relation_seen:
        first_appearance_of_r[r] = {}
        ent_per_r[r] = set()

        for entity in entities.values():

            timeline_r = entity.get_triples_with_r(r)
            if timeline_r != None:
                ent_per_r[r].add(entity)
                first_date = tp.ordered_timeline_of_r_mono_value_per_int(entity, r)[0][1]
                if not first_date in first_appearance_of_r[r]:
                    first_appearance_of_r[r][first_date] = 0
                first_appearance_of_r[r][first_date] += 1

    mini_appearance = 10
    threshold_global = 0.95

    global_relation = set()
    
    for r in first_appearance_of_r:

        nb_apparition = 0
        date_first = np.datetime64("2050", "Y")

        for date in first_appearance_of_r[r]:
            
            if date_first > date:
                nb_apparition = first_appearance_of_r[r][date]
                date_first = date

        if nb_apparition != 0:

            total_ent_alive_at_the_moment = 0

            for ent in ent_per_r[r]:
                if ent.get_lifespan().get_start() <= date_first:
                    total_ent_alive_at_the_moment+=1

        if nb_apparition > mini_appearance : 
            if nb_apparition / total_ent_alive_at_the_moment > threshold_global:
                global_relation.add(r)

    return global_relation

def find_multivaluation_temporal(entities):
    multi_r = set()
    multi_r_count_kept = {}
    count_per_r = {}
    count_v_per_r = {}
    #threhsold value to allow multivaluation for a value V
    # threshold_value = 10

    for ent in entities.values():
        
        for r in ent.triples_per_r:

            if not r in count_v_per_r:
                count_v_per_r[r] = {}
                if not r in multi_r_count_kept:
                    multi_r_count_kept[r] = 0
                multi_r_count_kept[r] += 1 
            
            if not r in count_per_r:
                count_per_r[r] = 0
                multi_r_count_kept[r] = 0

            count_per_r[r] += 1
        
            seq = tp.TimeSequence(tp.ordered_time_sequence_first_start(ent, r))
            if seq.multi_valuation_temporal:
                multi_r_count_kept[r] += 1 

            for t in ent.triples_per_r[r]:
                v = t.value

                if not v in count_v_per_r[r]:
                    count_v_per_r[r][v] = 0

                count_v_per_r[r][v] += 1

    for r in count_per_r:
        if multi_r_count_kept[r] * (1-seuil) >= count_per_r[r]:
            multi_r.add(r)

    rxv_allowed = set()
    for r in count_v_per_r:
        for v in count_v_per_r[r]:
            uri_name = "http://www.wikidata.org/entity/Q"
            if (type(v) == str) and (v[:len(uri_name)] == uri_name):
                if count_v_per_r[r][v] > mini_entity:
                    rxv_allowed.add((r,v))

    for ent in entities.values():
        ent.generate_triples_per_r_and_rxv(rxv_allowed)

    return multi_r

def generate_rules(couple, property, error_percent, coverage):

    first = None
    first_precision = None
    if type(couple[0]) == tuple:
        first = couple[0][0]
        first_precision = couple[0][1]
    else:
        first = couple[0]

    second = None
    second_precision = None
    if type(couple[1]) == tuple:
        second = couple[1][0]
        second_precision = couple[1][1]
    else:
        second = couple[1]

    if property[0] == "A":
        return tp.TemporalRule(first, first_precision,\
                                property[2:-2],\
                                second, second_precision,\
                                error_percent, coverage)
    else:    
        return tp.TemporalRule(second, second_precision,\
                                property[2:-2],\
                                first, first_precision,\
                                error_percent, coverage)
    
def find_rules_only_r(entities, multivaluation_relations, global_relation):

    comparison_per_couple_of_r = {}

    for ent in entities.values():
        # print(ent)
        
        r = list(set(ent.triples_per_r.keys()).difference(global_relation).difference(multivaluation_relations))
        
        for i, r_1 in enumerate(r):
            sequence_r_1 = tp.TimeSequence(tp.ordered_time_sequence_first_start(ent, r_1))
            if not sequence_r_1.multi_valuation_temporal:
                for r_2 in r[i+1:]:
                    sequence_r_2 = tp.TimeSequence(tp.ordered_time_sequence_first_start(ent, r_2))
                    if not sequence_r_2.multi_valuation_temporal:
                        relations_between_1_2 = tp.TimeSequenceRelation(r_1, r_2, sequence_r_1, sequence_r_2)
                        name = relations_between_1_2.get_name()
                        if not name in comparison_per_couple_of_r:
                            comparison_per_couple_of_r[name] = set()
                        comparison_per_couple_of_r[name].add(relations_between_1_2)
    
    props_per_couple = {}
    for r_1, r_2 in comparison_per_couple_of_r:
        props_per_couple[(r_1, r_2)] = {"total": len(comparison_per_couple_of_r[(r_1, r_2)])}
        for tsr in comparison_per_couple_of_r[(r_1, r_2)]:
            for props_r_1_o_r_2 in tsr.A_o_B:
                name_props = "A "+props_r_1_o_r_2+" B"
                if not name_props in props_per_couple[(r_1, r_2)]:
                    props_per_couple[(r_1, r_2)][name_props] = 0
                props_per_couple[(r_1, r_2)][name_props] += 1 

            for props_r_1_o_r_2 in tsr.B_o_A:
                name_props = "B "+props_r_1_o_r_2+" A"
                if not name_props in props_per_couple[(r_1, r_2)]:
                    props_per_couple[(r_1, r_2)][name_props] = 0
                props_per_couple[(r_1, r_2)][name_props] += 1 

    rules = set()

    for couple in props_per_couple:
        total = props_per_couple[couple]["total"]

        if total > mini_entity:
            for property in set(props_per_couple[couple].keys()).difference(['total']):
                if props_per_couple[couple][property] > total*seuil:
                    rules.add(generate_rules(couple, property, props_per_couple[couple][property]/total, total))
    return rules

def verify_comparison_allowed(r_1, r_2):
    if (type(r_1) == type("")) and (type(r_2) == type("")):
        return r_1 != r_2
    elif (type(r_1) == type("")):
        return r_1 != r_2[0]
    elif (type(r_2) == type("")):
        return r_1[0] != r_2
    else:
        return (r_1[0] != r_2[0]) or (r_1[1] != r_2[1])

def find_rules_r_and_rxv(entities, multivaluation_relations, global_relation):
    comparison_per_couple_of_r = {}

    for ent in entities.values():
        # print(ent)

        r = list(set(ent.triples_per_r_and_rxv.keys()).difference(global_relation).difference(multivaluation_relations))

        for i, r_1 in enumerate(r):
            # print(r_1)
            sequence_r_1 = tp.TimeSequence(tp.ordered_time_sequence_first_start_with_rxv(ent, r_1))
            if not sequence_r_1.multi_valuation_temporal:
                for r_2 in r[i+1:]:
                    if verify_comparison_allowed(r_1, r_2):
                        sequence_r_2 = tp.TimeSequence(tp.ordered_time_sequence_first_start_with_rxv(ent, r_2))
                        
                        if not sequence_r_2.multi_valuation_temporal:   
                            relations_between_1_2 = tp.TimeSequenceRelation(str(r_1), str(r_2), sequence_r_1, sequence_r_2)
                            name = relations_between_1_2.get_name()
                            if not name in comparison_per_couple_of_r:
                                comparison_per_couple_of_r[name] = set()
                            comparison_per_couple_of_r[name].add(relations_between_1_2)

    props_per_couple = {}
    for r_1, r_2 in comparison_per_couple_of_r:
        props_per_couple[(r_1, r_2)] = {"total": len(comparison_per_couple_of_r[(r_1, r_2)])}
        for tsr in comparison_per_couple_of_r[(r_1, r_2)]:
            for props_r_1_o_r_2 in tsr.A_o_B:
                name_props = "A "+props_r_1_o_r_2+" B"
                if not name_props in props_per_couple[(r_1, r_2)]:
                    props_per_couple[(r_1, r_2)][name_props] = 0
                props_per_couple[(r_1, r_2)][name_props] += 1 

            for props_r_1_o_r_2 in tsr.B_o_A:
                name_props = "B "+props_r_1_o_r_2+" A"
                if not name_props in props_per_couple[(r_1, r_2)]:
                    props_per_couple[(r_1, r_2)][name_props] = 0
                props_per_couple[(r_1, r_2)][name_props] += 1 
    
    rules = set()

    for couple in props_per_couple:
        total = props_per_couple[couple]["total"]

        if total > mini_entity:
            for property in set(props_per_couple[couple].keys()).difference(['total']):
                if props_per_couple[couple][property] > total*seuil:
                    rules.add(generate_rules(couple, property, props_per_couple[couple][property]/total, total))
                    
    return rules

if __name__ == '__main__':
    
    type_entity = sys.argv[1]
    percentage_entity = int(sys.argv[2])
    seuil = float(sys.argv[3])
    entities = {}
    relation_seen = set()

    with open(f"{root_data}{type_entity}/train_cst_knowledge.quintuplet", "r", encoding="UTF-8") as f_read:
        for line in f_read.readlines():
            head, relation, value, start, end = line[:-1].split("\t")

            relation = to_common_uri(relation)

            if not head in entities:
                entities[head] = tp.Entity(head, today, temporal_granularity) 

            entities[head].add_triple(tp.Triple(head, relation, value,\
                                    tp.Interval(processing_date_unknown_allowed(start),\
                                                processing_date_unknown_allowed(end))))

            relation_seen.add(relation)

    mini_entity = max(1,len(entities)*(int(percentage_entity)/100))

    global_relation = set() #find_global_appiration(relation_seen, entities)

    multivaluation_relations = find_multivaluation_temporal(entities)

    rules_r = find_rules_only_r(entities, multivaluation_relations, global_relation)
    # print(rules_r)
    rules_clean = tp.remove_useless_complex_rules(rules_r)
    # with open(f"{root_data}{type_entity}/Rules_R_{percentage_entity}_{seuil}.txt", "w", encoding="UTF-8") as f:
    #     for rule in rules_clean:
    #         f.write(str(rule)+"\n")
            
    with open(f"{root_data}{type_entity}/Rules_R_{percentage_entity}_{seuil}.tsv", "w", encoding="UTF-8") as f:
        for rule in rules_clean:
            f.write(rule.to_tsv()+"\n")

    rules_r_and_rxv = find_rules_r_and_rxv(entities, multivaluation_relations, global_relation)
    rules_clean = tp.remove_useless_complex_rules(rules_r_and_rxv)
    # with open(f"{root_data}{type_entity}/Rules_RxV_{percentage_entity}_{seuil}.txt", "w", encoding="UTF-8") as f:
    #     for rule in rules_clean:
    #         f.write(str(rule)+"\n")
    
    with open(f"{root_data}{type_entity}/Rules_RxV_{percentage_entity}_{seuil}.tsv", "w", encoding="UTF-8") as f:
        for rule in rules_clean:
            f.write(rule.to_tsv()+"\n")
