from google.appengine.ext import db
from google.appengine.api import users
import time
import tweepy

class Friend(db.Model):
    login_name = db.StringProperty()
    name = db.StringProperty()
    link = db.StringListProperty()
    
class Show(db.Model):
    name=db.StringProperty()
    fo=db.StringListProperty()
    unfo=db.StringListProperty()
  
class Diff():
    def __init__(self,auth,user_name,mark,clear=0,login_name=users.get_current_user()):
        login_name=str(login_name)
        tmp=db.GqlQuery('SELECT * FROM Show WHERE name=:1',user_name)
        showtmp=[]
        for j in tmp:
            showtmp=j
        if(not showtmp):
            showtmp=Show()
        showtmp.name=user_name
        if(clear):
            showtmp.fo=[]
            showtmp.unfo=[]
            showtmp.put()
            return
        link=[]
        tmp0=tweepy.API(auth).followers(screen_name=user_name,cursor=-1)
        for i in tmp0[0]:
            link.append(i.screen_name)
        while(tmp0[1][1]):
            cur=tmp0[1][1]
            tmp0=tweepy.API(auth).followers(screen_name=user_name,cursor=cur)
            for i in tmp0[0]:
                link.append(i.screen_name)
        find=[]
        tmp=db.GqlQuery('SELECT * FROM Friend WHERE name=:1',user_name)
        datatmp=[]
        for j in tmp:
            datatmp=j
            find=j.link
        if(not datatmp):
            datatmp=Friend()
        datatmp.login_name=login_name    
        datatmp.name=user_name
        datatmp.link=link
        l0=len(link)
        l1=len(find)
        find.sort()
        link.sort()
        i0=0
        i1=0
        s1=[]
        s2=[]
        while i0<l0 or i1<l1:
            if(i0==l0):
                s2.append(find[i1])
                i1+=1
            elif(i1==l1):
                s1.append(link[i0])
                i0+=1
            else:
                if(link[i0]==find[i1]):
                    i0+=1
                    i1+=1
                elif(link[i0]<find[i1]):
                    s1.append(link[i0])
                    i0+=1
                else:
                    s2.append(find[i1])
                    i1+=1
        if(mark):
            datatmp.put()
        self.fo=s1
        self.unfo=s2
        nowtime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        for j in s1:
            showtmp.fo.append(('%s  '%j)+nowtime)
        for j in s2:
            showtmp.unfo.append(('%s  '%j)+nowtime)
        showtmp.put()
        