# 🚀 Bitbucket Create PR Automation Script

This script automates the process of creating pull requests in Bitbucket using the Bitbucket REST API. It allows users to specify the source branch, reviewers, and target repositories via command-line arguments.

🎯 Aim of This Script

The goal of this script is to automate the creation of pull requests for multiple backend-for-frontend (BE4FE) repositories, that shares a common development branch, avoiding the need to manually interact with the Bitbucket GUI.

---

## 📌 Prerequisites

Before running this script, ensure you have the following:

- **Node.js** installed (version 14 or higher recommended)
- **Bitbucket HTTP Access Token** (see instructions below)
- Required **environment variables** properly set

---

## ⚙️ Setting Up Environment Variables

This script requires the following environment variables:

| Variable               | Description                                                      |
|------------------------|------------------------------------------------------------------|                
| `BITBUCKET_BASE_URL`   | Your Bitbucket instance URL                                      |
| `BITBUCKET_USERNAME`   | Your Bitbucket username (UXXXXX)                                 |
| `BITBUCKET_PASSWORD`   | Your Bitbucket HTTP token (see below)                            |
| `BITBUCKET_PROJECT_KEY`          | The Bitbucket project key                                        |
| `DEFAULT_REPO_SLUGS`   | Comma-separated list of default repositories                     |
| `POSSIBLE_REVIEWERS`   | Comma-separated list of possible reviewers (UXXXXX values)       |
| `BE4FE_REPOS`        | (Optional) Comma-separated list of BE4FE repos |
| `LIB_REPO`          | (Optional) Lib repo   |


### 🔑 How to Create a Bitbucket HTTP Token

To generate an HTTP access token for authentication, follow this guide:
👉 [Bitbucket HTTP Access Tokens](https://confluence.atlassian.com/bitbucketserver/http-access-tokens-939515499.html)

After creating a token, set the `BITBUCKET_PASSWORD` environment variable to the generated token.

---

## 📜 Installation

Clone this repository and install the required dependencies:

```sh
cd personal-scripts/create_PRs/
npm install
```

If using a `.env` file, create one in _create_PRs/_ and add:

```ini
BITBUCKET_BASE_URL=https://your-bitbucket-instance.com
BITBUCKET_USERNAME=your-username
BITBUCKET_PASSWORD=your-http-token
BITBUCKET_PROJECT_KEY=your-project-key
DEFAULT_REPO_SLUGS=repo1,repo2,repo3
POSSIBLE_REVIEWERS=reviewer1,reviewer2,reviewer3
```

---

## 🚀 Running the Script

Run the script using:

```sh
node create_PRs.js -b <branch_name> -rvw <user1,user2> -rs <repo1,repo2>
```

### 🔹 Command-Line Arguments

| Argument    | Description                                              |
|-------------|----------------------------------------------------------|
| `-b` / `--branch` | The **source branch** name for the PR                   |
| `--prj` / `--project` | Project key of .env to load                   |
| `--rvw` / `--reviewers` | **Comma-separated list** of reviewers (e.g., `UXXXX,UXXXX`) |
| `--rs` / `--repos` | **Comma-separated list** of repositories (e.g., `repo1,repo2`) |
| `--be4fe`          | Flag to operate just with BE4FE repos                          |
| `--lib`            | Flag to operate just with lib repos                            |

Note: 
- `--prj` flag is mandatory in order to choose which .env file load
- if `--rvw` flag is not specified, two random reviewers will be chosen from the `POSSIBLE_REVIEWERS` list.
- `--be4fe` and `--lib` **cannot** be used together.
- `--lib` and `--rs` **cannot** be used together.
- `--rs` and `--be4fe` **cannot** be used together.
- If **none** of `--rs`, `--be4fe`, or `--lib` is passed, the script defaults to `DEFAULT_REPO_SLUGS`.

### ✅ Example Usage

```sh
node create_PRs.js -b feature-xyz --prj myproj --rvw reviewer1,reviewer2 --rs repo1,repo2
```

---

## ❌ Troubleshooting

- If you see **missing environment variable errors**, ensure they are properly set.
- If authentication fails, check your **HTTP token** and ensure it has **sufficient permissions**.
- If PR creation fails, check Bitbucket API responses for more details.

---

## 📄 License

This project is open-source. Feel free to modify and enhance it!

---

🚀 Happy coding! Let me know if you need further improvements!