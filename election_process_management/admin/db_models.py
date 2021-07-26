from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Candidacy(db.Model):
    __tablename__ = "candidacy"

    id = db.Column(db.Integer, primary_key=True)

    participant_id = db.Column(db.Integer, db.ForeignKey("participant.id"), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey("election.id"), nullable=False)
    poll_number = db.Column(db.Integer, nullable=False)


class Participant(db.Model):
    __tablename__ = "participant"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(256), nullable=False)
    individual = db.Column(db.Boolean, nullable=False)

    elections = db.relationship("Election", secondary=Candidacy.__table__, back_populates="participants")

    def as_dict(self):
        return {
            "id":self.id,
            "name":self.name,
            "individual":self.individual
        }



class Election(db.Model):
    __tablename__ = "election"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    start = db.Column(db.DateTime, nullable=False, unique=True)
    end = db.Column(db.DateTime, nullable=False, unique=True)
    individual = db.Column(db.Boolean, nullable=False)

    participants = db.relationship("Participant", secondary=Candidacy.__table__, back_populates="elections")

    def as_dict(self):
        return {
            "id": self.id,
            "start": str(self.start),
            "end": str(self.end),
            "individual": self.individual,
            "participants": [{"id":p.id, "name":p.name} for p in self.participants]
        }



class Ballot(db.Model):
    __tablename__ = 'ballot'

    id = db.Column(db.Integer, primary_key=True)

    election_official_jmbg = db.Column(db.String(13), nullable=False)
    guid = db.Column(db.String(36), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'ballot',
    }


class ValidBallot(Ballot):
    __tablename__ = 'valid_ballot'

    id = db.Column(db.Integer, db.ForeignKey('ballot.id'), primary_key=True)
    candidacy_id = db.Column(db.Integer, db.ForeignKey('candidacy.id'))

    __mapper_args__ = {
        'polymorphic_identity': 'invalid_ballot'
    }


class InvalidBallot(Ballot):
    __tablename__ = 'invalid_ballot'

    id = db.Column(db.Integer, db.ForeignKey('ballot.id'), primary_key=True)

    poll_number = db.Column(db.Integer, nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey("election.id"), nullable=False)
    reason = db.Column(db.String(256), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'invalid_ballot'
    }
    def as_dict(self):
        return {
            "electionOfficialJmbg": self.election_official_jmbg,
            "ballotGuid": self.guid,
            "pollNumber": self.poll_number,
            "reason": self.reason,
        }
