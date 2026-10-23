# SARU 1.6.0 social connections and release updates

Open Social Media > Connect social accounts. Enter the Graph API version supported by your Meta app, WhatsApp Phone Number ID and access token, and/or Facebook Page ID and Page access token. Tokens are stored inside the existing Windows DPAPI-protected keys dictionary. Do not paste tokens into chat or GitHub.

Use Write WhatsApp message or Write Facebook Page post. Review the destination and exact text, then approve the request. WhatsApp API acceptance is not proof of delivery; SARU shows the returned message ID. There is no automatic retry after an ambiguous network failure. Facebook integration publishes text to a Page; it does not publish to a personal profile. WhatsApp uses a Business account; ordinary personal WhatsApp Web remains a manual draft workflow. Account permissions, eligible recipients/conversations and Meta account setup are required. Incoming messages, media, templates, scheduling and personal-account browser automation are not implemented.

Open Update Center > Configure repository / automatic checks and downloads. Supply your trusted owner/repository or GitHub repository URL. Enable launch/six-hour checks and optional verified downloads. Publish a stable vMAJOR.MINOR.PATCH GitHub release containing SARU_AI_*.zip and the exactly matching .zip.sha256 file. SARU downloads only newer releases; installing still requires closing SARU and running the downloaded setup wizard. No repository is preconfigured. Existing source upgrades preserve separately stored AppData settings/memory.

GitHub SKILL.md files are instructions/code for particular runtimes; they are not automatically compatible SARU plugins. This release does not import or execute arbitrary GitHub skills or modify itself. A real extension requires reviewing its dependencies, permissions, adapter and tests, then shipping it through the trusted SARU release repository.

Official integration references:
- https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages
- https://developers.facebook.com/docs/pages-api/posts/

Validation: five mocked API/update tests, Python compile checks and isolated Windows dashboard GUI smoke test. No production message/post has been sent and no real GitHub release has been downloaded in this change.
