import path from "path";
import { fileURLToPath } from "url";
import dotenv from "dotenv";
import axios from "axios";
import yargs from "yargs";
import { hideBin } from "yargs/helpers";
import { Buffer } from "buffer";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const argv = yargs(hideBin(process.argv))
    .option("prj", {
        alias: "project",
        type: "string",
        describe: "Project key of .env to load",
        demandOption: true,
    })
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
    "LIB_REPOS",
    "AUTO_PR_USERNAME"
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
const LIB_REPOS = process.env.LIB_REPOS.split(",");
const AUTO_PR_USERNAME = process.env.AUTO_PR_USERNAME;

async function main() {

    for(const libRepo of LIB_REPOS) {
        const PRsInfos = await getPRsInfos(libRepo, "master", DESTINATION_BRANCH, AUTO_PR_USERNAME);
    
        if (!PRsInfos) {
            console.error(`There a was problem fetching automatic PRs for ${libRepo} repo.`);
            process.exit(1);
        }
    
        for(const pr of PRsInfos) {
            await mergePR(libRepo, pr.id, pr.version);
        }        
    }

}

const authHeader = {
    Authorization: `Basic ${Buffer.from(`${BITBUCKET_USERNAME}:${BITBUCKET_PASSWORD}`).toString("base64")}`,
};

async function getPRsInfos(repoSlug, sourceBranch, destinationBranch, autoPrUsername) {
    try {
        const url = `${BITBUCKET_BASE_URL}/rest/api/latest/projects/${BITBUCKET_PROJECT_KEY}/repos/${repoSlug}/pull-requests?state=OPEN`;
        const response = await axios.get(url, { headers: authHeader });
        return response.data
            .values
            .filter((pr) => pr.author.user.name === autoPrUsername && pr.fromRef.displayId === sourceBranch && pr.toRef.displayId === destinationBranch);
    } catch (error) {
        console.error(`❌ Error fetching PRs for repo ${repoSlug}:`, error.response?.data || error.message);
        return [];
    }
}

async function mergePR(repoSlug, prId, prVersion) {
    try {
        const url = `${BITBUCKET_BASE_URL}/rest/api/latest/projects/${BITBUCKET_PROJECT_KEY}/repos/${repoSlug}/pull-requests/${prId}/merge`;
        await axios.post(url, { version: prVersion }, { headers: authHeader });

        console.log(`✅ Automatic PR #${prId} merged successfully in ${repoSlug}.`);
    } catch (error) {
        console.error(`❌ Failed to merge PR #${prId} in ${repoSlug}:`, error.response?.data || error.message);
    }
}

main();