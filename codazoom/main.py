# Caleb Smith wrote this! how cool is that?

import json
from zoomus import ZoomClient
import config
from codaio import Coda, Document, Cell

# Initialize coda
coda = Coda(config.coda_api_token)
doc = Document(config.coda_doc, coda=coda)
table = doc.get_table(config.coda_table)

print("... Coda Initialized!")

# Initialize Zoom
client = ZoomClient(config.CLIENT_ID, config.CLIENT_SECRET)
users = client.user.list()
users = json.loads(users.content)  # grab a list of all users in the account, make python objects out of them

print("... Zoom Initialized!")
# global variables are bad, kids. do as I say, not as I do
recordings = []
list_of_ids = []
columns = []

# grab just the user IDs, we'll need those for the next bit
# TODO: make the IDs persist or just make the user IDs a configuration option
# TODO: write a script that makes getting IDs ezpz
for user in users["users"]:
    list_of_ids.append(user["id"])

print("... Zoom IDs collected")
# quickly grab column IDs from the coda table
# TODO: persist these too? maybe not, that adds up to a lot of configuration.
for column in table.columns():
    columns.append(column.id)
print("... Coda IDs collected")

print("SCRIPT RESULTS UPSERTED TO CODA:")

# For every zoom user we grab, let's grab the recordings tied to their account and add them each as a row in Coda
for id in list_of_ids:
    id_recordings = json.loads(client.recording.list(user_id=id).content)

    for meeting in id_recordings["meetings"]:
        if "On-Boarding" in meeting["topic"]:  # filtering based on topic -- should this be a config value????

            """ Warning: The following line of code below is a mess.
            
                Here's why: codaio's upsert function won't let you check against key columns, so I had to use an
                internal library function and craft the json myself. If anyone knows a better way to do it, I'd love to hear it!
            """
            data = {"rows": [{"cells": [{"column": columns[0], "value": meeting["topic"]},
                                        {"column": columns[1], "value": meeting["share_url"]}]}],
                    "keyColumns": [columns[1]]}

            coda.upsert_row(config.coda_doc, config.coda_table, data)
            print(meeting["topic"], meeting["share_url"])  # debugging is always nice
