import sys
from sklearn import tree
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from sklearn.datasets import make_circles, make_classification, make_moons
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.inspection import DecisionBoundaryDisplay
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

if __name__ == '__main__':
    
    type_ent = sys.argv[1]
    path = f"./../0.Data/{type_ent}/"
    data = pd.read_csv(path+sys.argv[2], index_col=0, header=None)
    gt = pd.read_csv(path+sys.argv[3], names=["GT"], header=None)

    full = data.merge(left_index=True, right_index=True, right=gt)
    size = len(data.columns)
    to_keep = data.apply(lambda x: sum([i in [2, 3, 4] for i in x]) !=  size, axis=1).values
    X_train = full[to_keep].drop("GT", axis=1)
    Y_train = full[to_keep].get("GT")


    data_to_test = pd.read_csv(path+sys.argv[4], index_col=0, header=None)
    gt_test = pd.read_csv(path+sys.argv[5], names=["GT"], header=None)

    full_test = data_to_test.merge(left_index=True, right_index=True, right=gt_test)
    # X_test = full_test.drop("GT", axis=1)
    to_keep = full_test.apply(lambda x: sum([i in [2, 3, 4] for i in x]) !=  size, axis=1).values
    X_test = full_test[to_keep].drop("GT", axis=1)
    Y_test = full_test[to_keep].get("GT")

    print(len(X_train), len(X_train))
    print(X_train.columns)
    print(X_test.columns)

    names = [
        "Nearest Neighbors",
        "Linear SVM",
        "RBF SVM",
        "Gaussian Process",
        "Decision Tree",
        "Random Forest",
        "Neural Net",
        "AdaBoost",
        "Naive Bayes",
        "QDA",
    ]

    classifiers = [
        KNeighborsClassifier(3),
        SVC(kernel="linear", C=0.025, random_state=42),
        SVC(gamma=2, C=1, random_state=42),
        GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
        DecisionTreeClassifier(max_depth=5, random_state=42),
        RandomForestClassifier(
            max_depth=5, n_estimators=10, max_features=1, random_state=42
        ),
        MLPClassifier(alpha=1, max_iter=1000, random_state=42),
        AdaBoostClassifier(random_state=42),
        GaussianNB(),
        QuadraticDiscriminantAnalysis(),
    ]
    # iterate over classifiers
    with open(f"{path}AllModels_{sys.argv[4]}.csv", "w", encoding="UTF-8") as f_w:
        for name, clf in zip(names, classifiers):

            # clf = make_pipeline(StandardScaler(), clf)
            clf.fit(X_train, Y_train)
            score = clf.score(X_test, Y_test)
            f_w.write(f"{name},{score}\n")