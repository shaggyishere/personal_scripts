import path from "path";
import { fileURLToPath } from "url";
import dotenv from "dotenv";
import axios from "axios";
import { Buffer } from "buffer";
import yargs from "yargs";
import { hideBin } from "yargs/helpers";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const argv = yargs(hideBin(process.argv))
    .option("b", {
        alias: "branch",
        type: "string",
        describe: "Source branch name",
        demandOption: true,
    })
    .option("prj", {
        alias: "project",
        type: "string",
        describe: "Project key of .env to load",
        demandOption: true,
    })
    .option("rs", {
        alias: "repos",
        type: "string",
        describe: "Comma-separated list of repository slugs",
        demandOption: false,
    })
    .option("be4fe", {
        type: "boolean",
        describe: "Flag to operate just with BE4FE repos",
        demandOption: false,
    })
    .option("lib", {
        type: "boolean",
        describe: "Flag to operate just with lib repos",
        demandOption: false,
    })
    .conflicts("be4fe", "lib")
    .conflicts("lib", "rs")
    .conflicts("rs", "be4fe")
    .help()
    .argv;

const dotEnvFileToLoad = `.env.${argv.prj}`;

dotenv.config({ path: path.resolve(__dirname, dotEnvFileToLoad) });

const REQUIRED_ENV_VARS = [
    "BITBUCKET_BASE_URL",
    "BITBUCKET_USERNAME",
    "BITBUCKET_PASSWORD",
    "BITBUCKET_PROJECT_KEY",
    "DESTINATION_BRANCH",
    "DEFAULT_REPO_SLUGS"
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

var repos = DEFAULT_REPO_SLUGS;


if (argv.be4fe) {
    const BE4FE_REPOS = process.env.BE4FE_REPOS.split(",");
    repos = BE4FE_REPOS;
}
else if (argv.lib) {
    const LIB_REPOS = process.env.LIB_REPOS.split(",");
    repos = LIB_REPOS;
}
else if (argv.rs) {
    repos = argv.rs.split(",");
}

const branchToMerge = argv.b;

async function main() {
    for (const repo of repos) {
        const prInfos = await getPRInfos(repo, branchToMerge, DESTINATION_BRANCH);

        if (!prInfos) {
            console.error(`There a was problem fetching PR info for ${branchToMerge} branch of ${repo} repo.`);
            continue;
        }

        await mergePR(repo, branchToMerge, prInfos.id, prInfos.version);
    }
}

const authHeader = {
    Authorization: `Basic ${Buffer.from(`${BITBUCKET_USERNAME}:${BITBUCKET_PASSWORD}`).toString("base64")}`,
};

async function getPRInfos(repoSlug, sourceBranch, destinationBranch) {
    try {
        const url = `${BITBUCKET_BASE_URL}/rest/api/latest/projects/${BITBUCKET_PROJECT_KEY}/repos/${repoSlug}/pull-requests?state=OPEN`;
        const response = await axios.get(url, { headers: authHeader });
        return response.data
            .values
            .filter((pr) => pr.fromRef.displayId === sourceBranch && pr.toRef.displayId === destinationBranch)
            [0]; // there should be always just one PR that satisay this condition
    } catch (error) {
        console.error(`❌ Error fetching PRs for repo ${repoSlug}:`, error.response?.data || error.message);
        return [];
    }
}

async function mergePR(repoSlug, branchToMerge, prId, prVersion) {
    try {
        const url = `${BITBUCKET_BASE_URL}/rest/api/latest/projects/${BITBUCKET_PROJECT_KEY}/repos/${repoSlug}/pull-requests/${prId}/merge`;
        const response = await axios.post(url, { version: prVersion }, { headers: authHeader });

        if (response.status === 200) {
            console.log(`✅ PR #${prId} merged successfully in ${repoSlug}.`);
            await deleteBranch(repoSlug, branchToMerge);
        }
    } catch (error) {
        console.error(`❌ Failed to merge PR #${prId} in ${repoSlug}:`, error.response?.data || error.message);
    }
}

async function deleteBranch(repoSlug, branch) {
    const deleteBranchUrl = `${BITBUCKET_BASE_URL}/rest/branch-utils/latest/projects/${BITBUCKET_PROJECT_KEY}/repos/${repoSlug}/branches`;

    try {
        await axios.delete(deleteBranchUrl, {
            headers: authHeader,
            data: { name: `refs/heads/${branch}` },
        });

        console.log(`✅ Source branch '${branch}' deleted successfully.`);
    } catch (error) {
        console.error("❌ Error deleting source branch:", error.response?.data || error.message);
    }
}

main();