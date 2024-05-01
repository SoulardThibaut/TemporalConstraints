import sys
import TimePackage as tp
import pandas as pd

def to_common_uri(uri_relation):
    namespace_common = "http://www.wikidata.org/prop/P"
    namespace_direct = "http://www.wikidata.org/prop/direct/P"
    if uri_relation[:len(namespace_direct)] == namespace_direct:
        return namespace_common+uri_relation[len(namespace_direct):]
    else:
        return uri_relation

if __name__ == '__main__':
    
    type_ent = sys.argv[1]
    path = f"./../0.Data/{type_ent}/"

    data_to_test = pd.read_csv(path+sys.argv[2], index_col=0)
    gt_test = pd.read_csv(path+sys.argv[3], names=["GT"])
    size = len(data_to_test.columns)
    full_test = data_to_test.merge(left_index=True, right_index=True, right=gt_test)
    # X_test = full_test.drop("GT", axis=1)
    unknown_bool = full_test.apply(lambda x: sum([i in [2, 3, 4] for i in x]) ==  size, axis=1).values
    unknown = full_test[unknown_bool]
    print(len(unknown)/len(data_to_test)*100)
    
    fully_unknown = sum(unknown.apply(lambda x: sum([i == 2 for i in x]) == size, axis=1).values)
    print(fully_unknown/len(data_to_test)*100)

    fully_unknown = sum(unknown.apply(lambda x: sum([i in [3,4] for i in x]) != 0, axis=1).values)
    print(fully_unknown/len(data_to_test)*100)

    constraint = sys.argv[4]
    rules = {}
    rule_indexed = {}
    with open(f"{path}{constraint}", "r", encoding="UTF-8") as f_r:

        line = f_r.readline()

        while line != '':
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

            line = f_r.readline()


    total = 0
    can_work_on = 0
    with open(f"{path}data.quintuplet", "r", encoding="UTF-8") as f_r:
        with open(f"{path}data.metadata", "r", encoding="UTF-8") as f_r_meta:

            line = f_r.readline()
            line_meta = f_r_meta.readline()

            while line != '':
                if line_meta != "True\n":
                    total+=1

                    h, r, v, s, e = line.split("\t")

                    r = to_common_uri(r)

                    if r in rule_indexed:
                        can_work_on+=1
                
                line = f_r.readline()
                line_meta = f_r_meta.readline()

    print(can_work_on/total*100)

