import json
from datetime import datetime, timedelta
import pytz

from flask import Flask
from redis import Redis
from sqlalchemy import and_

from conf import Configuration
from db_models import Election, Ballot, InvalidBallot, db, Candidacy, ValidBallot

app = Flask(__name__)
app.config.from_object(Configuration)
db.init_app(app)


def is_duplicate(ballots, guid):
    return next(filter(lambda ballot: ballot.guid == guid, ballots), None) is not None \
           or Ballot.query.filter(Ballot.guid == guid).first() is not None


with app.app_context() as context:

    with Redis(host=Configuration.REDIS_HOST, port=6379, db=0) as r:

        pubsub = r.pubsub()
        pubsub.subscribe(Configuration.REDIS_VOTE_CHANNEL)

        while True:
            message = pubsub.get_message()
            if message and not message['data'] == 1:

                just_now = datetime.now() + timedelta(seconds=1) #latency

                r.publish("x", "Pokusao da glasa:" + str(just_now))
                election = Election.query \
                    .filter(and_(Election.start < just_now, just_now < Election.end)) \
                    .first()
                if election is not None:
                    r.publish("x", "Pronasao izbore")
                    votes_batch = json.loads(message['data'].decode('utf-8'))
                    election_official_jmbg = votes_batch.get('election_official_jmbg')

                    ballots = []

                    for vote in votes_batch.get('votes'):
                        verified_ballot = None
                        guid = vote.get('guid')
                        if is_duplicate(ballots, guid):
                            verified_ballot = InvalidBallot(guid=guid,
                                                            election_official_jmbg=election_official_jmbg,
                                                            poll_number=vote.get('poll_number'),
                                                            election_id=election.id,
                                                            reason='Duplicate ballot.')
                            r.publish("x", 'kreirao duplikejt')

                        else:
                            candidacy = Candidacy.query \
                                .filter(
                                and_(Candidacy.election_id == election.id,
                                     Candidacy.poll_number == vote.get('poll_number'))) \
                                .first()

                            if candidacy is None:
                                verified_ballot = InvalidBallot(guid=guid,
                                                                election_official_jmbg=election_official_jmbg,
                                                                poll_number=vote.get('poll_number'),
                                                                election_id=election.id,
                                                                reason='Invalid poll number.')
                                r.publish("x", 'kreirao invalid poll')

                            else:
                                verified_ballot = ValidBallot(guid=guid,
                                                              election_official_jmbg=election_official_jmbg,
                                                              candidacy_id=candidacy.id)
                                r.publish("x", 'kreirao valid')

                        ballots.append(verified_ballot)
                    db.session.add_all(ballots)
                    # db.session.add(verified_ballot)
                    db.session.commit()
                    r.publish("x", "Stavio u bazu")

                    # Optimization -> Put ballots in array, commit afterwards
