import sys
import pandas as pd

def pred(x):
    respected = sum([i == 0 for i in x])
    violated = sum([i == 1 for i in x])
    if (respected+violated) != 0:
        return respected/(respected+violated)
    else:
        return None

if __name__ == '__main__':
    
    type_ent = sys.argv[1]
    path = f"./../0.Data/{type_ent}/"
    str_file = sys.argv[2]
    str_gt = sys.argv[3]
    seuil = sys.argv[4]

    constraint_application = pd.read_csv(f"{path}{str_file}", sep=",", header=None, index_col=0)
    ratio = constraint_application.apply(lambda x: pred(x))
    final_prediction = pd.DataFrame(ratio[ratio!=None].apply(lambda x: x>seuil), columns=["P"])

    gt = pd.read_csv(f"{path}{str_gt}", names=["GT"], header=None)

    merge = final_prediction.merge(gt, left_index=True, right_index=True )
    print(sum(merge.apply(lambda x: x["GT"] == x["P"]).values))