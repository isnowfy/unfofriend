from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
import tweepy

class Friend(db.Model):
    name = db.StringProperty()
    link = db.StringListProperty()
  
class Diff():
    def __init__(self,auth,user_name,mark):
        link=[]
        num=tweepy.API(auth).get_user(user_name).followers_count
        tmp0=tweepy.API(auth).followers(screen_name=user_name,cursor=-1)
        for i in tmp0[0]:
            link.append(i.screen_name)
        while(tmp0[1][1]):
            cur=tmp0[1][1]
            tmp0=tweepy.API(auth).followers(screen_name=user_name,cursor=cur)
            for i in tmp0[0]:
                link.append(i.screen_name)
        find=[]
        tmp=db.GqlQuery('SELECT * FROM Friend WHERE name=:1','__%s'%user_name)
        for j in tmp:
            find=j.link
        datatmp=Friend()
        datatmp.name='__%s'%user_name
        datatmp.link=link
        l0=len(link)
        l1=len(find)
        self.response.out.write('ever %d followers now %d followers'%(l1,l0))
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