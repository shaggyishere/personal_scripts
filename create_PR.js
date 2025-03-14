import dotenv from "dotenv";
import axios from "axios";

dotenv.config();

const BITBUCKET_BASE_URL = process.env.BITBUCKET_BASE_URL;
const USERNAME = process.env.BITBUCKET_USERNAME;
const PASSWORD = process.env.BITBUCKET_PASSWORD;
const PROJECT_KEY = process.env.PROJECT_KEY;

async function createPullRequest(repoSlug, sourceBranch, reviewers) {
    const url = `${BITBUCKET_BASE_URL}/rest/api/latest/projects/${PROJECT_KEY}/repos/${repoSlug}/pull-requests`;

    const prData = generatePRInfo(repoSlug, sourceBranch, reviewers);

    try {
        const response = await axios.post(url, prData, {
            headers: {
                "Content-Type": "application/json",
                Authorization: `Basic ${Buffer.from(`${USERNAME}:${PASSWORD}`).toString("base64")}`
            }
        });

        console.log("✅ PR Created Successfully:", response.data);
    } catch (error) {
        if (error.response) {
            console.error("❌ Error creating PR:");
            console.error("Status:", error.response.status, error.response.statusText);
            console.error("Response Data:", JSON.stringify(error.response.data, null, 2));
        } else if (error.request) {
            console.error("❌ No response from server. Check API URL or network connection.");
        } else {
            console.error("❌ Unexpected error:", error.message);
        }
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
