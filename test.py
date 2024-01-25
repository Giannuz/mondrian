import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def is_k_anonymized(anonymized_dataset, k, QI, anon_name):

    if all(anonymized_dataset[QI].value_counts() >= k):
        print(
            f'\n\033[92mThe dataset "{anon_name}" is {k}-anonymous on the QIs: {[i for i in QI]}.\033[0m')
    else:
        print(
            f'\n\033[1;31mThe dataset "{anon_name}" is NOT {k}-anonymous on the QIs: {[i for i in QI]}\033[0m.')


def compute_statistic_info(original_dataset,anonymized_dataset, QI):
    
    stat1 = original_dataset.mean().round(2)
    stat2 = anonymized_dataset.mean().round(2)
    stat3 = original_dataset.std().round(2)
    stat4 = anonymized_dataset.std().round(2)
    # stat5 = ((stat1 - stat2) / stat1 * 100).round(2)
    stat6 = ((stat3 - stat4) / stat3 * 100).round(2)


    result = pd.concat([stat1, stat2, stat3, stat4, stat6], axis=1, ignore_index=True)
    new_column_names = ['Original Mean',
                        'Anon Mean', 'Original Std', 'Anon Std', 'Δ% Std']
    result = result.set_axis(new_column_names, axis=1)
    print('\n'+"#"*19+' Statistical Information Before/After '+"#"*19, '\n')

    print(result, '\n')
    print('#'*76,'\n')


def plot_correlation_heatmap(dataframe, ax, title):
    corr_matrix = dataframe.corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm',
                fmt='.2f', linewidths=0.5, ax=ax)
    ax.set_title(title)

def l_diversity(anonymized_dataset,QI,SD):
    anon = pd.read_csv(anonymized_dataset)
    
    y = anon[SD]
    anon['diversity'] = y.apply(tuple, axis=1)
    anon = anon.drop(SD,axis=1)
    x = anon.groupby(QI)['diversity'].size().reset_index(name='diversity_count')

    print(f"\n\033[92mThe dataset {anonymized_dataset} is {x['diversity_count'].min()}-diverse.\033[0m\n")

def test_all(original_dataset_file, anonymized_dataset_file, k, QI,SD,stat):
    original_dataset = pd.read_csv(original_dataset_file)[QI]
    anonymized_dataset = pd.read_csv(anonymized_dataset_file)[QI]
    is_k_anonymized(anonymized_dataset, k, QI, anonymized_dataset_file)
    l_diversity(anonymized_dataset_file,QI,SD)
    if stat == "M":
        compute_statistic_info(original_dataset, anonymized_dataset, QI)
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        plot_correlation_heatmap(
            original_dataset, ax=axes[0], title='Correlation Matrix - Original Data')
        plot_correlation_heatmap(
            anonymized_dataset, ax=axes[1], title='Correlation Matrix - Anonymized Data')
        plt.tight_layout()
        plt.show()
# SD = ['Legal Situation','Disease']
# QI = ['Age', 'Income', 'Dependants', 'Insurance Coverage']
# test_all('dataset.csv', 'test_id.csv', 3, QI)
