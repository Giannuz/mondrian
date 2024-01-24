# Mondrian

Implementation of the mondrian algorithm in python with support to categorical attributes

Requirements

- [Faker](https://pypi.org/project/Faker/)

- [numpy](https://pypi.org/project/numpy/)

- [pandas](https://pypi.org/project/pandas/)

## Setup

```shell
git clone https://github.com/Giannuz/mondrian.git
cd mondrian
pip install -r requirements.txt
python mondrian.py
```

## Usage

Arguments:

- `--dataset` provide the path to the csv file that you want anonymize

- `-k` anonimity level that you want to achieve

- `--sensitive-data` list of columns in your dataset that contains sensitive data

- `--outputfile` (optional) name of the file that will be created (default: Anonymized_dataset.csv)

- `--categorical` (optional) list of columns in your dataset that contains categorical data

- `--hierarchy` (optional) if you provide categorical columns you need to provide a mapping .json file containing the hierarchy of the attributes for generalization (the order must be the same of the categorical list)

- `--explicit-identifiers` if your csv file still contains EI columns you can specify a list of explicit identifiers, the columns will be removed from the csv.

example:

```shell
python mondrian.py -o test_id.csv -d dataset.csv -k 2 -SD Disease -EI Name Surname -c City -hv mapping_city.json
```

## GenerateCSV.py

This script generates a dataset which could be used within an insurance company, returns a csv file containing the following columns:

| Name | Surname | Sex | Age | City | Income | Dependants | Insurance Coverage | Legal Situation | Disease |
| ---- | ------- | --- | --- | ---- | ------ | ---------- | ------------------ | --------------- | ------- |
