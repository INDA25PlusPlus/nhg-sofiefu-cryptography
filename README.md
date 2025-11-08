# Cryptography assignment in python


### Working together with branches
Our code is in the main branch. We dont want to directly make edits in the main branch and push it,
in case we change something important the other person wrote. Instead, we make a branch through:
`git checkout -b new_branch_name`

To check which branch you are on: 
`git branch`

To merge our changes with existing changes, we make a so called pull request: 
1. `git add .`
2. `git commit -m "message"`
3. `git push` 
On the third step the terminal will suggest you run something like git push set-upstream blabla 
and you are supposed to run that but i cant remember it so i first run git push to make it suggest it. 
After that, you will get a link to github where you click on a button to create the pull request. 

You or your partner review the PR and if its approved, it will be merged with the main branch. 

Sometimes while working on a branch there are new merges to main, then simply run
`git pull`