#!/usr/bin/env bash
# Fetch real GitHub stats into assets/data.json (consumed by gen_profile.py).
# Needs GH_TOKEN / gh auth in the environment.
set -euo pipefail
cd "$(dirname "$0")/.."
gh api graphql -f query='
{ user(login:"ImFelipeOliveira"){
    followers{ totalCount } following{ totalCount }
    repositories(isFork:false, ownerAffiliations:OWNER){ totalCount }
    contributionsCollection{
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ contributionCount date } }
      }
    }
} }' > assets/data.json
echo "wrote assets/data.json"
