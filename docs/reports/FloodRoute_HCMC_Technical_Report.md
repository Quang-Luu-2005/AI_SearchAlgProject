# BÁO CÁO KỸ THUẬT: TỐI ƯU HÓA TUYẾN ĐƯỜNG GIAO HÀNG ĐÔ THỊ TP. HỒ CHÍ MINH TRONG ĐIỀU KIỆN KẸT XE VÀ NGẬP NƯỚC (FLOODROUTE HCMC)

**Môn học**: Nhập môn Trí tuệ Nhân tạo (Introduction to Artificial Intelligence)  
**Trường**: Đại học Khoa học Tự nhiên -- Đại học Quốc gia TP. Hồ Chí Minh  
**Khoa**: Công nghệ Thông tin  
**Đề tài**: Lab 1 -- Thuật toán Tìm kiếm Tối ưu Tuyến đường Giao thông Đô thị  
**Mã đồ án**: `FloodRoute_HCMC_v0.1`  
**Ngày cập nhật**: 17/08/2026  

---

## 1. Giới thiệu Nhóm & Phân công Đóng góp

### 1.1. Thông tin Nhóm
- **Tên nhóm**: FloodRoute Team
- **Bảng Trello Quản lý Dự án**: [AI_Project_1 (https://trello.com/b/AGK7CP4q/aiproject1)](https://trello.com/b/AGK7CP4q/aiproject1)
- **Giảng viên hướng dẫn**: TS. Nguyễn Văn Tân

### 1.2. Bảng Phân công Trách nhiệm & Đóng góp Chi tiết

| Thành viên | Tài khoản / MSSV | Thẻ Trello đảm nhiệm | Đóng góp & Trách nhiệm chi tiết | Tỷ lệ đóng góp |
|---|---|---|---|:---:|
| **Lưu Huy Minh Quang** | `lhmquang232`<br>**23127016** | `Card BE-01`<br>`Card BE-02`<br>`Card BE-03` | • **`BE-01`**: Thiết kế mô hình dữ liệu bất biến `Graph`, `Node`, `Edge`, `GraphView`; kiểm soát đồ thị có hướng, deterministic neighbor sorting, phát hiện chu trình.<br>• **`BE-02`**: Xây dựng `ScenarioCostEngine`, 3 kịch bản `BALANCED`, `PEAK_TRAFFIC`, `RAIN_SAFE`, mô hình chi phí 4 thành phần, breakdown chi tiết từng cạnh và xử lý đóng cạnh.<br>• **`BE-03`**: Xây dựng FastAPI Router (`/locations`, `/scenarios`, `/search`, `/compare`), validate schema Pydantic, xử lý lỗi chuẩn và sinh dữ liệu giải thích đường đi. | 25% |
| **Vũ Lê Trọng Văn** | `vuletrngvan`<br>**20127095** | `Card FE-01`<br>`Card FE-02`<br>`Card OPT` | • **`FE-01`**: Xây dựng API client TypeScript, hệ thống controls chọn Start/Goal/Algorithm/Scenario, tích hợp loading/error state và phím tắt.<br>• **`FE-02`**: Tích hợp MapLibre GL JS, hiển thị đồ thị qua GPU layers, phát triển Trace Player (Play/Pause/Step/Speed) và Dashboard hiển thị metrics, explanation.<br>• **`OPT`**: Giải bài toán giao hàng đa điểm (TSP): xây dựng `PairwiseMatrix`, giải thuật chính xác **Held-Karp DP** ($O(N^2 \cdot 2^N)$), giải thuật xấp xỉ **Nearest Neighbor**, đo % Approximation Gap và % Baseline Savings. | 25% |
| **Nguyễn Duy Khang** | `11nguynduykhang`<br>**23127202** | `Card ALG-01`<br>`Card ALG-03`<br>`Card QA-01` | • **`ALG-01`**: Cài đặt thuật toán BFS (Queue) và DFS (Stack) với cơ chế deterministic tie-breaking, ghi nhận trace, và xây dựng các phản ví dụ chứng minh giới hạn của BFS/DFS.<br>• **`ALG-03`**: Cài đặt Greedy Best-First Search và Bidirectional Search, xác định điểm giao nhau và chốt điều kiện dừng, viết ADR Bidirectional Search.<br>• **`QA-01`**: Xây dựng bộ kiểm thử so sánh thuật toán, golden regression test suite, kịch bản demo và kiểm thử tính hợp lệ của hệ thống. | 25% |
| **Ngô Quang Thắng** | `tartzuser`<br>**23127473** | `Card ALG-02`<br>`Card DATA-01`<br>`Card DATA-02` | • **`ALG-02`**: Cài đặt thuật toán UCS và A* Search, phát triển Scenario-aware Cost Lower-Bound Heuristic $h_s(n)=\rho_s D_{\text{Haversine}}(n,Goal)$, chứng minh tính Admissible/Consistent và kiểm tra với UCS.<br>• **`DATA-01`**: Xây dựng pipeline dữ liệu OSM 4 lớp (`raw` $\rightarrow$ `interim` $\rightarrow$ `processed` $\rightarrow$ `fixtures`), quản lý metadata manifest và SHA-256 checksums.<br>• **`DATA-02`**: Map-match danh mục 24 điểm ngập lụt TP. Thủ Đức vào đồ thị, thiết lập kịch bản triều cường/mưa lớn, kiểm định chất lượng dữ liệu (QC) và gán nhãn provenance. | 25% |

### 1.3. Bảng Tự Đánh giá Mức độ Hoàn thành Mục tiêu Đề cương (Rubric Matrix)

| Tiêu chí Đánh giá (Rubric) | Điểm chuẩn | Tự đánh giá | Minh chứng mã nguồn & Kết quả thực tế |
|---|:---:|:---:|---|
| **1. Bối cảnh giao thông Việt Nam & Kịch bản thực tế** | 10 | 10/10 | Bối cảnh shipper giao hàng TP. Thủ Đức, kẹt xe giờ cao điểm và ngập nước triều cường/mưa lớn thực tế. |
| **2. Mô hình đồ thị, tập dữ liệu & Hàm chi phí** | 15 | 15/15 | Đồ thị có hướng bất biến, 3 dataset (Landmark 65, Market 90, Capacity 3229), chi phí tổng hợp 4 thành phần ($D, T_{\text{ff}}, P_{\text{traffic}}, R_{\text{flood}}$). |
| **3. Cài đặt các thuật toán bắt buộc (BFS, DFS, UCS, A\*)** | 20 | 20/20 | 4 thuật toán chuẩn với deterministic tie-break, sinh trace từng bước, chứng minh toán học Heuristic Haversine Admissible/Consistent. |
| **4. Cài đặt các thuật toán mở rộng (Greedy, Bidirectional)** | 10 | 10/10 | Cài đặt Greedy Best-First Search và Bidirectional Search trên đồ thị có hướng chuyển vị; kèm phản ví dụ và ADR. |
| **5. Bài toán tối ưu hóa nhiều địa điểm (TSP)** | 10 | 10/10 | Xây dựng Pairwise Matrix có hướng, giải thuật chính xác Held-Karp DP ($O(N^2 \cdot 2^N)$), Nearest Neighbor, đo % Gap và % Baseline Savings. |
| **6. Giao diện người dùng (GUI) & Trực quan hóa tiến trình** | 10 | 10/10 | Web app React + MapLibre GL JS vector tiles, GPU layers, snap 200m, Trace Player (Frontier/Current/Visited), i18n EN/VI, Responsive. |
| **7. Giải thích tuyến đường & So sánh phương án** | 10 | 10/10 | Tự động sinh diễn giải ngôn ngữ tự nhiên: phân tích thành phần chi phí chiếm ưu thế, chỉ ra đoạn đường gây penalty lớn nhất, so sánh shortest vs fastest vs best cost. |
| **8. Chất lượng Báo cáo Kỹ thuật** | 10 | 10/10 | Đầy đủ 10 chương mục theo chuẩn học thuật HCMUS, số liệu thực nghiệm từ 3.600 lượt chạy benchmark, công thức toán và sơ đồ rõ ràng. |
| **9. Chất lượng Video Demo** | 5 | 5/5 | Video demo trực quan đầy đủ các tính năng, giải thích thuật toán từng bước qua trace player và so sánh kịch bản. |
| **TỔNG CỘNG** | **100** | **100/100** | **Dự án hoàn thành toàn diện 100% các tiêu chí kỹ thuật.** |

---

## 2. Bối cảnh Đề tài Thực tế

### 2.1. Thực trạng Giao thông Đô thị tại TP. Hồ Chí Minh & TP. Thủ Đức
Tại các đô thị lớn của Việt Nam, đặc biệt là TP. Hồ Chí Minh, giao thông đô thị có mật độ phương tiện xe máy rất cao kết hợp với mạng lưới hẻm và đường một chiều dày đặc. Vào các khung giờ cao điểm (07:00 -- 08:30 sáng và 16:30 -- 18:30 chiều), các trục đường huyết mạch khu vực TP. Thủ Đức như **Võ Văn Ngân, Kha Vạn Cân, Đặng Văn Bi, Tô Ngọc Vân, Quốc lộ 13** thường xuyên rơi vào tình trạng ùn ứ nghiêm trọng, làm gia tăng thời gian di chuyển gấp 2--4 lần so với điều kiện lưu thông tự do (*Free-Flow*).

### 2.2. Vấn đề Ngập nước do Triều cường & Mưa lớn
Đặc thù địa hình trũng thấp và hệ thống thoát nước quá tải khiến khu vực xung quanh **Chợ Thủ Đức (đường Dương Văn Cam, Đặng Thị Rành, Kha Vạn Cân, Hồ Văn Tư)** trở thành "rốn ngập" kinh niên mỗi khi có mưa lớn hoặc triều cường dâng cao (mực nước ngập thường từ 0.3m đến 0.6m). Đối với người giao hàng bằng xe máy:
- Đi vào đường ngập sâu gây chết máy, hư hỏng hàng hóa và nguy cơ tai nạn.
- Tuyến đường ngắn nhất về mặt khoảng cách địa lý ($D$) nếu băng qua rốn ngập sẽ trở thành **tuyến đường bất khả thi** hoặc có chi phí rủi ro cực cao.

### 2.3. Mục tiêu Ứng dụng FloodRoute HCMC
Hệ thống **FloodRoute HCMC** giải quyết bài toán:
- **Tìm đường 2 điểm thích ứng động**: Không chỉ dựa trên cự ly hình học, mà kết hợp đồng thời khoảng cách, thời gian lưu thông, mức độ kẹt xe và nguy cơ ngập lụt để đề xuất lộ trình an toàn, tối ưu nhất.
- **Tối ưu hóa hành trình giao hàng đa điểm (TSP)**: Cho phép shipper nhập 1 kho hàng (*depot*) và 5--10 điểm giao hàng (*stops*), từ đó giải thuật tự động sắp xếp thứ tự giao hàng tối ưu nhằm giảm thiểu tổng chi phí, thời gian và nhiên liệu.

---

## 3. Mô hình hóa Bài toán & Hàm Chi phí

### 3.1. Mô hình Không gian Trạng thái (State-Space Formulation)
Bài toán tìm đường được mô hình hóa toán học dưới dạng bài toán tìm kiếm trên không gian trạng thái:
- **Tập trạng thái ($S$)**: Tập hợp tất cả các nút giao thông và địa điểm trọng yếu trên mạng lưới đường bộ ($S = V$).
- **Trạng thái bắt đầu ($s_0$)**: Vị trí xuất phát của shipper ($s_0 = \text{Start} \in V$).
- **Tập hành động ($A(s)$)**: Tập các cạnh có hướng xuất phát từ nút $s$ mà không bị đóng trong kịch bản hiện tại:
  $$A(s) = \{ (s, v) \in E \mid (s, v) \notin \text{ClosedEdges}(\text{Scenario}) \}$$
- **Mô hình chuyển trạng thái ($\text{Result}(s, a)$)**: Khi thực hiện hành động $a = (s, v)$, trạng thái mới đạt được là $v$.
- **Kiểm tra trạng thái đích ($\text{GoalTest}(s)$)**: Kiểm tra xem $s$ có trùng với điểm đích $\text{Goal}$ hay không ($s = \text{Goal}$).
- **Chi phí từng bước ($c(s, a, s')$)**: Chi phí tổng hợp của cạnh $a = (s, s')$ tính theo mô hình chi phí của kịch bản đang chọn.

### 3.2. Mô hình Chi phí Tổng hợp 4 Thành phần (Composite Cost Function)
Chi phí của mỗi cạnh có hướng $e = (u, v)$ được tính toán thông qua hàm tuyến tính có trọng số chuẩn hóa:

$$C(e) = w_{\text{dist}} \cdot D(e) + w_{\text{time}} \cdot T_{\text{ff}}(e) + w_{\text{cong}} \cdot P_{\text{traffic}}(e) + w_{\text{flood}} \cdot R_{\text{flood}}(e)$$

Trong đó:
- **$D(e)$ -- Khoảng cách (Distance)**: Độ dài vật lý của đoạn đường, quy đổi ra kilômét:
  $$D(e) = \frac{\text{distance\_m}(e)}{1000} \quad (\text{km})$$
- **$T_{\text{ff}}(e)$ -- Thời gian lưu thông tự do (Free-flow Time)**: Thời gian di chuyển ở điều kiện đường thông thoáng với vận tốc thiết kế:
  $$T_{\text{ff}}(e) = \text{free\_flow\_time\_min}(e) \quad (\text{phút})$$
- **$P_{\text{traffic}}(e)$ -- Độ trễ do kẹt xe (Traffic Delay Penalty)**:
  $$T_{\text{travel}}(e) = T_{\text{ff}}(e) \times \text{TrafficMultiplier}(e)$$
  $$P_{\text{traffic}}(e) = \max\big(0,\, T_{\text{travel}}(e) - T_{\text{ff}}(e)\big) \quad (\text{phút})$$
  *Lưu ý thiết kế*: Việc tách riêng $P_{\text{traffic}}$ khỏi $T_{\text{ff}}$ giúp chi phí không bị tính trùng lặp thời gian di chuyển cơ sở.
- **$R_{\text{flood}}(e)$ -- Chỉ số Rủi ro Ngập nước (Flood Risk)**: Giá trị chuẩn hóa $R_{\text{flood}} \in [0.0, 1.0]$ dựa trên mức độ ngập lịch sử (0: khô ráo, 1: ngập sâu nguy hiểm).
- **Bộ trọng số ($w_{\text{dist}}, w_{\text{time}}, w_{\text{cong}}, w_{\text{flood}}$)**: Thỏa mãn điều kiện chuẩn hóa $w_i \ge 0$ và $\sum w_i = 1.0$.

### 3.3. Các Thiết lập Kịch bản Chuẩn (Cost Presets)

| Preset ID | $w_{\text{dist}}$ | $w_{\text{time}}$ | $w_{\text{cong}}$ | $w_{\text{flood}}$ | Mục tiêu Tối ưu hóa |
|---|:---:|:---:|:---:|:---:|---|
| **BALANCED** | 0.25 | 0.30 | 0.20 | 0.25 | Cân bằng hài hòa giữa cự ly, thời gian, kẹt xe và an toàn ngập nước (mặc định). |
| **PEAK_TRAFFIC** | 0.15 | 0.25 | 0.45 | 0.15 | Ưu tiên cao nhất cho việc tránh các điểm nóng kẹt xe trong giờ cao điểm. |
| **RAIN_SAFE** | 0.10 | 0.25 | 0.15 | 0.50 | Ưu tiên tối đa việc đi vòng qua các tuyến đường ngập sâu khi trời mưa to / triều cường. |

Các giá trị trên là **hệ số ưu tiên mô phỏng/empirical**, không phải phần trăm
đóng góp thực tế của từng thành phần: distance (km), free-flow time (phút),
traffic penalty (phút) và flood risk ([0, 1]) có đơn vị và scale khác nhau.
Road closure không được biểu diễn bằng một weight nhỏ; đây là **hard
constraint**. Cạnh đóng có `total_cost = null` và không thể xuất hiện trong
route, bất kể profile đang chọn. Public API hiện chốt ba profile trên; custom
weights chưa mở trong phạm vi deadline để giữ contract ổn định.

### 3.4. Hai ví dụ route thay đổi để trình bày

| Ví dụ | Điều kiện | Tuyến trước | Tuyến sau | Diễn giải |
|---|---|---|---|---|
| `EX01_TOY_PROFILE_AND_RAIN` (`SIMULATED`) | `N01 → N06`, `OFFPEAK_BALANCED` → `HEAVY_RAIN_SAFE` | `N01 → N02 → N06`, cost `2.343000` | `N01 → N02 → N04 → N06`, cost `2.562625` | `E03/E04` bị đóng như hard constraint; route buộc đi vòng qua `E11/E09`. |
| `EX02_TOY_ALTERNATIVE_RAIN` (`SIMULATED`) | `N05 → N01`, off-peak → heavy rain | 3 cạnh, cost `3.733000` | 4 cạnh, cost `3.713250` | `E04` đóng; tuyến mô phỏng đổi sang detour qua `E10/E12`. |

Ở fixture toy, `PEAK_TRAFFIC` giữ nguyên tuyến vì topology nhỏ và tuyến đó vẫn
đủ rẻ, nhưng cost tăng từ `2.343000` lên `2.920900` và ETA tăng từ `5.560` lên
`8.062` phút. Đây là cách giải thích đúng: tăng congestion weight làm phạt
delay mạnh hơn; nó có thể đổi route khi có alternative đủ cạnh tranh, nhưng
không được hứa rằng route luôn đổi.

---

## Active dataset scope

The application keeps only `thu_duc_landmarks_v1.0.0` as its selectable
processed map: 65 nodes and 178 derived road-path edges. The former 90-node
processed map is retired; raw provenance is unchanged.

## 4. Tập Dữ liệu & Quy trình Quản lý

### 4.1. Quy trình Xử lý Dữ liệu 4 Tầng (4-Tier Data Pipeline)
1. **`data/raw/` (Bất biến)**: Snapshot OpenStreetMap (`osm_relation_19407794.geojson`), snapshot Kaggle UTraffic (8.952 nodes, 14.043 edges), và danh mục 24 điểm ngập lịch sử. Khóa cấm sửa đổi, kiểm tra toàn vẹn bằng SHA-256.
2. **`data/interim/` (Dữ liệu trung gian)**: Lưu trữ các graph dạng thô sau khi trích lọc theo Bounding Box địa lý.
3. **`data/processed/` (Tập dữ liệu phát hành)**: Các graph chính thức phục vụ chạy ứng dụng và thực nghiệm khoa học.
4. **`data/fixtures/` (Môi trường kiểm thử)**: Các đồ thị kích thước nhỏ phục vụ unit test và golden validation (`toy_graph_v0.1`).

### 4.2. Chi tiết 3 Bản Phát hành Dữ liệu (Processed Releases)

| Tên Dataset | Số Đỉnh ($V$) | Số Cạnh ($E$) | Trạng thái Dữ liệu | Mục đích Sử dụng |
|---|:---:|:---:|---|---|
| **`thu_duc_landmarks_v1.0.0`** | **65** POI | **178** Cạnh | `LANDMARK_DEMO` | 65 địa điểm lớn có tên thật từ OSM (Trường ĐH, Bệnh viện, Chợ); cạnh lưu tọa độ polyline thực tế từ UTraffic. Mặc định trên GUI. |
| **`thu_duc_core_capacity_v0.1.0`** | **3.229** Nút | **5.057** Cạnh | `CAPACITY_ONLY` | Mạng lưới giao thông lõi TP. Thủ Đức phục vụ đo đạc hiệu năng và stress-test thuật toán. |

### 4.3. Hệ thống Nhãn Dữ liệu Minh bạch (Provenance Transparency)
- `SOURCE_BACKED`: Dữ liệu có nguồn trích xuất xác thực từ OpenStreetMap hoặc UTraffic.
- `DERIVED`: Dữ liệu được tính toán qua công thức xác định (cự ly Haversine, Free-flow time).
- `SIMULATED / ASSUMPTION`: Dữ liệu mô phỏng tham số giao thông (hiển thị rõ trên GUI để đảm bảo tính liêm chính học thuật).
- `REVIEW_REQUIRED`: Dữ liệu map-matching ngập nước đang chờ thẩm định bổ sung.

---

## 5. Cơ sở Lý thuyết & Nguyên lý Thuật toán

### 5.1. Thuật toán Tìm kiếm Không Trọng số (Unweighted Search)
- **Breadth-First Search (BFS)**: Cấu trúc FIFO Queue (`collections.deque`). Khám phá đều theo từng mức độ sâu; đảm bảo tìm được đường đi có **số chặng ít nhất (*minimum hop count*)**.
- **Depth-First Search (DFS)**: Cấu trúc LIFO Stack kết hợp tập `expanded` chống lặp chu trình. Khám phá sâu dọc theo từng nhánh đường trước khi quay lui (*backtracking*); không đảm bảo tính tối ưu chi phí.

### 5.2. Thuật toán Tìm kiếm Có Trọng số (Weighted Search)
- **Uniform Cost Search (UCS / Dijkstra)**: Cấu trúc Min-Heap (`heapq`), khóa sắp xếp là hàm $g(n)$ (chi phí tích lũy từ Start đến $n$). Đảm bảo tìm được đường đi có **tổng chi phí $C^*$ nhỏ nhất** khi mọi chi phí bước $c(e) \ge 0$.
- **A\* Search**: Cấu trúc Min-Heap với hàm đánh giá $f(n) = g(n) + h_s(n)$ và
  Scenario-aware Cost Lower-Bound Heuristic:
  $$\rho_s = \min_{e\ \text{open}} \frac{Cost_s(e)}{D_{\text{Haversine}}(e)},\qquad
  h_s(n) = \rho_s \cdot D_{\text{Haversine}}(n, \text{Goal})$$
  Trong đó cạnh đóng và cạnh có khoảng cách Haversine gần 0 không tham gia tính
  $\rho_s$; scenario được freeze trong một lần search.

### 5.3. Chứng minh Toán học về Tính Đúng đắn của Heuristic

> **Định lý 1 (Tính Chấp nhận được -- Admissibility)**:  
> Với mọi cạnh mở, $Cost_s(e) \ge \rho_s D_{\text{Haversine}}(e)$ theo định nghĩa của
> $\rho_s$. Vì vậy $h_s(n) = \rho_s D_{\text{Haversine}}(n, \text{Goal})$ là lower bound
> và thỏa mãn $0 \le h_s(n) \le h^*(n)$ khi cost không âm và scenario tĩnh.
> 
> *Chứng minh*:
> 1. Khoảng cách đường cong trắc địa $D_{\text{Haversine}}(n, \text{Goal})$ là khoảng cách vật lý ngắn nhất giữa hai điểm trên bề mặt Trái Đất. Do đó, $D^*(n, \text{Goal}) \ge D_{\text{Haversine}}(n, \text{Goal})$.
> 2. Mọi thành phần chi phí trong hàm mục tiêu ($T_{\text{ff}}, P_{\text{traffic}}, R_{\text{flood}}$) và các trọng số $w_i \ge 0$.
> 3. Trên một đường đi, tổng Haversine của các cạnh không nhỏ hơn Haversine từ $n$ đến Goal theo bất đẳng thức tam giác.
> 4. Do đó tổng cost của đường đi không nhỏ hơn $\rho_s D_{\text{Haversine}}(n, \text{Goal}) = h_s(n)$.
> 5. $\implies h_s(n)$ **Admissible** (A* vẫn bảo đảm nghiệm tối ưu toàn cục). ■

> **Định lý 2 (Tính Nhất quán / Đơn điệu -- Consistency / Monotonicity)**:  
> Với mọi cạnh mở $e = (n, n')$, hàm heuristic thỏa mãn $h_s(n) \le c_s(n, n') + h_s(n')$.
> 
> *Chứng minh*:
> 1. Theo bất đẳng thức tam giác cầu: $D_{\text{Haversine}}(n, \text{Goal}) \le D_{\text{Haversine}}(n, n') + D_{\text{Haversine}}(n', \text{Goal})$.
> 2. Nhân hai vế với $\rho_s \ge 0$: $h_s(n) \le \rho_s D_{\text{Haversine}}(n, n') + h_s(n')$.
> 3. Theo định nghĩa $\rho_s$, $\rho_s D_{\text{Haversine}}(n, n') \le c_s(n, n')$ trên mọi cạnh mở.
> 4. $\implies h_s(n) \le c_s(n, n') + h_s(n') \quad \forall (n, n') \in E$, nên $h_s(n)$ **Consistent**. ■

### 5.3.1. Kiểm chứng trên fixture

Benchmark tái lập `npm run benchmark:lower-bound` chạy 5 cặp Start--Goal trên
ba scenario `OFFPEAK_BALANCED`, `PEAK_TRAFFIC` và `HEAVY_RAIN_SAFE` (15 case).
Kết quả chi phí A* trùng UCS ở cả 15/15 case; A* khám phá không quá UCS ở
15/15 case. Bảng chi tiết nằm tại
`experiments/results/astar_ucs_lower_bound_v1.md` và được gắn nhãn
`DERIVED_BENCHMARK` trên fixture `SIMULATED`.

### 5.4. Thuật toán Tìm kiếm Mở rộng
- **Greedy Best-First Search**: Min-Heap với hàm đánh giá $f(n) = h(n)$. Tốc độ cực nhanh nhưng không đảm bảo tính tối ưu.
- **Bidirectional Search (Tìm kiếm Hai đầu)**: Duyệt đồng thời hai luồng BFS thuận (Forward từ Start) và nghịch (Backward từ Goal trên đồ thị chuyển vị). Giảm không gian tìm kiếm từ $O(b^d)$ xuống $O(2 \cdot b^{d/2})$.

### 5.5. Bảng Mô phỏng Từng bước Duyệt Nút (Trace Walkthrough)
Xét đồ thị mẫu 4 nút: $A \xrightarrow{c=2, h=5} B \xrightarrow{c=4, h=0} D$ và $A \xrightarrow{c=5, h=3} C \xrightarrow{c=1, h=0} D$ với $\text{Start}=A, \text{Goal}=D$.

| Bước | Thuật toán | Nút mở rộng (EXPAND) | Danh sách Frontier Mở (Nút, $g$, $h$, $f$) | Nút đóng (CLOSE) | Ghi chú Trạng thái |
|:---:|---|---|---|---|---|
| 1 | **UCS** | $A$ ($g=0$) | $[(B, g=2), (C, g=5)]$ | $\{A\}$ | Mở rộng $A$, phát hiện $B$ và $C$. |
| 2 | **UCS** | $B$ ($g=2$) | $[(C, g=5), (D, g=6)]$ | $\{A, B\}$ | $B$ có $g=2$ nhỏ nhất. Thêm $D$ ($g=6$). |
| 3 | **UCS** | $C$ ($g=5$) | $[(D, g=6)_{\text{qua } C}, (D, g=6)_{\text{qua } B}]$ | $\{A, B, C\}$ | $C$ có $g=5$. Thêm $D$ qua $C$ ($g=6$). |
| 4 | **UCS** | $D$ ($g=6$) | Đích đạt được | $\{A, B, C, D\}$ | Nghiệm tối ưu: $A \to B \to D$ ($C = 6.0$). |
| 1 | **A\*** | $A$ ($f=5$) | $[(B, g=2, h=5, f=7), (C, g=5, h=3, f=8)]$ | $\{A\}$ | $A$ khởi tạo với $h(A)=5$. |
| 2 | **A\*** | $B$ ($f=7$) | $[(D, g=6, h=0, f=6), (C, g=5, h=3, f=8)]$ | $\{A, B\}$ | $B$ có $f=7 < f(C)=8$. Thêm $D$ ($f=6$). |
| 3 | **A\*** | $D$ ($f=6$) | Đích đạt được | $\{A, B, D\}$ | **A\* dừng sớm, không cần duyệt $C$**! |

---

## 6. Kiến trúc Hệ thống & Luồng Thực thi

### 6.1. Sơ đồ Kiến trúc Phân lớp (Clean Architecture)
Hệ thống tuân thủ nghiêm ngặt nguyên lý kiến trúc sạch, phân tách độc lập các tầng:
- **Frontend Layer (React + MapLibre GL JS)**: Giao diện điều khiển, render bản đồ vector tiles qua GPU layers, Trace Player phát lại từng bước duyệt nút, Dashboard thống kê.
- **API Layer (FastAPI)**: Router tiếp nhận request, validate dữ liệu qua Pydantic Schemas, điều phối dịch vụ.
- **Core & Domain Services**: `SearchService`, `TourOptimizerService`, `ScenarioCostEngine`, `ExplanationEngine`.
- **Algorithm Engine (Pure Python)**: Bộ cài đặt thuần Python của 6 thuật toán tìm kiếm và 2 thuật toán TSP; độc lập hoàn toàn với framework Web.
- **Data & Contracts Layer**: Hợp đồng dữ liệu bất biến (`Graph`, `GraphView`, `Node`, `Edge`, `Scenario`).

### 6.2. Luồng Xử lý Tìm kiếm 2 Điểm
1. **Người dùng**: Chọn Start, Goal trên bản đồ (snapping 200m), chọn Kịch bản và Thuật toán.
2. **React $\to$ FastAPI**: Gửi request `POST /api/v1/search`.
3. **FastAPI $\to$ Core Engine**: Thực thi thuật toán trên `GraphView` với trọng số kịch bản từ `ScenarioCostEngine`.
4. **Thuật toán $\to$ Trace Logger**: Ghi nhận toàn bộ sự kiện (`OPEN`, `EXPAND`, `RELAX`, `CLOSE`, `GOAL`).
5. **Explanation Engine**: Phân tích đóng góp chi phí và sinh diễn giải ngôn ngữ tự nhiên.
6. **FastAPI $\to$ React**: Trả về payload JSON; React vẽ Polyline lộ trình và kích hoạt Trace Player trực quan.

---

## 7. So sánh Thuật toán & Kết quả Thực nghiệm

### 7.1. Bảng So sánh Lý thuyết Toàn diện giữa 6 Thuật toán

| Tiêu chí | BFS | DFS | UCS (Dijkstra) | A\* Search | Greedy Best-First | Bidirectional BFS |
|---|---|---|---|---|---|---|
| **Cấu trúc Dữ liệu** | Hàng đợi FIFO (Queue) | Ngăn xếp LIFO (Stack) | Min-Heap Priority Queue | Min-Heap ($g+h$) | Min-Heap ($h$) | 2 Hàng đợi song song |
| **Độ phức tạp Thời gian** | $O(b^d)$ | $O(b^m)$ | $O(b^{1 + \lfloor C^*/\epsilon \rfloor})$ | $O(b^d)$ | $O(b^m)$ | $O(2 \cdot b^{d/2})$ |
| **Độ phức tạp Bộ nhớ** | $O(b^d)$ | $O(b \cdot m)$ | $O(b^{1 + \lfloor C^*/\epsilon \rfloor})$ | $O(b^d)$ | $O(b \cdot m)$ | $O(2 \cdot b^{d/2})$ |
| **Tính Đầy đủ (Complete)** | Có ($b < \infty$) | Có (đồ thị hữu hạn) | Có ($c(e) \ge \epsilon > 0$) | Có ($h$ Admissible) | Không (dễ kẹt lặp) | Có |
| **Tính Tối ưu (Optimal)** | Chỉ tối ưu số chặng | Không tối ưu | **Tối ưu chi phí $C^*$** | **Tối ưu chi phí $C^*$** | Không tối ưu | Chỉ tối ưu số chặng |
| **Yêu cầu Heuristic** | Không | Không | Không | Bắt buộc ($h \le h^*$) | Bắt buộc | Không |

### 7.2. Kết quả Thực nghiệm Khoa học từ 3.600 Lượt chạy Benchmark
Số liệu được trích xuất trực tiếp từ artifact chuẩn `experiments/results/search_benchmark_v1.json` (10 cặp O-D $\times$ 3 kịch bản $\times$ 6 thuật toán $\times$ 20 lần lặp độc lập):

| Thuật toán | Số Node duyệt (Avg) | Số Node duyệt (Median) | Thời gian Median (ms) | Thời gian P95 (ms) | Chi phí TB ($C^*$) | Cự ly TB (km) | ETA TB (phút) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **A_STAR** | **46.5** | **42.5** | 1.5082 ms | 1.9687 ms | **0.5715** | **0.322 km** | **0.89 phút** |
| **UCS** | 49.7 | 47.0 | 1.2712 ms | 1.6317 ms | **0.5715** | **0.322 km** | **0.89 phút** |
| **GREEDY** | **17.3** | **17.0** | 0.3825 ms | 0.5998 ms | 0.5825 *(kém 1.9%)* | 0.321 km | 0.85 phút |
| **BIDIRECTIONAL** | 27.0 | 22.5 | **0.0997 ms** | **0.1424 ms** | 0.6469 *(kém 13.2%)* | 0.356 km | 0.96 phút |
| **BFS** | 43.8 | 39.0 | 0.2053 ms | 0.3059 ms | 0.6469 *(kém 13.2%)* | 0.356 km | 0.96 phút |
| **DFS** | 59.7 | 70.0 | 0.2723 ms | 0.3762 ms | 0.5963 *(kém 4.3%)* | 0.332 km | 0.90 phút |

**Đánh giá Thực nghiệm**:
- **Tính Tối ưu Tuyệt đối của A\* và UCS**: Chi phí trung bình của A\* và UCS luôn bằng nhau chính xác 100% ($0.5715$), khẳng định tính đúng đắn của hàm heuristic và tính tối ưu toán học.
- **Hiệu quả Tiết giảm Không gian Tìm kiếm của A\***: Nhờ hàm Heuristic định hướng, A\* mở rộng ít hơn UCS trung bình 3.2 nút trên đồ thị pilot và đạt mức tiết kiệm lên tới 28.4% trên các cặp O-D khoảng cách xa.
- **Tốc độ Đột phá của Bidirectional Search**: Bidirectional đạt thời gian thực thi siêu nhanh ($0.0997$ ms), nhanh hơn A\* gấp 15 lần nhờ giảm bán kính tìm kiếm.

### 7.3. Phân tích Ca Điển hình: Tuyến đường Thay đổi theo Kịch bản
Xét cặp điểm O-D số `OD03` (khu vực kết nối xuyên qua Chợ Thủ Đức):
- **Kịch bản `HISTORICAL_OFFPEAK`**: Đường phố thông thoáng, thuật toán chọn tuyến đường thẳng ngắn nhất xuyên qua trung tâm Chợ Thủ Đức (Cự ly $0.163$ km, Chi phí $0.1045$, ETA $0.22$ phút).
- **Kịch bản `HISTORICAL_PM_PEAK`**: Giao thông xung quanh chợ ùn tắc, chi phí cạnh tăng lên do thành phần $P_{\text{traffic}}$, tổng chi phí tuyến tăng lên $0.1250$ (ETA tăng lên $0.31$ phút).
- **Kịch bản `RAIN_FLOOD_AWARE_2025_2026`**: Các cạnh qua đường Dương Văn Cam và Đặng Thị Rành có rủi ro ngập $R_{\text{flood}} = 1.0$. Thuật toán tự động chuyển hướng đường đi vòng qua đường vành đai cao ráo, bảo đảm phương tiện không bị chết máy.

---

## 8. Tối ưu hóa Tuyến đường Giao hàng Đa điểm (TSP)

### 8.1. Đặc tả Bài toán TSP cho Shipper Xe máy
Khi shipper cần giao hàng cho $N$ khách hàng ($5 \le N \le 10$) từ 1 kho hàng (*Depot*):
- Cần xác định một chu trình ghé thăm mỗi điểm giao hàng đúng một lần rồi quay về kho sao cho tổng chi phí là nhỏ nhất.
- Vì mạng lưới đường phố đô thị có nhiều đường một chiều, ma trận khoảng cách giữa các điểm là **Ma trận Bất đối xứng (*Asymmetric Distance/Cost Matrix*)**: $c(u, v) \ne c(v, u)$.

### 8.2. Hai Giải thuật Giải quyết
1. **Giải thuật Quy hoạch Động Chính xác Held-Karp (Exact DP Solver)**:
   Sử dụng mặt nạ bit (*bitmask*) để biểu diễn tập các đỉnh đã thăm và lưu trạng thái memoization:
   $$dp(\text{mask}, u) = \min_{v \in \text{mask} \setminus \{u\}} \Big[ dp(\text{mask} \setminus \{u\}, v) + c(v, u) \Big]$$
   Chi phí chu trình hoàn chỉnh:
   $$\text{Cost}_{\text{optimal}} = \min_{u \in \{1, \dots, N-1\}} \Big[ dp((1 \ll N) - 1, u) + c(u, 0) \Big]$$
   Độ phức tạp: Thời gian $O(N^2 \cdot 2^N)$, Bộ nhớ $O(N \cdot 2^N)$. Với $N \le 10$, thời gian thực thi $< 5$ ms, đảm bảo nghiệm tối ưu tuyệt đối.
2. **Giải thuật Tham lam Xấp xỉ Láng giềng Gần nhất (Nearest Neighbor Heuristic)**:
   Xuất phát từ kho, tại mỗi bước luôn chọn đỉnh tiếp theo chưa thăm có chi phí bước $c(\text{current}, \text{next})$ nhỏ nhất. Độ phức tạp: Thời gian $O(N^2)$, Bộ nhớ $O(N)$.

### 8.3. Đánh giá Thực nghiệm: So sánh Held-Karp vs Nearest Neighbor vs Thứ tự Gốc
Thực nghiệm trên bài toán giao hàng 6 điểm dừng ($N = 6$) quanh TP. Thủ Đức:

| Phương pháp | Lộ trình Ghé thăm (Visit Order) | Tổng Chi phí ($C$) | Tổng Cự ly ($D$) | Độ lệch Xấp xỉ (% Gap) | Tiết kiệm so với Gốc (% Savings) |
|---|---|:---:|:---:|:---:|:---:|
| **Thứ tự Gốc (User Input)** | $\text{Depot} \to S_1 \to S_2 \to S_3 \to S_4 \to S_5 \to \text{Depot}$ | 14.850 | 4.250 km | --- | **0.0%** *(Baseline)* |
| **Nearest Neighbor** | $\text{Depot} \to S_2 \to S_1 \to S_3 \to S_5 \to S_4 \to \text{Depot}$ | 11.230 | 3.120 km | **+8.9%** | **24.4%** |
| **Held-Karp (Optimal)** | $\text{Depot} \to S_2 \to S_3 \to S_5 \to S_4 \to S_1 \to \text{Depot}$ | **10.310** | **2.890 km** | **0.0%** *(Exact)* | **30.6%** |

**Kết luận**: Thuật toán chính xác **Held-Karp DP** giúp shipper tiết kiệm đến **30.6% chi phí và quãng đường di chuyển** so với việc giao hàng theo thứ tự đơn hàng nhập ngẫu nhiên ban đầu.

---

## 9. Hướng dẫn Cài đặt & Sử dụng Ứng dụng

### 9.1. Yêu cầu Hệ thống & Cài đặt Môi trường
- Yêu cầu phần mềm: Python 3.11+, Node.js 22.12+ và npm.

```bash
# Bước 1: Khởi tạo môi trường ảo Python và cài đặt Backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".\backend[dev]"

# Bước 2: Cài đặt thư viện Frontend
npm --prefix frontend install

# Bước 3: Khởi chạy đồng thời cả Backend và Frontend
npm run dev
```

Địa chỉ truy cập:
- **Giao diện Web UI**: `http://localhost:5173`
- **FastAPI Documentation (Swagger UI)**: `http://localhost:8000/docs`

### 9.2. Hướng dẫn Sử dụng Giao diện Người dùng (GUI Guide)
1. **Chọn Điểm Trực quan trên Bản đồ (Auto-snapping 200m)**: Người dùng click trực tiếp lên bản đồ; hệ thống tự động snap vào điểm nút giao thông gần nhất trong bán kính 200m mà không làm giật camera. Điểm Start ghim màu cam, điểm Goal ghim màu hồng.
2. **Chế độ Giao hàng Đa điểm (Multi-Stop Tour Mode)**: Click chọn liên tiếp tối đa 10 điểm dừng trên bản đồ; hệ thống đánh số thứ tự trực quan và tự động tính toán lộ trình tối ưu qua Held-Karp DP.
3. **Thanh điều khiển Trace Player**: Xem từng bước duyệt nút thuật toán với 3 màu phân biệt: Vàng (*frontier* -- nút đang chờ), Xanh lá (*current* -- nút đang duyệt), Xám (*closed* -- nút đã duyệt xong).
4. **Chế độ So sánh (Compare Mode)**: Chạy song song cả 6 thuật toán trên cùng một cặp điểm và kịch bản, hiển thị bảng so sánh trực quan đa tiêu chí.
5. **Chuyển đổi Ngôn ngữ & Responsive**: Hỗ trợ song ngữ Tiếng Việt (`vi`) / Tiếng Anh (`en`) và tự động co giãn menu ngăn kéo trên thiết bị di động/tablet.

---

## 10. Hạn chế & Hướng Phát triển Tương lai

### 10.1. Khó khăn Kỹ thuật Đã Vượt qua
- **Xử lý Đồ thị Nén nhưng Bảo toàn Hình học Tuyến đường**: Rút gọn mạng lưới giao thông phức tạp 14.043 cạnh thành 178 cạnh nối giữa 65 địa điểm lớn mà vẫn giữ nguyên tọa độ polyline khúc khuỷu của đường phố thật thay vì vẽ đường thẳng giả tạo.
- **Đảm bảo Tính Đúng đắn của Heuristic Đa Chi phí**: Chứng minh và thiết lập hàm heuristic Haversine có trọng số vừa thỏa mãn tính chấp nhận được (*Admissible*), vừa thỏa mãn tính đơn điệu (*Consistent*) trong không gian chi phí 4 thành phần.
- **Kiến trúc Bất biến & Deterministic Tie-breaking**: Đảm bảo thuật toán độc lập 100% với framework HTTP và luôn cho kết quả tái lập tuyệt đối trên mọi nền tảng.

### 10.2. Các Hạn chế Hiện tại của Hệ thống
1. **Dữ liệu Giao thông Lịch sử**: Sử dụng hồ sơ giao thông lịch sử phân chia theo khung giờ (*Historical Traffic Profile*), chưa kết nối luồng dữ liệu GPS xe máy theo thời gian thực (*Live Telemetry Feed*).
2. **Mô hình Ngập nước Tĩnh**: Kịch bản ngập dựa trên danh mục điểm đen thống kê, chưa tích hợp mô hình mô phỏng thủy lực/thủy văn động lực học (*Hydraulic Dynamic Inundation*) theo lượng mưa tức thời.
3. **Phạm vi Bài toán TSP**: Giải quyết tối ưu cho 1 shipper xe máy đơn lẻ (Single-vehicle TSP), chưa mở rộng cho bài toán phân phối đội xe nhiều phương tiện có ràng buộc tải trọng và khung giờ giao hàng (*Capacitated Vehicle Routing Problem with Time Windows -- CVRPTW*).

### 10.3. Định hướng Mở rộng Tương lai
- **Tích hợp API Bản đồ Thời gian Thực**: Kết nối Live Traffic API (Here Maps, TomTom, Vietbando) để cập nhật độ trễ thời gian thực vào $P_{\text{traffic}}$.
- **Ứng dụng Meta-heuristics cho Bài toán Quy mô Lớn**: Cài đặt thuật toán Di truyền (*Genetic Algorithm -- GA*) và Tối ưu hóa Đàn kiến (*Ant Colony Optimization -- ACO*) để giải bài toán VRP cho đội xe quy mô lớn ($N > 50$ điểm giao hàng).
- **Hệ thống Cảnh báo Dự báo Mưa ngập Tức thời (Nowcasting)**: Kết hợp dữ liệu radar thời tiết để dự báo trước 30--60 phút các cung đường sắp ngập và tự động tái định tuyến (*dynamic rerouting*) cho shipper đang di chuyển.

---

## Tài liệu Tham khảo

1. Stuart Russell and Peter Norvig. *Artificial Intelligence: A Modern Approach*. 4th Edition, Pearson, 2020.
2. Michael Held and Richard M. Karp. A Dynamic Programming Approach to Sequencing Problems. *Journal of the Society for Industrial and Applied Mathematics*, 10(1):196--210, 1962.
3. Peter E. Hart, Nils J. Nilsson, and Bertram Raphael. A Formal Basis for the Heuristic Determination of Minimum Cost Paths. *IEEE Transactions on Systems Science and Cybernetics*, 4(2):100--107, 1968.
4. OpenStreetMap Contributors. Planet dump retrieved from https://planet.openstreetmap.org, 2026.
5. UTraffic Dataset: Urban Traffic Flow and Speed Profiling in Ho Chi Minh City. Kaggle Open Dataset, 2025.
