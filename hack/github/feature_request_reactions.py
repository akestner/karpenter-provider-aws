#!/usr/bin/env python3

import csv
import os
import sys
from operator import itemgetter
from typing import Union

# This script requires the python GitHub client:
# pip install PyGithub
from github import Github, Auth
from github.Repository import Repository

# To create a GitHub token, see below (the token doesn't need to include any scopes):
# https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line
auth = Auth.Token(token=os.environ.get('GH_TOKEN'))
github = Github(auth=auth)

def unique_reaction_count(issues):
  reaction_count: list[dict[str, Union[int, str]]] = []
  plus_one_reaction_strings = ['+1', 'heart', 'hooray', 'rocket', 'eyes']
  for issue in issues:
    # count unique +1s
    usernames: set[str] = set()
    plus_ones = 0
    for reaction in issue.get_reactions():
      username = reaction.user.login
      if reaction.content in plus_one_reaction_strings and username not in usernames:
        usernames.add(reaction.user.login)
        plus_ones += 1

    reaction_count.append({
      'title': issue.title,
      'url': issue.html_url,
      'reactions': plus_ones
    })

  return reaction_count

provider_repo: Repository = github.get_repo('aws/karpenter-provider-aws')
core_repo: Repository = github.get_repo('kubernetes-sigs/karpenter')

provider_reaction_count = unique_reaction_count(provider_repo.get_issues(state='open', labels=['feature']))
core_reaction_count = unique_reaction_count(core_repo.get_issues(state='open', labels=['kind/feature']))
issue_reaction_count = provider_reaction_count + core_reaction_count

issue_row_list = [['Title', 'Url', 'Plus Ones']]
for issue in sorted(issue_reaction_count, key=itemgetter('reactions'), reverse=True):
  issue_row_list.append([
    issue['title'],
    issue['url'],
    issue['reactions']
  ])

# Write CSV data to STDOUT, redirect to file to persist, e.g.
# ./hack/github/feature_request_reactions.py > "karpenter-feature-requests-$(date +"%Y-%m-%d").csv"
writer = csv.writer(sys.stdout)
writer.writerows(issue_row_list)
