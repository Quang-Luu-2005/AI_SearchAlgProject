---
marp: true
theme: gaia
_class: lead
paginate: true
backgroundColor: #070B14
color: #F8FAFC
math: mathjax
style: |
  section {
    font-family: 'Inter', 'Outfit', sans-serif;
    padding: 32px 48px;
    font-size: 0.85rem;
  }
  h1 {
    color: #38BDF8;
    font-size: 1.8rem;
    margin-bottom: 0.4em;
  }
  h2 {
    color: #38BDF8;
    font-size: 1.35rem;
    margin-bottom: 0.3em;
    border-bottom: 1px solid rgba(56, 189, 248, 0.3);
    padding-bottom: 4px;
  }
  h3 {
    color: #F59E0B;
    font-size: 1.05rem;
    margin-bottom: 0.2em;
  }
  p, li {
    line-height: 1.45;
    color: #CBD5E1;
  }
  ul, ol {
    margin-left: 18px;
    margin-bottom: 6px;
  }
  table {
    font-size: 0.72rem;
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0;
  }
  th {
    background-color: #1E293B;
    color: #38BDF8;
    padding: 6px 10px;
    font-weight: 700;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
  td {
    background-color: rgba(15, 23, 42, 0.8);
    padding: 5px 10px;
    border: 1px solid rgba(255, 255, 255, 0.08);
  }
  tr:hover td {
    background-color: rgba(56, 189, 248, 0.1);
  }
  .highlight {
    color: #F59E0B;
    font-weight: bold;
  }
  .badge {
    background: rgba(56, 189, 248, 0.2);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.4);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.68em;
    font-weight: bold;
    display: inline-block;
  }
  .badge-gold {
    background: rgba(245, 158, 11, 0.2);
    color: #F59E0B;
    border-color: rgba(245, 158, 11, 0.4);
  }
  .badge-emerald {
    background: rgba(16, 185, 129, 0.2);
    color: #10B981;
    border-color: rgba(16, 185, 129, 0.4);
  }
  .badge-rose {
    background: rgba(244, 63, 94, 0.2);
    color: #F43F5E;
    border-color: rgba(244, 63, 94, 0.4);
  }
  .code-block {
    background: #020617;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 6px;
    padding: 8px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #E2E8F0;
    line-height: 1.4;
    margin: 6px 0;
  }
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  .grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
  }
  .card {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 8px;
    padding: 10px 14px;
  }
---

<!-- slide -->
# FLOODROUTE HCMC

- **Môn học**: Nhập môn Trí tuệ Nhân tạo (*Introduction to Artificial Intelligence*)
- **Trường**: Đại học Khoa học Tự nhiên – Đại học Quốc gia TP. Hồ Chí Minh · **Khoa**: Công nghệ Thông tin
- **Giảng viên hướng dẫn**: Bùi Tiến Lên – Võ Nhật Tân – Bùi Duy Đăng

---

<!-- slide -->
## 1. Thành viên Nhóm & Ma trận Đóng góp Kỹ thuật

| Thành viên | MSSV | Thẻ Trello Đảm nhiệm | Trách nhiệm Kỹ thuật Chi tiết | Đóng góp |
|---|:---:|---|---|:---:|
| **Lưu Huy Minh Quang** | **23127016** | `BE-01`<br>`BE-02`<br>`BE-03` | • **`BE-01`**: Thiết kế cấu trúc đồ thị có hướng bất biến `Graph`, `Node`, `Edge`, `GraphView`, phát hiện chu trình.<br>• **`BE-02`**: Xây dựng `ScenarioCostEngine` 4 thành phần ($D, T_{\text{ff}}, P_{\text{traffic}}, R_{\text{flood}}$) & 3 presets.<br>• **`BE-03`**: Phát triển FastAPI Router, Pydantic v2 schemas và AI diễn giải đường đi (*Explainable AI*). | **25%** |
| **Vũ Lê Trọng Văn** | **20127095** | `FE-01`<br>`FE-02`<br>`OPT` | • **`FE-01`** & **`FE-02`**: React Web App, tích hợp MapLibre GL JS vector GPU layers, Trace Player 3 trạng thái.<br>• **`OPT`**: Giải bài toán giao hàng đa điểm (TSP): xây dựng `PairwiseMatrix`, giải thuật chính xác **Held-Karp DP** ($O(N^2 2^N)$) và **Nearest Neighbor**, đo % Gap & % Savings. | **25%** |
| **Nguyễn Duy Khang** | **23127202** | `ALG-01`<br>`ALG-03`<br>`QA-01` | • **`ALG-01`**: Cài đặt thuật toán BFS (Queue) & DFS (Stack) với tie-break deterministic.<br>• **`ALG-03`**: Cài đặt Greedy Best-First Search & Bidirectional BFS trên đồ thị chuyển vị `rev_adj`.<br>• **`QA-01`**: Xây dựng phản ví dụ Greedy/DFS, golden regression suite và kiểm định hệ thống. | **25%** |
| **Ngô Quang Thắng** | **23127473** | `ALG-02`<br>`DATA-01`<br>`DATA-02` | • **`ALG-02`**: Cài đặt UCS & A* Search, thiết lập Scenario-Aware Heuristic $\rho_s$, chứng minh toán học Admissible & Consistent.<br>• **`DATA-01`** & **`DATA-02`**: Xây dựng pipeline dữ liệu OSM 4 tầng, map-matching 24 điểm ngập lụt TP. Thủ Đức, kiểm định mã băm SHA-256. | **25%** |

> **Tự Đánh Giá Rubric**: **100/100 Điểm Chuẩn Toàn Diện** · Quản lý minh bạch qua Trello: `https://trello.com/b/AGK7CP4q/aiproject1`

---

<!-- slide -->
## 2. Bối cảnh Thực tế Giao thông & Ngập Úng TP.HCM

<div class="grid-2">
<div class="card">

### 🚦 Thực trạng Giao thông TP.HCM & TP. Thủ Đức
- **Mật độ xe máy áp đảo**: Chiếm trên 85% phương tiện cá nhân, phụ thuộc mạng lưới hẻm và đường một chiều dày đặc.
- **Ùn tắc nghiêm trọng giờ cao điểm**:
  - Khung giờ: 07:00–08:30 (Sáng) & 16:30–18:30 (Chiều).
  - Trục huyết mạch: *Võ Văn Ngân, Kha Vạn Cân, Đặng Văn Bi, Tô Ngọc Vân, Quốc lộ 13*.
  - Vận tốc thực tế giảm từ $35\text{ km/h} \to 8 - 12\text{ km/h}$, thời gian di chuyển tăng gấp **$2\times - 4\times$**.

</div>
<div class="card">

### 🌊 Hiểm họa Ngập Úng do Mưa Lớn & Triều Cường
- **"Rốn ngập" Chợ Thủ Đức**: Địa hình trũng thấp, hệ thống thoát nước quá tải (*Dương Văn Cam, Đặng Thị Rành, Kha Vạn Cân, Hồ Văn Tư*).
- **Mực nước ngập thường kỳ**: $0.3\text{m} - 0.6\text{m}$ $\implies$ Gây chết máy xe, hư hỏng bưu kiện, tê liệt giao thông.
- **Nghịch lý đường ngắn nhất**: Tuyến đường ngắn nhất về khoảng cách địa lý ($D$) nếu băng qua rốn ngập sẽ trở thành **tuyến đường bất khả thi** hoặc có chi phí rủi ro cực lớn.

</div>
</div>

---

<!-- slide -->
## 3. Mục tiêu Ứng dụng & Chuẩn mực Kỹ thuật

<div class="grid-3">
<div class="card">

### 🎯 1. Định tuyến Đa tiêu chí
- Tìm đường 2 điểm không chỉ dựa vào cự ly hình học mà kết hợp đồng thời **Khoảng cách + Thời gian lưu thông + Độ trễ kẹt xe + Nguy cơ ngập úng**.
- Tự động chuyển hướng (*Dynamic Rerouting*) khi xảy ra ngập hoặc kẹt xe.

</div>
<div class="card">

### 📦 2. Tối ưu Giao hàng Đa điểm
- Giải bài toán TSP bất đối xứng (*Asymmetric TSP*) cho shipper xe máy: Xuất phát từ 1 Kho (*Depot*), giao $5 - 10$ điểm (*Stops*) và quay về kho.
- Áp dụng giải thuật chính xác **Held-Karp DP** và xấp xỉ **Nearest Neighbor**.

</div>
<div class="card">

### 💡 3. Trí tuệ Nhân tạo Giải thích
- Hệ thống **Explainable AI (XAI)**: Tự động phân tích đóng góp chi phí, phát hiện đoạn đường chịu phạt cao nhất, so sánh phương án và công bố cam kết toán học.
- 100% Deterministic và tái lập.

</div>
</div>

---

<!-- slide -->
## 4. Mô hình Không gian Trạng thái (State-Space Formulation)

Bài toán tìm đường được hình thức hóa toán học chặt chẽ:

$$\mathcal{P} = \langle S,\, s_0,\, A(s),\, \text{Result}(s, a),\, \text{GoalTest}(s),\, c(s, a, s') \rangle$$

- **Tập trạng thái ($S$)**: Tập hợp tất cả các nút giao thông và địa điểm trọng yếu trên mạng lưới đường bộ ($S = V$).
- **Trạng thái bắt đầu ($s_0$)**: Vị trí xuất phát của shipper ($s_0 = \text{Start} \in V$).
- **Tập hành động ($A(s)$)**: Tập các cạnh có hướng mở xuất phát từ nút $s$ trong kịch bản hiện tại:
  $$A(s) = \{ (s, v) \in E \mid (s, v) \notin \text{ClosedEdges}(\text{Scenario}) \}$$
- **Mô hình chuyển trạng thái ($\text{Result}(s, a)$)**: Khi thực hiện hành động $a = (s, v)$, trạng thái mới đạt được là đỉnh đích $v$.
- **Kiểm tra trạng thái đích ($\text{GoalTest}(s)$)**: Kiểm tra trạng thái hiện tại $s$ có trùng với điểm đích $\text{Goal}$ hay không ($s = \text{Goal}$).
- **Chi phí bước ($c(s, a, s')$)**: Chi phí tổng hợp của cạnh $a = (s, s')$ được xác định bởi mô hình chi phí của kịch bản đang chọn.

---

<!-- slide -->
## 5. Mô hình Chi phí Tổng hợp 4 Thành phần (Composite Cost Model)

Chi phí của mỗi cạnh có hướng $e = (u, v)$ trong kịch bản $s$ được xác định bởi hàm tuyến tính có trọng số chuẩn hóa:

$$C_s(e) = w_{\text{dist}} \cdot D(e) + w_{\text{time}} \cdot T_{\text{ff}}(e) + w_{\text{cong}} \cdot P_{\text{traffic}}(e) + w_{\text{flood}} \cdot R_{\text{flood}}(e)$$

<div class="grid-2">
<div class="card">

### Chi tiết các Đại lượng Thành phần:
1. **$D(e)$ - Khoảng cách**: Độ dài vật lý thực tế: $D(e) = \frac{\text{distance\_m}(e)}{1000} \text{ (km)}$.
2. **$T_{\text{ff}}(e)$ - Free-Flow Time**: Thời gian di chuyển ở vận tốc thiết kế: $T_{\text{ff}}(e) = \text{free\_flow\_time\_min}(e) \text{ (phút)}$.
3. **$P_{\text{traffic}}(e)$ - Độ trễ Kẹt xe (Delay Penalty)**:
   $$T_{\text{travel}}(e) = T_{\text{ff}}(e) \times \text{TrafficMultiplier}(e)$$
   $$P_{\text{traffic}}(e) = \max\big(0,\, T_{\text{travel}}(e) - T_{\text{ff}}(e)\big) \text{ (phút)}$$
4. **$R_{\text{flood}}(e)$ - Rủi ro Ngập nước**: Chỉ số chuẩn hóa $R_{\text{flood}} \in [0.0, 1.0]$.

</div>
<div class="card">

### ⚠️ Lưu ý Thiết kế Cốt lõi:
- **Tách riêng $P_{\text{traffic}}$ khỏi $T_{\text{ff}}$**: Giúp hàm chi phí không bị tính trùng lặp thời gian di chuyển cơ sở hai lần khi áp dụng trọng số.
- **Ràng buộc Chuẩn hóa Trọng số**:
  $$w_i \ge 0 \quad \text{và} \quad \sum w_i = 1.0$$
- **Hard Constraint**: Đoạn đường ngập đóng hoàn toàn $\implies \text{Cost} = \text{null}$, loại bỏ triệt để khỏi đồ thị tìm kiếm.

</div>
</div>

---

<!-- slide -->
## 6. Các Thiết lập Kịch bản Chi phí Chuẩn (Cost Presets)

| Kịch bản (Preset ID) | $w_{\text{dist}}$ | $w_{\text{time}}$ | $w_{\text{cong}}$ | $w_{\text{flood}}$ | Mục tiêu Tối ưu hóa & Ứng dụng Thực tế |
|---|:---:|:---:|:---:|:---:|---|
| **`BALANCED`** | 0.25 | 0.30 | 0.20 | 0.25 | **Cân bằng đa mục tiêu**: Hài hòa giữa cự ly, thời gian, kẹt xe và rủi ro ngập úng (Kịch bản mặc định). |
| **`PEAK_TRAFFIC`** | 0.15 | 0.25 | 0.45 | 0.15 | **Ưu tiên giờ cao điểm**: Phạt nặng các cung đường ùn tắc, chấp nhận đi xa hơn để tiết kiệm thời gian. |
| **`RAIN_SAFE`** | 0.10 | 0.25 | 0.15 | 0.50 | **Ưu tiên mưa bão/triều cường**: Phạt tối đa rủi ro ngập nước, ưu tiên tuyệt đối tuyến vành đai cao ráo. |

### Minh chứng Đổi Tuyến Thực tế trên Đồ thị Mẫu (`toy_graph_v0.1`):
- **Cặp $N01 \to N06$**: 
  - Ở `OFFPEAK_BALANCED`: Tuyến ngắn nhất $N01 \to N02 \to N06$ (Cost = $2.343$).
  - Ở `HEAVY_RAIN_SAFE`: Cạnh $E03$ bị ngập đóng $\implies$ Thuật toán tự động chuyển sang $N01 \to N02 \to N04 \to N06$ (Cost = $2.562$).
- **Ở `PEAK_TRAFFIC`**: Tuyến đường giữ nguyên nhưng Cost tăng từ $2.343 \to 2.920$ và ETA tăng từ $5.56\text{p} \to 8.06\text{p}$ do bị phạt độ trễ.

---

<!-- slide -->
## 7. Pipeline Dữ liệu 4 Tầng & Nguồn gốc Dữ liệu (Provenance)

<div class="grid-2">
<div class="card">

### Quy trình 4 Tầng Quản lý Dữ liệu
```
[ data/raw/ (Bất biến) ]
   ├── osm_relation_19407794.geojson (Ranh TP. Thủ Đức cũ)
   ├── utraffic_hcm_v6.zip (8.952 nodes, 14.043 edges)
   └── Khóa toàn vẹn bằng SHA-256 Checksum Manifest
            │
            ▼
[ data/interim/ (Xử lý Trung gian) ]
   └── Trích xuất BBox, Map-matching, Topology cleaning
            │
            ▼
[ data/processed/ (Bản phát hành Chính thức) ]
   ├── thu_duc_landmarks_v1.0.0 (65 POI, 178 edges)
   └── thu_duc_core_capacity_v0.1.0 (3.229 nodes, 5.057 edges)
            │
            ▼
[ data/fixtures/ (Môi trường Kiểm thử) ]
   └── toy_graph_v0.1 (6 nodes, 12 edges) & Graph Examples
```

</div>
<div class="card">

### Hệ thống Nhãn Dữ liệu Minh bạch
- **`SOURCE_BACKED`**: Dữ liệu có nguồn trích xuất xác thực từ OpenStreetMap hoặc Kaggle UTraffic.
- **`DERIVED`**: Dữ liệu được tính toán xác định (cự ly Haversine, Free-flow time qua vận tốc đường).
- **`SIMULATED / ASSUMPTION`**: Dữ liệu giả lập tham số kẹt xe/ngập lụt (hiển thị rõ trên GUI bảo đảm liêm chính học thuật).
- **`REVIEW_REQUIRED`**: Dữ liệu map-matching ngập nước đang chờ thẩm định bổ sung.

</div>
</div>

---

<!-- slide -->
## 8. Chi tiết Bản Phát Hành Đồ Thị: Landmark 65 vs Capacity 3229

| Tiêu chí So sánh | `thu_duc_landmarks_v1.0.0` (Release Demo Chính) | `thu_duc_core_capacity_v0.1.0` (Stress-Test Graph) |
|---|---|---|
| **Số lượng Đỉnh ($V$)** | **65 Địa điểm lớn** (Named Major POIs từ OpenStreetMap) | **3.229 Nút giao thông** (Mạng lưới đường bộ lõi TP. Thủ Đức) |
| **Số lượng Cạnh ($E$)** | **178 Cạnh có hướng** (Directed road-path edges) | **5.057 Cạnh có hướng** (Directed street segments) |
| **Bản chất Cạnh** | **Đường đi ngắn nhất nén (Polyline UTraffic)** nối các địa điểm lớn | Từng đoạn đường vật lý chi tiết giữa các giao lộ |
| **Loại địa điểm** | Trường Đại học, Bệnh viện, Chợ đầu mối, Ga tàu, TTTM, Bến xe | Toàn bộ giao lộ đường phố chi tiết trong khu vực nghiên cứu |
| **Mục đích sử dụng** | **Trực quan hóa trên Web UI**: Tránh quá tải hàng nghìn node kỹ thuật, giao diện trực quan cho người dùng chọn điểm. | **Benchmark & Stress-test**: Đo đạc năng lực chịu tải và độ phức tạp tính toán của thuật toán trên đồ thị lớn. |
| **Hình học Cạnh** | Giữ nguyên tọa độ Polyline khúc khuỷu theo đường UTraffic thực | Tuyến đường vật lý nguyên bản trích xuất từ OpenStreetMap |

---

<!-- slide -->
## 9. Kiến Trúc Hệ Thống & Luồng Dữ Liệu Phân Tầng

```mermaid
flowchart LR
    subgraph Client ["Client Presentation"]
        UI[React Controls] --> Map[MapLibre GL JS]
        Player[Trace Player] --> Reducer[Visual State Reducer]
    end

    subgraph API ["FastAPI Router"]
        V1[/api/v1/search]
        V2[/api/v1/compare]
        V3[/api/v1/optimize-tour]
    end

    subgraph Service ["Domain Services"]
        SearchSvc[SearchService]
        TourSvc[TourOptimizerService]
        Explain[ExplanationEngine]
    end

    subgraph Algorithms ["Pure Python Engines"]
        BFS_DFS[BFS / DFS]
        UCS_ASTAR[UCS / A* Search]
        GREEDY_BI[Greedy / Bidirectional]
        TSP_SOLVER[Held-Karp / Nearest Neighbor]
    end

    subgraph Core ["Immutable Core"]
        GraphCore[(Immutable Graph)]
        CostEng[ScenarioCostEngine]
    end

    UI --> API
    API --> Service
    SearchSvc --> Algorithms
    TourSvc --> Algorithms
    Algorithms --> Core
    Service --> Explain
    Explain --> API
    API --> Client
```

---

<!-- slide -->
## 10. Scenario-Aware Lower-Bound Heuristic (ADR-0015)

<div class="grid-2">
<div class="card">

### ❓ Vấn đề Toán học Đặt ra
- Hàm chi phí $C_s(e)$ là tổ hợp tuyến tính của 4 đại lượng khác đơn vị (km, phút, rủi ro).
- Khoảng cách Haversine thuần túy $D_{\text{Haversine}}(n, \text{Goal})$ có đơn vị km.
- **Nếu gán trực tiếp $h(n) = D_{\text{Haversine}}$**: Heuristic có thể vượt quá chi phí thực tế $h^*(n)$ khi trọng số cự ly $w_{\text{dist}} < 1.0$ $\implies$ **Mất tính Admissible, A* không còn tối ưu!**

</div>
<div class="card">

### 💡 Giải pháp Đột phá trong ADR-0015
1. **Tính Hệ số Tỷ lệ Chi phí Tối thiểu Toàn cục ($\rho_s$)**:
   $$\rho_s = \min_{e \in E_{\text{open}},\, D_{\text{Haversine}}(e) > 10^{-6}} \frac{\text{Cost}_s(e)}{D_{\text{Haversine}}(e)}$$
2. **Hàm Heuristic Scenario-Aware cho A\***:
   $$h_s(n) = \rho_s \times D_{\text{Haversine}}(n, \text{Goal})$$
   $$f(n) = g(n) + h_s(n)$$
3. Cạnh đóng hoặc cạnh có $D \le 10^{-6}\text{km}$ bị loại khỏi phép tính $\rho_s$. Khi thiếu tọa độ, $\rho_s = 0 \implies h(n) = 0$ (A* tự động fallback về UCS an toàn).

</div>
</div>

---

<!-- slide -->
## 11. Chứng Minh Toán Học: Tính Đúng Đắn của Heuristic A*

<div class="grid-2">
<div class="card">

### 📜 Định lý 1: Tính Chấp nhận được (Admissibility)
> **Phát biểu**: Với mọi nút $n \in V$, $0 \le h_s(n) \le h^*(n)$.
> 
> **Chứng minh**:
> 1. Gọi $P^* = (n = v_0, v_1, \dots, v_k = \text{Goal})$ là đường đi tối ưu từ $n$ đến $\text{Goal}$ trong kịch bản $s$.
> 2. Chi phí tối ưu: $h^*(n) = \sum_{i=0}^{k-1} \text{Cost}_s(v_i, v_{i+1})$.
> 3. Theo định nghĩa $\rho_s$, trên mỗi cạnh mở $(v_i, v_{i+1})$:
>    $$\text{Cost}_s(v_i, v_{i+1}) \ge \rho_s \cdot D_{\text{Haversine}}(v_i, v_{i+1})$$
> 4. Theo bất đẳng thức tam giác cầu:
>    $$\sum_{i=0}^{k-1} D_{\text{Haversine}}(v_i, v_{i+1}) \ge D_{\text{Haversine}}(n, \text{Goal})$$
> 5. $\implies h^*(n) \ge \rho_s D_{\text{Haversine}}(n, \text{Goal}) = h_s(n)$. $\blacksquare$

</div>
<div class="card">

### 📜 Định lý 2: Tính Nhất quán (Consistency / Monotonicity)
> **Phát biểu**: Với mọi cạnh mở $e = (n, n')$, $h_s(n) \le c_s(n, n') + h_s(n')$.
> 
> **Chứng minh**:
> 1. Xét 3 điểm $n, n'$ và $\text{Goal}$ trên mặt cầu trắc địa. Theo bất đẳng thức tam giác cầu:
>    $$D_{\text{Haversine}}(n, \text{Goal}) \le D_{\text{Haversine}}(n, n') + D_{\text{Haversine}}(n', \text{Goal})$$
> 2. Nhân cả hai vế với $\rho_s \ge 0$:
>    $$\rho_s D(n, G) \le \rho_s D(n, n') + \rho_s D(n', G)$$
> 3. Do $\rho_s D(n, n') \le c_s(n, n')$ theo định nghĩa của $\rho_s$:
>    $$h_s(n) \le c_s(n, n') + h_s(n') \quad \forall (n, n') \in E$$
> 4. $\implies h_s(n)$ **Consistent** $\implies$ Nút đã đóng không bao giờ bị mở lại! $\blacksquare$

</div>
</div>

---

<!-- slide -->
## 12. Bộ Thuật Toán Tìm Kiếm Không Trọng Số (Unweighted Search)

<div class="grid-2">
<div class="card">

### 🟦 Breadth-First Search (BFS)
- **Cấu trúc dữ liệu**: Hàng đợi FIFO (`collections.deque`).
- **Nguyên lý**: Mở rộng đồng mức theo bán kính lân cận (*shallowest unexpanded node*).
- **Hàm đánh giá**: $f(n) = \text{depth}(n)$ (số chặng di chuyển).
- **Độ phức tạp**: Thời gian $O(b^d)$, Bộ nhớ $O(b^d)$.
- **Tính Tối ưu**: Đảm bảo tối ưu **số bước nhảy (*minimum hop count*)**, không tối ưu tổng chi phí trọng số.
- **Ứng dụng**: Dùng trong `RandomScenarioService` để kiểm tra cực nhanh tính liên thông (*Reachability*).

</div>
<div class="card">

### 🟨 Depth-First Search (DFS)
- **Cấu trúc dữ liệu**: Ngăn xếp LIFO (`list.pop()`).
- **Nguyên lý**: Đi sâu dọc theo từng nhánh đường cho đến nút lá rồi mới quay lui (*backtracking*).
- **Tránh lặp vô hạn**: Bắt buộc duy trì tập `discovered` / `expanded` để ngăn chu trình.
- **Độ phức tạp**: Thời gian $O(b^m)$, Bộ nhớ tối ưu $O(b \cdot m)$.
- **Tính Tối ưu**: **Hoàn toàn không tối ưu**, dễ đi đường vòng cực dài.
- **Tie-break**: Neighbor sorting đảo chiều để bảo đảm tính tất định.

</div>
</div>

---

<!-- slide -->
## 13. Bộ Thuật Toán Tìm Kiếm Có Trọng Số (Weighted Search)

<div class="grid-2">
<div class="card">

### 🟩 Uniform Cost Search (UCS / Dijkstra)
- **Cấu trúc dữ liệu**: Min-Priority Queue (`heapq`).
- **Nguyên lý**: Luôn chọn mở rộng nút có chi phí tích lũy $g(n)$ nhỏ nhất:
  $$f(n) = g(n)$$
- **Độ phức tạp**: Thời gian & Bộ nhớ $O(b^{1 + \lfloor C^*/\epsilon \rfloor})$ với $c(e) \ge \epsilon > 0$.
- **Tính Tối ưu**: **Bảo đảm nghiệm tối ưu toàn cục tuyệt đối ($C^*$)** trên mọi đồ thị có trọng số không âm.
- **Nhược điểm**: Mở rộng đều theo mọi hướng (*blind search*), duyệt nhiều nút không hướng đích.

</div>
<div class="card">

### 🟪 A* Search (Informed Search)
- **Cấu trúc dữ liệu**: Min-Priority Queue (`heapq`).
- **Nguyên lý**: Kết hợp chi phí thực tế $g(n)$ và ước lượng hướng đích $h_s(n)$:
  $$f(n) = g(n) + h_s(n)$$
- **Độ phức tạp**: Thời gian & Bộ nhớ $O(b^d)$, cắt tỉa không gian tìm kiếm vượt trội nhờ Heuristic.
- **Tính Tối ưu**: **Bảo đảm nghiệm tối ưu toàn cục ($C^*$)** nhờ Heuristic $\rho_s \cdot D_{\text{Haversine}}$ thỏa mãn Admissible & Consistent.
- Khám phá ít nút hơn UCS, hướng thẳng về Goal.

</div>
</div>

---

<!-- slide -->
## 14. Thuật Toán Mở Rộng: Greedy Best-First & Bidirectional BFS

<div class="grid-2">
<div class="card">

### 🟧 Greedy Best-First Search
- **Cấu trúc dữ liệu**: Min-Heap Priority Queue.
- **Hàm đánh giá**: $f(n) = h_s(n) = \rho_s \cdot D_{\text{Haversine}}(n, \text{Goal})$.
- **Nguyên lý**: Luôn chọn nút có khoảng cách ước lượng gần Goal nhất.
- **Độ phức tạp**: Thời gian $O(b^m)$, Bộ nhớ $O(b \cdot m)$.
- **Ưu / Nhược điểm**: Tốc độ tìm kiếm cực nhanh, duyệt rất ít nút nhưng **không đảm bảo tối ưu**, dễ bị bẫy bởi vật cản/đường vòng.

</div>
<div class="card">

### 🌐 Bidirectional Breadth-First Search
- **Cấu trúc dữ liệu**: 2 Hàng đợi FIFO song song (`q_fwd`, `q_bwd`).
- **Nguyên lý**: Tìm kiếm đồng thời từ Start (thuận) và từ Goal (nghịch) cho đến khi gặp nhau tại điểm giao nhau (*intersection*).
- **Đồ thị chuyển vị**: Luồng nghịch duyệt trên đồ thị đảo chiều `rev_adj` để tuân thủ đúng luật đường 1 chiều.
- **Độ phức tạp**: Giảm ngoạn mục từ $O(b^d) \to O(2 \cdot b^{d/2})$.
- **Tốc độ**: Nhanh hơn A* gấp 15 lần trên benchmark thực tế.

</div>
</div>

---

<!-- slide -->
## 15. Mô Phỏng Từng Bước Duyệt Nút (Step-by-Step Trace Simulation)

Xét đồ thị mẫu 4 nút: $A \xrightarrow{c=2, h=5} B \xrightarrow{c=4, h=0} D$ và $A \xrightarrow{c=5, h=3} C \xrightarrow{c=1, h=0} D$ ($\text{Start}=A, \text{Goal}=D$).

| Bước | Thuật toán | Nút mở rộng (EXPAND) | Trạng thái Frontier Hàng Đợi $[(\text{Node}, g, h, f)]$ | Tập Đóng (CLOSE) | Diễn giải Chi tiết |
|:---:|---|---|---|---|---|
| 1 | **UCS** | **A** ($g=0$) | $[(B, g=2), (C, g=5)]$ | $\{A\}$ | Khởi tạo từ $A$, phát hiện 2 nhánh đi $B$ và $C$. |
| 2 | **UCS** | **B** ($g=2$) | $[(C, g=5), (D, g=6)_{\text{qua } B}]$ | $\{A, B\}$ | $B$ có $g=2$ nhỏ nhất $\implies$ mở rộng $B$, đưa $D$ vào hàng đợi. |
| 3 | **UCS** | **C** ($g=5$) | $[(D, g=6)_{\text{qua } C}, (D, g=6)_{\text{qua } B}]$ | $\{A, B, C\}$ | $C$ có $g=5 < g(D)=6 \implies$ phải duyệt $C$ dù đi lệch hướng! |
| 4 | **UCS** | **D** ($g=6$) | Đích đạt được! | $\{A, B, C, D\}$ | **Tìm ra nghiệm tối ưu: $A \to B \to D$ ($C^* = 6.0$), duyệt 4 nút.** |
| 1 | **A\*** | **A** ($f=5$) | $[(B, g=2, h=5, f=7), (C, g=5, h=3, f=8)]$ | $\{A\}$ | Khởi tạo từ $A$ với $f(A) = 0 + 5 = 5$. |
| 2 | **A\*** | **B** ($f=7$) | $[(D, g=6, h=0, f=6), (C, g=5, h=3, f=8)]$ | $\{A, B\}$ | $B$ có $f=7 < f(C)=8 \implies$ chọn $B$, đưa $D$ vào với $f=6$. |
| 3 | **A\*** | **D** ($f=6$) | Đích đạt được! | $\{A, B, D\}$ | **A\* dừng ngay lập tức tại bước 3, KHÔNG CẦN DUYỆT C!** |

> **Quy tắc Tie-breaking Deterministic**: Ưu tiên $g(n)$ nhỏ hơn $\implies$ `node_id` tăng dần theo bảng chữ cái $\implies$ 100% tái lập kết quả.

---

<!-- slide -->
## 16. Phản Ví Dụ Thực Tế & Xử Lý Trường Hợp Biên (Edge Cases)

<div class="grid-3">
<div class="card">

### ⚠️ Phản ví dụ Greedy
- Trên đồ thị `thu_duc_landmarks_v1.0.0`, Greedy bị "đánh lừa" bởi đường chim bay hướng thẳng Goal.
- Kết quả: Chọn đường vòng có nhiều đoạn kẹt xe $\implies$ **Chi phí đắt hơn UCS từ $1.9\% - 15\%$** (được kiểm chứng trong test suite).

</div>
<div class="card">

### 🔄 Xử lý Đồ thị 1 Chiều
- Khi tìm kiếm Bidirectional trên mạng lưới đường đô thị, luồng Backward duyệt trên **đồ thị chuyển vị (`rev_adj`)**:
  $$E_{\text{rev}} = \{ (v, u) \mid (u, v) \in E \}$$
- Bảo đảm đường đi ghép nối hợp lệ 100% theo chiều lưu thông thực tế.

</div>
<div class="card">

### 🛡️ Xử lý Trường hợp Biên
- **$\text{Start} = \text{Goal}$**: Trả kết quả tức thì với 0 chi phí, 0 cạnh, 0 nút duyệt.
- **Unreachable (Bị cô lập)**: Báo lỗi chuẩn `RouteNotFoundError (404)`.
- **Đồ thị có Chu trình**: Duy trì tập `expanded` ngăn ngừa vòng lặp vô tận.

</div>
</div>

---

<!-- slide -->
## 17. Kết Quả Thực Nghiệm Khoa Học (3.600 Lượt Benchmark)

Số liệu thực nghiệm từ artifact `experiments/results/search_benchmark_v1.json` ($10\text{ O-D} \times 3\text{ Scenarios} \times 6\text{ Algorithms} \times 20\text{ Lần chạy}$):

| Thuật toán | Số Node duyệt (TB) | Số Node duyệt (Median) | Thời gian Median | Thời gian P95 | Chi phí Tuyến ($C^*$) | Cự ly TB (km) | ETA TB (phút) | Đánh giá Tính Năng |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **A_STAR** | **46.5** | **42.5** | 1.5082 ms | 1.9687 ms | **0.5715** | **0.322 km** | **0.89 phút** | <span class="badge badge-emerald">Optimal 100% · Pruned</span> |
| **UCS** | 49.7 | 47.0 | 1.2712 ms | 1.6317 ms | **0.5715** | **0.322 km** | **0.89 phút** | <span class="badge badge-emerald">Optimal 100% · Baseline</span> |
| **GREEDY** | **17.3** | **17.0** | 0.3825 ms | 0.5998 ms | 0.5825 *(+1.9%)* | 0.321 km | 0.85 phút | <span class="badge badge-gold">Suboptimal · Fast</span> |
| **BIDIRECTIONAL** | 27.0 | 22.5 | **0.0997 ms** | **0.1424 ms** | 0.6469 *(+13.2%)*| 0.356 km | 0.96 phút | <span class="badge">Super Fast (15× A*)</span> |
| **BFS** | 43.8 | 39.0 | 0.2053 ms | 0.3059 ms | 0.6469 *(+13.2%)*| 0.356 km | 0.96 phút | <span class="badge">Hop-count Optimal</span> |
| **DFS** | 59.7 | 70.0 | 0.2723 ms | 0.3762 ms | 0.5963 *(+4.3%)* | 0.332 km | 0.90 phút | <span class="badge badge-rose">Non-optimal · Deep</span> |

### 3 Kết luận Khoa học Then chốt:
1. **Tính Tối ưu Tuyệt đối của A\* và UCS**: Chi phí $C^*$ của A\* và UCS luôn bằng nhau chính xác 100% ($0.5715$) trên toàn bộ các ca kiểm thử.
2. **Khả năng Cắt tỉa của A\***: Mở rộng ít hơn UCS trung bình $3.2$ nút trên đồ thị nhỏ và tiết kiệm đến $28.4\%$ nút duyệt trên các cặp O-D khoảng cách xa.
3. **Tốc độ của Bidirectional**: Đạt thời gian thực thi siêu nhanh ($0.0997\text{ ms}$), nhanh hơn A\* gấp **15 lần** nhờ chia đôi bán kính tìm kiếm.

---

<!-- slide -->
## 18. Nghiên Cứu Điển Hình: Tuyến Đường Thích Ứng Theo Kịch Bản

Xét cặp điểm `OD03` (xuyên qua khu vực Chợ Thủ Đức):

| Kịch bản Giao thông | Lộ trình Được Chọn | Chi phí Tổng ($C$) | Cự ly | ETA Dự kiến | Diễn giải Hành vi của Thuật toán |
|---|---|:---:|:---:|:---:|---|
| **`HISTORICAL_OFFPEAK`** | Đi thẳng xuyên tâm Chợ Thủ Đức | **0.1045** | 0.163 km | 0.22 phút | Đường phố thông thoáng, thuật toán chọn tuyến cự ly ngắn nhất. |
| **`HISTORICAL_PM_PEAK`** | Đi thẳng qua Chợ Thủ Đức | **0.1250** *(+19.6%)* | 0.163 km | 0.31 phút | Kẹt xe làm tăng $P_{\text{traffic}}$, chi phí tăng nhưng chưa có đường vòng nào rẻ hơn. |
| **`RAIN_FLOOD_AWARE`** | **Tự động đi vòng qua đường vành đai cao** | **0.1480** | 0.245 km | 0.38 phút | Các cạnh qua Chợ Thủ Đức có rủi ro ngập $R_{\text{flood}} = 1.0$. **Thuật toán tự động đổi tuyến đi vòng để tránh chết máy!** |

```
[ Kịch bản Bình thường ] : Start ══════ (Đoạn qua Chợ: Khô ráo) ══════> Goal (Nhanh nhất)
[ Kịch bản Ngập lụt ]   : Start ─── (Né Chợ Ngập) ───> Tuyến Vành Đai Cao ───> Goal (An toàn)
```

---

<!-- slide -->
## 19. Bài Toán Tối Ưu Lộ Trình Giao Hàng Đa Điểm (Asymmetric TSP)

<div class="grid-2">
<div class="card">

### 📦 Đặc tả Bài toán Giao hàng Đa điểm
- **Đầu vào**: 1 Kho hàng (*Depot*) + $K$ điểm giao hàng (*Stops*, $5 \le K \le 10$).
- **Mục tiêu**: Tìm một chu trình ghé thăm mỗi điểm giao hàng đúng một lần rồi quay về kho với **tổng chi phí là nhỏ nhất**.
- **Đặc thù Đô thị**: Có đường một chiều $\implies$ **Ma trận Bất đối xứng**: $c(u, v) \ne c(v, u)$.

</div>
<div class="card">

### ⚙️ Quy trình Giải quyết 3 Bước
1. **Xây dựng `PairwiseMatrix` ($M \times M$, $M=K+1$)**:
   - Chạy $M(M-1)$ lượt A* tìm đường ngắn nhất giữa mọi cặp điểm.
2. **Giải bài toán tối ưu thứ tự**:
   - Chính xác: **Held-Karp DP** ($O(N^2 2^N)$).
   - Xấp xỉ: **Nearest Neighbor** ($O(N^2)$).
3. **Ghép nối lộ trình con (Subpath Stitching)**:
   - Khử trùng lặp nút nối biên, tạo đường đi liền mạch.

</div>
</div>

---

<!-- slide -->
## 20. Hai Giải Thuật Giải Quyết TSP: Held-Karp DP vs Nearest Neighbor

<div class="grid-2">
<div class="card">

### 🏆 1. Held-Karp DP (Exact DP Solver)
- **Quy hoạch động Bitmask Memoization**:
  $$dp(\text{mask}, u) = \min_{v \in \text{mask} \setminus \{u\}} \Big[ dp(\text{mask} \setminus \{u\}, v) + c(v, u) \Big]$$
- **Chi phí chu trình tối ưu hoàn chỉnh**:
  $$\text{Cost}^* = \min_{u \in \{1, \dots, N-1\}} \Big[ dp((1 \ll N) - 1, u) + c(u, 0) \Big]$$
- **Độ phức tạp**: Thời gian $O(N^2 \cdot 2^N)$, Bộ nhớ $O(N \cdot 2^N)$. Với $N \le 10$, giải xong trong **$< 5\text{ ms}$**.
- **Bảo đảm nghiệm tối ưu tuyệt đối 100%**.
- Được kiểm chứng chéo với **Brute Force** ($N \le 7$).

</div>
<div class="card">

### ⚡ 2. Nearest Neighbor (Heuristic Solver)
- **Tham lam từng bước**: Xuất phát từ kho, tại mỗi bước luôn chọn điểm gần nhất chưa ghé thăm:
  $$\text{next} = \arg\min_{v \in \text{Unvisited}} c(\text{current}, v)$$
- **Độ phức tạp**: Thời gian $O(N^2)$, Bộ nhớ $O(N)$.
- **Nhược điểm**: Dễ bị "bẫy" ở chặng cuối cùng, chi phí quay về Depot có thể cực kỳ đắt $\implies$ Nghiệm lệch xấp xỉ so với tối ưu.

</div>
</div>

---

<!-- slide -->
## 21. Đánh Giá Thực Nghiệm TSP & Hiệu Quả Tiết Kiệm Chi Phí

Thực nghiệm trên bài toán giao hàng 6 điểm dừng ($N = 6$) quanh khu vực TP. Thủ Đức:

| Phương pháp Định tuyến | Lộ trình Ghé thăm (Visit Order) | Tổng Chi phí ($C$) | Tổng Cự ly | % Lệch Xấp xỉ (Gap) | % Tiết kiệm so với Gốc |
|---|---|:---:|:---:|:---:|:---:|
| **Thứ tự Gốc (User Input)** | $\text{Depot} \to S_1 \to S_2 \to S_3 \to S_4 \to S_5 \to \text{Depot}$ | 14.850 | 4.250 km | — | **0.0%** *(Baseline)* |
| **Nearest Neighbor** | $\text{Depot} \to S_2 \to S_1 \to S_3 \to S_5 \to S_4 \to \text{Depot}$ | 11.230 | 3.120 km | <span class="badge badge-gold">+8.9% Gap</span> | <span class="badge">Tiết kiệm 24.4%</span> |
| **Held-Karp DP (Optimal)** | $\text{Depot} \to S_2 \to S_3 \to S_5 \to S_4 \to S_1 \to \text{Depot}$ | **10.310** | **2.890 km** | <span class="badge badge-emerald">0.0% (Exact)</span> | <span class="badge badge-emerald">Tiết kiệm 30.6%</span> |

### 💡 Ý nghĩa Kinh tế & Thực tiễn:
- **Held-Karp DP giúp shipper tiết kiệm đến 30.6% chi phí và quãng đường di chuyển** (rút ngắn $1.36\text{ km}$ trên mỗi chuyến giao hàng).
- Nearest Neighbor cho nghiệm nhanh nhưng vẫn có khoảng cách xấp xỉ $+8.9\%$ so với nghiệm tối ưu.

---

<!-- slide -->
## 22. Dịch Vụ Sinh Kịch Bản Ngẫu Nhiên Có Kiểm Soát

<div class="grid-2">
<div class="card">

### 🎲 Cơ chế Sinh Kịch bản Kiểm soát
- **Seed-based Reproducibility**: Tham số `seed="DEFENSE_2026"` bảo đảm cùng 1 seed luôn sinh ra sự cố trên đúng tập cạnh y hệt nhau khi vấn đáp.
- **Phân bổ Sự cố Cân đối**:
  - Tối đa **1 cạnh bị đóng hoàn toàn (`CLOSED`)**.
  - Các cạnh còn lại chia đều cho kẹt xe (`CONGESTED` - thêm $5\text{p}$ delay) và ngập úng (`FLOODED` - gán $R_{\text{flood}} = 1.0$).

</div>
<div class="card">

### 🛡️ Reachability Check bằng Fast BFS
```
Request (Start, Goal, Seed, NumEdges)
   │
   ▼
Chọn ngẫu nhiên tập cạnh bị ảnh hưởng
   │
   ▼
Tạo Scenario tạm ──> Chạy BFS kiểm tra đường đi
   │
   ├──> [CÒN ĐƯỜNG] ──> Trả về Response 200 OK
   │
   └──> [BỊ ĐỨT ĐƯỜNG] ──> Tự động Retry seed mới (max 5)
                            └──> Tránh kịch bản cụt đường
```

</div>
</div>

---

<!-- slide -->
## 23. Trí Tuệ Nhân Tạo Giải Thích Được (Explainable AI - XAI)

Hệ thống tự động sinh diễn giải ngôn ngữ tự nhiên minh bạch:

```
"A_STAR đã chọn lộ trình LM_001 -> LM_012 -> LM_045 -> LM_065 dưới kịch bản PEAK_TRAFFIC.
Tổng chi phí là 0.571500; cự ly 0.322 km và thời gian dự kiến 0.89 phút.
Thành phần chiếm tỷ trọng lớn nhất là freeflow_time (0.285).
Đoạn đường chịu phạt nặng nhất là E_024: độ trễ kẹt xe 1.45 phút và rủi ro ngập 0.00.
Dữ liệu lịch sử UTraffic, không phải real-time. Cam kết: Optimal for non-negative costs."
```

<div class="grid-4" style="margin-top: 10px;">
<div class="card" style="text-align: center;"><strong>1. Tỷ trọng Chi phí</strong><br><small>Xác định yếu tố chi phối</small></div>
<div class="card" style="text-align: center;"><strong>2. Cảnh báo Điểm Nóng</strong><br><small>Chỉ đích danh đoạn kẹt/ngập</small></div>
<div class="card" style="text-align: center;"><strong>3. So sánh Đa tiêu chí</strong><br><small>Shortest vs Fastest vs Best</small></div>
<div class="card" style="text-align: center;"><strong>4. Cam kết Toán học</strong><br><small>Optimal / Near-optimal badge</small></div>
</div>

---

<!-- slide -->
## 24. Giao Diện Người Dùng & Trải Nghiệm Trực Quan (GUI & UX)

<div class="grid-3">
<div class="card">

### 🗺️ Bản đồ Vector GPU
- Tích hợp **MapLibre GL JS** và OpenFreeMap vector basemap, render 60 FPS qua GPU.
- **Snapping 200m thông minh**: Click tự hút vào nút giao gần nhất.
- Marker START (màu cam), GOAL (màu hồng) cố định tọa độ.
- Ranh giới đỏ lịch sử TP. Thủ Đức.

</div>
<div class="card">

### ▶️ Trình phát lại Trace Player
- Quan sát diễn tiến duyệt nút với 3 trạng thái trực quan:
  - 🟡 **Frontier**: Hàng đợi đang chờ
  - 🟢 **Current**: Nút đang xét
  - ⚪ **Closed**: Nút đã đóng
- Thanh trượt Step Slider & Tốc độ phát linh hoạt ($0.5\times - 10\times$).

</div>
<div class="card">

### 🌐 Song ngữ & Phím tắt
- Chuyển đổi tức thì **Tiếng Việt / English (i18n)**.
- Bảng phím tắt tiện lợi:
  - `Space`: Play / Pause
  - `[` / `]`: Lùi / Tiến bước
  - `?`: Mở bảng trợ giúp
- Responsive hoàn chỉnh trên mọi thiết bị.

</div>
</div>

---

<!-- slide -->
## 25. Chiến Lược Kiểm Thử & Đảm Bảo Chất Lượng (QA Suite)

<div class="grid-2">
<div class="card">

### 🧪 11 Bộ Kiểm Thử Tự Động Toàn Diện
1. `test_graph.py`: Tính bất biến của Graph, loaders, Scenario View.
2. `test_cost.py` & `test_cost_profiles.py`: Chi phí 4 thành phần, 3 presets.
3. `test_weighted_algorithms.py`: Tính tối ưu UCS, Admissible/Consistent A*.
4. `test_unweighted_algorithms.py`: BFS, DFS, chu trình, Start = Goal.
5. `test_advance_algorithms.py`: Phản ví dụ Greedy, Bidirectional directed.
6. `test_tc04_multi_stop.py`: Pairwise matrix, Held-Karp vs Brute Force.
7. `test_random_scenario.py`: Tính tái lập của seed và xử lý ngắt kết nối.
8. `test_api.py`: Toàn bộ REST API endpoints, Pydantic schemas, HTTP errors.

</div>
<div class="card" style="justify-content: center; align-items: center; text-align: center;">

### 🏆 Kết Quả Kiểm Thử
<div class="stat-box" style="width: 100%; margin-bottom: 12px;">
  <div style="font-size: 2rem; font-weight: 800; color: #10B981;">100% PASS</div>
  <div style="font-size: 0.8rem; color: #94A3B8;">Toàn bộ Test Suites Backend (Pytest) & Frontend (Vitest)</div>
</div>
<div class="stat-box" style="width: 100%;">
  <div style="font-size: 1.5rem; font-weight: 800; color: #38BDF8;">CI/CD Ready</div>
  <div style="font-size: 0.8rem; color: #94A3B8;">Automated Dataset Checksum & Schema Validation</div>
</div>

</div>
</div>

---

<!-- slide -->
## 26. Chuẩn Bị Câu Hỏi Vấn Đáp Trọng Tâm (Phần 1)

<div class="card" style="margin-bottom: 12px;">

### Q1: Tại sao nhóm dùng khoảng cách Haversine mà không dùng khoảng cách Euclidean trong Heuristic A*?
> **Trả lời**: Trái Đất có bề mặt cong hình cầu. Công thức Euclidean $\sqrt{\Delta x^2 + \Delta y^2}$ trên tọa độ kinh vĩ độ bị biến dạng cự ly nghiêm trọng khi quy đổi ra mét tại vĩ độ Việt Nam ($~10.8^\circ\text{N}$). Hàm **Haversine** tính chính xác khoảng cách cung đại vòng tròn trên mặt cầu trắc địa chuẩn WGS84, bảo đảm bất đẳng thức tam giác cầu luôn đúng.

</div>
<div class="card">

### Q2: Tại sao phải tách riêng Traffic Penalty ($P_{\text{traffic}}$) khỏi Free-Flow Time ($T_{\text{ff}}$) trong hàm chi phí?
> **Trả lời**: Nếu đưa trực tiếp $T_{\text{travel}} = T_{\text{ff}} \times \text{Multiplier}$ vào hàm chi phí cùng với $T_{\text{ff}}$, thời gian di chuyển cơ sở sẽ bị cộng dồn hai lần. Việc tách riêng $P_{\text{traffic}} = \max(0, T_{\text{travel}} - T_{\text{ff}})$ giúp đo lường chính xác phần thời gian trễ phát sinh do kẹt xe và gán trọng số $w_{\text{cong}}$ độc lập.

</div>

---

<!-- slide -->
## 27. Chuẩn Bị Câu Hỏi Vấn Đáp Trọng Tâm (Phần 2)

<div class="card" style="margin-bottom: 12px;">

### Q3: Khi số điểm giao hàng tăng lên 20 - 50 điểm, thuật toán Held-Karp có áp dụng được không?
> **Trả lời**: Không, vì bài toán TSP là NP-hard. Held-Karp có độ phức tạp $O(N^2 2^N)$ sẽ bùng nổ tổ hợp khi $N \ge 20$. Với quy mô lớn, cần chuyển sang các giải thuật Heuristic/Metaheuristic như **Genetic Algorithm (GA), Ant Colony Optimization (ACO), Simulated Annealing** hoặc thư viện tối ưu chuyên dụng Google OR-Tools.

</div>
<div class="card">

### Q4: Làm thế nào bảo đảm A* luôn tìm được đường tối ưu khi kịch bản thay đổi trọng số liên tục?
> **Trả lời**: Nhờ cơ chế tính động hệ số $\rho_s = \min(\text{Cost}_s(e) / D_{\text{Haversine}}(e))$ ngay khi đóng băng kịch bản trước khi chạy A*. Hệ số $\rho_s$ bảo đảm hàm Heuristic luôn là lower-bound (Admissible & Consistent) của mọi đường đi khả thi trong kịch bản đó.

</div>

---

<!-- slide -->
## 28. Tổng Kết Dự Án & Định Hướng Phát Triển Tương Lai

<div class="grid-2">
<div class="card">

### 🌟 4 Điểm Sáng Nổi Bật của Đồ Án
1. **Hoàn thành toàn diện 100% yêu cầu**: Đủ 6 thuật toán tìm kiếm 2 điểm, 2 giải thuật TSP và hệ thống AI giải thích.
2. **Cơ sở Toán học vững chắc**: Heuristic $\rho_s \cdot \text{Haversine}$ được chứng minh chặt chẽ, kiểm chứng qua 3.600 lượt chạy thực nghiệm.
3. **Bám sát thực tế giao thông TP.HCM**: Dữ liệu thật từ OSM/UTraffic, giải quyết bài toán kẹt xe và rốn ngập Chợ Thủ Đức.
4. **Sản phẩm Web hoàn thiện cao cấp**: Bản đồ GPU vector mượt mà, Trace Player trực quan, Đa ngôn ngữ.

</div>
<div class="card">

### 🚀 Hướng Phát triển Tương lai
- **Dữ liệu Thời gian Thực**: Kết nối Live Traffic & Camera giao thông thông minh.
- **Mô hình Thủy lực Động**: Tích hợp mô phỏng ngập lụt theo thời gian thực dựa trên lượng mưa radar (*Nowcasting*).
- **Mở rộng Đội xe (CVRPTW)**: Tối ưu hóa phân phối cho đội xe có ràng buộc tải trọng và khung giờ giao hàng.
- **Deep Reinforcement Learning**: Dự báo luồng giao thông và tự động tái định tuyến (*Dynamic Rerouting*).

</div>
</div>

---

<!-- slide -->
_class: lead
# XIN CHÂN THÀNH CẢM ƠN THẦY VÀ CÁC BẠN ĐÃ LẮNG NGHE!

### Nhóm FloodRoute HCMC sẵn sàng cho phần Vấn đáp (Q&A)

- **Live Demo**: `http://localhost:5173`
- **FastAPI Documentation**: `http://localhost:8000/docs`
- **GitHub Repository**: `Quang-Luu-2005/AI_SearchAlgProject`
