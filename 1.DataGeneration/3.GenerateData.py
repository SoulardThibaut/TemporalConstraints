import ijson 
import sys 
import numpy as np

# INPUT :
#   type_entity

temporal_granularity = "D"
root_data = "./../0.Data/"

def processing_date(date_raw) -> np.datetime64:
    return np.datetime64(date_raw, temporal_granularity)

def adding_one(date, heuristic=False) -> np.datetime64:
    if not heuristic:
        return date + np.timedelta64(1, temporal_granularity)
    
    else:
        # The heuristic is if a we are at the first of january of a year then it goes for a full year
        m = date.astype('datetime64[M]').astype(int)%12+1
        d = (date.astype('datetime64[D]') - date.astype('datetime64[M]')).astype(int) + 1 

        if (m == 1) * (d == 1):
            added = date+np.timedelta64(365, "D")
            # In the case we are in a leap year
            if added.astype("datetime64[Y]").astype(int) == date.astype("datetime64[Y]").astype(int):
                added+=np.timedelta64(1, "D")
            return added        
        else:
            return date + np.timedelta64(1, temporal_granularity)

if __name__ == '__main__':

    type_entity = sys.argv[1]
    
    # f_out_meta = open(f"./Results/{type_entity}/data.metadata", "w", encoding="UTF-8")
    with open(f"{root_data}{type_entity}/data.quintuplet", "w", encoding="UTF-8") as f_write:
        f_read = open(f"{root_data}{type_entity}/res_direct_{type_entity}.json", 'r', encoding="UTF-8")
        for record in ijson.items(f_read, "results.bindings.item"):
            f_write.write(record["h"]["value"] + "\t")
            r = record["r"]["value"]
            base = "http://www.wikidata.org/prop/direct/"
            if r[:len(base)] == base:
                r = "http://www.wikidata.org/prop/"+r[len(base):]
            f_write.write(r + "\t")
            date = processing_date(record["v"]["value"])
            f_write.write(str(date) + "\t")
            f_write.write(str(date) + "\t")
            f_write.write(str(adding_one(date)) + "\n")
            # f_out_meta.write("True\n")
        f_read.close()

        f_read = open(f"{root_data}{type_entity}/res_statement_interval_{type_entity}.json", 'r', encoding="UTF-8")
        for record in ijson.items(f_read, "results.bindings.item"):
            f_write.write(record["h"]["value"] + "\t")
            f_write.write(record["r"]["value"] + "\t")
            f_write.write(record["v"]["value"] + "\t")
            if "start" in record:
                f_write.write(str(processing_date(record["start"]["value"])) + "\t")
            else:
                f_write.write(str(None) + "\t")
            if "end" in record:
                f_write.write(str(processing_date(record["end"]["value"])) + "\n")
            else:
                f_write.write(str(None) + "\n")
                
        f_read.close()

        f_read = open(f"{root_data}{type_entity}/res_statement_point_{type_entity}.json", 'r', encoding="UTF-8")
        for record in ijson.items(f_read, "results.bindings.item"):
            f_write.write(record["h"]["value"] + "\t")
            f_write.write(record["r"]["value"] + "\t")
            f_write.write(record["v"]["value"] + "\t")
            point = processing_date(record["point"]["value"])
            f_write.write(str(point) + "\t")
            f_write.write(str(adding_one(point, True)) + "\n")
            
        f_read.close()

        f_read = open(f"{root_data}{type_entity}/res_statement_interval_{type_entity}_inverse.json", 'r', encoding="UTF-8")
        for record in ijson.items(f_read, "results.bindings.item"):
            f_write.write(record["v"]["value"] + "\t")
            f_write.write(record["r"]["value"]+"/Inverse" + "\t")
            f_write.write(record["h"]["value"] + "\t")
            if "start" in record:
                f_write.write(str(processing_date(record["start"]["value"])) + "\t")
            else:
                f_write.write(str(None) + "\t")
            if "end" in record:
                f_write.write(str(processing_date(record["end"]["value"])) + "\n")
            else:
                f_write.write(str(None) + "\n")

        f_read.close()

        f_read = open(f"{root_data}{type_entity}/res_statement_point_{type_entity}_inverse.json", 'r', encoding="UTF-8")
        for record in ijson.items(f_read, "results.bindings.item"):
            f_write.write(record["v"]["value"] + "\t")
            f_write.write(record["r"]["value"]+"/Inverse" + "\t")
            f_write.write(record["h"]["value"] + "\t")
            point = processing_date(record["point"]["value"])
            f_write.write(str(point) + "\t")
            f_write.write(str(adding_one(point, True)) + "\n")

        f_read.close()
