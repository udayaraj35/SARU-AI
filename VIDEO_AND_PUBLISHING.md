# SARU 2.0.0 — Video creation and approval-based publishing

Open **YouTube & Video** or **Social Media > Video Studio**. Chat also accepts `create video`, `video studio` and `publish video`.

## Create locally
Choose 1–30 photos in order, enter one caption per photo, choose landscape 16:9 or portrait 9:16, and 1–15 seconds per photo. Optionally choose your own audio file. SARU renders an H.264 MP4 on your PC using FFmpeg, without uploading source material. This is a photo/caption slideshow editor, not a generative cinematic video service. Encoder threads are bounded and rendering runs off the UI thread.

## Connect accounts
- **YouTube:** Enable YouTube Data API v3 in your own Google Cloud project, create a Desktop OAuth client JSON, and use Accounts > Connect YouTube to choose that file. You perform the Google browser sign-in/consent yourself. SARU uses an ephemeral localhost callback with state validation and PKCE. OAuth credentials/refresh token are saved only inside the existing Windows DPAPI-encrypted keys store. Google verification/test-user restrictions may apply; some API projects are limited to private uploads.
- **Facebook:** Connect a Facebook Page ID, Page access token and supported Graph API version in Social accounts. The token needs the relevant Page content/video permissions and the account must have Page access. Personal-profile automation is not added.
- **TikTok:** Save an authorized access token with `video.publish` scope in Accounts. Load creator information to get the available visibility choices and duration limits. SARU honors creator-disabled interactions. TikTok developer app approval/audit and platform restrictions apply; unaudited clients cannot publish publicly. This release does not create/audit a TikTok app or implement a public OAuth callback service for TikTok.

Never paste access tokens into chat or commit them to Git.

## Review and approve
1. Load the exact connected destination account.
2. Choose an MP4 (up to 64 MiB), title, description, visibility and relevant audience/disclosure/interaction settings.
3. Press Prepare exact draft. SARU makes a separate local copy and hashes its contents. No upload occurs.
4. Open Preview prepared video and inspect it. The frozen review shows the account, visibility, title, caption, disclosures and SHA256. Edits in the form require preparing a new draft.
5. Approve that exact draft using the final confirmation. SARU rechecks video integrity and account identity before uploading.
6. Keep the returned server operation ID. API acceptance is not proof that processing/publication finished. Use Check submitted video processing/status to inspect server status. Recent drafts/receipts survive restarts.

Every approved draft can be claimed only once. Content/metadata changes invalidate approval. Uncertain failures enter `needs_check` and are not automatically retried; inspect the destination account before preparing any replacement. No uploads run automatically on launch. After a crash, drafts marked uploading/needs_check require human inspection. Review copies and receipts are local under `%APPDATA%\SARU_AI\content_studio`; tokens are not copied there.

## Responsiveness work
The PC screen was inspected and the running 1.9.1 dashboard/chat panel responded. Voice was stopped in that observed state. No definitive cause of the intermittent user-reported freeze was established. This update avoids unnecessary same-color widget/ttk style reconfiguration, reduces full native audio/display reads to every third telemetry cycle, and stops rebuilding the chat dock for every transcript fragment. Voice text chunks render as a continuous message. Escape now correctly exits fullscreen.

## Validation and limits
Approval, metadata/video tampering, duplicate submission, uncertain network outcomes, account mismatch and all three platform request paths were tested with mocked services. A real 2-second H.264 MP4 was generated and decoded locally. Studio tabs and dashboard/Settings/fullscreen/theme/slider routes were checked with isolated GUI tests. Production OAuth login, real uploads and platform publication were not tested because user account authorization is still required. No test post was published.

Official references:
- https://developers.google.com/youtube/data/guides/using_resumable_upload_protocol
- https://developers.google.com/youtube/data/reference/rest/v3/videos/insert
- https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post
- https://github.com/facebook/facebook-python-business-sdk/blob/main/facebook_business/adobjects/page.py
