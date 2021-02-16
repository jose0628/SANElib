import Model
from jinja2 import Template
import sqlTemplates as sql
from sqlalchemy import text
import Utils
import pandas as pd

class Prediction():
    def __init__(self):
        self.utils = Utils()
        self.model = Model()
        self.eval = self.model.analysis.eval
        self.model_id = self.model.analysis.model_id



    def predict(self):  # table_eval is the test set
        """
        This function estimates the probabilities for the evaluation data
        """
        self.utils.materializedView(
            'Quantization metadata for evaluation table',
            self.model_id + '_qe',
            Template(sql.tmplt['_qe']).render(input=self)) ## generate SQL using Jinja 2 template
        self.utils.execute('Creating index _qe ',
            Template(sql.tmplt['_qe_ix']).render(input=self))
        self.utils.materializedView(
            'Class prediction for evaluation dataset',
            self.model_id + '_p',
            Template(sql.tmplt['_p']).render(input=self))  ## generate SQL using Jinja 2 template
        self.execute('Updating prediction with default prediction for null predictions',
            Template(sql.tmplt['_p_update']).render(input=self))


    def accuracy(self):
        """
        Computing the accuracy of the model and returning the results to the user
        """

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

        df = pd.DataFrame(results)
        df.columns = ['Total', 'TP', 'Accuracy']
        print(df)