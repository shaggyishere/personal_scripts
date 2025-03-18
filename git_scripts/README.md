# Repository Management Scripts

This repository contains three Bash scripts for managing Git repositories. These scripts help with creating branches, updating repositories, and deleting local development branches.

These scripts streamline common Git operations across multiple repositories, making development workflow more efficient.

## Scripts Overview

### 1. `create_branches.sh`
This script creates a new branch across multiple repositories and pushes it to the remote repository.

#### Usage:
```bash
sh create_branches.sh -b <branch_name> -r path-to-myrepo1,path-to-myrepo2
```

#### Options:
- `-h` : Display help message.
- `-b <branch_name>` : Specify the branch name to create.
- `-l` : Operate only on the `lib-market-info-v1` repository instead of all default repositories.
- `-r` : Specify the repos you want to operate as comma string list

#### Behavior:
- Checks out the `env/svil` branch in each repository.
- Pulls the latest changes.
- Creates a new branch and pushes it to origin.

---

### 2. `delete_all_local_dev_branches.sh`
This script deletes all local branches except `env/svil` in specified repositories.

#### Usage:
```bash
sh delete_all_local_dev_branches.sh
```

#### Options:
- `-h` : Display help message.
- `-r` : Specify the repos you want to operate as comma string list

#### Behavior:
- Checks out `env/svil`.
- Deletes all other local branches.
- Can also operate on specific repositories if passed as arguments:
```bash
sh delete_all_local_dev_branches.sh -r path-to-myrepo1,path-to-myrepo2
```

---

### 3. `update_repos.sh`
This script updates specified repositories by fetching the latest changes and optionally adding a `RELEASE` commit.

#### Usage:
```bash
sh update_repos.sh
```

#### Options:
- `-h` : Display help message.
- `-b <branch_name>` : Specify the branch to checkout before updating (default: `env/svil`).
- `-R` : Add an empty `RELEASE` commit and push it.
- `-l` : Operate only on the `lib-market-info-v1` repository.
- `-r` : Specify the repos you want to operate as comma string list

#### Behavior:
- Fetches updates.
- Checks out the specified branch and pulls updates.
- If `-R` is used, creates an empty commit with the message `RELEASE` and pushes it.

