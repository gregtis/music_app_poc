Project Name: Music App POC
Project Summary: A fun simple app like something that would be found in a Nintendo museum. The app runs on a ras pi and has a touch screen and spreakers. you will have access to:
/dev/fb0        ← screen
/dev/input/event5  ← touchscreen
/dev/snd        ← audio

The app will show several nintendo characters, and allow the user to touch them on the screen. This brings you to a screen for that charcter where music from their series will play. you can play/pause and switch songs. You can switch to different versions of the same song, or different eras of music for that character. 

Hardware/Environment: App will run on Ras Pi without desktop environment. It will run in a docker container. Rough plan is to build the app locally on laptop, push to GitHub, then SSH into Pi, pull the repo, build and run the docker container.

Core Features:
- Simple, fun with no extra frills.
- Nintendo like aura
- Kids can use it.
- Extensible, easy to add to.
- No extra features.

Style/Vibe: Nintendo-like

Technical Requirements:
- Development environment: Development on Windows machine with WSL Ubuntu environment (using Claude Code) that is SSH into Raspberry Pi.
- Use git for version source control locally.
- Create  folder with all necssary files for the program. This folder will be placed onto the raspi under projects/ in its own folder. 
- Files would include claude.md, docker-compose.yml, Dockerfile, public folder/index.html, QUICKSTART.md, and scripts folder/deploy.sh
- The folder/files should be deployed to the raspi with git.
- I will use the following command to 'start the program' by creating a live docker instance to run it on the pi: sudo docker compose up -d.

---

PHASE 0 — CLARIFY BEFORE ANYTHING ELSE

Do NOT write any code, files, or plans yet.

Step 1: Ask me exactly 10 clarifying questions about this project.
- Group them into: Technical, UX/Behavior, and Constraints
- For each question, give 3 multiple-choice options (A, B, C)
- Mark your recommended option with a ★ and briefly explain why
- Wait for ALL my answers before proceeding

Step 2: After I answer, reflect back a one-paragraph summary of what
we're building and confirm I agree before moving on.

---

PHASE 1 — PLANNING (only after Phase 0 is complete)

Once confirmed, generate:
1. A "Master Plan" broken into phases (Phase 1 = MVP, Phase 2 = polish, Phase 3 = stretch)
2. A tasks.md file I can use to track progress
3. Identify the single riskiest technical decision and explain why

---

PHASE 2 — AI CONTEXT FILE

Generate an AI.md (also called CLAUDE.md) that captures:
- What this project is
- Stack and file structure
- Key decisions we made and why
- What "done" looks like for MVP
- Rules for any future AI session working on this codebase

---

PHASE 3 — SCAFFOLD

Only after I approve the plan:
- Create the folder structure and starter files
- Set up version control with git init + initial commit
- Include a QUICKSTART.md explaining how to run the project
