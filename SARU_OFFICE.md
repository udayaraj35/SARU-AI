# SARU 2.6 Office

Open **SARU Office** from the sidebar or Settings. SARU is the office manager. Research, Writing, Data and Video rooms are supplied initially. Use **New room / agent** to add a role; click a room to change its name, instructions/resources and preferred format. Rooms and agent settings persist locally.

1. Describe the job and select 1–6 agents.
2. Supply reference notes, or attach TXT/MD/CSV/JSON, DOCX, XLSX or a readable text PDF. Review extracted excerpts; scans need OCR elsewhere. Shared context is limited to 30,000 characters.
3. Review the provider and shared content before starting. SARU requests a delegation plan, then runs up to two agent model requests concurrently. Each agent submits a draft/table result to SARU.
4. SARU merges and reviews the submissions. The office shows actual stored states: planning, working, submitted, SARU review, ready for owner review, needs revision, error, approved and saved. Agent submissions can be read below the merged result. Animations reflect work/handoff states; idle or completed rooms do not pretend to be working.
5. Read the merged result and SARU's review. Approve it, choose a format and use **Save to my PC**. The owner selects the destination and confirms any overwrite. Editing preview text does not change the stored reviewed result.

Examples: `open office`, `office task prepare a PDF report from these notes`, `office status`, `मेरो काम के भयो`. A single requested format in the task is suggested automatically; the owner can change the export choice.

Exports are real local files: UTF-8 TXT, Word DOCX, Excel XLSX, PDF and MP4. DOCX/XLSX include supplied result tables. Spreadsheet cells are saved as literal data, not executable formulas. PDFs use rasterized Unicode text pages (not searchable text), up to 20 pages. MP4 makes a silent short text-slide video; it does not generate cinematic footage or narration. Large reports should use DOCX/TXT. SARU's existing Video/Publishing Studio and MoneyPrinterTurbo remain separate workflows.

The office uses the owner's configured model/provider/key and can make several billed model requests. Tests use a deterministic fake provider for delegation/review, and real local document, spreadsheet, PDF and FFmpeg exports. No paid/live model call, web browsing, application input, account action or publication was performed by the tests. These agents currently draft text/tables/scripts from supplied material; their role instructions do not grant arbitrary PC tools, web access or shell execution. Source facts and AI review still need owner verification.

Jobs, submissions, reviews and export records are stored under the SARU data directory's `office/office.db`. API keys remain in the existing protected settings store. An interrupted process is marked interrupted on the next office open; it is not reported as completed. Cancellation stops further accepted results after in-flight requests return. Create a new job to retry or revise.

The public [Inventor Usman site](https://inventorusman.com/) was reviewed for its broad agent/memory/tool architecture ideas. Its paid course and private source were not accessed or copied. SARU Office is implemented in this application. A later user-supplied video can guide further layout/behavior changes.
