import re
from datetime import datetime, timedelta

import iso8601
import pytz

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from sqlalchemy import func, and_

from conf import Configuration
from db_models import db, Participant, Candidacy, Election, ValidBallot, \
    InvalidBallot
from utils.permission_control import permission_control

utc = pytz.UTC

app = Flask(__name__)
app.config.from_object(Configuration)
jwt = JWTManager(app)



def is_valid_iso8601_date(date_str):
    try:
        return datetime.fromisoformat(date_str) # doesn't work with arbitrary iso8601
    except:
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            match = re.search(
                r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:?\d{2}$',
                date_str
            )
            if match is not None:
                try:
                    return iso8601.parse_date(date_str)
                except:
                    pass
    return None


def format_missing_field_message(field):
    return 'Field ' + field + ' is missing.'

def create_missing_fields_message(missing_fields):
    return ['Field ' + field + ' is missing.' for field in missing_fields]


@app.route("/createParticipant", methods=["POST"])
@permission_control('admin')
def create_participant():
    if request.json is None:
        missing_fields = ['name', 'individual']
        missing_fields = create_missing_fields_message(missing_fields)
        return jsonify(message=missing_fields), 400


    # Check for missing fields
    # missing_fields = []

    name = request.json.get('name', '')
    if len(name) == 0:
        return jsonify(message=format_missing_field_message('name')), 400
        # missing_fields.append('name')

    individual = request.json.get('individual', '')
    if not isinstance(individual, bool):
        return jsonify(message=format_missing_field_message('individual')), 400
        # missing_fields.append('individual')

    # if len(missing_fields) != 0:
    #     missing_fields = create_missing_fields_message(missing_fields)
    #     return jsonify(message=missing_fields), 400

    participant = Participant(name=name, individual=individual)

    db.session.add(participant)
    db.session.commit()

    return jsonify(id=participant.id), 200


@app.route("/getParticipants", methods=["GET"])
@permission_control('admin')
def get_participants():
    return jsonify(participants=[p.as_dict() for p in Participant.query.all()])


@app.route("/createElection", methods=["POST"])
@permission_control('admin')
def create_election():

    if request.json is None:
        missing_fields = ['start', 'end', 'individual', 'participants']
        missing_fields = create_missing_fields_message(missing_fields)
        return jsonify(message=missing_fields), 400

    start = request.json.get('start', '')
    end = request.json.get('end', '')
    individual = request.json.get('individual', '')
    participants = request.json.get('participants', '')

    if len(start) == 0:
        return jsonify(message=format_missing_field_message('start')), 400
    if (len(end)) == 0:
        return jsonify(message=format_missing_field_message('end')), 400
    if not isinstance(individual, bool):
        return jsonify(message=format_missing_field_message('individual')), 400
    if not isinstance(participants, list):
        return jsonify(message=format_missing_field_message('participants')), 400

    # Validate start and end
    start = is_valid_iso8601_date(start)
    if start is None:
        return jsonify(message='Invalid date and time.'), 400

    end = is_valid_iso8601_date(end)
    if end is None or start > end:
        return jsonify(message='Invalid date and time.'), 400

    start = start.replace(tzinfo=None)
    end = end.replace(tzinfo=None)

    elections = Election.query.all()
    for election in elections:

        # def is_aware(date):
        #     return date.tzinfo is not None and date.tzinfo.utcoffset(date) is not None
        # print("Aware/naive +++++++++++++++++++++++++++++++++++++")
        # print("Is aware ESTART: " + str(is_aware(election.start)))
        # print("Is aware START: " + str(is_aware(start)))
        # try:
        #     print("Is aware LOCALIZED START: " + str(is_aware(utc.localize(start))))
        # except Exception as e:
        #     print('error occured '+  str(e))

        election_start =election.start          #utc.localize(election.start) --- conversion naive -> aware
        election_end =election.end              #utc.localize(election.end)
        if election_start <= start <= election_end \
                or election_start <= end <= election_end \
                or start <= election_start <= end:
            return jsonify(message='Invalid date and time.'), 400

    # Validate participants

    # if len(participants) !=0: participants = list(dict.fromkeys(participants))  # remove duplicates

    if len(participants) < 2:
        return jsonify(message='Invalid participants.'), 400

    for participant_id in participants:
        if Participant.query.filter(
                and_(Participant.id == participant_id, Participant.individual == individual)).first() is None:
            return jsonify(message='Invalid participants.'), 400

    election = Election(start=start, end=end, individual=individual)

    db.session.add(election)
    db.session.commit()

    for poll_number, participant_id in enumerate(participants):
        candidacy = Candidacy(participant_id=participant_id, election_id=election.id, poll_number=poll_number + 1)
        db.session.add(candidacy)
    db.session.commit()

    return jsonify(pollNumbers=[i for i in range(1, len(participants) + 1)]),200


@app.route("/getElections", methods=["GET"])
@permission_control('admin')
def get_elections():
    return jsonify(elections=[e.as_dict() for e in Election.query.all()]), 200


@app.route("/getResults", methods=["GET"])
@permission_control('admin')
def get_results():
    # return "now container: " + str(datetime.now())
    election_id = request.args.get('id')
    if election_id is None or len(election_id) == 0:
        return jsonify(message="Field id is missing."), 400
    election_id = int(election_id)
    election = Election.query.filter(Election.id == election_id).first()
    if election is None:
        return jsonify(message="Election does not exist."), 400
    # tz=pytz.timezone('Europe/Belgrade')
    just_now = datetime.now()+timedelta(seconds=1) # latency
    if just_now < election.end:
        # print('Pokusao da prikupi rezultate tacno u: ' + str(just_now))
        return jsonify(message="Election is ongoing."), 400

    votes = Candidacy.query \
        .filter(Candidacy.election_id == election_id) \
        .join(Participant, Participant.id == Candidacy.participant_id) \
        .outerjoin(ValidBallot, ValidBallot.candidacy_id == Candidacy.id) \
        .group_by(Candidacy.id) \
        .with_entities(Candidacy.poll_number, Participant.name, func.count(ValidBallot.id)) \
        .all()
    # print(votes)
    votes_original = {}
    votes_copy = {}
    for vote in votes:
        votes_original[vote[0]] = {
            "name": vote[1],
            "vote_cnt": vote[2],
        }
        votes_copy[vote[0]] = {
            "vote_cnt": vote[2]
        }

    total = sum([value['vote_cnt'] for value in votes_copy.values()])
    # print('total == ' + str(total))
    if election.individual and total != 0:
        for vote in votes_copy.values():
            vote['result'] = round(vote['vote_cnt'] / total, 2)
    else:
        for vote in votes_copy.values():
            vote['result'] = 0
        if not election.individual and total!=0:
            census = 0.05 * total
            # Remove the ones who didn't pass census
            to_delete = []
            # print(len(votes_copy.keys()))
            for key, val in votes_copy.items():
                if val['vote_cnt'] < census:
                    to_delete.append(key)
            for key in to_delete:
                del votes_copy[key]
            # print(len(votes_copy.keys()))

            # Calculate results (number of seats)
            n_seats = 250
            while sum([vote['result'] for vote in votes_copy.values()]) < n_seats:
                max_votes = max([vote['vote_cnt'] for vote in votes_copy.values()])
                next_seat = list(votes_copy.keys())[[vote['vote_cnt'] for vote in votes_copy.values()].index(max_votes)]
                votes_copy[next_seat]['result'] += 1
                votes_copy[next_seat]['vote_cnt'] = votes_original[next_seat]['vote_cnt'] / (votes_copy[next_seat]['result'] + 1)

    # Format result
    participants= [{"pollNumber":key,"name":val["name"],"result":votes_copy[key]['result'] if key in votes_copy.keys() else 0} for key,val in votes_original.items()]
    invalid_votes = InvalidBallot.query.filter(InvalidBallot.election_id == election_id).all()

    return jsonify(participants=participants, invalidVotes=[invalid_vote.as_dict() for invalid_vote in invalid_votes]), 200


@app.route("/", methods=["GET"])
def index():
    return "Hello world!"


if __name__ == "__main__":
    db.init_app(app)
    app.run(debug=True, host="0.0.0.0", port=5002)
