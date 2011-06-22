from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
from auth import getauth,OAuth,OAuthCallback,OAuthLogout
import tweepy

datatmp=None

class MainPage(webapp.RequestHandler):
  def get(self):
    if users.get_current_user() is None:
      url = users.create_login_url(self.request.uri)
      self.response.out.write("<a href='"+url+"'>Google Login</a>\n")
    else:
      self.redirect('/home')
      
class Friend(db.Model):
  name = db.StringProperty()
  link = db.StringListProperty()

class Find(webapp.RequestHandler):
  def post(self):
    if(datatmp):
        datatmp.put()
    self.redirect('/home')
      
class Home(webapp.RequestHandler):
  def get(self):    
    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      self.response.out.write("<a href='"+url+"'>Google Logout</a>\n")
    else:
      self.redirect('/')
    auth=getauth()
    if auth:
      self.response.out.write("<a href='/oauth_logout'>OAuth Logout</a><br /><br />\n")
      if tweepy.API(auth).test():
        link=[]
        user_name=users.get_current_user()
        #temp=tweepy.API(auth).followers()
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
        global datatmp
        for j in tmp:
          datatmp=j
          find=j.link;
        if(not datatmp):
            datatmp=Friend()
        datatmp.name='__%s'%user_name
        datatmp.link=link
        l0=len(link)
        l1=len(find)
        #l0=tweepy.API(auth).get_user(user_name).followers_count;
        #self.response.out.write(tweepy.API(auth).get_user(user_name).followers_count);
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
        self.response.out.write('<p><font color="#FF0000">new %d unfo:</font></p>'%len(s2))
        for i in s2:
            self.response.out.write(i+'</br>')
        self.response.out.write('<p><font color="#FF0000">new %d fo:</font></p>'%len(s1))
       # for i in s1:
       #     self.response.out.write(i+'</br>')
        self.response.out.write("""
          <form action="/set" method="post">
            <div><input type="submit" value="set"></div>
          </form>
        </body>
        when you push the set button,it will record your followers's list
        </br>
        and show the difference from the record and the current list 
      </html>""")          
      else:
        self.response.out.write('OAuth Error.<br />\n')
    else:
      self.response.out.write("<a href='/auth'>OAuth Login</a>\n")


application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/home', Home),
  ('/auth', OAuth),
  ('/callback', OAuthCallback),
  ('/oauth_logout', OAuthLogout),
  ('/set', Find)
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
