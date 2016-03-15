#!/usr/bin/env python
#-*- coding:utf-8 -*-

# favoしたものに画像があれば保存
#chainerからI2vで画像分類したい。
#途中の画像保存のpathとリプ先は変更したり削除したりお願いします。
#3-日付超える9時間で前日で保存されてしまうのを修正
'''
import json
#key.txt#
access_keys={'key':"XXXXXXXXXXXXX",
    'secret':"XXXXXXXXXXXX",
    'token':"XXXXXXXXXXX",
    'token_secret':"XXXXXXXXXX"
    }
with open('tweetkeys.txt','w') as f:
    f.write(json.dumps(access_keys,indent=4))

#count.txt#
cnt = {'fav_count':1}
with open('count.txt','w') as f:
    f.write(json.dumps(cnt,indent=4))
'''

import json
import tweepy
import urllib
import datetime
import time
from tqdm import tqdm

def get_oauth():
    with open('tweetkeys.txt','r') as f:
        j_d=json.loads(f.read())
    consumer_key = j_d['key']
    consumer_secret = j_d['secret']
    access_key = j_d['token']
    access_secret = j_d['token_secret']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    return auth

def downloading(url,path):
    a = urllib.request.urlopen(url).read()
    with open(path,'wb') as f:
        f.write(a)

def create_clock(string_time):
    jikoku=create_date(string_time)
    jj= jikoku.hour+9
    if jj < 24:
        jh,jd = jj,jikoku.day
    else:
        jh = jj-24
        jd = jikoku.day+1
    jikan = '%d-%d%d-%02d%02d%02d'%(jikoku.year,jikoku.month,jd,jh,jikoku.minute,jikoku.second)#,jikoku.microsecond)
    return jikan

def create_date(num):
    m_l = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
    day_info = num.split()
    h,m,s = map(int,day_info[3].split(':'))
    date2 = '%d/%d/%d %d:%d:%d'%(int(day_info[5]),m_l[day_info[1]],int(day_info[2]),h,m,s)
    d = datetime.datetime.strptime(date2, '%Y/%m/%d %H:%M:%S')
    return d

#testtext = ''
class StreamListener(tweepy.StreamListener):
    def on_event(self, status):
        global cnt
        #global testtext
        #testtext = status
        if status.event=='favorite':
            try:
                medias = status.target_object['extended_entities']['media']
                str_date = status.target_object['created_at']
                for c,m in enumerate(medias):
                    downloading(m['media_url'],'fav_image/%s-%d-%d.png'%(create_clock(str_date),c+1,cnt))
                cnt+=1
                #print('ok')
            except Exception:
                pass
            if cnt%100==0:
                try:
                    message='@自分の垢 \n%d個目です'%cnt
                    api.update_status(status=message)#, in_reply_to_status_id=status.id)
                    print(cnt)
                except Exception:
                    pass
if __name__ == "__main__":
    #
    try:
        with open('count.txt','r') as f:
            j=json.loads(f.read())
            cnt=j['fav_count']
    except Exception:
        j={'fav_count':1}
        cnt=j['fav_count']
    #
    auth = get_oauth()
    api = tweepy.API(auth)
    stream = tweepy.Stream(auth, StreamListener(), secure=True)
    print ("Start Streaming!")
    #接続弾かれてもいいように回し続ける
    while True :
        try:
            stream.userstream()#
        except Exception:
            pass
        #streaming弾かれたら、再接続
        print('destroy client,reconnecti')
        [time.sleep(1) for i in tqdm(range(180))]#tqdmなしならtime.sleep(180)で、ただプログレスバーの安心感
        auth = get_oauth()
        api = tweepy.API(auth)
        stream = tweepy.Stream(auth,StreamListener())
        try:
            dt=datetime.now()
            message='@自分の垢\n接続切断、復旧します。\n%d-%d/%d-%02d:%02d'%(dat.year,dt.month,dt.day,dt.hour,dt.minute)
            api.update_status(status=message)
        except Exception:
            pass

    #Nonetypeとか何かのerrorでwhileを出てきたら
    auth = get_oauth()
    api = tweepy.API(auth)
    #とりあえず終了をリプ
    try:
        message='@自分の垢\n異常あり、システムを終了しました。\n%d-%d/%d-%02d:%02d'%(dat.year,dt.month,dt.day,dt.hour,dt.minute)
        api.update_status(status=message)
    except Exception:
        pass
    #cntを保存
    j['fav_count']=cnt
    with open('count.txt') as f:
        f.write(json.dumps(j,indent=4))
    print('fin')
