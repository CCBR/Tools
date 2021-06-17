

[TOC]



### List Branches

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

### Create Branch

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

### Delete Branch

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

### View and Set remote

View:

```bash
> git remote -v
```

Set:

```bash
> git remote add origin "repo URL"
```

### Adding files

```bash
> git add file1							# adds one file
> git add folder1/file1			# adds one file inside a folder
> git add file1 file2 file3 # add multiple files at the same time
> git add . 								# add all files and folders in the current folder
> git add -all							# add all folders in the curre
```

### Removing files

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

### Commiting

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

### Pulling

Download content from remote and merge with local files:

`pull` is basically a `fetch` + `merge`

```bash
> git pull origin master
OR simply
> git pull
```

`origin` is the convention name for the remote repository and `master` is the branch being pulled

### Pushing

To push the currently checkedout branch to remote repo's `master` branch:

```bash
> git push origin master
```

To push multiple (all) branches at the same time

```bash
> git push origin --all
```

### Reference

https://www.jquery-az.com/git-commands/