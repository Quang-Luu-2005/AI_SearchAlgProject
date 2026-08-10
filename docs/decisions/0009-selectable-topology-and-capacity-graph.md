# ADR 0009: Selectable topology và graph benchmark Thủ Đức

- Trạng thái: Accepted
- Ngày: 2026-08-09

## Bối cảnh

Basemap OpenFreeMap hiển thị nhiều POI/đường nhưng các feature này không phải node của
graph UTraffic. API locations của processed pilot cũng chỉ trả sáu POI demo dù graph có
90 node, làm người dùng hiểu rằng nhiều vị trí nhìn thấy trên map không thể chọn.

Cần tách rõ hai mục tiêu: chọn điểm thuận tiện trên basemap và đo giới hạn tải bằng graph
lớn hơn, nhưng không được biến basemap thành nguồn topology runtime hoặc làm thay đổi
release học thuật 90/155 đã đóng băng.

## Quyết định

- `/locations` trả một location duy nhất cho mọi topology node. POI thật được xếp trước;
  node còn lại có tên deterministic từ `road_name` kề.
- Khi chế độ START/GOAL bật, click ngoài circle node được snap tới topology node gần nhất
  trong 200 m. Popup công bố khoảng cách `SNAP`; không tạo virtual edge/node và không gọi
  geocoder runtime.
- Giữ `thu_duc_market_v1.0.0` làm dataset mặc định.
- Thêm `thu_duc_core_capacity_v0.1.0` chỉ để benchmark. Graph được trích từ UTraffic trong
  bbox lõi Thủ Đức, giữ thành phần liên thông mạnh lớn nhất: 3.229 node và 5.057 directed
  edge. Node là `SOURCE_BACKED`; travel time là `DERIVED`; scenario là `ASSUMPTION`.
- Benchmark graph có trạng thái `CAPACITY_BENCHMARK_ONLY`, không được trình bày là release
  flood-aware, real-time hoặc chỉ dẫn an toàn.

## Hệ quả

- Người dùng có thể click POI/đường trên nền và nhận endpoint hợp lệ gần nhất.
- Picker có thể tìm toàn bộ topology; frontend chỉ render tối đa 40 kết quả một lần.
- Catalog có thêm graph lớn để stress-test API, GeoJSON và MapLibre mà không ảnh hưởng
  dataset mặc định.
- A* hiện dùng `h=0`, nên số node explored tương đương UCS; benchmark này đo implementation
  hiện tại, không chứng minh giới hạn production hay SLA.
