#!/usr/bin/env python

import argparse
import json
import os
import re
import sys
import logging

import requests

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="[%(levelname)-8s] %(message)s")
logger = logging.getLogger(__name__)

ISSUE_PATTERN = re.compile("^([A-Z]{1,10}-[0-9]+)")

github_token = os.getenv("GITHUB_TOKEN")

jira_url = os.getenv("JIRA_URL")
if not jira_url:
    raise Exception("Missing JIRA URL")
jira_email = os.getenv("JIRA_EMAIL")
if not jira_email:
    raise Exception("Missing JIRA account's email address")
jira_api_token = os.getenv("JIRA_API_TOKEN")
if not jira_api_token:
    raise Exception("Missing JIRA API token")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("payload_string")
    parser.add_argument("transition")
    args = parser.parse_args()

    event = json.loads(args.payload_string)

    commits_url = event["pull_request"]["_links"]["commits"]["href"]

    response = requests.get(
        commits_url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {github_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        })
    response.raise_for_status()
    commits = response.json()

    issue_keys = set()
    for commit in commits:
        sha = commit["sha"]
        message = commit["commit"]["message"]
        logger.info("Analyzing: %s (%s)", sha, message)
        result = ISSUE_PATTERN.match(message)
        if result is None:
            logger.info("Commit is not associated with any issue; skipping %s", sha)
            continue
        issue_key = result.group(1)
        logger.info("Commit %s is associated with JIRA issue: %s", sha, issue_key)
        issue_keys.add(issue_key)

    for issue_key in issue_keys:
        logger.info(f"Transitioning issue: {issue_key}")
        response = requests.post(
            f"{jira_url}/rest/api/latest/issue/{issue_key}/transitions",
            auth=(jira_email, jira_api_token),
            json={
                "transition": {
                    "id": args.transition
                }
            })
        response.raise_for_status()


if __name__ == "__main__":
    main()
