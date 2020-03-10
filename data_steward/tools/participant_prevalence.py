# Python imports
import argparse
import logging
import sys

# Third party imports
from googleapiclient.errors import HttpError
import pandas as pd

# Project imports
from notebooks import bq
import common

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

PARTICIPANT_ROWS = """
SELECT '{table}' AS table_id, COUNT(*) AS all_count, 
COUNT(IF({table_id} > {const}, 1, NULL)) as ehr_count
FROM `{project}.{dataset}.{table}`
WHERE person_id IN ({pids_string})
"""

UNION_ALL = """
UNION ALL
"""

PID_QUERY = """
SELECT person_id
FROM `{pid_project}.{sandbox_dataset}.{pid_table}`
"""

DATASET_ID = 'dataset_id'
TABLE_ID = 'table_id'
COUNT = 'count'

# Query to list all tables within a dataset that contains person_id in the schema
PERSON_TABLE_QUERY = """
SELECT table_name, column_name
FROM `{project}.{dataset}.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name IN
(SELECT table_name
FROM `{project}.{dataset}.INFORMATION_SCHEMA.COLUMNS`
WHERE COLUMN_NAME = 'person_id'
AND ordinal_position = 2)
AND ordinal_position = 1
"""

TABLE_NAME_COLUMN = 'table_name'
COLUMN_NAME = 'column_name'


def get_tables_with_person_id(project_id, dataset_id):
    """
    Get df of table_ids(first column) and table names that have a person_id column as the second column
    
    :param project_id: identifies the project
    :param dataset_id: identifies the dataset
    :return dataframe containing table_id, table_name
    """
    person_table_query = PERSON_TABLE_QUERY.format(project=project_id,
                                                   dataset=dataset_id)
    result_df = bq.query(person_table_query)
    return result_df


def get_pid_counts(project_id, dataset_id, hpo_id, pids_string):
    """
    Returns dataframe with table_name, all_counts and ehr_counts of rows pertaining to the participants

    :param project_id: identifies the project
    :param dataset_id: identifies the dataset
    :param hpo_id: identifies the hpo site that submitted the pids
    :param pids_string: string containing pids or pid_query
    :return: df containing table_name, all_counts and ehr_counts
    """
    person_tables = get_tables_with_person_id(project_id,
                                              dataset_id).get_values()
    pid_query_list = []
    count_df = pd.DataFrame(columns=['table_id', 'all_count', 'ehr_count'])

    for table, table_id in person_tables:
        pid_table_query = PARTICIPANT_ROWS.format(
            project=project_id,
            dataset=dataset_id,
            table=table,
            table_id=table_id,
            const=common.ID_CONSTANT_FACTOR + common.RDR_ID_CONSTANT,
            pids_string=pids_string)
        pid_query_list.append(pid_table_query)

    if len(pid_query_list) > 20:
        pid_query_list = [
            pid_query for pid_query in pid_query_list if hpo_id in pid_query
        ]
    unioned_query = UNION_ALL.join(pid_query_list)
    if unioned_query:
        count_df = bq.query(unioned_query)
    return count_df


def estimate_prevalence(project_id, hpo_id, pids_string):
    """
    Logs dataset_name, table_name, all_count and ehr_count to count rows pertaining to pids

    :param project_id: identifies the project
    :param hpo_id: Identifies the hpo site that submitted the pids
    :param pids_string: string containing query or pids in bq string format
    :return: 
    """

    all_datasets = bq.list_datasets()
    for dataset in all_datasets:
        dataset_id = dataset.dataset_id
        try:
            count_summaries = get_pid_counts(project_id, dataset_id, hpo_id,
                                             pids_string)
            non_zero_counts = count_summaries[
                count_summaries['all_count'] > 0].get_values()
            if non_zero_counts.size > 0:
                for count_row in non_zero_counts:
                    logging.info(
                        'DATASET_ID: {}\tTABLE_ID: {}\tALL_COUNT: {}\tEHR_COUNT: {}'
                        .format(dataset_id, *count_row))
        except HttpError:
            logging.exception('Dataset %s could not be analyzed' % dataset_id)
    return


def get_pids(pid_list=None,
             pid_project_id=None,
             sandbox_dataset_id=None,
             pid_table_id=None):
    """
    Converts either 
     - a list of integer pids into a bq-compatible string containing the pids or
     - a project_id, dataset_id and table_id into a SELECT query that selects pids from the table
    
    :param pid_list: list of pids
    :param pid_project_id: identifies project containing the sandbox dataset
    :param sandbox_dataset_id: identifies dataset containing the pid table
    :param pid_table_id: identifies the table containing pids to consider
    :return: bq-compatible string or SELECT query that selects pids from table
    """
    if pid_list:
        # convert to string and trim the brackets off
        pid_list = [int(pid) for pid in pid_list]
        return str(pid_list)[1:-1]
    elif pid_project_id and sandbox_dataset_id and pid_table_id:
        pid_query = PID_QUERY.format(pid_project=pid_project_id,
                                     sandbox_dataset=sandbox_dataset_id,
                                     pid_table=pid_table_id)
        return pid_query
    else:
        raise ValueError('Please specify pids or pid_table')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Estimates the prevalence of specified pids in the project',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-p',
                        '--project_id',
                        action='store',
                        dest='project_id',
                        help='Identifies the project to retract data from',
                        required=True)
    parser.add_argument('-o',
                        '--hpo_id',
                        action='store',
                        dest='hpo_id',
                        help='Identifies the site submitting the person_ids',
                        required=True)
    parser.add_argument(
        '-q',
        '--pid_project_id',
        action='store',
        dest='pid_project_id',
        help='Identifies the project containing the sandbox dataset',
        required=False)
    parser.add_argument('-s',
                        '--sandbox_dataset_id',
                        action='store',
                        dest='sandbox_dataset_id',
                        help='Identifies the dataset containing the pid table',
                        required=False)
    parser.add_argument('-t',
                        '--pid_table_id',
                        action='store',
                        dest='pid_table_id',
                        help='Identifies the table containing the person_ids',
                        required=False)
    parser.add_argument('-i',
                        '--pid_list',
                        nargs='+',
                        dest='pid_list',
                        help='Person_ids to check for',
                        required=False)

    args = parser.parse_args()

    pids_string = get_pids(args.pid_list, args.pid_project_id,
                           args.sandbox_dataset_id, args.pid_table_id)

    estimate_prevalence(args.project_id, args.hpo_id, pids_string)
