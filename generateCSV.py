import pandas as pd
import numpy as np
import random
import json
from faker import Faker

fake = Faker('it_IT')

# We used the list of cities from the mapping file since we already written it.
json_data = json.load(open('mapping.json'))
def get_city_number_dict(json_data, parent_key=''):
    """Given a json files it gets all the cities"""
    city_number_dict = {}
    if isinstance(json_data, dict):
        for sub_key, sub_value in json_data.items():
            city_number_dict.update(get_city_number_dict(sub_value, f"{parent_key}.{sub_key}" if parent_key else sub_key))
    else:
        city_name = parent_key.split('.')[-1] if parent_key else parent_key
        city_number_dict[city_name] = json_data
    return city_number_dict

def generate_dataset(n_desired_rows=200):
    """Generates a fake dataset with some elements which may be coherent to the ones needed by an insurance company"""
    cities = [elem for elem in get_city_number_dict(json_data)]
    # List of some diseases
    diseases = np.array(["Angine", "Appendicite", "Chlamydia", "Cataracte", "Dengue", "Eczéma", "Grippe", "Hépatite B", "Hépatite C", "Rhino-pharyngite", "Otite", "Rougeole", "Scarlatine", "Urticaire", "Varicelle", "Zona"])
    # List of possible legal situations of the client
    legal_situations = ['Investigated','Convicted','Prescribed','On Parole','On Probation','Acquitted','Pardoned','No Records']

    
    average_income = 34000
    sigma = 0.8
    # Generate data from a distribution -> we used average RAL of an italian citizen.
    income = np.random.lognormal(mean=np.log(average_income), sigma=sigma,size=n_desired_rows)
    # Number of people which depend on the insurance owner
    dependant = random.choices([i for i in range(6)], weights=[30,15,35,14,5,1])
    coverage = random.choices([1,3,5,10])
    rows = []
    dataframe = pd.DataFrame(columns=['Name','Surname','Age','City','Income','Dependants','Insurance Coverage','Legal Situation','Disease'])
    for i in range(n_desired_rows):
        row = {'Name': fake.first_name(),'Surname':fake.last_name(),'Age':random.randint(18,80), 'City':random.choice(cities),\
               'Income':int(income[i]),'Dependants':dependant[0],'Insurance Coverage':coverage[0]\
               ,'Legal Situation':random.choice(legal_situations),'Disease':random.choice(diseases)}

        while row in rows: 
            # If a row already exists it must be discarded (it also contains explicit identifiers)
            print('Row already exists! Generating a new one')
            row = {'Name': fake.first_name(),'Surname':fake.last_name(),'Age':random.randint(18,80), 'City':random.choice(cities),\
               'Income':int(income[i]),'Dependants':dependant[0],'Insurance Coverage':coverage[0]\
               ,'Legal Situation':random.choice(legal_situations),'Disease':random.choice(diseases)}
        rows.append(row)
        dataframe = dataframe._append(row,ignore_index=True)
    return dataframe

data = generate_dataset()
data.to_csv('dataset.csv',index=False)

