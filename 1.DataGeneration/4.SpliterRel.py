import sys 
import numpy as np
import random 

sys.path.append("./..")
import TimePackage as tp

temporal_granularity = "D"
today = np.datetime64("2023-12-31", temporal_granularity)
root_data = "./../0.Data/"

def processing_date_unknown_allowed(date_raw) -> np.datetime64:
    if date_raw == "None":
        return None
    else:
        return np.datetime64(date_raw, temporal_granularity)

def to_common_uri(uri_relation):
    namespace_common = "http://www.wikidata.org/prop/P"
    namespace_direct = "http://www.wikidata.org/prop/direct/P"
    if uri_relation[:len(namespace_direct)] == namespace_direct:
        return namespace_common+uri_relation[len(namespace_direct):]
    else:
        return uri_relation

type_ent = sys.argv[1]
path = f"{root_data}{type_ent}/"

# Open the final files
train_cst_knw = open(path+"train_cst_knowledge.quintuplet", "w", encoding="UTF-8")

train_ml = open(path+"train_ML.quintuplet", "w", encoding="UTF-8")
train_ml_gt = open(path+"train_ML.gt", "w", encoding="UTF-8")

valid = open(path+"valid.quintuplet", "w", encoding="UTF-8")
valid_gt = open(path+"valid.gt", "w", encoding="UTF-8")

test = open(path+"test.quintuplet", "w", encoding="UTF-8")
test_gt = open(path+"test.gt", "w", encoding="UTF-8")


random.seed(0)

entities_all = {}
triples_train_ml = []
triples_valid = []
triples_test = []

with open(path+"data.quintuplet", "r", encoding="UTF-8") as f:

    line = f.readline()
    previous_in_valid_or_test = False

    while line != "":

        head, relation, value, start, end = line[:-1].split("\t")

        if (( processing_date_unknown_allowed(start) == None) or\
            (processing_date_unknown_allowed(start) < today)) and\
            (( processing_date_unknown_allowed(end) == None) or\
              (processing_date_unknown_allowed(end) <= today)):
            
            relation = to_common_uri(relation)

            triple = tp.Triple(head, relation, value,\
                                    tp.Interval(processing_date_unknown_allowed(start),\
                                                processing_date_unknown_allowed(end)))

            if not head in entities_all:
                entities_all[head] = tp.Entity(head, today, temporal_granularity)

            entities_all[head].add_triple(triple)

            # if (head in h_to_keep) and (relation in r_to_keep):
            value_rand = random.random()
            if value_rand < 0.8:
                triples_train_ml.append(triple)
                train_cst_knw.write(f"{head}\t{relation}\t{value}\t{start}\t{end}\n")

            elif value_rand < 0.9:
                triples_valid.append(triple)

            else:
                triples_test.append(triple)

        line = f.readline()

train_cst_knw.close()

slack = 0.1

for t in triples_train_ml:
    #Retrieve data of original triple
    h = t.head
    r = t.relation
    v = t.value
    s = t.date.get_start()
    e = t.date.get_end()

    if entities_all[h].life_span.get_start() != None:

        #Write the True data
        train_ml.write(f"{h}\t{r}\t{v}\t{s}\t{e}\n")
        train_ml_gt.write("True\n")
            
        # Generate the False data
        lifespan = entities_all[h].life_span 
        nb_days = tp.Interval.day_in_the_interval(lifespan)
        
        allowed_start = int((lifespan.get_start()-np.datetime64("1970-01-01", "D")-np.timedelta64(int(nb_days*slack))).astype("D"))
        
        max_end = int((today-np.datetime64("1970-01-01", "D")).astype("D"))
        allowed_end = min(max_end,int((lifespan.get_end()-np.datetime64("1970-01-01", "D")+np.timedelta64(int(nb_days*slack))).astype("D")))

        s_int = random.randint(allowed_start,allowed_end-1)
        s = np.datetime64(s_int, "D")
        e = np.datetime64(random.randint(s_int+1, allowed_end), "D")
        train_ml.write(f"{h}\t{r}\t{v}\t{s}\t{e}\n")
        train_ml_gt.write("False\n")

# Generate False values
for t in triples_valid:
    #Retrieve data of original triple
    h = t.head
    r = t.relation
    v = t.value
    s = t.date.get_start()
    e = t.date.get_end()

    if entities_all[h].life_span.get_start() != None:

        #Write the True data
        valid.write(f"{h}\t{r}\t{v}\t{s}\t{e}\n")
        valid_gt.write("True\n")
            
        # Generate the False data
        lifespan = entities_all[h].life_span 
        nb_days = tp.Interval.day_in_the_interval(lifespan)
        
        allowed_start = int((lifespan.get_start()-np.datetime64("1970-01-01", "D")-np.timedelta64(int(nb_days*slack))).astype("D"))
        
        max_end = int((today-np.datetime64("1970-01-01", "D")).astype("D"))
        allowed_end = min(max_end,int((lifespan.get_end()-np.datetime64("1970-01-01", "D")+np.timedelta64(int(nb_days*slack))).astype("D")))

        s_int = random.randint(allowed_start,allowed_end-1)
        s = np.datetime64(s_int, "D")
        e = np.datetime64(random.randint(s_int+1, allowed_end), "D")
        valid.write(f"{h}\t{r}\t{v}\t{s}\t{e}\n")
        valid_gt.write("False\n")
    
valid.close()
valid_gt.close()

for t in triples_test:
    #Retrieve data of original triple
    h = t.head
    r = t.relation
    v = t.value
    s = t.date.get_start()
    e = t.date.get_end()

    if entities_all[h].life_span.get_start() != None:

        #Write the True data
        test.write(f"{h}\t{r}\t{v}\t{s}\t{e}\n")
        test_gt.write("True\n")
            
        # Generate the False data
        lifespan = entities_all[h].life_span 
        nb_days = tp.Interval.day_in_the_interval(lifespan)
        
        allowed_start = int((lifespan.get_start()-np.datetime64("1970-01-01", "D")-np.timedelta64(int(nb_days*slack))).astype("D"))
        
        max_end = int((today-np.datetime64("1970-01-01", "D")).astype("D"))
        allowed_end = min(max_end,int((lifespan.get_end()-np.datetime64("1970-01-01", "D")+np.timedelta64(int(nb_days*slack))).astype("D")))

        s_int = random.randint(allowed_start,allowed_end-1)
        s = np.datetime64(s_int, "D")
        e = np.datetime64(random.randint(s_int+1, allowed_end), "D")
        test.write(f"{h}\t{r}\t{v}\t{s}\t{e}\n")
        test_gt.write("False\n")

test.close()
test_gt.close()
