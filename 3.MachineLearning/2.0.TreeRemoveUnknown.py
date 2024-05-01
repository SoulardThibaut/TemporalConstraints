import sys
from sklearn import tree
import pandas as pd

if __name__ == '__main__':
    
    type_ent = sys.argv[1]
    path = f"./../0.Data/{type_ent}/"
    data = pd.read_csv(path+sys.argv[2], index_col=0, header=None)
    gt = pd.read_csv(path+sys.argv[3], names=["GT"], header=None)

    full = data.merge(left_index=True, right_index=True, right=gt)
    # X = full.drop("GT", axis=1)
    size = len(data.columns)
    to_keep = data.apply(lambda x: sum([i in [2, 3, 4] for i in x]) !=  size, axis=1).values
    X_known = full[to_keep].drop("GT", axis=1)
    Y = full[to_keep].get("GT")

    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(X_known/4, Y)


    data_to_test = pd.read_csv(path+sys.argv[4], index_col=0, header=None)
    gt_test = pd.read_csv(path+sys.argv[5], names=["GT"], header=None)

    full_test = data_to_test.merge(left_index=True, right_index=True, right=gt_test)
    # X_test = full_test.drop("GT", axis=1)
    to_keep = full_test.apply(lambda x: sum([i in [2, 3, 4] for i in x]) !=  size, axis=1).values
    X_test_known = full_test[to_keep].drop("GT", axis=1)
    Y_test = full_test[to_keep].get("GT")
    
    res = clf.predict(X_test_known/4)

    with open(f"{path}Weights_{sys.argv[2]}_{sys.argv[4]}.txt", "w") as f:

        f.write(f"{sum([res[i] ==  Y_test.iloc[i] for i in range(len(res))])} / {len(res)}\n")
        weights = clf.feature_importances_
        f.write(",".join([str(i) for i in weights]))
    