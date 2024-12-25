from flask_restful import Resource
from .database import db
from .models import *





class myAPI(Resource):
    def get(self):
        itotal = Influencer.query.count()
        sports = Influencer.query.filter_by(i_category = 'sports').count()
        fashion = Influencer.query.filter_by(i_category = 'fashion').count()
        travel = Influencer.query.filter_by(i_category = 'travel').count()
        gym = Influencer.query.filter_by(i_category = 'gym').count()
        gaming = Influencer.query.filter_by(i_category = 'gaming').count()
        inf = {'total' : itotal, 's' : sports, 'f' : fashion, 't' : travel, 'g' : gym, 'ga' : gaming}

        ctotal = Campaign.query.count()
        low = Campaign.query.filter(Campaign.c_budget < 1000).count()
        high = Campaign.query.filter(Campaign.c_budget > 999).count()
        camp = {'total' : ctotal, 'l' : low, 'h' : high}

        atotal = Adreq.query.count()
        acc = Adreq.query.filter_by(status = 'accepted').count()
        neg1 = Adreq.query.filter_by(status = 'sent').count()
        neg2 = Adreq.query.filter_by(status = 'countered').count()
        neg = neg1+neg2
        sponrej = Adreq.query.filter_by(status = 'rejspon').count()
        infrej = Adreq.query.filter_by(status = 'rejinf').count()
        adreq = {'total' : atotal, 'a' : acc, 'n' : neg, 'rs' : sponrej, 'ri' : infrej}

        data = {'inf' : inf, 'camp' : camp, 'adreq' : adreq }
        return data
    

class listAPI(Resource):
    def get(self, type):
        if type == 'sponsor':
            spons = Sponsor.query.all()
            sponsors = [{'id' : s.id, 'name' : s.s_name, 'budget' : s.s_budget} for s in spons]
            return sponsors
        if type == 'campaign':
            camps = Campaign.query.all()
            campaigns = [{'id' : c.c_id, 'name' : c.c_name, 'sponsor' : c.spon_name} for c in camps]
            return campaigns
        if type == 'adreq':
            reqs = Adreq.query.all()
            adreqs = [{'id' : ad.reqid, 'inf' : ad.influencer_name, 'campaign' : ad.campaign_name} for ad in reqs]
            return adreqs
        if type == 'influencer':
            infs = Influencer.query.all()
            influencers = [{'id' : i.id, 'name' : i.i_name, 'reach' : i.i_reach} for i in infs]
            return influencers
        

class flagAPI(Resource):
    def get(self):
        fusrs = User.query.filter_by(user_status = 'flagged').all()
        fusers = [{'id' : u.user_id, 'name' : u.user_name, 'type': u.user_type} for u in fusrs]
        goodusers = User.query.filter(User.user_status.is_(None)).all()
        infs = []
        spons = []
        for u in goodusers:
            if u.user_type == 'influencer':
                inf = Influencer.query.filter_by(id = u.user_id).first()
                thisinf = {'id' : inf.id, 'name' : u.user_name, 'about': inf.i_about}
                infs.append(thisinf)
            if u.user_type == 'sponsor':
                spon = Sponsor.query.filter_by(id = u.user_id).first()
                thispon = {'id' : spon.id, 'name' : u.user_name, 'about': spon.s_about}
                spons.append(thispon)
        data = {'flagged' : fusers, 'infs' : infs, 'spons' : spons}
        return data
    
    def post(self, action, id):
        if action == 'flag':
            thisuser = User.query.filter_by(user_id = id).first()
            thisuser.user_status = 'flagged'
            db.session.commit()
            return 200
        if action == 'unflag':
            thisuser = User.query.filter_by(user_id = id).first()
            thisuser.user_status = None
            db.session.commit()
            return 200