## Election Process Management System

A system of several Python Flask applications and other services running on Docker Swarm that simulates an electoral system. The system provides features like registration of election participants (political parties or individuals), creating elections, voting and getting insight of election results. The results of parliamentary elections are formed using D'Hondt method, while the results of presidential elections are formed based on the number of votes that participant received and the total number of votes.

## Architecture

The system consists of 2 main components - one used for authentication and authorization (access control stack) and one for managing the election process (election process management stack). Both of the components consist of network(s) of Docker containers, where each container has a different role in the system. There are two types of users: administrator, whose responsibilities include creating participants, creating elections and getting election results, and election official, whose responsibilities include providing batches of ballots. 

Access control stack consists of 4 Docker containers:
- access_control:

	Runs Python Flask application which provides functionalities like user log in (i.e. obtaining JSON web access and refresh tokens), user registration, user deletion and refreshing access token.
- access_control_db:

	Runs mysql Docker image which contains the access control database.
- ac_db_migration:

	Runs Python application which initializes the access_control database.
- phpmyadmin:

	Runs phpmyadmin Docker image.

Election process management control stack consists of 7 Docker containers:
- epm_admin:
	
	Runs Python Flask application which provides functionalities available for administrators (creating participants, fetching participant list, creating elections, fetching list of elections and collecting the results of elections that have ended). Communicates with epm_db container only.
- epm_db:

	Runs mysql Docker image which contains the election_process database.
- epm_election_official:

	Runs Python Flask application which provides functionalities available for election officials (providing batches of ballots via .csv file). Uploaded ballots stored on a Redis service which is run on another container.
- redis:

	Runs redis Docker image.
- epm_daemon:

	A daemon container which runs a simple Python application whose only responsibility is reading ballots from Redis service (using publish/subscribe method), validating them and inserting them into the election_process database.
- epm_db_migration:
	
	Runs Python application which initializes the election_process database.
- phpmyadmin:
	
	Runs phpmyadmin Docker image.

## Deployment

- Building Docker images:
```bash
docker build -t ac --file ac.dockerfile . 
docker build -t ac_db_migration --file ac_db_migration.dockerfile . 
docker build -t epm_admin --file epm_admin.dockerfile . 
docker build -t epm_election_official --file epm_election_official.dockerfile . 
docker build -t epm_daemon --file epm_daemon.dockerfile . 
docker build -t epm_db_migration --file epm_db_migration.dockerfile . 
```
- Initializing Docker Swarm:
```bash
docker swarm init
```
- Deploying stacks:
```bash
docker stack deploy --compose-file ac.yaml ac
docker stack deploy --compose-file epm.yaml epm
```
