# Báo cáo & Tài liệu Thuyết trình Dự án FloodRoute HCMC

Thư mục này chứa các tài liệu báo cáo kỹ thuật, mã nguồn LaTeX và bộ slide thuyết trình phục vụ bảo vệ đồ án.

## 1. Bộ Slide Thuyết Trình (Presentation Slides)

- [`presentation_slides.pptx`](presentation_slides.pptx): **Microsoft PowerPoint Slide Deck** xuất bản từ Marp (24 slides hoàn chỉnh).
- [`presentation_slides.html`](presentation_slides.html): **Interactive Web Slide Deck** chạy trực tiếp trên trình duyệt (Dark Glassmorphism, MathJax LaTeX, phím tắt `Left`/`Right`/`Space`/`F`/`O`, thanh tiến trình và bộ Flashcards vấn đáp).
- [`presentation_slides.md`](presentation_slides.md): **Markdown Slide Deck** chuẩn 24 slides tương thích Marp, Reveal.js, Pandoc để xuất PDF hoặc PPTX.

## 2. Báo Cáo Kỹ Thuật (Technical Reports)

- [`FloodRoute_HCMC_Technical_Report.md`](FloodRoute_HCMC_Technical_Report.md): Báo cáo kỹ thuật chi tiết 10 chương mục chuẩn (a–j).
- [`FloodRoute_HCMC_Technical_Report.html`](FloodRoute_HCMC_Technical_Report.html): Bản HTML định dạng hoàn chỉnh của báo cáo kỹ thuật.
- [`FloodRoute_HCMC_Technical_Report.pdf`](FloodRoute_HCMC_Technical_Report.pdf): Bản PDF xuất bản chuẩn.

## 3. Mã Nguồn LaTeX Báo Cáo

- [`main.tex`](main.tex): File LaTeX chính theo mẫu chuẩn HCMUS.
- [`hcmus-report-template.sty`](hcmus-report-template.sty): Style package HCMUS.
- `content/`: Các chương mục nội dung LaTeX phân tách.
- `ref/`: Thư viện tài liệu tham khảo BibTeX và hình ảnh.

## 4. Artefact tạm

Log biên dịch, file trung gian LaTeX (`.aux`, `.toc`, `.nav`, ...) và ảnh
render kiểm tra không thuộc source tree. Các file này được ignore trong
`.gitignore` và có thể tạo lại khi build report/slides.
