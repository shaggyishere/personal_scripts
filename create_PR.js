import dotenv from "dotenv";

dotenv.config();

const BITBUCKET_BASE_URL = process.env.BITBUCKET_BASE_URL;
const USERNAME = process.env.BITBUCKET_USERNAME;
const PASSWORD = process.env.BITBUCKET_PASSWORD;
const PROJECT_KEY = process.env.PROJECT_KEY;

async function createPullRequest(repoSlug, sourceBranch, reviewers) {
  const url = `${BITBUCKET_BASE_URL}/rest/api/1.0/projects/${PROJECT_KEY}/repos/${repoSlug}/pull-requests`;

  const prData = generatePRInfo(repoSlug, sourceBranch, reviewers);

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Basic ${Buffer.from(`${USERNAME}:${PASSWORD}`).toString("base64")}`
      },
      body: JSON.stringify(prData),
    });

    if (!response.ok) {
        const errorData = await response.json(); // Get full error details
        console.error(`HTTP Error! Status:`, response.status);
        console.error(`Response:`, JSON.stringify(errorData, null, 2));
    }

    const data = await response.json();
    console.log("✅ PR Created Successfully: ", data);
  } catch (error) {
    console.error("❌ Error creating PR:", error.message);
  }
}

function generatePRInfo(repoSlug, sourceBranch, reviewers) {
    const branchTypes = ["feature/", "hotfix/", "bugfix/"]

    return {
        title: removePrefixes(sourceBranch, branchTypes),
        description: "PR created using bitbucket APIs",
        fromRef: {
            id: `refs/heads/${sourceBranch}`,
            repository: {
                project: {
                    key: PROJECT_KEY
                },
                slug: repoSlug
            },
            type: "BRANCH"
        },
        reviewers: [
            {
                user: {
                    name: reviewers[0]
                }
            },
            // {
            //     user: {
            //         name: reviewers[1]
            //     }
            // },
            // {
            //     user: {
            //         name: reviewers[2]
            //     }
            // }
        ],
        toRef: {
            id: `refs/heads/env/svil`,
            repository: {
                project: {
                    key: PROJECT_KEY
                },
                slug: repoSlug
            },
            type: "BRANCH"
        }
    };
}

function removePrefixes(word, prefixes) {
    for (let prefix of prefixes) {
      if (word.startsWith(prefix)) {
        return word.replace(prefix, "");
      }
    }
    return word;
}



createPullRequest();
