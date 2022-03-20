#!/usr/bin/env python

import csv
import os
import sys
from operator import itemgetter

from github import Github
from github import StatsContributor, Repository, NamedUser

# To create a GitHub token, see below (the token doesn't need to include any scopes):
# https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line
github: Github = Github(os.environ.get('GH_TOKEN'))

karpenter_team_members: [NamedUser] = github.get_organization('aws').get_team_by_slug('karpenter').get_members()
repo: Repository = github.get_repo('aws/karpenter')
contributor_stats: StatsContributor = repo.get_stats_contributors()
external_contributor_stats = filter(lambda c: c.author not in karpenter_team_members, contributor_stats)

contributor_row_list = [['Contributor', 'Commits']]
for contributor_stat in sorted(external_contributor_stats, key=lambda c: c.total, reverse=True):
  contributor_row_list.append([contributor_stat.author.name, contributor_stat.total])

# Write CSV data to STDOUT, redirect to file to persist, e.g.
# ./hack/github/external_contributors.py > "karpenter-external-contributors-$(date +"%Y-%m-%d").csv"
writer = csv.writer(sys.stdout)
writer.writerows(contributor_row_list)
