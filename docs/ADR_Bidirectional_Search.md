# Architecture Decision Record
    
## Áp dụng Bidirectional Breadth-First Search

## Bối cảnh: cần cải thiện tốc dộ tìm kiếm trên đồ thị lớn bằng cách tìm đồng thời từ 2 phía. Khó khăn là đồ thị hiện tại là đồ thị có hướng và cấu trúc Graph hiện tại chỉ lưu danh sách cạnh đi ra, không lưu cạnh đi vào.

## Quyết định:
1. Chọn biến thể Unweighted Bidirectional Breadth-First Search: Tối ưu được số node mở rộng từ $O(b^d)$ xuống $O(b^{d/2})$ mà vẫn đảm bảo số hop nhỏ nhất.
2. Xây dựng Reverse Adjacency List động ở $O(\vert{}E\vert{})$ ngay đầu hàm search thay vì sửa đổi Graph contract cốt lõi để duy trì tính bất biến của kiến trúc cũ.
3. Điều kiện dừng: Khi một node được pop ra từ frontier bên này đã tồn tại trong tập visited của frontier bên kia.

## Hệ quả:
Nối path dễ dàng bằng cách lấy path xuôi và path ngược.
