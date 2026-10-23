# SARU Office workspace · 2.7.0

Home is now an office floor rather than a small preview. Use Full screen to expand it. Chat and voice stay at the bottom; Controls reveals the existing device/provider panels.

Click Mind to inspect the configured provider/model, delegated tasks, saved review and local queue events. This is operational state, not private model reasoning. Click Memory to open the existing saved-notes workflow. Team rooms open the existing agent configuration. The complete Office opens with a large floor; Task desk reveals assignment/review/export controls, and + Room adds an agent.

Assignment changes drive finite routes: collect an assignment, return to the desk, work, deliver a completed draft, and return home. Routes go through the side aisles and corridor. Monitor activity and room badges reflect stored assignment states. Animation is a visualization, not a progress estimate or evidence of browser/PC actions. It never delays or starts paid AI work.

Idle agents query the local office task queue every 30 seconds while an office view is open, staggered across the team. Each inquiry is recorded in the bounded local event log. There are no repeated cloud requests and no invented jobs. Existing approved job execution remains responsible for dispatching queued assignments. Reduced-motion mode stops movement and monitor animation.

Navigating away from Office no longer cancels a running job. It continues in the current application process. Reopen Office and select Cancel job to request cancellation; in-flight provider requests must return first. Exiting SARU ends the process, and the next launch records unfinished work as interrupted.

Verification: finite-route, submitted-result, reduced-motion, local queue/event tests; existing delegation/approval/export tests; GUI smoke checks including office rooms, drawer, full screen and three window sizes. Cloud provider quality is not covered by the local tests.
