import path from "path";
import { fileURLToPath } from "url";
import dotenv from "dotenv";
import axios from "axios";
import { Buffer } from "buffer";
import yargs from "yargs";
import { hideBin } from "yargs/helpers";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, ".env") });

const REQUIRED_ENV_VARS = [
    "BITBUCKET_BASE_URL",
    "BITBUCKET_USERNAME",
    "BITBUCKET_PASSWORD",
    "BITBUCKET_PROJECT_KEY",
    "DESTINATION_BRANCH",
    "DEFAULT_REPO_SLUGS",
    "POSSIBLE_REVIEWERS",
];

const missingVars = REQUIRED_ENV_VARS.filter((key) => !process.env[key]);

if (missingVars.length > 0) {
    console.error("Missing required environment variables:");
    missingVars.forEach((key) => console.error(`   - ${key}`));
    console.error("Please set these variables in your environment before running the script.");
    process.exit(1);
}

const BITBUCKET_BASE_URL = process.env.BITBUCKET_BASE_URL;
const BITBUCKET_USERNAME = process.env.BITBUCKET_USERNAME;
const BITBUCKET_PASSWORD = process.env.BITBUCKET_PASSWORD;
const BITBUCKET_PROJECT_KEY = process.env.BITBUCKET_PROJECT_KEY;
const DESTINATION_BRANCH = process.env.DESTINATION_BRANCH;
const DEFAULT_REPO_SLUGS = process.env.DEFAULT_REPO_SLUGS.split(",");
const POSSIBLE_REVIEWERS = process.env.POSSIBLE_REVIEWERS.split(",");

if (POSSIBLE_REVIEWERS.length < 2) {
    console.error("Please set at least two possible reviewers using POSSIBLE_REVIEWERS env variable.");
    process.exit(1);
}

const argv = yargs(hideBin(process.argv))
    .option("b", {
        alias: "branch",
        type: "string",
        describe: "Source branch name",
        demandOption: true,
    })
    .option("rvw", {
        alias: "reviewers",
        type: "string",
        describe: "Comma-separated list of reviewers",
        demandOption: false,
    })
    .option("rs", {
        alias: "repos",
        type: "string",
        describe: "Comma-separated list of repository slugs",
        demandOption: false,
    })
    .help()
    .argv;

const repos = argv.rs ? argv.rs.split(",") : DEFAULT_REPO_SLUGS;
const sourceBranch = argv.b;
const reviewers = argv.rvw ? argv.rvw.split(",").map((user) => ({ user: { name: user } })) : extractTwoRandomElementsFromList(POSSIBLE_REVIEWERS);

async function main() {
    for (const repo of repos) {
        createPullRequest(repo, sourceBranch, reviewers);
    }
}

async function createPullRequest(repoSlug, sourceBranch, reviewers) {
    const url = `${BITBUCKET_BASE_URL}/rest/api/latest/projects/${BITBUCKET_PROJECT_KEY}/repos/${repoSlug}/pull-requests`;

    const prData = generatePullRequestInfo(repoSlug, sourceBranch, reviewers);

    try {
        const response = await axios.post(url, prData, {
            headers: {
                "Content-Type": "application/json",
                Authorization: `Basic ${Buffer.from(`${BITBUCKET_USERNAME}:${BITBUCKET_PASSWORD}`).toString("base64")}`
            }
        });

        console.log(`✅ PR Created Successfully for repo: ${repoSlug}`);
        console.log(response.data);
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

function generatePullRequestInfo(repoSlug, sourceBranch, reviewers) {
    const branchTypes = ["feature/", "hotfix/", "bugfix/"];

    return {
        title: removePrefixes(sourceBranch, branchTypes),
        description: "PR created using bitbucket APIs",
        fromRef: {
            id: `refs/heads/${sourceBranch}`,
            repository: {
                project: {
                    key: BITBUCKET_PROJECT_KEY
                },
                slug: repoSlug
            },
            type: "BRANCH"
        },
        reviewers: reviewers,
        toRef: {
            id: `refs/heads/${DESTINATION_BRANCH}`,
            repository: {
                project: {
                    key: BITBUCKET_PROJECT_KEY
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

function extractTwoRandomElementsFromList(arr, count = 2) {
    if (arr.length < count) {
        console.error("The following array should contain at least two element: ", arr);
        process.exit(1);
    }

    const result = new Set();
    while (result.size < count) {
        const randomIndex = Math.floor(Math.random() * arr.length);
        result.add(arr[randomIndex]);
    }

    return [...result];
}

main();