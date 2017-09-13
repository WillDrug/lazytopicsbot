import random
import os
import yaml
import json

# print generated insult for the 'user'
def get_insult(insults_pref, insults_postfs='.'):
    insults_config = yaml.load(open(os.path.dirname(__file__) + '\insults.yml'))
    #insults_pref = 'Thou art a'
    insults_col1 = random.choice(insults_config['column1'])
    insults_col2 = random.choice(insults_config['column2'])
    insults_col3 = random.choice(insults_config['column3'])
    return insults_pref + ' ' + insults_col1 + ' ' + insults_col2 + ' ' + insults_col3 + insults_postfs
