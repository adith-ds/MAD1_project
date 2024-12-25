from flask import Flask, render_template, redirect, url_for, request
from flask import current_app as app
from .models import *
from datetime import datetime
import requests

API_URL = 'http://127.0.0.1:5000/api'

#home page
@app.route('/')
def home():
    return render_template('index.html')

#login for sponsors
@app.route('/splog', methods=['GET', 'POST'])
def sponsor_login():
    if request.method == 'GET':
        return render_template('splogin.html')
    else:
        name = request.form['u_name'].strip()
        pwd = request.form['u_pwd']
        spon = User.query.filter_by(user_name=name, user_pwd=pwd, user_type = 'sponsor').first()
        if spon is None:
            return redirect(url_for('invalid_details'))
        else:
            if spon.user_status == 'flagged':
                return render_template('flagged.html')
            else:
                return redirect(url_for('sponsor', sid=spon.user_id))        



#login for influencers
@app.route('/inflog', methods=['GET', 'POST'])
def inf_login():
    if request.method == 'GET':
        return render_template('inflogin.html')
    else:
        name = request.form['u_name'].strip()
        pwd = request.form['u_pwd']
        inf = User.query.filter_by(user_name=name, user_pwd=pwd, user_type = 'influencer').first()
        if inf is None:
            return redirect(url_for('invalid_details'))
        else:
            if inf.user_status == 'flagged':
                return render_template('flagged.html')
            else:
                return redirect(url_for('influencer', iid=inf.user_id))
        


#login for admins
@app.route('/adlog', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('adlogin.html')
    else:
        name = request.form['u_name'].strip()
        pwd = request.form['u_pwd']
        mod = User.query.filter_by(user_name=name, user_pwd=pwd, user_type = 'admin').first()
        if mod is None:
            return redirect(url_for('invalid_details'))
        else:
            return redirect(url_for('admin'))


#invalid details entered page
@app.route('/inv')
def invalid_details():
    return render_template('invalid.html')

#username already exists page
@app.route('/alr')
def already():
    return render_template('already.html')



#influencer register page 
@app.route('/infreg', methods=['GET', 'POST'])
def inf_register():
    if request.method == 'GET':
        return render_template('infregister.html')
    else:
        name = request.form['username'].strip()
        alias = request.form['alias']
        category = request.form['category']
        niche = request.form['niche']
        reach = request.form['reach']
        reacher = {'0':5000, '1':50000, '2':200000, '3':500000, '4':1000000, '5':5000000, '6':10000000}
        about = request.form['about']
        password =  request.form['password']
        check = User.query.filter_by(user_name=name).first()
        if check:
            return redirect(url_for('already'))
        newuser = User(user_type = 'influencer', user_name = name, user_pwd = password)
        db.session.add(newuser)
        db.session.commit()
        newinf = Influencer(id = newuser.user_id, i_name = alias, i_category = category, i_niche = niche, i_reach = reacher[reach], i_about = about )
        db.session.add(newinf)
        db.session.commit()
        return redirect(url_for('inf_login'))        


#sponsor register page
@app.route('/spreg', methods=['GET', 'POST'])
def sponsor_register():
    if request.method == 'GET':
        return render_template('spregister.html')
    else:
        name = request.form['username'].strip()
        industry = request.form['industry']
        budget = request.form['budget']
        about = request.form['about']
        password =  request.form['password']
        check = User.query.filter_by(user_name=name).first()
        if check:
            return redirect(url_for('already'))
        newuser = User(user_type = 'sponsor', user_name = name, user_pwd = password)
        db.session.add(newuser)
        db.session.commit()
        newspon = Sponsor(id = newuser.user_id, s_name = name, s_industry = industry, s_budget = budget, s_about = about)
        db.session.add(newspon)
        db.session.commit()
        return redirect(url_for('sponsor_login'))


    
#sponsor home page
@app.route('/sponsor/<sid>', methods=['GET', 'POST'])
def sponsor(sid):
    spon = Sponsor.query.filter_by(id=sid).first()
    return render_template('sponsor.html', sponsor=spon)

#sponsor page for ad requests
@app.route('/spreqlist/<sid>')
def spreqlist(sid):
    spon = Sponsor.query.filter_by(id=sid).first()
    sentreqs = Adreq.query.filter_by(spon_id=sid, status="sent").all()
    coreqs = Adreq.query.filter_by(spon_id=sid, status="countered").all()
    rejreqs = Adreq.query.filter_by(spon_id=sid, status="rejinf").all()
    accreqs = Adreq.query.filter_by(spon_id=sid, status="accepted").all()
    return render_template('spreqlist.html', s = sentreqs, c = coreqs, r = rejreqs, a = accreqs, sponsor=spon)


#sponsor page to look for influencer
@app.route('/findinf/<sid>', methods=['GET', 'POST'])
def find_inf(sid):
    if request.method == 'GET':
        spon = Sponsor.query.filter_by(id=sid).first()
        influencers =  Influencer.query.all()
        return render_template('findinf.html', sponsor=spon, infs = influencers)
    else:
        spon = Sponsor.query.filter_by(id=sid).first()
        query= Influencer.query
        name = request.form['name'].strip()
        category = request.form['category']
        reach = request.form['reach']
        if name:
            query= query.filter(Influencer.i_name.ilike(f'%{name}%'))
        if category:
            query= query.filter(Influencer.i_category == category)
        if reach:
            query= query.filter(Influencer.i_reach == reach)
        influencers = query.all()
        return render_template('findinf.html', sponsor=spon, infs = influencers)




#make an ad request
@app.route('/makereq/<sid>/<iid>', methods=['GET', 'POST'])
def make_req(sid, iid):
    if request.method == 'GET':
        spon = Sponsor.query.filter_by(id=sid).first()
        inf =  Influencer.query.filter_by(id=iid).first()
        return render_template('makereq.html', sponsor=spon, influencer = inf)
    else:
        spon = Sponsor.query.filter_by(id=sid).first()
        inf =  Influencer.query.filter_by(id=iid).first()
        cid = request.form['campaignid']
        messages = request.form['messages']
        requirements = request.form['requirements']
        fee = request.form['fee']
        camp = Campaign.query.filter_by(c_id=cid).first()
        newreq = Adreq(spon_id = sid, campaign_id = cid, campaign_name = camp.c_name, influencer_id = iid, influencer_name = inf.i_name, messages = messages, requirements = requirements, fee_amount = fee, status="sent")
        db.session.add(newreq)
        db.session.commit()
        return redirect(url_for('find_inf', sid = sid))

#update ad request
@app.route('/updatereq/<reqid>', methods=['GET', 'POST'])
def update_adreq(reqid):
    if request.method == 'GET':
        thisreq = Adreq.query.filter_by(reqid=reqid).first()
        return render_template('spupreq.html', req = thisreq)
    else:
        thisreq = Adreq.query.filter_by(reqid=reqid).first()
        thisreq.messages = request.form['messages']
        thisreq.requirements = request.form['requirements']
        thisreq.fee_amount = request.form['fee']
        db.session.commit()
        return redirect(url_for('spreqlist', sid=thisreq.spon_id))
    

#counter ad req - spon
@app.route('/scounter/<reqid>', methods=['GET', 'POST'])
def scounter(reqid):
    if request.method == 'GET':
        thisreq = Adreq.query.filter_by(reqid=reqid).first()
        return render_template('spcounter.html', req = thisreq)
    else:
        c = request.form['counter']
        thisreq = Adreq.query.filter_by(reqid=reqid).first()
        thisreq.fee_amount = c
        thisreq.status = "sent"
        db.session.commit()
        return redirect(url_for('spreqlist', sid=thisreq.spon_id))

#delete ad request - sponsor
@app.route('/sprejreq/<reqid>', methods=['GET', 'POST'])
def sprej(reqid):
    thisreq = Adreq.query.filter_by(reqid=reqid).first()
    thisreq.status = "rejspon"
    db.session.commit()
    return redirect(url_for('spreqlist', sid = thisreq.spon_id))

#delete a campaign
@app.route('/deletecampaign/<campid>', methods=['GET', 'POST'])
def delete_campaign(campid):
    thiscamp = Campaign.query.filter_by(c_id=campid).first()
    sname = thiscamp.spon_name
    spon = Sponsor.query.filter_by(s_name=sname).first()
    sid = spon.id
    adreqs = Adreq.query.filter_by(campaign_id=campid).all()
    db.session.delete(thiscamp)
    for ad in adreqs:
        db.session.delete(ad)
    db.session.commit()
    return redirect(url_for('sponsor', sid = sid))


#update a campaign
@app.route('/updatecampaign/<campid>', methods=['GET', 'POST'])
def update_campaign(campid):
    if request.method == 'GET':
        camp = Campaign.query.filter_by(c_id=campid).first()
        return render_template('updatecamp.html', campaign=camp)
    else:
        camp = Campaign.query.filter_by(c_id=campid).first()
        camp.c_desc = request.form['desc']
        camp.c_budget = request.form['budget']
        camp.c_goals = request.form['goals']
        db.session.commit()
        spon = Sponsor.query.filter_by(s_name = camp.spon_name).first()
        return redirect(url_for('sponsor', sid = spon.id))


#create a campaign
@app.route('/createcampaign/<spon_name>', methods=['GET', 'POST'])
def create_campaign(spon_name):
    if request.method == 'GET':
        return render_template('createcamp.html', sname=spon_name)
    else:
        name = request.form['name']
        desc = request.form['desc']
        sdate = request.form['sdate']
        sobj = datetime.strptime(sdate, '%Y-%m-%d')
        snew = sobj.strftime('%d-%B-%Y')
        edate = request.form['edate']
        eobj = datetime.strptime(edate, '%Y-%m-%d')
        enew = eobj.strftime('%d-%B-%Y')
        budget = request.form['budget']
        goals = request.form['goals']
        newcamp = Campaign(spon_name = spon_name, c_name = name, c_desc = desc, start_date = snew, end_date = enew, c_budget = budget, c_goals = goals)
        db.session.add(newcamp)
        db.session.commit()
        spon = Sponsor.query.filter_by(s_name=spon_name).first()
        return redirect(url_for('sponsor', sid=spon.id))


#influencer home page 
@app.route('/influencer/<iid>', methods=['GET', 'POST'])
def influencer(iid):
    thisinf = Influencer.query.filter_by(id=iid).first()
    sentreqs = Adreq.query.filter_by(influencer_id=iid, status="sent").all()
    rejreqs = Adreq.query.filter_by(influencer_id=iid, status="rejspon").all()
    accreqs = Adreq.query.filter_by(influencer_id=iid, status="accepted").all()
    return render_template('infhome.html', inf = thisinf, s = sentreqs, r = rejreqs, a = accreqs)


#counter ad req - inf
@app.route('/counter/<reqid>', methods=['GET', 'POST'])
def counter_req(reqid):
    if request.method == 'GET':
        thisreq = Adreq.query.filter_by(reqid=reqid).first()
        return render_template('infcounter.html', req = thisreq)
    else:
        c = request.form['counter']
        thisreq = Adreq.query.filter_by(reqid=reqid).first()
        thisreq.counter_amount = c
        thisreq.status = "countered"
        db.session.commit()
        return redirect(url_for('influencer', iid=thisreq.influencer_id))




#reject ad req - inf
@app.route('/infrejreq/<reqid>', methods=['GET', 'POST'])
def infrej(reqid):
    thisreq = Adreq.query.filter_by(reqid=reqid).first()
    thisreq.status = "rejinf"
    db.session.commit()
    return redirect(url_for('influencer', iid = thisreq.influencer_id))


#view campaigns
@app.route('/findcampaigns/<iid>', methods=['GET', 'POST'])
def viewcamps(iid):
    if request.method == 'GET':
        thisinf = Influencer.query.filter_by(id=iid).first()
        sponsors = Sponsor.query.all()
        campaigns = Campaign.query.all()
        return render_template('findcamps.html', inf=thisinf, spons=sponsors, camps=campaigns )
    else:
        thisinf = Influencer.query.filter_by(id=iid).first()
        sponsors = Sponsor.query.all()
        query= Campaign.query
        name = request.form['name'].strip()
        spon = request.form['company']
        budget = request.form['budget']
        if name:
            query= query.filter(Campaign.c_name.ilike(f'%{name}%'))
        if spon:
            query= query.filter(Campaign.spon_name == spon)
        if budget:
            query= query.filter(Campaign.c_budget >= budget)
        campaigns = query.all()
        return render_template('findcamps.html', inf=thisinf, spons=sponsors, camps=campaigns )
    

#view profile
@app.route('/profile/<iid>', methods=['GET', 'POST'])
def profile(iid):
    thisinf = Influencer.query.filter_by(id=iid).first()
    return render_template('profile.html', inf = thisinf)

#edit profile
@app.route('/editprofile/<iid>', methods=['GET', 'POST'])
def editprof(iid):
    if request.method == 'GET':
        thisinf = Influencer.query.filter_by(id=iid).first()
        return render_template('editprof.html', inf = thisinf)
    else:
        thisinf = Influencer.query.filter_by(id=iid).first()
        thisinf.i_name = request.form['alias']
        thisinf.i_category = request.form['category']
        thisinf.i_niche = request.form['niche']
        thisinf.i_reach = request.form['reach']
        thisinf.i_about = request.form['about']
        db.session.commit()
        return redirect(url_for('profile', iid=thisinf.id))



#accept ad req - sponsor and influencer
@app.route('/accept/<id>/<reqid>', methods=['GET', 'POST'])
def accept_adreq(id, reqid):
    thisreq = Adreq.query.filter_by(reqid=reqid).first()
    thisreq.status = "accepted"
    user = User.query.filter_by(user_id=id).first()
    if user.user_type == "sponsor":
        thisreq.fee_amount = thisreq.counter_amount
        db.session.commit()
        return redirect(url_for('sponsor', sid = id))
    else:
        db.session.commit()
        return redirect(url_for('influencer', iid = id))
    



#admin page
@app.route('/admin')
def admin():
    if request.method == 'GET':
        #query = request.args.get('query')
        response = requests.get(f'{API_URL}/data')
        data = response.json()
        return render_template('admin.html', data = data)

#admin displaying stuff
@app.route('/admin/<type>')
def display_list(type):
    if type == 'sponsor':
        response = requests.get(f'{API_URL}/{type}')
        sponsors = response.json()
        return render_template('adminstats.html', spons = sponsors)
        
    elif type == 'influencer':
        response = requests.get(f'{API_URL}/{type}')
        influencers = response.json()
        return render_template('adminstats.html', infs = influencers)
    elif type == 'adreq':
        response = requests.get(f'{API_URL}/{type}')
        ads = response.json()
        return render_template('adminstats.html', reqs = ads)
    elif type == 'campaign':
        response = requests.get(f'{API_URL}/{type}')
        campaigns = response.json()
        return render_template('adminstats.html', camps = campaigns)
    
#flagged user list
@app.route('/admin/flags', methods=['GET', 'POST'])
def flaglist():
    if request.method == 'GET':
        response = requests.get(f'{API_URL}/flaglist')
        data = response.json()
        return render_template('flaglist.html', data = data)
    else:
        action = request.form['action']
        id = request.form['id']
        update = requests.post(f'{API_URL}/action/{action}/{id}')
        response = requests.get(f'{API_URL}/flaglist')
        data = response.json()
        return render_template('flaglist.html', data = data)
