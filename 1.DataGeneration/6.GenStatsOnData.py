import sys 
import numpy as np

sys.path.append("./../../..")
import TimePackage as tp

def to_common_uri(uri_relation):
    namespace_common = "http://www.wikidata.org/prop/P"
    namespace_direct = "http://www.wikidata.org/prop/direct/P"
    if uri_relation[:len(namespace_direct)] == namespace_direct:
        return namespace_common+uri_relation[len(namespace_direct):]
    else:
        return uri_relation
    
if __name__ == '__main__':
    
    type_entity = sys.argv[1]
    root_data = "./../0.Data/"

    with open(f"{root_data}{type_entity}/data.quintuplet", "r", encoding="UTF-8") as f_r:
        line = f_r.readline()
        h_seen = set()
        r_seen = set()
        cpt =0
        while (line!= ""):

            h, r, v, s, e = line[:-1].split("\t")
            h_seen.add(h)
            r_seen.add(to_common_uri(r))
            cpt+=1
            line = f_r.readline()

    print(len(h_seen), len(r_seen), cpt)