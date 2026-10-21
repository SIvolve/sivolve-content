# SIvolve Weekly — shared spiral-revision quizzes

The public repository publishes one complete, immutable JSON quiz per ISO week at:

`weekly/archive/YYYY-WNN.json`

The iOS/web app requests the snapshot for the current `Australia/Melbourne` week; it never generates student-specific Weekly questions or falls back to an old quiz if publication is unavailable.

## Selection

Released topics are sorted using `weekly/curriculum_order.json`, based on VCAA Physical Education Study Design key-knowledge order (not Git commit dates).

- 1 topic: all ten questions from that topic.
- 2 topics: four from the earlier, six from the newest.
- 3+ topics: split consecutive topics into three near-equal groups, distributing any remainder towards earlier groups, and draw 3 earlier / 3 middle / 4 recent questions.
- If the most recent group contains multiple topics, exactly two of its four questions come from the newest individual topic. If it contains only one topic, that topic supplies the entire group quota.
- Overall types: 3 Foundation / 4 Application / 2 Stimulus / 1 SAC-style.
- Questions and topics recently seen in the previous six Weekly archives are deprioritised when valid alternatives exist. The final question order is fixed in the snapshot.
- No unreleased content. If these constraints cannot be satisfied, publication **fails**; the app will not substitute another quiz.

## Publication

The GitHub Actions workflow `.github/workflows/publish-weekly.yml` runs Sunday at 13:15 and 14:15 UTC. Those cover Monday 00:15 in Melbourne in daylight and standard time respectively; the generation script checks the Melbourne weekday and skips the wrong run. GitHub Actions scheduling can be delayed; do not promise publication to the minute.

A manual `workflow_dispatch` generates the *current* Melbourne week even on a non-Monday, provided it does not already exist. Archive creation is create-only, and a re-run skips the published week. No force pushes or file replacement are used. Published files must not be manually edited; protect the branch if necessary.

To run tests in the content repo:

`python3 -m unittest discover -s weekly/tests -v`

To publish locally for inspection (does not upload to GitHub):

`python3 -m weekly.publish_weekly --manual`

**Caution:** Do not run that command in the live clone unless you intend to stage the newly created archive; the automation is normally responsible for publication.

When expanding to Units 1, 3 or 4, add their new topic names and study-design sequence numbers to `curriculum_order.json` *before* marking those topics `released` in `config.json`.

## Privacy and access

Published snapshots contain full questions, options, answers and feedback, matching the existing public question-bank model. Student performance data stays in local device storage; cloud sync and teacher dashboards are separate future features.
