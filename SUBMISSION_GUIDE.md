# Finish the submission

The PDF requests a `.txt` file containing the link to a **public repository**.
That repository must have a folder for each task, containing code and a video
demonstration or a public demonstration link.

## Complete the local work

1. Run all three tasks using START_HERE.txt.
2. Read EXPLAINED.md and practice explaining the code.
3. Privately give the three Task 2 keys to three assigned testers, one each.
4. Have those testers use cURL. Follow `task2_api_keys/TESTER_INSTRUCTIONS.md`.
5. Add sanitized tester evidence to `task2_api_keys/TESTER_RESULTS.md`.
6. Review the videos. Replace them or add your own recording if your instructor
   expects you to narrate or demonstrate personally.

## Publish a clean copy on GitHub

The simplest upload path is a **fresh extraction of the supplied ZIP**. This
avoids uploading the virtual environment, databases and secrets created while
running your working copy. Copy only your reviewed, sanitized changes into that
fresh extraction before uploading it.

1. Sign in to your own account at [GitHub](https://github.com/).
2. Create a new repository named `software-engineering-assignment-1`.
3. Set visibility to **Public**. The supplied files already include a README and
   `.gitignore`, so leave GitHub's initialization options unselected.
4. Use the repository's file-upload option. Upload the CONTENTS of the fresh
   `assignment_1` folder, preserving the three task folders. Do not upload only
   the ZIP file. Include the supplied `.gitignore`.
5. Review the file list and commit the upload. Each task folder should contain
   its source files, README and demo.mp4.
6. Open the repository URL in a private/incognito browser window. Confirm it is
   readable without signing in and that each demonstration can be accessed.

`.gitignore` affects Git's normal tracking commands. It does not stop you from
manually uploading a secret through a browser. Do not upload `private_consumers`,
`api_keys.json`, `.session_secret`, databases, cookies, password files or `.venv`.

Official instructions: [create a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)
and [upload files](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository).

## Make the required text file

Open Notepad and paste the URL of the public repository you actually created.
Save it as `submission.txt` (not `submission.txt.txt`). Its contents should be one
real URL, for example the shape below:

```text
https://github.com/YOUR_USERNAME/software-engineering-assignment-1
```

`YOUR_USERNAME` is an example placeholder. Replace it with your actual account
name and verify the link before submitting. No public repository was created
as part of this package, so there is no real submission URL yet.

## If a video will not preview

The MP4 remains downloadable from the task folder. Alternatively, upload your
demonstration to a video service with public or link-access viewing, then place
the real URL in that task's DEMONSTRATION.md. Verify that the instructor can
open it without requesting access. Keep API keys and passwords off screen.
