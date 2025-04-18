# Repository Management Scripts

This repository contains variuous Bash scripts for managing Git repositories. These scripts help with creating branches, updating repositories, and deleting local development branches.

These scripts streamline common Git operations across multiple repositories, making development workflow more efficient.

## **📌 Environment Configuration**
Create environment-specific `.env` files in the project root for each project you wanna handle.

### **Example `.env.project` Configuration**
```ini
repos=("path-to-myrepo1" "path-to-myrepo2")
lib_repos=("path-to-myrepo1" "path-to-myrepo2")
default_development_branch=develop
```

## Scripts Overview

Please note that every script requires a project defined in order to execute git commands.

### 1. `create_branches.sh`
This script creates a new branch across multiple repositories and pushes it to the remote repository.

#### Usage:
```bash
sh create_branches.sh -b <branch_name> -p <project> -r path-to-myrepo1,path-to-myrepo2
```

#### Options:
- `-h` : Display help message.
- `-b <branch_name>` : Specify the branch name to create.
- `-p` : Set the correct .env file to load.
- `-l` : Operate only on the `lib-market-info-v1` repository instead of all default repositories.
- `-r` : Specify the repos you want to operate as comma string list

#### Behavior:
- Checks out the `$default_development_branch` branch in each repository.
- Pulls the latest changes.
- Creates a new branch and pushes it to origin.

---

### 2. `show_all_local_dev_branches.sh`
This script shows all local branches except `$default_development_branch` in specified repositories. (Preferibly use it before `delete_all_local_dev_branches.sh`)

#### Usage:
```bash
sh show_all_local_dev_branches.sh -p <project>
```

#### Options:
- `-h` : Display help message.
- `-p` : Set the correct .env file to load.
- `-r` : Specify the repos you want to operate as comma string list

#### Behavior:
- Shows all other local branches.
- Can also operate on specific repositories if passed as arguments:
```bash
sh show_all_local_dev_branches.sh -p <project> -r path-to-myrepo1,path-to-myrepo2
```

---

### 3. `delete_all_local_dev_branches.sh`
This script deletes all local branches except `$default_development_branch` in specified repositories.

#### Usage:
```bash
sh delete_all_local_dev_branches.sh -p <project>
```

#### Options:
- `-h` : Display help message.
- `-p` : Set the correct .env file to load.
- `-r` : Specify the repos you want to operate as comma string list

#### Behavior:
- Checks out `$default_development_branch`.
- Deletes all other local branches.
- Can also operate on specific repositories if passed as arguments:

```bash
sh delete_all_local_dev_branches.sh -p <project> -r path-to-myrepo1,path-to-myrepo2
```

---

### 4. `update_repos.sh`
This script updates specified repositories by fetching the latest changes and optionally adding a `RELEASE` commit.

#### Usage:
```bash
sh update_repos.sh -p <project> -b <branch_name>
```

#### Options:
- `-h` : Display help message.
- `-b <branch_name>` : Specify the branch to checkout before updating.
- `-p` : Set the correct .env file to load.
- `-R` : Add an empty `RELEASE` commit and push it.
- `-l` : Operate only on the `lib-market-info-v1` repository.
- `-r` : Specify the repos you want to operate as comma string list

#### Behavior:
- Fetches updates.
- Checks out the specified branch and pulls updates.
- If `-R` is used, creates an empty commit with the message `RELEASE` and pushes it.

