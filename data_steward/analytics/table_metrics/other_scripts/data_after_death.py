# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from google.cloud import bigquery

client = bigquery.Client()

# %load_ext google.cloud.bigquery

# %reload_ext google.cloud.bigquery

# +
#######################################
print('Setting everything up...')
#######################################

import warnings

warnings.filterwarnings('ignore')
import pandas_gbq
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.lines import Line2D

import matplotlib.ticker as ticker
import matplotlib.cm as cm
import matplotlib as mpl

import matplotlib.pyplot as plt
# %matplotlib inline

import os
import sys
from datetime import datetime
from datetime import date
from datetime import time
from datetime import timedelta
import time
import math

DATASET = ''

plt.style.use('ggplot')
pd.options.display.max_rows = 999
pd.options.display.max_columns = 999
pd.options.display.max_colwidth = 999

from IPython.display import HTML as html_print


def cstr(s, color='black'):
    return "<text style=color:{}>{}</text>".format(color, s)


print('done.')
# -

cwd = os.getcwd()
cwd = str(cwd)
print(cwd)

# +
dic = {
    'src_hpo_id': [
        "saou_uab_selma", "saou_uab_hunt", "saou_tul", "pitt_temple",
        "saou_lsu", "trans_am_meyers", "trans_am_essentia", "saou_ummc",
        "seec_miami", "seec_morehouse", "seec_emory", "uamc_banner", "pitt",
        "nyc_cu", "ipmc_uic", "trans_am_spectrum", "tach_hfhs", "nec_bmc",
        "cpmc_uci", "nec_phs", "nyc_cornell", "ipmc_nu", "nyc_hh",
        "ipmc_uchicago", "aouw_mcri", "syhc", "cpmc_ceders", "seec_ufl",
        "saou_uab", "trans_am_baylor", "cpmc_ucsd", "ecchc", "chci", "aouw_uwh",
        "cpmc_usc", "hrhc", "ipmc_northshore", "chs", "cpmc_ucsf", "jhchc",
        "aouw_mcw", "cpmc_ucd", "ipmc_rush", "va", "saou_umc"
    ],
    'HPO': [
        "UAB Selma", "UAB Huntsville", "Tulane University", "Temple University",
        "Louisiana State University",
        "Reliant Medical Group (Meyers Primary Care)",
        "Essentia Health Superior Clinic", "University of Mississippi",
        "SouthEast Enrollment Center Miami",
        "SouthEast Enrollment Center Morehouse",
        "SouthEast Enrollment Center Emory", "Banner Health",
        "University of Pittsburgh", "Columbia University Medical Center",
        "University of Illinois Chicago", "Spectrum Health",
        "Henry Ford Health System", "Boston Medical Center", "UC Irvine",
        "Partners HealthCare", "Weill Cornell Medical Center",
        "Northwestern Memorial Hospital", "Harlem Hospital",
        "University of Chicago", "Marshfield Clinic",
        "San Ysidro Health Center", "Cedars-Sinai", "University of Florida",
        "University of Alabama at Birmingham", "Baylor", "UC San Diego",
        "Eau Claire Cooperative Health Center", "Community Health Center, Inc.",
        "UW Health (University of Wisconsin Madison)",
        "University of Southern California", "HRHCare",
        "NorthShore University Health System", "Cherokee Health Systems",
        "UC San Francisco", "Jackson-Hinds CHC", "Medical College of Wisconsin",
        "UC Davis", "Rush University", 
        "United States Department of Veterans Affairs - Boston",
        "University Medical Center (UA Tuscaloosa)"
    ]
}

site_df = pd.DataFrame(data=dic)
site_df

# +
######################################
print('Getting the data from the database...')
######################################

site_map = pd.io.gbq.read_gbq('''
    select distinct * from (
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_visit_occurrence`
         
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_condition_occurrence`  
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_device_exposure`

    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_drug_exposure`        
         
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_measurement`            
         
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_observation`         
                
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_procedure_occurrence`         
    
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_visit_occurrence`   
    )
    WHERE src_hpo_id NOT LIKE '%rdr%'
    order by 1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET, DATASET, DATASET, DATASET, DATASET),
                              dialect='standard')
print(site_map.shape[0], 'records received.')
# -

site_df = pd.merge(site_map, site_df, how='outer', on='src_hpo_id')

site_df

# # No data point exists beyond 30 days of the death date. (Achilles rule_id #3)

# ## Visit Occurrence Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(visit_start_date, death_date, DAY)>30) then 1 else 0 end) as wrong_death_date
    FROM
       `{}.visit_occurrence` AS t1
    INNER JOIN
        `{}.death` AS t2
        ON
            t1.person_id=t2.person_id
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_visit_occurrence`)  AS t3
    ON
        t1.visit_occurrence_id=t3.visit_occurrence_id
    WHERE src_hpo_id NOT LIKE '%rdr%'
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['success_rate'] = 100 - round(
    100 * temporal_df['wrong_death_date'] / temporal_df['total'], 1)
temporal_df

# - main reason death date entered as default value ("1890")

visit_occurrence = temporal_df.rename(
    columns={"success_rate": "visit_occurrence"})
visit_occurrence = visit_occurrence[["src_hpo_id", "visit_occurrence"]]
visit_occurrence = visit_occurrence.fillna(100)
visit_occurrence

# ## Condition Occurrence Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(condition_start_date, death_date, DAY)>30) then 1 else 0 end) as wrong_death_date
    FROM
       `{}.condition_occurrence` AS t1
    INNER JOIN
        `{}.death` AS t2
        ON
            t1.person_id=t2.person_id
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_condition_occurrence`)  AS t3
    ON
        t1.condition_occurrence_id=t3.condition_occurrence_id
    WHERE src_hpo_id NOT LIKE '%rdr%'
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['success_rate'] = 100 - round(
    100 * temporal_df['wrong_death_date'] / temporal_df['total'], 1)
temporal_df

condition_occurrence = temporal_df.rename(
    columns={"success_rate": "condition_occurrence"})
condition_occurrence = condition_occurrence[[
    "src_hpo_id", "condition_occurrence"
]]
condition_occurrence = condition_occurrence.fillna(100)
condition_occurrence

# ## Drug Exposure Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(drug_exposure_start_date, death_date, DAY)>30) then 1 else 0 end) as wrong_death_date
    FROM
       `{}.drug_exposure` AS t1
    INNER JOIN
        `{}.death` AS t2
        ON
            t1.person_id=t2.person_id
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_drug_exposure`)  AS t3
    ON
        t1.drug_exposure_id=t3.drug_exposure_id
    WHERE src_hpo_id NOT LIKE '%rdr%'
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['success_rate'] = 100 - round(
    100 * temporal_df['wrong_death_date'] / temporal_df['total'], 1)
temporal_df

drug_exposure = temporal_df.rename(columns={"success_rate": "drug_exposure"})
drug_exposure = drug_exposure[["src_hpo_id", "drug_exposure"]]
drug_exposure = drug_exposure.fillna(100)
drug_exposure

# ## Measurement Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(measurement_date, death_date, DAY)>30) then 1 else 0 end) as wrong_death_date
    FROM
       `{}.measurement` AS t1
    INNER JOIN
        `{}.death` AS t2
        ON
            t1.person_id=t2.person_id
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_measurement`)  AS t3
    ON
        t1.measurement_id=t3.measurement_id
    WHERE src_hpo_id NOT LIKE '%rdr%'
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['success_rate'] = 100 - round(
    100 * temporal_df['wrong_death_date'] / temporal_df['total'], 1)
temporal_df

measurement = temporal_df.rename(columns={"success_rate": "measurement"})
measurement = measurement[["src_hpo_id", "measurement"]]
measurement = measurement.fillna(100)
measurement

# ## Procedure Occurrence Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(procedure_date, death_date, DAY)>30) then 1 else 0 end) as wrong_death_date
    FROM
       `{}.procedure_occurrence` AS t1
    INNER JOIN
        `{}.death` AS t2
        ON
            t1.person_id=t2.person_id
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_procedure_occurrence`)  AS t3
    ON
        t1.procedure_occurrence_id=t3.procedure_occurrence_id
    WHERE src_hpo_id NOT LIKE '%rdr%'
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['success_rate'] = 100 - round(
    100 * temporal_df['wrong_death_date'] / temporal_df['total'], 1)
temporal_df

procedure_occurrence = temporal_df.rename(
    columns={"success_rate": "procedure_occurrence"})
procedure_occurrence = procedure_occurrence[[
    "src_hpo_id", "procedure_occurrence"
]]
procedure_occurrence = procedure_occurrence.fillna(100)
procedure_occurrence

# ## Observation Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(observation_date, death_date, DAY)>30) then 1 else 0 end) as wrong_death_date
    FROM
       `{}.observation` AS t1
    INNER JOIN
        `{}.death` AS t2
        ON
            t1.person_id=t2.person_id
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_observation`)  AS t3
    ON
        t1.observation_id=t3.observation_id
    WHERE src_hpo_id NOT LIKE '%rdr%'
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['success_rate'] = 100 - round(
    100 * temporal_df['wrong_death_date'] / temporal_df['total'], 1)
temporal_df

observation = temporal_df.rename(columns={"success_rate": "observation"})
observation = observation[["src_hpo_id", "observation"]]
observation = observation.fillna(100)
observation

# ## Device Exposure Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(device_exposure_start_date, death_date, DAY)>30) then 1 else 0 end) as wrong_death_date
    FROM
       `{}.device_exposure` AS t1
    INNER JOIN
        `{}.death` AS t2
        ON
            t1.person_id=t2.person_id
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_device_exposure`)  AS t3
    ON
        t1.device_exposure_id=t3.device_exposure_id
    WHERE src_hpo_id NOT LIKE '%rdr%'
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['success_rate'] = 100 - round(
    100 * temporal_df['wrong_death_date'] / temporal_df['total'], 1)
temporal_df

device_exposure = temporal_df.rename(columns={"success_rate": "device_exposure"})
device_exposure = device_exposure[["src_hpo_id", "device_exposure"]]
device_exposure = device_exposure.fillna(100)
device_exposure

# ## 4. Success Rate Temporal Data Points - Data After Death Date

datas = [
    condition_occurrence, drug_exposure, measurement, procedure_occurrence,
    observation, device_exposure
]

master_df = visit_occurrence

for filename in datas:
    master_df = pd.merge(master_df, filename, on='src_hpo_id', how='outer')

master_df

success_rate = pd.merge(master_df, site_df, how='outer', on='src_hpo_id')
success_rate = success_rate.fillna(100)

success_rate

success_rate.to_csv("{cwd}\data_after_death.csv".format(cwd = cwd))


