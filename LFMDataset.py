#%%
import pandas as pd
usersLow=pd.read_csv('dataset-LFM/Zenodo/low_main_users.txt', sep=',', names=['user_id', 'M_global_R_APC'], skiprows=1)
usersMedium=pd.read_csv('dataset-LFM/Zenodo/medium_main_users.txt', sep=',', names=['user_id', 'M_global_R_APC'], skiprows=1)
usersHigh=pd.read_csv('dataset-LFM/Zenodo/high_main_users.txt.', sep=',', names=['user_id', 'M_global_R_APC'], skiprows=1)
#%%
usersLow['Mainstream']='Low'
usersMedium['Mainstream']='Medium'
usersHigh['Mainstream']='High'
usersLow=usersLow.drop('M_global_R_APC',axis=1)
usersMedium=usersMedium.drop('M_global_R_APC',axis=1)
usersHigh=usersHigh.drop('M_global_R_APC',axis=1)
#%%
usersLow=usersLow.append(usersMedium)
usersLow=usersLow.append(usersHigh)
users=usersLow
#%%
#extract users from LFM-1b
usersLFM=pd.read_csv('dataset-LFM/LFM-1b/LFM-1b_users.txt', sep='\t', names=['user_id','country','age','gender','playcount','registered_unixtime'],skiprows=1)
#%%
#merge for extracing users information
usersMergedusersLFM=pd.merge(users,usersLFM,on='user_id',how='inner')
users=usersMergedusersLFM
#%%
#Data preprocessing for users
users=users.dropna()
users=users.drop(users[users.gender=='n'].index)
users=users.drop(users[users.age==-1].index)
users.country=pd.Categorical(users.country)
users.gender=pd.Categorical(users.gender)
users=users.drop('registered_unixtime',axis=1)
users['gender']=users['gender'].cat.codes
users['country']=users['country'].cat.codes
bins = [-1,10,20,30,40,50,60,70,80,90,100]
labels = ['[0,10)','[10,20)','[20,30)','[30,40)','[40,50)','[50,60)','[60,70)','[70,80)',
          '[80,90)','[90,100)']
users['Age'] = pd.cut(users['age'], bins=bins, labels=labels)
users=users.drop('age',axis=1)
users=users.drop('playcount',axis=1)
users=users.dropna()
print(users.head())
#%%
# users age frequency
report=users.groupby('Age')['user_id'].count()
report=report.reset_index()
report['The number of users']=report['user_id']
print(report)
 #%%
# plotting users age frequency
import seaborn as sns
import matplotlib.pyplot as plt
f, ax = plt.subplots(figsize=(6, 7.2))
plot=sns.barplot(x='Age',y='The number of users',data=report)
for item in plot.get_xticklabels():
    item.set_rotation(45)
plt.show()
#%%
# users mainstreamness frequency
report=users.groupby('Mainstream')['user_id'].count()
report=report.reset_index()
report['The number of users']=report['user_id']
print(report)
 #%%
#plotting users mainstreamness frequency
import seaborn as sns
import matplotlib.pyplot as plt
f, ax = plt.subplots(figsize=(5, 5))
plot=sns.barplot(x='Mainstream',y='The number of users',data=report)
plt.show()
#%%
# users gender frequency
report=users.groupby('gender')['user_id'].count()
report=report.reset_index()
report['The number of users']=report['user_id']
print(report)
 #%%
#plotting users gender frequency
import seaborn as sns
import matplotlib.pyplot as plt
f, ax = plt.subplots(figsize=(5, 6))
# plot=sns.ba(x='gender',y='The number of users',size=3,  aspect=2,kind='bar',wid,data=report)
plt.bar(report.gender,report['The number of users'],0.4,color=['red', 'green'])
ax.set_xlabel("Gender")
ax.set_ylabel("Frequency")
plt.show()
 #%%
 #tracks in LFM-1b
tracksLFM=pd.read_csv('dataset-LFM/LFM-1b/LFM-1b_tracks.txt', sep='\t', names=['track_id','track_name','artist_id'],skiprows=1)
#%%
#user-item interactions in LFM User groups
events=pd.read_csv('dataset-LFM/Zenodo/user_events.txt', sep='\t', names=['user_id', 'artist_id', 'album_id', 'track_id', 'timestamp'], skiprows=1)
#%%
print("number of items: ",len(events.track_id.unique()))
#%%
#sorting user-item interactions
events=events.sort_values(['user_id', 'timestamp'], ascending=False)
#%%
user_id_list=users.user_id.unique()
#%%
# extracting last 50 user-item interaction
d=events[events['user_id']==user_id_list[0]]
d1=d.head(50)
print(d1)
print("------------------")
#%%
FinalEvents=d[0:0]
FinalEvents=FinalEvents.append(d1)
for i in range(1,len(user_id_list)):
    print(i)
    d=events[events['user_id']==user_id_list[i]]
    d1 = d.head(50)
    # d1 = d
    FinalEvents = FinalEvents.append(d1)

#%%
#change timestamp to date
from datetime import datetime
FinalEvents['timestamp']= [datetime.fromtimestamp(x) for x in FinalEvents['timestamp']]
#%%
#extracting items that users intracted with
tracks=pd.merge(tracksLFM,FinalEvents,on='track_id',how='inner')
tracks=tracksLFM[tracksLFM['track_id'].isin(tracks.track_id.unique())]
#%%
print(len(tracks.track_id.unique()))
#%%
tracks=tracks.dropna()
print(len(tracks))
tracks.track_name=pd.Categorical(tracks.track_name)
tracks['track_name_id']=tracks['track_name'].cat.codes
tracks=tracks.drop('track_name',axis=1)
#%%
print(len(FinalEvents))
#%%
users.to_csv('dataset-LFM/usersModified.txt',sep=';',index=False)
#%%
tracks.to_csv('dataset-LFM/tracksModified.txt',sep=';',index=False)
#%%
FinalEvents.to_csv('dataset-LFM/eventsModified.txt',sep=';',index=False)


