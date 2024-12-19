The source code for the ESWC'25 submission : Explainable Temporal Fact Validation Through Constraints Discovery in Knowledge Graphs.

# Data 

The data is stored in the folder **0.Data** and is split into multiple zip files, to unzip you have to run the following commands in the **0.Data** folder : 
* `cat Data_chunka* > Data.zip`
* `unzip Data.zip` 

The data is then organised following per class with the following hierarchy : 
  * data.quintuplet : the full positive data non split 
  * train_cst_knowledge.quintuplet : the training positive data to discover the Contraints and used a the description of entities
  * train_ML.quintuplet : the training postive/negative data for the ML algorithm
  * train_ML.gt : the ground truth for the train_ML data
  * valid.quintuplet 
  * valid.gt 
  * test.quintuplet
  * test.gt

The data can be generated through the use of a HDT file and 

# Runable experiment
To run the experiment described in the paper, the following packages are required : 
* Pandas
* Sklearn
* Numpy

The experiment is launched by the following script, where Q6256 can be replaced by another class (i.e. **Q82955**, **Q215380**) :

`python3 0.3.RunStepTuning.py -type Q6256`

But sub experiment can be launched through the programs described in the folders **1.**, **2.** and **3.**. Examples of sub experiment are presented in the 0.3.RunStepTuning.py file.
