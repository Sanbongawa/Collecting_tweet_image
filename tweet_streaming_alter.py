#!/usr/bin/env python
#-*- coding:utf-8 -*-

# favoしたものに画像があれば保存
#chainerからI2vで画像分類したい。
#途中の画像保存のpathとリプ先は変更したり削除したりお願いします。
#5-動画をmp4で取ってこられるように対応
#6割と大きな誤字、脱字の改善⇦主にdatetime関係
#7自分のツイートは弾く、ファイル管理しやすい名前に
#8・７月取れてない説--要検証
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
import time
from datetime import datetime
from tqdm import tqdm

def get_oauth():
    with open('tweetkeys.txt','r') as f:
        t_key=json.loads(f.read())
    consumer_key = t_key['key']
    consumer_secret = t_key['secret']
    access_key = t_key['token']
    access_secret = t_key['token_secret']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    return auth

def downloading(url,path):
    image = urllib.request.urlopen(url).read()
    with open(path,'wb') as f:
        f.write(image)

def create_clock(string_time):
    jikoku=create_date(string_time)
    jj= jikoku.hour+9
    if jj < 24:
        jh,jd=jj,jikoku.day
    else:
        jh =jj-24
        jd = jikoku.day+1
    jikan = '%d-%d%02d-%02d%02d%02d'%(jikoku.year,jikoku.month,jd,jh,jikoku.minute,jikoku.second)#,jikoku.microsecond)
    return jikan

def create_date(c_day):
    m_l = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
    day_info = c_day.split()
    h,m,s = map(int,day_info[3].split(':'))
    date2 = '%d/%d/%d %d:%d:%d'%(int(day_info[5]),m_l[day_info[1]],int(day_info[2]),h,m,s)
    d = datetime.strptime(date2, '%Y/%m/%d %H:%M:%S')
    return d

#testtext3 = []

class StreamListener(tweepy.StreamListener):
    def on_event(self, status):
        global cnt
        #global testtext3
        if status.event=='favorite':
            try:
                #testtext3.append(status)
                medias = status.target_object['extended_entities']['media']
                str_date = status.target_object['created_at']
                if status.target_object['user']['screen_name']=='自分の垢のscreen_name':
                    #print('my tweet')
                    pass
                elif 'video_info' in medias[0]:
                    #別フォーマットでも大抵mp4で大本をとっているので
                    for _url in medias[0]['video_info']['variants']:#[0]['url']
                        if _url['url'][-4:] == '.mp4':
                            #保存場所は適宜変えてください
                            downloading(_url['url'],'../../Documents/streaming_image/%s-%d.mp4'%(create_clock(str_date),cnt))
                        elif _url['url'][-4:] == '.gif':
                            downloading(_url['url'],'../../Documents/streaming_image/%s-%d.gif'%(create_clock(str_date),cnt))
                        else:
                            pass
                    cnt+=1
                else:
                    for c,m in enumerate(medias):
                        downloading(m['media_url'],'../../Documents/streaming_image/%s-%d-%d.png'%(create_clock(str_date),c+1,cnt))
                    cnt+=1
            except Exception:
                pass
            if cnt%200==0:
                try:
                    message='@自分の垢のscreen_name\n%d個目です'%cnt
                    api.update_status(status=message)#, in_reply_to_status_id=status.id)
                except Exception:
                    pass
                print(cnt)
if __name__ == "__main__":
    try:
        with open('count.txt','r') as f:
            j_cnt=json.loads(f.read())
            cnt=j_cnt['fav_count']
    except Exception:
        j_cnt={'fav_count':1}
        cnt=j_cnt['fav_count']
    print(cnt)
    auth = get_oauth()
    api = tweepy.API(auth)
    stream = tweepy.Stream(auth, StreamListener(), secure=True)
    print ("Start Streaming!")

    #接続弾かれてもいいように回し続ける
    #tryでkeyborad(crtl+c)でcnt保存、正常終了
    ts=0
    try:
        while True :
            try:#streamでerrorでたらスルーして再接続する
                x=0
                stream.userstream()#
            except Exception:
                try:
                    auth = get_oauth()
                    api = tweepy.API(auth)
                    dt=datetime.now()
                    message='@自分の垢のscreen_name\n接続切断中、復旧しています。\n%d-%d/%d-%02d:%02d'%(dt.year,dt.month,dt.day,dt.hour,dt.minute)
                    api.update_status(status=message)
                    #print(message)
                except Exception:
                    #pass
                    print('message send error')
            #streaming弾かれたら、再接続
            print('destroy client,reconnect')
            [time.sleep(1) for i in tqdm(range(180))]#tqdmなしならtime.sleep(180)で、ただプログレスバーの安心感
            auth = get_oauth()
            api = tweepy.API(auth)
            stream = tweepy.Stream(auth,StreamListener())
            ts+=1
            if ts==200:
                break
            else:
                pass

        #Nonetypeとか何かのerrorでwhileを出てきたら
        #とりあえず終了をリプ
        try:
            auth = get_oauth()
            api = tweepy.API(auth)
            dt=datetime.now()
            message='@自分のscreen_name\n異常あり、システムを終了しました。\n%d-%d/%d-%02d:%02d'%(dt.year,dt.month,dt.day,dt.hour,dt.minute)
            api.update_status(status=message)
        except Exception:
            pass
        finally:
            j['fav_count']=cnt
            with open('count.txt','w') as f:
                f.write(json.dumps(j_cnt,indent=4))
            print('fin',cnt)

    except KeyboardInterrupt:
        print('Keyborad_Stop')
    #cntを保存
    j_cnt['fav_count']=cnt
    with open('count.txt','w') as f:
        f.write(json.dumps(j_cnt,indent=4))
    print('fin',cnt)
