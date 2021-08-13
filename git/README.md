<!-- vscode-markdown-toc -->
	* 1. [List Branches](#ListBranches)
	* 2. [Create Branch](#CreateBranch)
	* 3. [Delete Branch](#DeleteBranch)
	* 4. [View and Set remote](#ViewandSetremote)
	* 5. [Adding files](#Addingfiles)
	* 6. [Removing files](#Removingfiles)
	* 7. [Commiting](#Commiting)
	* 8. [Pulling](#Pulling)
	* 9. [Pushing](#Pushing)
	* 10. [PAT or Personal Access Token](#PATorPersonalAccessToken)
	* 11. [Reference](#Reference)

<!-- vscode-markdown-toc-config
	numbering=true
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->





###  1. <a name='ListBranches'></a>List Branches

The command to list all branches in local and remote repositories is:

```bash
> git branch -a
```

Show only remote branches

```bash
> git branch -r
```

Show only local branches

```bash
> git branch -a | grep -v remotes
```

###  2. <a name='CreateBranch'></a>Create Branch

Create and switch to local branch

```bash
> git branch newbr1
> git checkout newbr1
OR
> git checkout -b newbr1
```

Move the local branch to remote

```bash
> git push origin newbr1
```

###  3. <a name='DeleteBranch'></a>Delete Branch

Delete local branch:

```bash
> git branch -d newbr1
```

If branch has unmerged changes then

```bash
> git branch -d -f newbr1
```

Delete remote branch:

```bash
> git push origin --delete newbr1
```

Local and remote branches are distinct git objects, deleting one does not delete the other. You need to delete each explicitly.

###  4. <a name='ViewandSetremote'></a>View and Set remote

View:

```bash
> git remote -v
```

Set:

```bash
> git remote add origin "repo URL"
```

###  5. <a name='Addingfiles'></a>Adding files

```bash
> git add file1							# adds one file
> git add folder1/file1			# adds one file inside a folder
> git add file1 file2 file3 # add multiple files at the same time
> git add . 								# add all files and folders in the current folder
> git add -all							# add all folders in the curre
```

###  6. <a name='Removingfiles'></a>Removing files

Remove file from git working tree and local file system

```bash
> git rm file1
```

Remove file from git working tree but keep the local copy

```bash
> git rm --cached file1
```

Similar commands for removing folders recursively:

```bash
> git rm -r folder1						# rm from git working tree and local file system
> git rm -r --cached folder1	# rm from git working tree only
```

###  7. <a name='Commiting'></a>Commiting

```bash
> git commit -m "commit message"
```

Change/Amend the commit message

```bash
> git commit --amend -m "new commit message" 
```

Undo last commit: **hard** ... this will undo commit and roll back all the changed files/folders

```bash
> git reset --hard HEAD~1
```

Undo last commit: **sort** ... this will undo commit, but keep all the changed files/folders

```bash
> git reset --soft HEAD~1
```

###  8. <a name='Pulling'></a>Pulling

Download content from remote and merge with local files:

`pull` is basically a `fetch` + `merge`

```bash
> git pull origin master
OR simply
> git pull
```

`origin` is the convention name for the remote repository and `master` is the branch being pulled

###  9. <a name='Pushing'></a>Pushing

To push the currently checkedout branch to remote repo's `master` branch:

```bash
> git push origin master
```

To push multiple (all) branches at the same time

```bash
> git push origin --all
```

###  10. <a name='PATorPersonalAccessToken'></a>PAT or Personal Access Token

Github will stop letting users log in with simple username/password from Friday the 13th [08/13/21]! You can create PAT easily going to [Setting-->DeveloperSetting-->PAT](https://github.com/settings/tokens)


###  11. <a name='Reference'></a>Reference

https://www.jquery-az.com/git-commands/