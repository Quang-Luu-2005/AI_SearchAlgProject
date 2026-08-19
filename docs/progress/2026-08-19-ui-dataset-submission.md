# Gỡ thẻ dataset và tạo bundle nộp bài

## Thay đổi

- Gỡ thẻ `Historical traffic · not real-time` khỏi panel frontend, cùng CSS và
  khóa i18n không còn được sử dụng.
- Tạo bundle version hóa tại `data/submission/floodroute_dataset_v1.0.0/` từ
  release landmark 65 node/178 edge đang dùng trong ứng dụng.
- Bundle gồm `nodes.csv`, `edges.csv`, `landmarks.csv`, `scenarios.json`,
  `metadata.json`, `validation_report.json`, `checksums.sha256`, README và
  `submission_manifest.json`.
- Manifest phân biệt `SOURCE_BACKED`, `DERIVED`, `ASSUMPTION`; bundle không
  chứa raw snapshot và không có fixture/simulation không gắn nhãn.

## Kiểm tra

- Xác minh SHA-256 từng file trong bundle.
- Chạy `npm run test:data` sau thay đổi để kiểm tra registry, provenance và
  processed dataset hiện hành.
