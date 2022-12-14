# -*- coding: utf-8 -*-
"""빅데이터 분석 프로젝트

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CurW0z6zyXj4r10boWkgJEP2tFzc8W9p
"""

!pip install folium

from google.colab import drive
drive.mount('/content/drive')

!pip install geopy

!sudo apt-get install -y fonts-nanum
!sudo fc-cache -fv
!rm ~/.cache/matplotlib -rf

!pip install openpyxl

!pip install pingouin

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
plt.rc('font', family='NanumBarunGothic')
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
import scipy.stats
from scipy.stats import levene
import pingouin as pg
from sklearn.preprocessing import StandardScaler

import warnings
warnings.filterwarnings("ignore")

import requests, json, pprint

import folium

from geopy.geocoders import Nominatim
from tqdm import tqdm

from geopy.distance import great_circle

pd.options.display.max_columns = 999

def geocoding_reverse(lat_lng_str): 
    geolocoder = Nominatim(user_agent = 'South Korea', timeout=None)
    address = geolocoder.reverse(lat_lng_str)

    return address

address = geocoding_reverse('37.586230, 127.001694')
print(address)

train_2020 = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/2020년_버스노선별_정류장별_시간대별_승하차_인원_정보 (1).csv",encoding="cp949",usecols=[0] + list(range(0,55)))
train_2019 = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/2019년_버스노선별_정류장별_시간대별_승하차_인원_정보.csv",encoding="cp949",usecols=[0] + list(range(2,56)))
train_2018 = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/2018년_버스노선별_정류장별_시간대별_승하차_인원_정보.csv",encoding="cp949",usecols=[0] + list(range(2,56)))
train_2017 = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/2017년_버스노선별_정류장별_시간대별_승하차_인원_정보.csv",encoding="cp949",usecols=[0] + list(range(2,56)))
train_2016 = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/2016년_버스노선별_정류장별_시간대별_승하차_인원_정보.csv",encoding="cp949",usecols=[0] + list(range(1,55)))
train_2015 = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/2015년_버스노선별_정류장별_시간대별_승하차_인원_정보.csv",encoding="cp949",usecols=[0] + list(range(2,56)))

train_2020["표준버스정류장ID"] = train_2020["표준버스정류장ID"].astype(str)
train_2019["표준버스정류장ID"] = train_2019["표준버스정류장ID"].astype(str)
train_2018["표준버스정류장ID"] = train_2018["표준버스정류장ID"].astype(str)
train_2017["표준버스정류장ID"] = train_2017["표준버스정류장ID"].astype(str)
train_2016["표준버스정류장ID"] = train_2016["표준버스정류장ID"].astype(str)
train_2015["표준버스정류장ID"] = train_2015["표준버스정류장ID"].astype(str)

train = pd.concat([train_2020,train_2019,train_2018,train_2017,train_2016,train_2015])
train = train.reset_index(drop=True)
station = pd.read_excel("/content/drive/MyDrive/Colab Notebooks/20220429기준_서울시정류소리스트.xlsx",engine="openpyxl")

dust = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/서울시 대기질 자료 제공_2020-2021.csv",encoding="cp949")
dust_2019 = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/서울시 대기질 자료 제공_2016-2019.csv",encoding="cp949")
dust_2015 = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/서울시 대기질 자료 제공_2012-2015.csv",encoding="cp949")
dust = pd.concat([dust,dust_2019,dust_2015])
dust = dust.rename(columns={"구분":"행정구"})
dust = dust.loc[dust["행정구"]!="평균",]
dust

population = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/Report (3).csv",encoding="cp949",header=2)
population

def get_address(lat, lng):
    url = "https://dapi.kakao.com/v2/local/geo/coord2regioncode.json?x="+lng+"&y="+lat
    headers = {"Authorization": "KakaoAK d342cee0b80233ab5ca0de53cddee255"}
    api_json = requests.get(url, headers=headers)
    full_address = json.loads(api_json.text)

    return full_address

full_address = get_address('37.586230', '127.001694')
pprint.pprint(full_address)

gu = []
for i in zip(station["좌표Y"],tqdm(station["좌표X"])):
  address = get_address(str(i[0]),str(i[1]))
  gu.append(address["documents"][0]["region_2depth_name"])
station["행정구"] = gu

station["NODE_ID"] = station["NODE_ID"].astype(str)
train = train.merge(station,left_on="표준버스정류장ID",right_on="NODE_ID",how="left")
train = train.dropna(axis=0)
train

columns = ['사용년월', '노선번호', '노선명', '표준버스정류장ID', '버스정류장ARS번호', '역명', '00시승차총승객수',
        '1시승차총승객수', '2시승차총승객수',  '3시승차총승객수',
        '4시승차총승객수',  '5시승차총승객수',  '6시승차총승객수',
        '7시승차총승객수',  '8시승차총승객수', '9시승차총승객수',
        '10시승차총승객수',  '11시승차총승객수', 
       '12시승차총승객수',  '13시승차총승객수',  '14시승차총승객수',
        '15시승차총승객수',  '16시승차총승객수', 
       '17시승차총승객수',  '18시승차총승객수',  '19시승차총승객수',
        '20시승차총승객수',  '21시승차총승객수',
       '22시승차총승객수',  '23시승차총승객수', "좌표X","좌표Y"]
train = train[columns]
train["사용년월"] = train["사용년월"].astype(str)
train["사용년월"] = train["사용년월"].apply(lambda x : x[:4] + "-" + x[4:])
train["사용년월"] = pd.to_datetime(train["사용년월"])
train["month"] = train["사용년월"].dt.month

#train = train.merge(replace,on=["좌표X","좌표Y"],how="left")
#train = train.drop(["month_y"],axis=1)
#train = train.rename(columns={"month_x":"month"})
#train

train = pd.read_csv("/content/drive/MyDrive/구글 코랩/train.csv")
train["사용년월"] = pd.to_datetime(train["사용년월"])
train

replace = train.groupby(["좌표X","좌표Y","행정구"])["행정구"].nunique().to_frame("month").reset_index()
replace

class CountByWGS84() :
  def __init__(self,df,lat,lon,dist=1):
    self.df = df
    self.lat = lat
    self.lon = lon
    self.dist = dist

  def filter_by_rectangle(self):

    lat_min = self.lat - 0.01 * self.dist
    lat_max = self.lat + 0.01 * self.dist

    lon_min = self.lon - 0.015 * self.dist
    lon_max = self.lon + 0.015 * self.dist

    self.points = [[lat_min,lon_min],[lat_max,lon_max]]
    result = self.df.loc[(self.df["lat"] > lat_min) & (self.df["lat"] < lat_max) & (self.df["lon"] > lon_min) & (self.df["lon"] < lon_max),]

    resut = result.reset_index(drop=True)
    return result

  def filter_by_radius(self):

    tmp = self.filter_by_rectangle()
    center = (self.lat, self.lon)
    result = pd.DataFrame()
    for index, row in tmp.iterrows():
      point = (row["lat"],row["lon"])
      d = great_circle(center,point).kilometers
      if d <= self.dist:
        result = pd.concat([result,tmp.iloc[index,:].to_frame().T])
    
    result = result.reset_index(drop=True)
    return result

  def plot_by_rectangle(self,df):

    m = folium.Map(location=[self.lat,self.lon],zoom_start=14)
    for idx, row in df.iterrows():
      
      lat_ = row["lat"]
      lon_ = row["lon"]

      folium.Marker(location=[lat_,lon_],radius=15,tooltip=row["지점명"]).add_to(m)
    
    folium.Rectangle(bounds = self.points, color= "#ff7800",fill=True,fill_color="#ffff00",fill_opacity=0.2).add_to(m)
    return m

  def plot_by_radius(self,df):

    m = folium.Map(location=[self.lat,self.lon],zoom_start=14)

    for idx, row in df.iterrows():
      lat_ = row["lat"]
      lon_ = row["lon"]

      folium.Marker(location=[lat_,lon_],radius=15,tooltip=row["지점명"]).add_to(m)
    
    folium.Circle(radius = dist * 1000, location=[lat,lon],color="#ff7800",fill_color = "#ffff00", fill_opacity=0.2).add_to(m)
  
    return m

market = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/소상공인시장진흥공단_상가(상권)정보_서울.csv",encoding="cp949")
market = market.loc[(market["상호명"].str.contains("스타벅스",na=False)),]
market = market.rename(columns = {"경도":"lon","위도":"lat"})
market = market.reset_index(drop=True)

result_rectangle = []
for lat,lon in zip(train["좌표Y"],tqdm(train["좌표X"],total=len(train["좌표X"]))):
  cbw = CountByWGS84(market,lat,lon,dist=0.5)
  result_rectangle.append(len(cbw.filter_by_rectangle()))

starbucks_train = train[["좌표X","좌표Y","month","행정구"]]
starbucks_train["반경1KM내스타벅스"] = result_rectangle

subway = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/station_coordinate.csv",encoding="cp949")
subway = subway.rename(columns = {"lng":"lon"})
subway = subway.drop_duplicates(["name"]).reset_index(drop=True)

result_rectangle = []
for lat,lon in zip(train["좌표Y"],tqdm(train["좌표X"],total=len(train["좌표X"]))):
  cbw = CountByWGS84(subway,lat,lon,dist=0.5)
  result_rectangle.append(len(cbw.filter_by_rectangle()))

subway_train = train[["좌표X","좌표Y","month","행정구"]]
subway_train["반경1KM내지하철"] = result_rectangle

starbucks_train = pd.read_csv("/content/drive/MyDrive/구글 코랩/starbucks_train.csv")
starbucks_train = starbucks_train.loc[starbucks_train["행정구"]!="광명시",]
starbucks_train = starbucks_train.loc[starbucks_train["행정구"]!="하남시",]
starbucks_train = starbucks_train.loc[starbucks_train["행정구"]!="안양시 만안구",]
starbucks_train = starbucks_train.loc[starbucks_train["행정구"]!="성남시 수정구",]

subway_train = pd.read_csv("/content/drive/MyDrive/구글 코랩/subway_train.csv")
subway_train = subway_train.loc[subway_train["행정구"]!="광명시",]
subway_train = subway_train.loc[subway_train["행정구"]!="하남시",]
subway_train = subway_train.loc[subway_train["행정구"]!="안양시 만안구",]
subway_train = subway_train.loc[subway_train["행정구"]!="성남시 수정구",]

train_2020 = train.loc[(train["사용년월"] >= "2020-01-01") & (train["사용년월"] <= "2020-12-31"),]
train_2019 = train.loc[(train["사용년월"] >= "2019-01-01") & (train["사용년월"] <= "2019-12-31"),]
train_2018 = train.loc[(train["사용년월"] >= "2018-01-01") & (train["사용년월"] <= "2018-12-31"),]
train_2017 = train.loc[(train["사용년월"] >= "2017-01-01") & (train["사용년월"] <= "2017-12-31"),]
train_2016 = train.loc[(train["사용년월"] >= "2016-01-01") & (train["사용년월"] <= "2016-12-31"),]
train_2015 = train.loc[(train["사용년월"] >= "2015-01-01") & (train["사용년월"] <= "2015-12-31"),]

def train_stack(train):

  train = train.set_index(["사용년월","노선번호","노선명","표준버스정류장ID","버스정류장ARS번호","역명","좌표X","좌표Y","행정구","month"]).stack(dropna=False).to_frame().reset_index()
  train = train.rename(columns={"level_10":"hour"})
  train = train.rename(columns={0:"승차총승객수"})
  train["hour"] = train["hour"].apply(lambda x : x[0:2] if len(x) == 9 else x[0])
  train["hour"] = train["hour"].apply(lambda x : x.zfill(2))
  train["사용년월"] = train["사용년월"].astype(str)
  train["사용년월"] = train["사용년월"].apply(lambda x : x[0:4] + x[4:])
  train["사용년월"] = train["사용년월"] + "-" + train["hour"]
  train["사용년월"] = pd.to_datetime(train["사용년월"])
  train["hour"] = train["사용년월"].dt.hour
  train["quarter"] = train["사용년월"].dt.quarter
  train = train.loc[(train["행정구"]!= "광명시"),]
  train = train.loc[(train["행정구"]!= "하남시"),]
  train = train.loc[(train["행정구"]!= "안양시 만안구"),]
  train = train.loc[(train["행정구"]!= "성남시 수정구"),]
  X_train = train.groupby(["행정구","month","hour"])["승차총승객수"].sum().to_frame().reset_index()

  return X_train

train_2020 = train_stack(train_2020)
train_2019 = train_stack(train_2019)
train_2018 = train_stack(train_2018)
train_2017 = train_stack(train_2017)
train_2016 = train_stack(train_2016)
train_2015 = train_stack(train_2015)

train_2020 = pd.read_csv("/content/drive/MyDrive/구글 코랩/train_2020.csv")
train_2019 = pd.read_csv("/content/drive/MyDrive/구글 코랩/train_2019.csv")
train_2018 = pd.read_csv("/content/drive/MyDrive/구글 코랩/train_2018.csv")
train_2017 = pd.read_csv("/content/drive/MyDrive/구글 코랩/train_2017.csv")
train_2016 = pd.read_csv("/content/drive/MyDrive/구글 코랩/train_2016.csv")
train_2015 = pd.read_csv("/content/drive/MyDrive/구글 코랩/train_2015.csv")

train_2020["year"] = "2020"
train_2019["year"] = "2019"
train_2018["year"] = "2018"
train_2017["year"] = "2017"
train_2016["year"] = "2016"
train_2015["year"] = "2015"

X_train = pd.concat([train_2020,train_2019,train_2018,train_2017,train_2016,train_2015])

X_train = pd.read_csv("/content/drive/MyDrive/구글 코랩/X_train.csv")
X_train

plt.figure(figsize=(30,15))
month_train = X_train.groupby(["행정구","month"])["승차총승객수"].sum().to_frame().reset_index()
sns.pointplot(x="month",y="승차총승객수",data=month_train,hue="행정구")
plt.legend(loc="upper right")

fig,ax = plt.subplots(5,5,figsize=(30,20))

for i in range(25):

  data = X_train.loc[(X_train["행정구"]) == X_train["행정구"].unique()[i],]
  sns.pointplot(x="hour",y="승차총승객수",data=data,hue="month",ax=ax[i//5][i%5])
  ax[i//5][i%5].set_xlabel(X_train["행정구"].unique()[i])

dust["일시"] = pd.to_datetime(dust["일시"])
dust["year"] = dust["일시"].dt.year
dust["month"] = dust["일시"].dt.month
dust["hour"] = dust["일시"].dt.hour
dust = dust.loc[(dust["일시"] >= "2015-01-01 00:00:00") & (dust["일시"] <= "2020-12-31 23:00:00"),].reset_index(drop=True)
dust = dust.groupby(["행정구","year","month","hour"])["미세먼지(PM10)","초미세먼지(PM25)"].mean().reset_index()
dust

train["year"] = train["사용년월"].dt.year
X_train = X_train.merge(dust,on=["행정구","year","month","hour"],how="left")
X_train = X_train.merge(train.groupby(["행정구","year"])["노선번호"].nunique().to_frame().reset_index(),on=["행정구","year"],how="left")
X_train = X_train.merge(train.groupby(["행정구","year"])["역명"].nunique().to_frame().reset_index(),on=["행정구","year"],how="left")
X_train

population = population.iloc[1:,]
population["year"] = population["기간"].apply(lambda x : x[0:4])
population["quarter"] = population["기간"].apply(lambda x : x[5])
population = population.loc[(population["year"] >= "2015") & (population["year"] <= "2020"),]

population = population.rename(columns={"자치구":"행정구"})
population["quarter"] = population["quarter"].astype("int")
population = population.iloc[:,[1,3,14,15]]

X_train["quarter"] = X_train["month"].replace({1:1,2:1,3:1,4:2,5:2,6:2,7:3,8:3,9:3,10:4,11:4,12:4})
X_train["year"] = X_train["year"].astype(str)
X_train = X_train.merge(population,on=["행정구","year","quarter"],how="left")
X_train = X_train.rename(columns={"계":"인구"})
X_train

GunGu_train = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/Report (1).csv",encoding="cp949")

GunGu_train = GunGu_train.loc[GunGu_train["분류별"] == "동수"]
GunGu_train = GunGu_train[["자치구별","용도별","합계"]]
GunGu_train = GunGu_train.loc[(GunGu_train["자치구별"] != "서울시") & (GunGu_train["자치구별"] != "본청"),]
GunGu_train = GunGu_train.loc[(GunGu_train["용도별"] == "주거용") | (GunGu_train["용도별"] == "상업용") | (GunGu_train["용도별"] == "공업용"),]
GunGu_train

GunGu_train["합계"] = GunGu_train["합계"].astype("int")
fig,ax = plt.subplots(5,5,figsize=(20,15))

for i in range(25):

  sns.barplot(x = "용도별", y = "합계", data = GunGu_train.loc[GunGu_train["자치구별"] == GunGu_train["자치구별"].unique()[i],],ax = ax[i//5][i%5])
  ax[i//5][i%5].set_xlabel(GunGu_train["자치구별"].unique()[i])

X_train["용도"] = X_train["행정구"].replace({"종로구":0,"중구":0,"용산구":0,"성동구":0,"광진구":1,"동대문구":0,"중랑구":1,"성북구":1,"강북구":0,"도봉구":1,"노원구":0,"은평구":1,"서대문구":0,"마포구":0,"양천구":0,"강서구":0,"구로구":1,"금천구":1,"영등포구":0,"동작구":1,"관악구":1,"서초구":0,"강남구":0,"송파구":0,"강동구":1})
X_train

starbucks_km = starbucks_train.groupby(["행정구"])["반경1KM내스타벅스"].sum().to_frame().reset_index()
X_train = X_train.merge(starbucks_km,on="행정구",how="left")

subway_km = subway_train.groupby(["행정구"])["반경1KM내지하철"].sum().to_frame().reset_index()
X_train = X_train.merge(subway_km,on="행정구",how="left")
X_train

X_train = X_train.rename(columns={"반경1KM내스타벅스":"반경500m내스타벅스","반경1KM내지하철":"반경500m내지하철"})
X_train

X_train["인구"] = X_train["인구"].apply(lambda x : x[0:3] + "" + x[4:])
X_train["인구"] = X_train["인구"].astype("int")

X_train = X_train.rename(columns = {"미세먼지(PM10)":"미세먼지","초미세먼지(PM25)":"초미세먼지"})
X_train

"""# 인구수와 승차총승객수는 관련이 있을까?"""

corr_train = X_train.drop_duplicates(["행정구","year","quarter"]).groupby(["행정구","year"]).max().reset_index()
pearson_train = X_train.groupby(["행정구","year"])["승차총승객수"].sum().to_frame().reset_index()
corr_train  = corr_train.drop(["승차총승객수"],axis=1)
corr_train = corr_train.merge(pearson_train,on=["행정구","year"],how="left")
corr_train

scipy.stats.spearmanr(corr_train["인구"],corr_train["승차총승객수"])

sns.lmplot(x = "인구", y= "승차총승객수", data=corr_train)

"""# 연도별 승객수의 차이가 있을까?"""

X_train["승차총승객수"] = X_train["승차총승객수"] / X_train["인구"]
year_anova = X_train.groupby(["행정구","year"])["승차총승객수"].sum().to_frame().reset_index()
year_anova

sns.boxplot(x="year",y="승차총승객수",data=year_anova,showfliers=False)

for i in year_anova["year"].unique():
  globals()["year"+str(i)] = year_anova.loc[year_anova["year"] == i,"승차총승객수"]

variance = levene(year2015,year2016,year2017,year2018,year2019,year2020)
if variance[1] <= 0.05:
  print("등분산성을 만족하지 않습니다.\n")
else :
  print("등분산성을 만족합니다.\n")

pg.anova(dv = "승차총승객수", between = "year", data = year_anova,detailed=True)

variance = levene(year2015,year2016,year2017,year2018,year2019)
if variance[1] <= 0.05:
  print("등분산성을 만족하지 않습니다.\n")
else :
  print("등분산성을 만족합니다.\n")

pg.anova(dv = "승차총승객수", between = "year", data = year_anova.loc[year_anova["year"] != "2020",],detailed=True)

"""# 자치구 별 승객수의 차이가 있을까?"""

plt.figure(figsize=(15,10))
sns.barplot(X_train.groupby(["행정구"])["승차총승객수"].sum().sort_values(ascending=False).index,X_train.groupby(["행정구"])["승차총승객수"].sum().sort_values(ascending=False).values)

gu_anova = X_train.groupby(["행정구","year"])["승차총승객수"].sum().to_frame().reset_index()
gu_anova

plt.figure(figsize=(15,10))
sns.boxplot(gu_anova["행정구"],gu_anova["승차총승객수"],showfliers=False)
plt.xticks(rotation=45)

for i,value in enumerate(gu_anova["행정구"].unique(),1):
  globals()["place"+str(i)] = year_anova.loc[year_anova["행정구"] == value,"승차총승객수"]

variance = levene(place1,place2,place3,place4,place5,place6,place7,place8,place9,place10,place11,place12,place13,place14,place15,place16,place17,place18,place19,place20,place21,place22,place23,place24,place25)

if variance[1] <= 0.05:
  print("등분산성을 만족하지 않습니다.\n")
else :
  print("등분산성을 만족합니다.\n")

pg.anova(dv = "승차총승객수", between = "행정구", data = gu_anova.loc[gu_anova["year"] != "2020",],detailed=True)

"""# Month가 승객수와 연관이 있을까?"""

month_anova = X_train.groupby(["행정구","month"])["승차총승객수"].sum().to_frame().reset_index()
for i in range(1,month_anova["month"].nunique() + 1):
  globals()["month"+str(i)] = month_anova.loc[month_anova["month"] == i,"승차총승객수"]

plt.figure(figsize=(10,8))
sns.boxplot(month_anova["month"],month_anova["승차총승객수"])

variance = levene(month1,month2,month3,month4,month5,month6,month7,month8,month9,month10,month11,month12)
if variance[1] <= 0.05:
  print("등분산성을 만족하지 않습니다.\n")
else :
  print("등분산성을 만족합니다.\n")

pg.anova(dv = "승차총승객수", between = "month", data = month_anova,detailed=True)

"""# 시간과 승객수가 연관이 있을까?"""

hour_anova = X_train.groupby(["행정구","hour"])["승차총승객수"].sum().to_frame().reset_index()
hour_anova

plt.figure(figsize=(10,8))
for i in range(1,hour_anova["hour"].nunique() + 1):
  globals()["hour"+str(i)] = hour_anova.loc[hour_anova["hour"] == i,"승차총승객수"]

sns.boxplot(hour_anova["hour"],hour_anova["승차총승객수"],showfliers=False)

variance = pg.homoscedasticity(dv = "승차총승객수", group = "hour", data = hour_anova )
if variance["pval"][0] <= 0.05:
  print("등분산성을 만족하지 않습니다.\n")
else:
  print("등분산성을 만족합니다.\n")
variance

pg.welch_anova(dv = "승차총승객수",between="hour",data = hour_anova)

"""# 미세먼지와 초미세먼지와 승차총승객수는 관련이 있을까?"""

dust = X_train.groupby(["행정구","year"])["승차총승객수"].sum().to_frame().reset_index()
dust = dust.merge(X_train.groupby(["행정구","year"])["미세먼지","초미세먼지"].mean().reset_index(),on=["행정구","year"],how="left")
dust

print(scipy.stats.spearmanr(dust["승차총승객수"],dust["미세먼지"]))
print(scipy.stats.spearmanr(dust["승차총승객수"],dust["초미세먼지"]))

"""# 버스 노선의 개수와 운행하는 버스의 차량 개수가 승차총승객수와 관련이 있을까?"""

dust = dust.merge(X_train.drop_duplicates(["행정구","year","노선번호"]).loc[:,["행정구","year","노선번호"]],on=["행정구","year"],how="left")
dust = dust.merge(X_train.drop_duplicates(["행정구","year","역명"]).loc[:,["행정구","year","역명"]],on=["행정구","year"],how="left")
dust

print(scipy.stats.spearmanr(dust["승차총승객수"],dust["노선번호"]))
print(scipy.stats.spearmanr(dust["승차총승객수"],dust["역명"]))

sns.lmplot(x="노선번호",y="승차총승객수",data=dust)

model = ols("승차총승객수 ~ 노선번호", data=dust).fit()
model.summary()

"""# 주거지역 상업지역에 따라 승차총승객수와 관련이 있을까?"""

dust = dust.merge(X_train.drop_duplicates(["행정구","year","용도"]).loc[:,["행정구","year","용도"]],on=["행정구","year"],how="left")
dust

model = ols("승차총승객수 ~ C(행정구) * C(용도)", dust).fit()
anova_lm(model)

"""# 반경 500m내 스타벅스 개수와 버스 탑승량은 관련이 있을까?"""

train_starbucks = X_train.groupby(["행정구"])["승차총승객수"].sum().to_frame().reset_index()
train_starbucks = train_starbucks.merge(X_train.drop_duplicates(["행정구"]).loc[:,["행정구","반경500m내스타벅스"]],on=["행정구"],how="left")
train_starbucks

scipy.stats.spearmanr(train_starbucks["승차총승객수"],train_starbucks["반경500m내스타벅스"])

sns.lmplot(x="반경500m내스타벅스",y="승차총승객수",data=train_starbucks)

model = ols("승차총승객수 ~ 반경500m내스타벅스", data = train_starbucks).fit()
model.summary()

"""# 반경 500m내 지하철 역의 개수와 승차총승객수는 관련이 있을까?"""

train_subway = X_train.groupby(["행정구"])["승차총승객수"].sum().to_frame().reset_index()
train_subway = train_subway.merge(X_train.drop_duplicates(["행정구"]).loc[:,["행정구","반경500m내지하철"]],on=["행정구"],how="left")
train_subway

scipy.stats.spearmanr(train_subway["승차총승객수"],train_subway["반경500m내지하철"])

sns.lmplot(x="반경500m내지하철",y="승차총승객수",data=train_subway)

model = ols("승차총승객수 ~ 반경500m내지하철", data=train_subway).fit()
model.summary()

