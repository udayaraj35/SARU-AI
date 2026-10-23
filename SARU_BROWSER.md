# SARU Browser

Social web buttons open a SARU-owned tabbed Chromium browser window rather than the default Windows browser. Native Windows apps and dedicated Video/YouTube Player studios remain separate features.

Log in directly on the real site; SARU does not collect passwords or OTP codes. Cookies/site data use a separate local AppData/SARU_AI/browser/profile directory. Sites determine how long login persists. Some services may reject embedded-browser login; no authentication restrictions are bypassed.

Commands: open saru browser; browser back; browser forward; browser reload; browser new tab; browser close tab; browser tab 2; browser zoom in; browser zoom out; close saru browser. Explicit voice/text navigation runs directly; substantive file/account/source workflows retain their own reviews.

control saru browser connects its visible window to PC Control. Screen sharing and each proposed click/type retain their existing reviews. Navigation support does not imply universal autonomous operation or permission to send messages/posts.

The browser has tabs, address bar, navigation, zoom, keyboard shortcuts, context menus and a download Save dialog. It is not a full Chrome replacement: extension management, password manager and browser sync are not implemented. Downloads and login must be checked on the site.

The Qt browser runs in a separate child event loop to avoid blocking SARU voice/UI. Commands travel through a private process pipe; websites receive no SARU Python bridge. Chromium security remains enabled.

References: https://doc.qt.io/qtforpython-6/PySide6/QtWebEngineCore/QWebEngineProfile.html
