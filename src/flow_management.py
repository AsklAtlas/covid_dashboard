import pandas as pd
import io
import requests
import os
import numpy as np
import schedule
import time



def job():
    
    def extract(local=True):

        if local:
            df = pd.read_csv("../data/chiffres-cles.csv")
            quatre_taux = pd.read_csv("../data/table-indicateurs-open-data-dep-serie.csv")
        else: 
            url = "https://github.com/opencovid19-fr/data/raw/master/dist/chiffres-cles.csv"
            s = requests.get(url).content
            df = pd.read_csv(io.StringIO(s.decode('utf-8')))

            url= "https://www.data.gouv.fr/fr/datasets/r/4acad602-d8b1-4516-bc71-7d5574d5f33e"
            s=requests.get(url).content
            quatre_taux = pd.read_csv(io.StringIO(s.decode('utf-8')))

        dpt = pd.read_csv("../data/departements-region.csv")
        reg = pd.read_csv("../data/regions-france.csv")
        pop = pd.read_csv("../data/estim_pop.csv")


        df["date"] = df["date"].replace("_", "-", regex=True)
        df["date"] = pd.to_datetime(df["date"])

        df["dep_code"] = df[(df['maille_code'].str.startswith('DEP')) | (df['maille_code'].str.startswith('COM'))]["maille_code"]\
        .replace(".*-", "", regex=True)
        df["reg_code"] = df[df['maille_code'].str.startswith('REG')]["maille_code"]\
        .replace(".*-", "", regex=True).astype("int64")

        quatre_taux["extract_date"] = pd.to_datetime(quatre_taux["extract_date"])


        geo = dpt.merge(reg, right_on= 'nom_region', left_on='region_name')\
        .rename(columns = {'num_dep':'code_dep'})\
        .drop(columns=["nom_region"])[['code_region', 'region_name', 'code_dep', 'dep_name']]

        pop[["2020", "2021"]] = pop[["2020", "2021"]].replace("\s", "", regex=True).astype(int)

        return [df, quatre_taux, geo, pop]


    def transform(dataframe):

        df, quatre_taux, geo, pop = dataframe[0], dataframe[1], dataframe[2], dataframe[3]

        df_clean = df.merge(geo, right_on="code_dep", left_on='dep_code')[['date', 'code_region', 'region_name', 'code_dep',
               'dep_name', 'cas_confirmes',
               'cas_ehpad', 'cas_confirmes_ehpad', 'cas_possibles_ehpad', 'deces',
               'deces_ehpad', 'reanimation', 'hospitalises',
               'nouvelles_hospitalisations', 'nouvelles_reanimations', 'gueris',
               'depistes', 'source_nom', 'source_url', 'source_archive', 'source_type']]

        rs = []
        for ind, row in df_clean.iterrows():   #[["deces","gueris", 'reanimation', 'hospitalises']]
            if row["date"].year == 2020:
                effectif = pop.loc[pop['code_dpt'] == row['code_dep'], "2020"]
            else: 
                effectif = pop.loc[pop['code_dpt'] == row['code_dep'], "2021"]
            dc = row["deces"] / effectif * 100000
            gu = row["gueris"] / effectif * 100000
        #     rea = row["reanimation"] / effectif * 100000
            hos = row["hospitalises"] / effectif * 100000
        #     tot= dc.values[0] + gu.values[0] + hos.values[0]

            rs.append([row["date"], row["region_name"], row["code_dep"], row["dep_name"], dc.values[0], gu.values[0], hos.values[0]])
        col = ['date', 'region_name', 'dep_code', 'dep_name', 'deces', 'gueris', 'symptomatiques']            


        final = pd.DataFrame(rs, columns = col)\
        .merge(quatre_taux[["extract_date",'departement', 'tx_incid']], left_on=['date','dep_code'], right_on=["extract_date",'departement'],suffixes=('_x', '_y'))\
        .drop(columns=["extract_date",'departement'])#\
    #     .rename(columns= {"tx_incid" : "susceptibles"})

        final["asymptomatiques"] = final["tx_incid"] - final['symptomatiques']

    #     start_date = final[final['asymptomatiques']>0].sort_values('date').iloc[0,0]
        final = final[final["date"].duplicated()]
        final.loc[(final['asymptomatiques']<0), "asymptomatiques"] = float('NaN')
        t = final.groupby("dep_name").size()
        to_drop = t[t<50].index
        final = final[~final["dep_name"].isin(to_drop)]
    #     final = final.loc[(final['date'] >= start_date)  , : ]

        rs=[]
        for name, data in final.groupby('dep_name'):
            data = data.reset_index()
    #         print(name)
            data.sort_values('date', inplace=True)
            if data['tx_incid'].isnull().loc[0]:
                data.loc[0,'tx_incid'] = 0
            if data['deces'].isnull().loc[0]:
                data.loc[0,'deces'] = 0 
            if data['gueris'].isnull().loc[0]:
                data.loc[0,'gueris'] = 0 
            if data['symptomatiques'].isnull().loc[0]:
                data.loc[0,'symptomatiques'] = 0 
            if data['asymptomatiques'].isnull().loc[0]:
                data.loc[0,'asymptomatiques'] = 0 
                data = data.set_index('date').interpolate(method='linear')
                data = data[data.index.duplicated(keep="last")].drop(columns='index')
                rs.append(data)
        final = pd.concat(rs)

        return final

    def load(file, path = "../data/df_clean.csv"):
        if path = "../data/df_clean.csv":
            os.rename("../data/df_clean.csv", "../data/_old_df_clean.csv")
        file.to_csv(path)

    e = extract(local=False)
    df = transform(e)
    load(df)
    
schedule.every().day.at("02:00").do(job)

if __name__== '__main__':
    while True:
    schedule.run_pending()
    time.sleep(1)