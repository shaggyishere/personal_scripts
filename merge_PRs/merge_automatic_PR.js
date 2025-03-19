import path from "path";
import { fileURLToPath } from "url";
import dotenv from "dotenv";
import axios from "axios";
import { Buffer } from "buffer";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, ".env") });

const REQUIRED_ENV_VARS = [
    "BITBUCKET_BASE_URL",
    "BITBUCKET_USERNAME",
    "BITBUCKET_PASSWORD",
    "BITBUCKET_PROJECT_KEY",
    "DESTINATION_BRANCH",
    "LIB_REPO"
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
const LIB_REPO = process.env.LIB_REPO;

async function main() {
    const PRsInfos = await getPRsInfos(LIB_REPO, "master", DESTINATION_BRANCH);

    if (!PRsInfos) {
        console.error(`There a was problem fetching automatic PRs for ${LIB_REPO} repo.`);
        process.exit(1);
    }

    for(const pr of PRsInfos) {
        await mergePR(LIB_REPO, pr.id, pr.version);
    }

}

const authHeader = {
    Authorization: `Basic ${Buffer.from(`${BITBUCKET_USERNAME}:${BITBUCKET_PASSWORD}`).toString("base64")}`,
};

async function getPRsInfos(repoSlug, sourceBranch, destinationBranch) {
    try {
        const url = `${BITBUCKET_BASE_URL}/rest/api/latest/projects/${BITBUCKET_PROJECT_KEY}/repos/${repoSlug}/pull-requests?state=OPEN`;
        const response = await axios.get(url, { headers: authHeader });
        return response.data
            .values
            .filter((pr) => pr.author.user.name === "vobadm" && pr.fromRef.displayId === sourceBranch && pr.toRef.displayId === destinationBranch);
    } catch (error) {
        console.error(`❌ Error fetching PRs for repo ${repoSlug}:`, error.response?.data || error.message);
        return [];
    }
}

async function mergePR(repoSlug, prId, prVersion) {
    try {
        const url = `${BITBUCKET_BASE_URL}/rest/api/latest/projects/${BITBUCKET_PROJECT_KEY}/repos/${repoSlug}/pull-requests/${prId}/merge`;
        await axios.post(url, { version: prVersion }, { headers: authHeader });

        console.log(`✅ Automatic PR ${prId} merged successfully in ${repoSlug}.`);
    } catch (error) {
        console.error(`❌ Failed to merge PR ${prId} in ${repoSlug}:`, error.response?.data || error.message);
    }
}

main();