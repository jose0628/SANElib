# SANElib Prototype
# Standard-SQL Analytics for Numerical Estimation – SANE (vs. MADlib)
# (c) 2021        Michael Kaufmann, Gabriel Stechschulte, Anna Huber, HSLU

# coding: utf-8
import MDH
import constants as cns
import time
import matplotlib.pyplot as plt

# starting time
start = time.time()

db = {
        'drivername': 'mysql+mysqlconnector',
        'host': cns.DB_HOST,
        'port': cns.DB_PORT,
        'username': cns.DB_USER,
        'password': cns.DB_PW,
        'database': cns.DB_NAME,
        'query': {'charset': 'utf8'}
    }

classifier = MDH.SaneProbabilityEstimator(db, 'covtypall', 'Cover_Type', 'covtyptest2')

allNumFeat = [ "Elevation", "Aspect", "Slope", "Horizontal_Distance_To_Hydrology", "Vertical_Distance_To_Hydrology", \
                "Horizontal_Distance_To_Roadways", "Hillshade_9am", "Hillshade_Noon", "Hillshade_3pm", \
                "Horizontal_Distance_To_Fire_Points"]
allCatFeat = ["Wilderness_Area", "Soil_Type"]

#classifier.rank('table_train', allCatFeat, allNumFeat,  50)
print(f"Runtime of the program is { time.time() - start} seconds")

#TODO automate attribute selection based on threshold
numFeatures = [ "Elevation", "Horizontal_Distance_To_Roadways", "Horizontal_Distance_To_Fire_Points" ]
bins = 60
catFeatures = ["Wilderness_Area", "Soil_Type"]

#classifier.train_test_split(1, 0.8, 'covtyptest2_train', 'covtyptest2_eval')

# Training phase: _qt is trained on 0.8 of table ; _qmt based off of _qt ; _m based off of _qt
classifier.train(catFeatures, numFeatures, bins, 'covtyptest2_train')
print(f"Runtime of the program is {time.time() - start} seconds")

# Visualization methods
#classifier.visualize1D('Wilderness_Area', 'Covertype')
#classifier.visualize2D('Elevation', 'Wilderness_Area', 'CoverType')

# Predicting on test set: _qe tested on 0.2 of table ; _qe_ix based off of _qe ; _p ; _p_update
classifier.predict('covtyptest2_eval')
print(f"Runtime of the program is {time.time() - start} seconds")

classifier.accuracy()


# end time
end = time.time()

# total time taken
print(f"Runtime of the program is {time.time() - start} seconds")

# print('Training accuracy = ', classifier.trainingAccuracy())
