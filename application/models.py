from .database import db

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String)
    user_name = db.Column(db.String)
    user_pwd = db.Column(db.String)
    user_status = db.Column(db.String)

class Campaign(db.Model):
    __tablename__ = 'campaign'
    spon_name = db.Column(db.String, db.ForeignKey('sponsor.s_name'))
    c_id = db.Column(db.Integer, primary_key=True)
    c_name = db.Column(db.String)
    c_desc = db.Column(db.String)
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)
    c_budget = db.Column(db.Integer)
    c_goals = db.Column(db.String)
    sponsor = db.relationship('Sponsor', backref=db.backref('campaigns', lazy=True))



class Adreq(db.Model):
    __tablename__ = 'adreq'
    reqid = db.Column(db.Integer, primary_key=True)
    spon_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.c_id'))
    campaign_name = db.Column(db.String, db.ForeignKey('campaign.c_name'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'))
    influencer_name = db.Column(db.String, db.ForeignKey('influencer.i_name'))
    messages = db.Column(db.String)
    requirements = db.Column(db.String)
    fee_amount = db.Column(db.Integer)
    counter_amount = db.Column(db.Integer)
    status = db.Column(db.String)




class Influencer(db.Model):
    __tablename__ = 'influencer'
    id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    i_name = db.Column(db.String)
    i_category = db.Column(db.String)
    i_niche = db.Column(db.String)
    i_reach = db.Column(db.Integer)
    i_about = db.Column(db.String)
    

class Sponsor(db.Model):
    __tablename__ = 'sponsor'
    id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    s_name = db.Column(db.String)
    s_industry = db.Column(db.String)
    s_budget = db.Column(db.Integer)
    s_about = db.Column(db.String)