This is going to recap our entire learnings for Week 1 and also we will cover whatever errors we faced/what broke in detail.

#Day1: System Reverse Engeneering + System and Terminal Mastering

Before we begin with our training bootcamp, the initial steps involve to learn about the system we are going to work on.
Our Day 1 will cover the prominent information about our system and we will cover system inspection, terminal mastering and basic system engineering concepts so that we dont face any difficulties later on to adapt to our system.

**Topics of the Day**
1) OS Inpsection
2) System Inspection
3) Control Node Version 
4) Understand Shell
5) Buffer vs Stream

Lets start our Day 1 and journey with OS inspection-

OS version can be known with: /etc/os-release, this gives us the information for current os version, name etc details.

Using commands like which node, nvm install --lts, nvm use node, node -v to swtich different node version, get information about the path of different node version, get information about current working node version etc.

Then we created a system inspection report wher we gathered information OS, architecture, CPU cores, totam memory, uptime etc.

Last but not the least we completed an exercise on Stream vs Buffer, where we learned that stream divides and processes our data piece by piece/ chunk by chunk while Buffer processes the entire data/file in a single go. While stream is high scalable, risk friendly and requires less memory, Buffer consumes a lot of memory, High memory use and less scalability. 

**Problem Faced:** Understanding of env variables thoroughly and getting used to linux/ubuntu interface.

#Day 2: Node CLI + Concurrency

**Topics of the day**
1) Node CLI Tool
2) Concurrency
3) Benchmarking and storing results


Built an executable Node.js CLI tool using process arguments to analyze large text files and generate word statistics in JSON format.

Improved performance by splitting large files into chunks and processing them in parallel using Promise-based concurrency / worker threads.

Measured and compared execution time at different concurrency levels (1, 4, 8) and stored performance results in structured log files for analysis.

**Problem Faced:** Node js is single thread but how concurrency and worker threads deal with it had to be studied.

#Day3: Git Mastering

**Topics of the Day**
1)Git Bisect
2)Git Revert
3)Git Stash
4)Merge Conflict

Git bisect is used to find the first faulty commit. Git bisect doesnt fetch any error but detects if theres anything acting differently.

Git revert is used to uncommit the earlier faulty commit and fix it and make a new commit.

Git stash is used to temporarily save the uncommited/untracked files in stash so that they stay unaffected and you can work on other branches, files without them being disturbed.

Merge Conflicts arrises when 2 developers work on the same file, same line without following git discipline and without adhering to push pull workflow.

**Problem Faced:** Git bisect and merge conflict were the topic which took time but eventually were sorted.

#Day 4: HTTP/API Forensics
 
**Topics of the Day**
1)Headers
2)Pagination
3)Etag Caching
4)Request Response cycle

Headers are basically the metadata which store the information for the data which is being shared. There are different headers for btoh Request and Response APIs which guide us about whats going to be in them.

Pagination helps us to break the entire data into pages/chunks, which enables us to fetch them in a better way. We use skip and limit here to break them into smaller chunks.

Etag caching is a unique tag which give us information of the cache and returns us with metadata like status code, Status code 200 indicates success while status code 304 refers to not modified.

Request Format: GET Method, then URL, then Headers, then Body
Response Format: Status code, then Headers, then Body

**Problem Faced:** curl output was a bit difficult to read and cache and etag, success code 304 had to be given some time.

#Day 5: Automation and mini CI Pipeline

**Topics of the day**
1)Validate.sh
2)ESLint + Prettier
3)Husky-Git Hooks
4)Build Artifacts
5)Cron job

Validate.sh is a shell script which stops/restricts code before it reaches git/production. Validate.sh checks if src folder exists, logs everything with timesptamps, if conf.json is valid or not, exits if errors appear.

ESLint + Prettier are code quality enhancers which changes bad syntax/ spaces,quotes to look prettir.

Git hooks are scripts that run automatically at certain events like pre-commit, commit-msg and pre-push. Pre commit hook.
Husky is a tool that manages Git Hooks in a clean way.

Install Husky, Enable Husky, Create Pre Commit

Artifacts are snapshots of a project at the point in time such as source code, scripts, logs.

Cron jobs are scheduled automation to run commands on scheduled time.

**Problem Faced:** Husky was not working because 2 git repos were initially initialised but later we had to remove one, or create a new and copy its content in the main repo




