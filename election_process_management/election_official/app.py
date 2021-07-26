import csv
import io
import json

from flask import Flask, request, jsonify, Response
from flask_jwt_extended import get_jwt, JWTManager
from redis import Redis
from conf import Configuration
from utils.permission_control import permission_control

app = Flask(__name__)
app.config.from_object(Configuration)
jwt = JWTManager(app)


@app.route("/vote", methods=["POST"])
@permission_control('election_official')
def vote():
    file = request.files.get('file')
    if file is None:
        return jsonify(message='Field file is missing.'), 400

    additional_claims = get_jwt()
    election_official_jmbg = additional_claims['jmbg']

    content = file.stream.read().decode("utf-8")
    stream = io.StringIO(content)
    csv_reader = csv.reader(stream)

    votes = []
    for i, ballot in enumerate(csv_reader):
        if len(ballot) != 2:
            return jsonify(message='Incorrect number of values on line ' + str(i) + '.'), 400
        try:
            ballot[1] = int(ballot[1])
        except:
            return jsonify(message='Incorrect poll number on line ' + str(i) + '.'), 400
        if ballot[1] <= 0:
            return jsonify(message='Incorrect poll number on line ' + str(i) + '.'), 400

        ballot = {
            "guid":ballot[0],
            "poll_number":ballot[1]
        }
        votes.append(ballot)

    votes_batch = {
        "election_official_jmbg":election_official_jmbg,
        "votes":votes
    }

    with Redis(host=Configuration.REDIS_HOST) as redis:
        redis.publish(Configuration.REDIS_VOTE_CHANNEL, json.dumps(votes_batch))

    # for ballot in votes: # TODO dodati lpop kod Daemon kontejnera
    #     with Redis(host=Configuration.REDIS_HOST) as redis:
    #         redis.rpush(Configuration.REDIS_VOTE_LIST, ballot);
    return Response(status=200)

@app.route("/", methods=["GET"])
def index():
    return "Hello world!"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5003)
