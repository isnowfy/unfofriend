from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import mail
import time
import tweepy

class Friend(db.Model):
    login_name=db.StringProperty()
    name=db.StringProperty()
    link=db.StringListProperty()
    
class Show(db.Model):
    name=db.StringProperty()
    fo=db.StringListProperty()
    unfo=db.StringListProperty()
    
class Email(db.Model):
    name=db.StringProperty()
    timezone=db.IntegerProperty()
    email=db.StringProperty()
    fo=db.BooleanProperty()
    
def getemail(name):
    tmp=db.GqlQuery('SELECT * FROM Email WHERE name=:1',name)
    showtmp=tmp.get()
    if not showtmp:
        showtmp=Email()
    return showtmp
  
class Diff():
    def __init__(self,auth,user_name,mark,clear=0,login_name=users.get_current_user()):
        login_name=str(login_name)
        tmp=db.GqlQuery('SELECT * FROM Show WHERE name=:1',user_name)
        showtmp=tmp.get()
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
        tmp=db.GqlQuery('SELECT * FROM Friend WHERE name=:1',user_name)
        datatmp=tmp.get()
        if(not datatmp):
            datatmp=Friend()
        find=datatmp.link
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
        tmp=getemail(login_name)
        delta=0
        if tmp.timezone:
            delta=tmp.timezone
        nowtime=time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(time.time()+delta*3600))
        for j in s1:
            showtmp.fo.append(j+"@"+nowtime)
        for j in s2:
            showtmp.unfo.append(j+"@"+nowtime)
        showtmp.put()
        if(len(self.unfo)>0 and tmp.email):
            somebody=""
            body="<html><head></head><body><div>Hi %s,<br><br> the people below are no longer following you<br><table>"%login_name
            for j in self.unfo:
                somebody=j
                body+="<tr><td><a href=\"http://twitter.com/"+j+"\">"+j+"</a></td><td>"+nowtime+"</td></tr>"
            body+=""" 
            </table><br><br>
            Your follow/unfollow history here:<a href="https://unfofriend.appspot.com/home">https://unfofriend.appspot.com/home</a>
            <br><br>
            <span><font color="#888888"><br>--<br>
            Powerd by <a href="https://unfofriend.appspot.com" target="_blank">unfofriend.appspot.com</a><br>
            </font></span>
            </div></body></html>
            """
            message=mail.EmailMessage(sender="a3214668848@gmail.com",subject="unfofriend.appspot.com:%s unfollowed you"%somebody,to=tmp.email)
            message.html=body
            message.send()
        if(len(self.fo)>0 and tmp.email and tmp.fo):
            somebody=""
            body="<html><head></head><body><div>Hi %s,<br><br> the people below start to follow you<br><table>"%login_name
            for j in self.fo:
                somebody=j
                body+="<tr><td><a href=\"http://twitter.com/"+j+"\">"+j+"</a></td><td>"+nowtime+"</td></tr>"
            body+=""" 
            </table><br><br>
            Your follow/unfollow history here:<a href="https://unfofriend.appspot.com/home">https://unfofriend.appspot.com/home</a>
            <br><br>
            <span><font color="#888888"><br>--<br>
            Powerd by <a href="https://unfofriend.appspot.com" target="_blank">unfofriend.appspot.com</a><br>
            </font></span>
            </div></body></html>
            """
            message=mail.EmailMessage(sender="a3214668848@gmail.com",subject="unfofriend.appspot.com:%s followed you"%somebody,to=tmp.email)
            message.html=body
            message.send()
        