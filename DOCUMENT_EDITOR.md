# PDF and Word exact text editor

Say open document editor (or edit pdf / edit word). Choose the source, a NEW output path, exact old text and replacement. Review the exact request and approve. No document content is sent to AI by this editor.

Original overwrite is disabled. If the source changes after review, the edit is rejected. Existing output paths are refused. Successful PDF edits show original/edited page previews. Open DOCX output in Word to verify wrapping/pagination.

DOCX editing preserves original ZIP parts and existing run/style XML. Exactly one occurrence inside a single w:t node is supported, including table/header/footer text. Split-run, ambiguous and signed documents are rejected. Keeping font/size properties does not guarantee identical wrapping or glyph fallback in every Word installation.

PDF editing requires one exact complete horizontal text span. It reuses original Base-14 or reusable embedded font, original size/color/baseline, refuses missing glyphs, overlapping text and width overflow, and checks rendered pixels outside the target area remain unchanged. Scans/OCR, rotated/vertical text, unavailable fonts, encrypted and signature-enabled PDFs need another workflow. It never silently shrinks text or substitutes a font.

No editor can guarantee zero mistakes across arbitrary documents. Review the saved copy before relying on it. This is a bounded text-replacement feature, not arbitrary PDF/Word redesign.

Active local screen view/captured PC Control shows four primary-display corner marks in the current theme. Marks are click-through on Windows and disappear on stop/close or capture error. Color updates follow the shared theme configuration. Capture exclusion uses the supported Windows display-affinity API where available; older Windows versions may include marks in screenshots.

References: https://pymupdf.readthedocs.io/en/latest/page.html and https://python-docx.readthedocs.io/en/latest/api/text.html
