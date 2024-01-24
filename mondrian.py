from turtle import right
import numpy as np
import pandas as pd
import argparse
import json


def remove_explicit(dataset, identifiers):
    """Removes the explicit identifiers from the dataset"""
    dataset = dataset.drop(identifiers, axis=1)
    return dataset


def convert_categorical(data, categorical_columns, categorical_hierarchy):
    """Converts a categorical attribute's value into numbers"""

    def categorical_to_numeric(json_data, parent_key=''):
        categorical_numeric_dict = {}
        if isinstance(json_data, dict):
            for sub_key, sub_value in json_data.items():
                categorical_numeric_dict.update(categorical_to_numeric(
                    sub_value, f"{parent_key}.{sub_key}" if parent_key else sub_key))
        else:
            city_name = parent_key.split('.')[-1] if parent_key else parent_key
            categorical_numeric_dict[city_name] = json_data
        return categorical_numeric_dict
    #  for each categorical attribute it transforms it into a numeric one
    for index in range(len(categorical_columns)):
        categorical_column = categorical_columns[index]
        hierarchy = categorical_hierarchy[index]

        hierarchy_file = open(hierarchy)
        json_data = json.load(hierarchy_file)

        attribute_to_number = categorical_to_numeric(
            json_data, parent_key='')

        data[categorical_column +
             "tmp"] = data[categorical_column].map(attribute_to_number)

        data = data.drop(categorical_column, axis=1)
        data.rename(columns={categorical_column +
                    'tmp': categorical_column}, inplace=True)
    return data


def splitter(dataframe, axe, k):
    """Splits the datafram along a certain x to respect k value"""
    #print(dataframe[axe].median())
    left_partition = dataframe[(dataframe[axe] <= dataframe[axe].median())]
    right_partition = dataframe[(dataframe[axe] > dataframe[axe].median())]
    #print(left_partition,'\n\n',right_partition)
    if len(left_partition) >= k and len(right_partition) >= k:
        return left_partition, right_partition
    else:
        left_partition = dataframe.iloc[:k]
        right_partition = dataframe.iloc[k:]
        #print(left_partition,'\n\n',right_partition)

        return left_partition, right_partition


def numerical_to_categorical(dataset, hierarchy_columns, categorical_columns):
    """Convert numerical attributes back to categorical values (anonymized)."""
    for index in range(len(categorical_columns)):
        categorical_column = categorical_columns[index]
        hierarchy_file = json.load(open(hierarchy_columns[index]))

        unique_vals = dataset[categorical_column].unique()
        # Given an interval "[n1,n2]" it gets n1 and n2 and find the common root (the less generalized
        #  attribute in the hierarchy which includes both the attributes). It then replaces it in the dataset.
        for unique_val in unique_vals:
            tmp = unique_val.replace('[', '')
            tmp = tmp.replace(']', '')

            interval_min, interval_max = tmp.split(',')

            common_root = find_common_root(
                hierarchy_file, int(interval_min), int(interval_max))

            dataset[categorical_column] = dataset[categorical_column].replace(
                unique_val, common_root)

    return dataset


def find_common_root(json_data, value1, value2):
    """Algorithm to find the less general attribute which can generalize two attribute's values."""
    def find_path(d, value, path=None):
        """It finds the path of a certain value in a hierarchy."""
        if path is None:
            path = []
        for k, v in d.items():
            if isinstance(v, dict):
                result = find_path(v, value, path + [k])
                if result:
                    return result
            elif v == value:
                return path + [k]
        return None

    path1 = find_path(json_data, value1)
    path2 = find_path(json_data, value2)
    # Once it finds both path for the two values (extremes of interval), it finds the level
    # to which generalize to contain both.
    if not path1 or not path2:
        return None  # One or both values not found

    common_root = []
    for p1, p2 in zip(path1, path2):
        if p1 == p2:
            common_root.append(p1)
        else:
            break
    return common_root[len(common_root)-1] if common_root else None


def recursive_partition(dataset, k, sensitive_data):
    """Splits the dataset in partitions recursively."""
    def axe_to_split(dataframe, sensitive_data):
        #print(dataframe.drop(sensitive_data, axis=1).nunique().idxmax())
        return dataframe.drop(sensitive_data, axis=1).nunique().idxmax()

    if len(dataset) < k*2:
        dataframe_partitions.append(dataset)


    else:
        # Splits according to highest cardinality
        axe = axe_to_split(dataset, sensitive_data)
        left_partition, right_partition = splitter(
            dataset, axe, k)
        #print(left_partition,right_partition)
        recursive_partition(left_partition, k, sensitive_data)
        recursive_partition(right_partition, k, sensitive_data)


def mondrian_anonymization(dataframe_partitions, columns, sensitive_data_columns):
    """Performs mondrian anonymization on the dataset's partitions."""

    print("Anonymization started, wait...", end='')

    mondrian_dataframe = pd.DataFrame(columns=columns, index=None)
    partitions = []
    for partition_i in range(0, len(dataframe_partitions)):
        columns_and_intervals = {}
        rows = []
        for column_j in range(0, len(columns)):
            current_column = columns[column_j]
            if current_column not in sensitive_data_columns and current_column not in categorical_columns:
                # We chose the interval generalization which computes min and max for each partition
                # and returns [min(p),max(p)]
                if statistic == "R":
                    interval = "["+str(dataframe_partitions[partition_i]
                                    [current_column].min())
                    interval += "," + \
                        str(dataframe_partitions[partition_i]
                            [current_column].max()) + "]"
                    
                else:
                    interval = dataframe_partitions[partition_i][current_column].mean()
                columns_and_intervals[current_column] = interval
            elif current_column not in sensitive_data_columns and current_column in categorical_columns:
                interval = "["+str(dataframe_partitions[partition_i]
                                    [current_column].min())
                interval += "," + \
                        str(dataframe_partitions[partition_i]
                            [current_column].max()) + "]"
                columns_and_intervals[current_column] = interval
        for values in dataframe_partitions[partition_i][sensitive_data_columns].to_numpy():
            row = {col: val for col, val in zip(
                sensitive_data_columns, values)}
            row.update(columns_and_intervals)
            rows.append(row)
        partitions.append(pd.DataFrame(rows))
    mondrian_dataframe = pd.concat(partitions, ignore_index=True)
    print("\t OK")

    return mondrian_dataframe


if __name__ == '__main__':
    # Manage data from terminal
    DESC = 'Provsensitive_data_columnse the path of the dataset to anonymize, the grade of anonymization k,'
    DESC += 'the columns of Sensitive Data, the name of the output file, the list of '
    DESC += 'categorical columns and their hierarchy json schema'
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument("--dataset", "-d", required=True,
                        type=str, help="Dataset path")
    parser.add_argument("--explicit-identifiers", "-EI", nargs='+', required=False,
                        type=str, help="column name of explicit identifiers")
    parser.add_argument("--k", "-k", required=True, type=int, help="k value")
    parser.add_argument("--sensitive-data", "-SD", nargs='+', required=True,
                        type=str, help="names of the sensitive data column")
    parser.add_argument("--outputfile", "-o", required=False,
                        type=str, help="name of the file to output")
    parser.add_argument("--categorical", "-c", nargs='+', required=False,
                        type=str, help="categorical column")
    parser.add_argument("--hierarchy", "-hv", nargs='+', required=False,
                        type=str, help="categorical column hierarchy")
    parser.add_argument("--statistic", "-s", required=False,
                        type=str, help="type of statistic to use R/M")
    parser.add_argument("--ignore-cat", "-ic", required=False,
                        type=str, help="if true ignores categorical attributes (drop them)")
    #todo argument per ignorare categorici (dropparli)
    args = parser.parse_args()
    dataset = args.dataset
    k = args.k
    sensitive_data = args.sensitive_data
    explicit_ids = args.explicit_identifiers
    categorical_columns = args.categorical
    categorical_hierarchy = args.hierarchy
    outputfile = args.outputfile
    statistic = args.statistic
    ignore_cat = args.ignore_cat
    if ignore_cat in ["TRUE", "True", "true"]:
        ignore_cat = True
    else: ignore_cat=False
    if statistic != "M":
        statistic = "R"

    if not outputfile:
        outputfile = 'Anonymized_dataset.csv'
    
    if categorical_columns is not None and categorical_columns != "":
        if type(categorical_columns) != list:
            categorical_columns = [categorical_columns]
    else:
        categorical_columns = []
    
    if categorical_hierarchy is not None and categorical_hierarchy != "":
        if type(categorical_hierarchy) != list:
            categorical_hierarchy = [categorical_hierarchy]
    else:
        categorical_hierarchy = []

    if explicit_ids is not None and explicit_ids != "":
        if type(explicit_ids) != list:
            explicit_ids = [explicit_ids]
    else:
        explicit_ids = []
    
    assert len(categorical_hierarchy) == len(categorical_columns)

    print("\n" + "Started anonymization of \033[94m" + dataset +
          "\033[0m with \033[95m" + str(k) + "-anonymity\033[0m")
    print("Sensitive columns: \033[93m" +
          str(sensitive_data) + "\033[0m" + "\n")

    dataframe_partitions = []

    dataset = pd.read_csv(dataset)
    if ignore_cat:
        explicit_ids = explicit_ids + categorical_columns
        print(explicit_ids)
    if explicit_ids:  # eliminate explicit identifiers
        dataset = remove_explicit(dataset, explicit_ids)
    ordered_attributes = dataset.columns.to_list()

    if categorical_columns and not ignore_cat:
        dataset = convert_categorical(
            dataset, categorical_columns, categorical_hierarchy)
    # dataset = dataset.sort_values(by='City') debugging
    recursive_partition(dataset, k, sensitive_data)
    mondrian_dataframe = mondrian_anonymization(
        dataframe_partitions, list(dataset.columns), sensitive_data)
    if not ignore_cat:
        mondrian_dataframe = numerical_to_categorical(
        mondrian_dataframe, categorical_hierarchy, categorical_columns)

    mondrian_dataframe = mondrian_dataframe[ordered_attributes] # Same order as input file
    mondrian_dataframe.to_csv(outputfile, index=False)
    print("\n" + "\033[92mDONE!\033[0m")
