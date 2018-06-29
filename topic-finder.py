import argparse
import requests
import glob
import os

AIVEN_BASE_URL='https://api.aiven.io/v1beta'

parser = argparse.ArgumentParser(description='Find non-terraformed topic names')
parser.add_argument('auth_token', type=str, help='Aiven authentication token')
parser.add_argument('project', type=str, help='Aiven project name')
parser.add_argument('service', type=str, help='Kafka service name')
parser.add_argument('path', type=str, help='Relative path to directory to search for matching topics')

args = parser.parse_args()

# Query aiven for all topics in the specified service
headers = {'Authorization': 'aivenv1 {}'.format(args.auth_token)}
r = requests.get('{}/project/{}/service/{}/topic'.format(AIVEN_BASE_URL, args.project, args.service), headers=headers)

# Build a list of topics
topics = []
for topic in r.json()['topics']:
    for k, v in topic.items():
        if k == 'topic_name':
            topics.append(v)

remaining_topics = list(topics)

# Search through every terraform file in the specified directory
for file in glob.glob('{}/**/*.tf'.format(args.path), recursive=True):
    contents = None
    with open(file) as f:
        contents = f.read()
        for topic in topics:
            if topic in contents:
                try:
                    remaining_topics.remove(topic)
                except ValueError:
                    pass

# Dump the list of topics not foundin terraform scripts
print('The following topics were not found in {} using a simple pattern match:\n'.format(args.path))
for topic in remaining_topics:
    print('{}'.format(topic))





