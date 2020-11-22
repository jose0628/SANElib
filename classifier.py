import sqlTemplates as sql
from jinja2 import Template

class SaneProbabilityEstimator:

    def __init__(self, conn, table_train, target, model_id):
        '''
        This method takes the most commonly used parameters from the user during initialization of the classifier
        - conn = database connection (format: variable)
        - target = target variable (what you are wanting to predict) (format: str)
        - table_name = name of the table that is in the database (format: str)
        '''
        self.connection = conn
        self.table_train = table_train
        self.target = target # TODO default value: last column
        self.model_id = model_id # TODO default value: table name

# TODO use SQL alchemy or similar framework that works for all SQL DB types
    def execute(self, desc, query):
        cursor = self.connection.cursor()
        print(desc + '\nQuery: ' + query)
        cursor.execute(query)
        cursor.close()
        print('OK: ' + desc)
        print()

    def executeQuery(self, desc, query):
        cursor = self.connection.cursor()
        print('Query: ' + query)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        print('OK: ' + desc)
        print()
        return results

    def materializedView(self, desc, tablename, query):
        self.execute('Dropping table ' + tablename, '''
            drop table if exists {}'''
                .format(tablename))
        self.execute(desc, '''
            create table {} as '''
                .format(tablename) + query)

   # TODO develop an algorithm to optimize the hyper parameters
    #  for n buckets: Idea Nr. 1: Linear, straight forward. first sort the features according to 1D prediction accuracy;
    # Start with the first in the list;
    # for each feature, increase n-buckets until convergence;
    # Add next best feature, and so on, until convergence
    # Idea Nr. 2: Evolutionary. again sort by 1D accuracy. Start with the first in the list;
    # Always add the feature that brings the highest performance gain
    # Always increase the bucket number of the feature that brings the highest performance gain.
    # Until convergence => find method that scales well for large data set with acceptable performance
    # Idea 3: linear in feature list, but evolutionary in n-buckets
    # TODO idea: optimize feature list using "random restaurant" simliar to random forest, but using decision "tables" instead of "trees" <-- advanced stuff
    def hyperparameters(self, numFeatures, bins, catFeatures):
        '''
        This function sets the hyperparameters
        - features to estimate the probability of the target
        - features = right now it is just a string, but I think we may want to explore
                     having the user put the feature(s) into a numpy array. Similiar to
                     how the scikit-learn ML algorithms want them. (format:str)
        - Bins/buckets = # of bins
        '''
        # TODO array of features
        self.numFeatures = numFeatures # TODO default: all columns
        # TODO array of bins
        self.bins = bins; #TODO default:
        self.catFeatures = catFeatures

    def trainingAccuracy(self):
        '''
               This function evaluates the hyperparameters quickly on the training set.
               possible parameters: size of internal modeling / validation split to make it faster
        '''
        self.train('''(select * from {} where rand() < 0.8) as t'''
                     .format(self.table_train))
        self.predict('''(select * from {} where rand() >= 0.2) as t'''
                .format(self.table_train))
        return self.accuracy()

    def train(self):
        self.train(self.table_train)

    def train(self, table_train):
        '''
        This function is the training phase:
        - the input data table is quantized (equal size) and indexed.
        - This quantized index then represents an in-database model for probability estimation
        '''
        # make sure only 1 query is executed per call. So it works in PyCharm.
        # TODO Generate queries using n features x1, x2, ..., xn; differentiate between numerical and categorical
        self.materializedView(
            'Quantization of training table',
            self.model_id + '_qt',
            Template(sql.tmplt['_qt']).render(input=self))
        self.materializedView(
            'Quantization metadata for training table',
            self.model_id + '_qmt',
            Template(sql.tmplt['_qmt']).render(input=self))
        self.materializedView(
            'Computing predictive model as contingency table',
            self.model_id + '_m',
            Template(sql.tmplt['_m']).render(input=self))

    def predict(self, table_eval):
        '''
        This function estimates the probabilities for the evaluation data
        '''
        self.table_eval = table_eval;
        self.materializedView(
            'Quantization metadata for evaluation table',
            self.model_id + '_qe',
            Template(sql.tmplt['_qe']).render(input=self)) ## generate SQL using Jinja 2 template
        self.execute('Creating index _qe ',
            Template(sql.tmplt['_qe_ix']).render(input=self))
        self.materializedView(
            'Class prediction for evaluation dataset',
            self.model_id + '_p',
            Template(sql.tmplt['_p']).render(input=self))  ## generate SQL using Jinja 2 template
        self.execute('Updating prediction with default prediction for null predictions',
            Template(sql.tmplt['_p_update']).render(input=self))

    def accuracy(self):
        '''
        Computing the accuracy of the model and returning the results to the user
        '''

        results = self.executeQuery('Computing evaluation accuracy', '''
            select
            count(distinct id) as  cases,
            sum(case when e.y = p.y_ then 1 else 0 end) as tp,
            sum(case when e.y = p.y_ then 1 else 0 end) /  count(distinct id)  as accuracy
            from {}_qe e 
            left outer join {}_p p using(id);
                '''.format(
                    self.model_id,
                    self.model_id))
        accuracy = [result[2] for result in results]
        return accuracy
