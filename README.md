The source code for the ESWC'25 submission : Explainable Temporal Fact Validation Through Constraints Discovery in Knowledge Graphs.

# Data 

The data is stored in the folder **0.Data** and is split into multiple zip files, to unzip you have to run the following commands in the **0.Data** folder : 
* `zip -s0 Data.zip --out DataGathered.zip`
* `unzip DataGathered.zip` 

The data is then organised following per class with the following hierarchy : 
  * data.quintuplet 
  * train_cst_knowledge.quintuplet
  * train_ML.quintuplet
  * train_ML.gt
  * valid.quintuplet
  * valid.gt
  * test.quintuplet
  * test.gt

# Runable experiment

`python3 0.2.RunOnlyTests.py -type Q6256`
