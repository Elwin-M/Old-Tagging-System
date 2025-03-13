import os
from datetime import datetime, timedelta
from utils import *

# Load environment variables
def load_env():
    from dotenv import load_dotenv
    load_dotenv()

# Create default environment if missing
def create_env():
    if not os.path.exists(".env"):
        with open(".env", "w") as env_file:
            env_file.write(
                """
SONARR=true
RADARR=false
LISTMONK=false

SONARRINSTANCE=192.168.10.200:PORT
RADARRINSTANCE=192.168.10.200:PORT
LISTMONKINSTANCE=192.168.10.200:PORT

SONARRAPI=API
RADARRAPI=API
LISTMONKAPI=API

SEASONALTAG=seasonal
OLDTAG=old

OLDDIR=/Media/Library/old/
OLDDAYSCOUNT=60
EXPIRATIONDAYSCOUNT=30
                """
            )

# Authenticate with service and return a session
def auth_service(instance, api_key):
    import requests
    session = requests.Session()
    session.headers.update({"X-Api-Key": api_key})
    return session

# Pass a request to the service
def pass_to_service(session, url, method="GET", data=None):
    import requests
    if method == "GET":
        response = session.get(url)
    elif method == "POST":
        response = session.post(url, json=data)
    elif method == "DELETE":
        response = session.delete(url)
    response.raise_for_status()
    return response.json()

# Main function
def main():
    load_env()

    # Initialize services
    services = []
    if os.getenv("SONARR", "false").lower() == "true":
        services.append(("Sonarr", os.getenv("SONARRINSTANCE"), os.getenv("SONARRAPI")))
    if os.getenv("RADARR", "false").lower() == "true":
        services.append(("Radarr", os.getenv("RADARRINSTANCE"), os.getenv("RADARRAPI")))
    
    for service_name, instance, api_key in services:
        session = auth_service(instance, api_key)
        
        # Run all checks for the service
        list_tag(session, instance, os.getenv("SEASONALTAG"), os.getenv("OLDTAG"))
        #add_tag(session, instance, os.getenv("SEASONALTAG"), os.getenv("OLDTAG"))
        #remove_tag(session, instance)
        #delete_files(os.getenv("OLDDIR"), int(os.getenv("EXPIRATIONDAYSCOUNT")))

if __name__ == "__main__":
    main()
