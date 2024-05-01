import sys 
import numpy as np

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

if __name__ == '__main__':
    
    type_entity = sys.argv[1]
    root_data = "./../0.Data/"

    with open(f"{root_data}{type_entity}/data.quintuplet", "r", encoding="UTF-8") as f_r:
        line = f_r.readline()
        h_seen = {}
        entities = {}
        
        while (line!= ""):

            h, r, v, s, e = line[:-1].split("\t")
            
            if not h in h_seen:
                h_seen[h] = {}
                entities[h] = tp.Entity(h, today, temporal_granularity)
                
            entities[h].add_triple(tp.Triple(h, to_common_uri(r), v, \
                                    tp.Interval(processing_date_unknown_allowed(s),\
                                                processing_date_unknown_allowed(e))))
            
            if not r in h_seen[h]:
                h_seen[h][to_common_uri(r)] = {}

            if not v in h_seen[h][to_common_uri(r)]:
                h_seen[h][to_common_uri(r)][v] = set()  
        
            h_seen[h][to_common_uri(r)][v].add(("\t".join([h,r,v,s,e]), (s,e)))
            
            line = f_r.readline()

    with open(f"{root_data}{type_entity}/data_clean.quintuplet", "w", encoding="UTF-8") as f_w:
        for h in h_seen:
            for r in h_seen[h]:
                for v in h_seen[h][r]:
                    seen_none_start = False
                    seen_none_end = False
                    
                    if entities[h].life_span.get_start() != None:  
                        for (to_write,(s,e)) in h_seen[h][r][v]:
                            if (s == "None") :
                                if (s == "None") and (not seen_none_start):
                                    f_w.write(to_write+"\n")
                                    seen_none_start = True
                                    
                            elif (e == "None"):
                                if (e == "None") and (not seen_none_end):
                                    f_w.write(to_write+"\n")
                                    seen_none_end = True
                                    
                            else:
                                f_w.write(to_write+"\n")
                                