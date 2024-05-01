import sys
from subprocess import DEVNULL, STDOUT, check_call
import os 

# INPUT : 
#   Relation 
#   Type 

if __name__ == '__main__':

    # relation Type
    relation = sys.argv[1]
    type_entity = sys.argv[2]

    root_data = "./../0.Data/"

    # Generate the folder
    cmd = f"mkdir {root_data}{type_entity}"
    check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)

    query_v_time = """
    SELECT DISTINCT ?h ?r ?v
    WHERE {
        FILTER (datatype(?v) = <http://www.w3.org/2001/XMLSchema#dateTime>)
        ?h <http://www.wikidata.org/prop/direct/"""+relation+"> <http://www.wikidata.org/entity/"+type_entity+"""> .
        ?h ?r ?v.
    }
    """

    with open(f"{root_data}{type_entity}/query_direct_{type_entity}.query", "w", encoding="UTF-8") as f_write:
        f_write.write(query_v_time)

    query_statement_time_interval = """
    SELECT DISTINCT ?h ?r ?v ?start ?end
    WHERE {
        FILTER(strstarts(str(?statement), "http://www.wikidata.org/entity/statement/"))
        FILTER(strstarts(str(?rs), "http://www.wikidata.org/prop/statement/P"))
        FILTER((strlen(str(?start))>0) || (strlen(str(?end))>0))
        ?h <http://www.wikidata.org/prop/direct/"""+relation+"> <http://www.wikidata.org/entity/"+type_entity+"""> .
        ?h ?r ?statement.
        ?statement ?rs ?v.
        OPTIONAL{
            ?statement <http://www.wikidata.org/prop/qualifier/P580> ?start.
            FILTER(datatype(?start) = <http://www.w3.org/2001/XMLSchema#dateTime>)
        }
        OPTIONAL{
            ?statement <http://www.wikidata.org/prop/qualifier/P582> ?end.
            FILTER(datatype(?end) = <http://www.w3.org/2001/XMLSchema#dateTime>)
        }
        FILTER NOT EXISTS {
            ?statement <http://www.wikidata.org/prop/qualifier/P585> ?point.
       }
    }
    """
    
    with open(f"{root_data}{type_entity}/query_statement_interval_{type_entity}.query", "w", encoding="UTF-8") as f_write:
        f_write.write(query_statement_time_interval)

    query_statement_time_point = """
    SELECT DISTINCT ?h ?r ?v ?point
    WHERE {
        ?h <http://www.wikidata.org/prop/direct/"""+relation+"> <http://www.wikidata.org/entity/"+type_entity+"""> .
        
        FILTER(strstarts(str(?r), "http://www.wikidata.org/prop/P"))
        FILTER(strstarts(str(?statement), "http://www.wikidata.org/entity/statement/"))
        ?h ?r ?statement.

        FILTER(strstarts(str(?rs), "http://www.wikidata.org/prop/statement/P"))
        ?statement ?rs ?v.

        FILTER(datatype(?point) = <http://www.w3.org/2001/XMLSchema#dateTime>)
        ?statement <http://www.wikidata.org/prop/qualifier/P585> ?point
    }
    """
    with open(f"{root_data}{type_entity}/query_statement_point_{type_entity}.query", "w", encoding="UTF-8") as f_write:
        f_write.write(query_statement_time_point)

    
    query_statement_time_interval_inverse = """
    SELECT DISTINCT ?h ?r ?v ?start ?end
    WHERE {
        ?v <http://www.wikidata.org/prop/direct/"""+relation+"> <http://www.wikidata.org/entity/"+type_entity+"""> .
        
        
        FILTER(strstarts(str(?statement), "http://www.wikidata.org/entity/statement/"))
        FILTER(strstarts(str(?rs), "http://www.wikidata.org/prop/statement/P"))
        FILTER((strlen(str(?start))>0) || (strlen(str(?end))>0))
        ?statement ?rs ?v.
        ?h ?r ?statement.
        OPTIONAL{
            ?statement <http://www.wikidata.org/prop/qualifier/P580> ?start.
            FILTER(datatype(?start) = <http://www.w3.org/2001/XMLSchema#dateTime>)
        }
        OPTIONAL{
            ?statement <http://www.wikidata.org/prop/qualifier/P582> ?end.
            FILTER(datatype(?end) = <http://www.w3.org/2001/XMLSchema#dateTime>)
        }
        FILTER NOT EXISTS {
            ?statement <http://www.wikidata.org/prop/qualifier/P585> ?point.
       }
    }
    """
    
    with open(f"{root_data}{type_entity}/query_statement_interval_{type_entity}_inverse.query", "w", encoding="UTF-8") as f_write:
        f_write.write(query_statement_time_interval_inverse)

    query_statement_time_point_inverse = """
    SELECT DISTINCT ?h ?r ?v ?point
    WHERE {        
        ?v <http://www.wikidata.org/prop/direct/"""+relation+"> <http://www.wikidata.org/entity/"+type_entity+"""> .
        
        FILTER(strstarts(str(?rs), "http://www.wikidata.org/prop/statement/P"))
        ?statement ?rs ?v.

        FILTER(strstarts(str(?r), "http://www.wikidata.org/prop/P"))
        FILTER(strstarts(str(?statement), "http://www.wikidata.org/entity/statement/"))
        ?h ?r ?statement.

        FILTER(datatype(?point) = <http://www.w3.org/2001/XMLSchema#dateTime>)
        ?statement <http://www.wikidata.org/prop/qualifier/P585> ?point
    }
    """
    with open(f"{root_data}{type_entity}/query_statement_point_{type_entity}_inverse.query", "w", encoding="UTF-8") as f_write:
        f_write.write(query_statement_time_point_inverse)
