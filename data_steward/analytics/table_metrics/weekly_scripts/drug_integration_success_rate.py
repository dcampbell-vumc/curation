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

DATASET = ''

import os
import sys
from datetime import datetime
from datetime import date
from datetime import time
from datetime import timedelta
import time

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
         `{}._mapping_care_site`
         
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
         `{}._mapping_location`         
         
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_measurement`         
         
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_note`        
         
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_observation`         
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_person`         
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_procedure_occurrence`         
         
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_provider`
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_specimen`
    
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_visit_occurrence`   
    )     
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET, DATASET, DATASET, DATASET, DATASET),
                              dialect='standard')
print(site_map.shape[0], 'records received.')
# -

site_df = pd.merge(site_map, site_df, how='outer', on='src_hpo_id')

site_df

# # Improve the Definitions of Drug Ingredient

diuretics = (974166, 956874, 970250, 1395058, 904542, 942350, 932745,
            907013, 978555, 991382, 1309799)

ccb = (1332418, 1328165, 1318853, 1307863, 1353776, 1318137)

vaccine = (45637323, 529411, 529303, 42800027, 45658522, 45628027, 529218, 36212685, 40163692,
           528323, 528986, 792777, 596876)

oralhypoglycemics = (1503297, 1560171, 1580747, 1559684, 1525215, 1597756, 45774751,
                    40239216, 40166035, 1516766, 1529331)

opioids = (1124957, 1103314, 1201620, 1174888, 1126658, 1110410, 1154029, 1103640, 1102527)

antibiotics = (1734104, 1836430, 1713332, 1797513, 1705674, 1786621,
1742253, 997881, 1707164, 1738521, 1759842, 1746940, 902722, 45892419,
1717327, 1777806, 1836948, 1746114, 1775741)

statins = (1551860, 1545958, 1539403, 1510813, 1592085, 1549686, 40165636)

msknsaids = (1115008, 1177480, 1124300, 1178663, 1136980, 1118084, 1150345, 1236607, 1395573, 1146810)

painnsaids = (1177480, 1125315, 1112807, 1115008, 45660697, 45787568, 36156482, 45696636, 45696805)

ace_inhibitors = (1308216, 1341927, 1335471, 1331235, 1334456, 1340128, 1363749)

all_drugs = diuretics + ccb + vaccine + oralhypoglycemics + opioids + antibiotics + statins + msknsaids + painnsaids + ace_inhibitors

# ## Diuretics

print(len(all_drugs))

len(diuretics)

len(set(diuretics))

df_diuretics = pd.io.gbq.read_gbq('''
SELECT
     mde.src_hpo_id, 
     round(COUNT(DISTINCT ca.ancestor_concept_id) / {} * 100, 0) as ancestor_usage
 FROM
     `{}.unioned_ehr_drug_exposure` de
 JOIN
     `{}.concept_ancestor` ca
 ON
     de.drug_concept_id = ca.descendant_concept_id
 JOIN
     `{}._mapping_drug_exposure` mde
 ON
     de.drug_exposure_id = mde.drug_exposure_id
 WHERE
     ca.ancestor_concept_id IN {}
 GROUP BY 
     1
 ORDER BY 
     ancestor_usage DESC, 
     mde.src_hpo_id
    '''.format(len(set(diuretics)), DATASET, DATASET, DATASET, diuretics,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET),
                                  dialect='standard')
df_diuretics.shape

df_diuretics = df_diuretics.rename(columns={"ancestor_usage": 'diuretics'})

df_diuretics.head(100)

# ## CCB

len(ccb)

len(set(ccb))

df_ccb = pd.io.gbq.read_gbq('''
SELECT
     mde.src_hpo_id, 
     round(COUNT(DISTINCT ca.ancestor_concept_id) / {} * 100, 0) as ancestor_usage
 FROM
     `{}.unioned_ehr_drug_exposure` de
 JOIN
     `{}.concept_ancestor` ca
 ON
     de.drug_concept_id = ca.descendant_concept_id
 JOIN
     `{}._mapping_drug_exposure` mde
 ON
     de.drug_exposure_id = mde.drug_exposure_id
 WHERE
     ca.ancestor_concept_id IN {}
 GROUP BY 
     1
 ORDER BY 
     ancestor_usage DESC, 
     mde.src_hpo_id
    '''.format(len(set(ccb)), DATASET, DATASET, DATASET, ccb, DATASET, DATASET,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                            dialect='standard')
df_ccb.shape

df_ccb = df_ccb.rename(columns={"ancestor_usage": 'ccb'})

df_ccb.head(100)

# ## Vaccine

len(vaccine)

len(set(vaccine))

df_vaccine = pd.io.gbq.read_gbq('''
SELECT
     mde.src_hpo_id, 
     round(COUNT(DISTINCT ca.ancestor_concept_id) / {} * 100, 0) as ancestor_usage
 FROM
     `{}.unioned_ehr_drug_exposure` de
 JOIN
     `{}.concept_ancestor` ca
 ON
     de.drug_concept_id = ca.descendant_concept_id
 JOIN
     `{}._mapping_drug_exposure` mde
 ON
     de.drug_exposure_id = mde.drug_exposure_id
 WHERE
     ca.ancestor_concept_id IN {}
 GROUP BY 
     1
 ORDER BY 
     ancestor_usage DESC, 
     mde.src_hpo_id
    '''.format(len(set(vaccine)), DATASET, DATASET, DATASET, vaccine, DATASET,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                dialect='standard')
df_vaccine.shape

df_vaccine = df_vaccine.rename(columns={"ancestor_usage": 'vaccine'})

df_vaccine.head(100)

# ## oralHypoglycemics

len(oralhypoglycemics)

len(set(oralhypoglycemics))

df_oralhypoglycemics = pd.io.gbq.read_gbq('''
SELECT
     mde.src_hpo_id, 
     round(COUNT(DISTINCT ca.ancestor_concept_id) / {} * 100, 0) as ancestor_usage
 FROM
     `{}.unioned_ehr_drug_exposure` de
 JOIN
     `{}.concept_ancestor` ca
 ON
     de.drug_concept_id = ca.descendant_concept_id
 JOIN
     `{}._mapping_drug_exposure` mde
 ON
     de.drug_exposure_id = mde.drug_exposure_id
 WHERE
     ca.ancestor_concept_id IN {}
 GROUP BY 
     1
 ORDER BY 
     ancestor_usage DESC, 
     mde.src_hpo_id
    '''.format(len(set(oralhypoglycemics)), DATASET, DATASET, DATASET,
               oralhypoglycemics, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET, DATASET, DATASET),
                                          dialect='standard')
df_oralhypoglycemics.shape

df_oralhypoglycemics = df_oralhypoglycemics.rename(
    columns={"ancestor_usage": 'oralhypoglycemics'})

df_oralhypoglycemics.head(100)

# ## opioids

len(opioids)

len(set(opioids))

df_opioids = pd.io.gbq.read_gbq('''
SELECT
     mde.src_hpo_id, 
     round(COUNT(DISTINCT ca.ancestor_concept_id) / {} * 100, 0) as ancestor_usage
 FROM
     `{}.unioned_ehr_drug_exposure` de
 JOIN
     `{}.concept_ancestor` ca
 ON
     de.drug_concept_id = ca.descendant_concept_id
 JOIN
     `{}._mapping_drug_exposure` mde
 ON
     de.drug_exposure_id = mde.drug_exposure_id
 WHERE
     ca.ancestor_concept_id IN {}
 GROUP BY 
     1
 ORDER BY 
     ancestor_usage DESC, 
     mde.src_hpo_id
    '''.format(len(set(opioids)), DATASET, DATASET, DATASET, opioids, DATASET,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                dialect='standard')
df_opioids.shape

df_opioids = df_opioids.rename(columns={"ancestor_usage": 'opioids'})

df_opioids.head(100)

# ## Antibiotics

len(antibiotics)

len(set(antibiotics))

df_antibiotics = pd.io.gbq.read_gbq('''
SELECT
     mde.src_hpo_id, 
     round(COUNT(DISTINCT ca.ancestor_concept_id) / {} * 100, 0) as ancestor_usage
 FROM
     `{}.unioned_ehr_drug_exposure` de
 JOIN
     `{}.concept_ancestor` ca
 ON
     de.drug_concept_id = ca.descendant_concept_id
 JOIN
     `{}._mapping_drug_exposure` mde
 ON
     de.drug_exposure_id = mde.drug_exposure_id
 WHERE
     ca.ancestor_concept_id IN {}
 GROUP BY 
     1
 ORDER BY 
     ancestor_usage DESC, 
     mde.src_hpo_id
    '''.format(len(set(antibiotics)), DATASET, DATASET, DATASET, antibiotics,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET),
                                    dialect='standard')
df_antibiotics.shape

df_antibiotics = df_antibiotics.rename(
    columns={"ancestor_usage": 'antibiotics'})

df_antibiotics.head(100)

# ## Statins

len(statins)

len(set(statins))

df_statins = pd.io.gbq.read_gbq('''
SELECT
     mde.src_hpo_id, 
     round(COUNT(DISTINCT ca.ancestor_concept_id) / {} * 100, 0) as ancestor_usage
 FROM
     `{}.unioned_ehr_drug_exposure` de
 JOIN
     `{}.concept_ancestor` ca
 ON
     de.drug_concept_id = ca.descendant_concept_id
 JOIN
     `{}._mapping_drug_exposure` mde
 ON
     de.drug_exposure_id = mde.drug_exposure_id
 WHERE
     ca.ancestor_concept_id IN {}
 GROUP BY 
     1
 ORDER BY 
     ancestor_usage DESC, 
     mde.src_hpo_id
    '''.format(len(set(statins)), DATASET, DATASET, DATASET, statins, DATASET,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                dialect='standard')
df_statins.shape

df_statins = df_statins.rename(columns={"ancestor_usage": 'statins'})

df_statins.head(100)

# ## msknsaids

len(msknsaids)

len(set(msknsaids))

df_msknsaids = pd.io.gbq.read_gbq('''
SELECT
     mde.src_hpo_id, 
     round(COUNT(DISTINCT ca.ancestor_concept_id) / {} * 100, 0) as ancestor_usage
 FROM
     `{}.unioned_ehr_drug_exposure` de
 JOIN
     `{}.concept_ancestor` ca
 ON
     de.drug_concept_id = ca.descendant_concept_id
 JOIN
     `{}._mapping_drug_exposure` mde
 ON
     de.drug_exposure_id = mde.drug_exposure_id
 WHERE
     ca.ancestor_concept_id IN {}
 GROUP BY 
     1
 ORDER BY 
     ancestor_usage DESC, 
     mde.src_hpo_id
    '''.format(len(set(msknsaids)), DATASET, DATASET, DATASET, msknsaids,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET),
                                  dialect='standard')
df_msknsaids.shape

df_msknsaids = df_msknsaids.rename(columns={"ancestor_usage": 'msknsaids'})

df_msknsaids.head(100)

# ## painnsaids

len(painnsaids)

len(set(painnsaids))

df_painnsaids = pd.io.gbq.read_gbq('''
SELECT
     mde.src_hpo_id, 
     round(COUNT(DISTINCT ca.ancestor_concept_id) / {} * 100, 0) as ancestor_usage
 FROM
     `{}.unioned_ehr_drug_exposure` de
 JOIN
     `{}.concept_ancestor` ca
 ON
     de.drug_concept_id = ca.descendant_concept_id
 JOIN
     `{}._mapping_drug_exposure` mde
 ON
     de.drug_exposure_id = mde.drug_exposure_id
 WHERE
     ca.ancestor_concept_id IN {}
 GROUP BY 
     1
 ORDER BY 
     ancestor_usage DESC, 
     mde.src_hpo_id
    '''.format(len(set(painnsaids)), DATASET, DATASET, DATASET, painnsaids,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET),
                                   dialect='standard')
df_painnsaids.shape

df_painnsaids = df_painnsaids.rename(columns={"ancestor_usage": 'painnsaids'})

df_painnsaids.head(100)

# ## ace_inhibitors

len(ace_inhibitors)

len(set(ace_inhibitors))

df_ace_inhibitors = pd.io.gbq.read_gbq('''
SELECT
     mde.src_hpo_id, 
     round(COUNT(DISTINCT ca.ancestor_concept_id) / {} * 100, 0) as ancestor_usage
 FROM
     `{}.unioned_ehr_drug_exposure` de
 JOIN
     `{}.concept_ancestor` ca
 ON
     de.drug_concept_id = ca.descendant_concept_id
 JOIN
     `{}._mapping_drug_exposure` mde
 ON
     de.drug_exposure_id = mde.drug_exposure_id
 WHERE
     ca.ancestor_concept_id IN {}
 GROUP BY 
     1
 ORDER BY 
     ancestor_usage DESC, 
     mde.src_hpo_id
    '''.format(len(set(ace_inhibitors)), DATASET, DATASET, DATASET,
               ace_inhibitors, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET, DATASET, DATASET),
                                       dialect='standard')
df_ace_inhibitors.shape

df_ace_inhibitors = df_ace_inhibitors.rename(
    columns={"ancestor_usage": 'ace_inhibitors'})

df_ace_inhibitors.head(100)

# ## all_drugs

len(all_drugs)

len(set(all_drugs))

df_all_drugs = pd.io.gbq.read_gbq('''
SELECT
     mde.src_hpo_id, 
     round(COUNT(DISTINCT ca.ancestor_concept_id) / {} * 100, 0) as ancestor_usage
 FROM
     `{}.unioned_ehr_drug_exposure` de
 JOIN
     `{}.concept_ancestor` ca
 ON
     de.drug_concept_id = ca.descendant_concept_id
 JOIN
     `{}._mapping_drug_exposure` mde
 ON
     de.drug_exposure_id = mde.drug_exposure_id
 WHERE
     ca.ancestor_concept_id IN {}
 GROUP BY 
     1
 ORDER BY 
     ancestor_usage DESC, 
     mde.src_hpo_id
    '''.format(len(set(all_drugs)), DATASET, DATASET, DATASET, all_drugs,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET),
                                  dialect='standard')
df_all_drugs.shape

df_all_drugs = df_all_drugs.rename(columns={"ancestor_usage": 'all_drugs'})

df_all_drugs.head(100)

# ## Sites combined

sites_drug_success = pd.merge(df_ace_inhibitors,
                              df_painnsaids,
                              how='outer',
                              on='src_hpo_id')
sites_drug_success = pd.merge(sites_drug_success,
                              df_msknsaids,
                              how='outer',
                              on='src_hpo_id')
sites_drug_success = pd.merge(sites_drug_success,
                              df_statins,
                              how='outer',
                              on='src_hpo_id')
sites_drug_success = pd.merge(sites_drug_success,
                              df_antibiotics,
                              how='outer',
                              on='src_hpo_id')
sites_drug_success = pd.merge(sites_drug_success,
                              df_opioids,
                              how='outer',
                              on='src_hpo_id')
sites_drug_success = pd.merge(sites_drug_success,
                              df_oralhypoglycemics,
                              how='outer',
                              on='src_hpo_id')
sites_drug_success = pd.merge(sites_drug_success,
                              df_vaccine,
                              how='outer',
                              on='src_hpo_id')
sites_drug_success = pd.merge(sites_drug_success,
                              df_ccb,
                              how='outer',
                              on='src_hpo_id')
sites_drug_success = pd.merge(sites_drug_success,
                              df_diuretics,
                              how='outer',
                              on='src_hpo_id')
sites_drug_success = pd.merge(sites_drug_success,
                              df_all_drugs,
                              how='outer',
                              on='src_hpo_id')

sites_drug_success = sites_drug_success.fillna(0)
sites_drug_success

sites_drug_success[["ace_inhibitors","painnsaids","msknsaids","statins","antibiotics","opioids","oralhypoglycemics","vaccine","ccb","diuretics","all_drugs"]]\
    =sites_drug_success[["ace_inhibitors","painnsaids","msknsaids","statins","antibiotics","opioids","oralhypoglycemics","vaccine","ccb","diuretics","all_drugs"]]
sites_drug_success

sites_drug_success = pd.merge(sites_drug_success,
                              site_df,
                              how='outer',
                              on='src_hpo_id')
sites_drug_success = sites_drug_success.fillna(0)

sites_drug_success = sites_drug_success.sort_values(by='all_drugs', ascending = False)

sites_drug_success

sites_drug_success.to_csv("{cwd}\drug_success.csv".format(cwd = cwd))
