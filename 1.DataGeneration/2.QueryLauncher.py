import sys
from subprocess import DEVNULL, STDOUT, check_call

# INPUT : 
#   Type
#   Where is the SPARQL File 
#   HDT File 

size_memory = 120

if __name__ == '__main__':

    type_entity = sys.argv[1]
    hdtsparql_file = sys.argv[2]
    hdt_file = sys.argv[3]

    root_data = "./../0.Data/"

    cmd = f"java -Xmx{size_memory}G -jar {hdtsparql_file} "\
        + f"{hdt_file} {root_data}{type_entity}/query_direct_{type_entity}.query {root_data}{type_entity}/res_direct_{type_entity}.json"
    check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)

    cmd = f"java -Xmx{size_memory}G -jar {hdtsparql_file} "\
        + f"{hdt_file} {root_data}{type_entity}/query_statement_interval_{type_entity}.query {root_data}{type_entity}/res_statement_interval_{type_entity}.json"
    check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)

    cmd = f"java -Xmx{size_memory}G -jar {hdtsparql_file} "\
        + f"{hdt_file} {root_data}{type_entity}/query_statement_point_{type_entity}.query {root_data}{type_entity}/res_statement_point_{type_entity}.json"
    check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)

    cmd = f"java -Xmx{size_memory}G -jar {hdtsparql_file} "\
        + f"{hdt_file} {root_data}{type_entity}/query_statement_interval_{type_entity}_inverse.query {root_data}{type_entity}/res_statement_interval_{type_entity}_inverse.json"
    check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)

    cmd = f"java -Xmx{size_memory}G -jar {hdtsparql_file} "\
        + f"{hdt_file} {root_data}{type_entity}/query_statement_point_{type_entity}_inverse.query {root_data}{type_entity}/res_statement_point_{type_entity}_inverse.json"
    check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)