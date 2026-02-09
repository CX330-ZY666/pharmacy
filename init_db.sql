-- ============================================================
-- 药品存销信息管理系统 - 数据库初始化脚本
-- 使用方法：在 MySQL Workbench 中打开此文件，全选执行
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS pharmacy DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_general_ci;
USE pharmacy;

-- ============================================================
-- 一、建表（8张表）
-- ============================================================

-- 1. 药品表
CREATE TABLE IF NOT EXISTS drug (
    drug_id    INT PRIMARY KEY AUTO_INCREMENT COMMENT '药品编号',
    name       VARCHAR(100) NOT NULL COMMENT '药品名称',
    drug_type  VARCHAR(20)  NOT NULL COMMENT '处方药/非处方药',
    unit       VARCHAR(20)  NOT NULL COMMENT '单位（盒/瓶/支）',
    spec       VARCHAR(50)  DEFAULT NULL COMMENT '规格（如250mg×24粒）'
) COMMENT '药品信息表';

-- 2. 供应商表
CREATE TABLE IF NOT EXISTS supplier (
    supplier_id    INT PRIMARY KEY AUTO_INCREMENT COMMENT '供应商编号',
    name           VARCHAR(100) NOT NULL COMMENT '供应商名称',
    contact_person VARCHAR(50)  DEFAULT NULL COMMENT '联系人',
    phone          VARCHAR(20)  DEFAULT NULL COMMENT '电话',
    address        VARCHAR(200) DEFAULT NULL COMMENT '地址'
) COMMENT '供应商信息表';

-- 3. 客户表
CREATE TABLE IF NOT EXISTS customer (
    customer_id    INT PRIMARY KEY AUTO_INCREMENT COMMENT '客户编号',
    name           VARCHAR(100) NOT NULL COMMENT '客户名称',
    contact_person VARCHAR(50)  DEFAULT NULL COMMENT '联系人',
    phone          VARCHAR(20)  DEFAULT NULL COMMENT '电话',
    address        VARCHAR(200) DEFAULT NULL COMMENT '地址'
) COMMENT '客户信息表';

-- 4. 采购单表
CREATE TABLE IF NOT EXISTS purchase (
    purchase_id   INT PRIMARY KEY AUTO_INCREMENT COMMENT '采购单编号',
    supplier_id   INT NOT NULL COMMENT '供应商编号',
    purchase_date DATE NOT NULL COMMENT '采购日期',
    total_amount  DECIMAL(10,2) DEFAULT 0.00 COMMENT '总金额',
    note          VARCHAR(200) DEFAULT NULL COMMENT '备注',
    FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id)
) COMMENT '采购单表';

-- 5. 采购明细表（关键：记录批次号和有效期）
CREATE TABLE IF NOT EXISTS purchase_detail (
    detail_id   INT PRIMARY KEY AUTO_INCREMENT COMMENT '明细编号',
    purchase_id INT NOT NULL COMMENT '采购单编号',
    drug_id     INT NOT NULL COMMENT '药品编号',
    batch_no    VARCHAR(50) NOT NULL COMMENT '批次号',
    quantity    INT NOT NULL COMMENT '数量',
    price       DECIMAL(10,2) NOT NULL COMMENT '进货单价',
    expiry_date DATE NOT NULL COMMENT '有效期',
    FOREIGN KEY (purchase_id) REFERENCES purchase(purchase_id),
    FOREIGN KEY (drug_id) REFERENCES drug(drug_id)
) COMMENT '采购明细表';

-- 6. 销售单表
CREATE TABLE IF NOT EXISTS sale (
    sale_id      INT PRIMARY KEY AUTO_INCREMENT COMMENT '销售单编号',
    customer_id  INT NOT NULL COMMENT '客户编号',
    sale_date    DATE NOT NULL COMMENT '销售日期',
    total_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '总金额',
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
) COMMENT '销售单表';

-- 7. 销售明细表
CREATE TABLE IF NOT EXISTS sale_detail (
    detail_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '明细编号',
    sale_id   INT NOT NULL COMMENT '销售单编号',
    drug_id   INT NOT NULL COMMENT '药品编号',
    batch_no  VARCHAR(50) NOT NULL COMMENT '批次号',
    quantity  INT NOT NULL COMMENT '数量',
    price     DECIMAL(10,2) NOT NULL COMMENT '销售单价',
    FOREIGN KEY (sale_id) REFERENCES sale(sale_id),
    FOREIGN KEY (drug_id) REFERENCES drug(drug_id)
) COMMENT '销售明细表';

-- 8. 库存表（按药品+批次维度记录）
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id   INT PRIMARY KEY AUTO_INCREMENT COMMENT '库存记录编号',
    drug_id        INT NOT NULL COMMENT '药品编号',
    batch_no       VARCHAR(50) NOT NULL COMMENT '批次号',
    quantity       INT NOT NULL DEFAULT 0 COMMENT '当前库存数量',
    expiry_date    DATE NOT NULL COMMENT '有效期',
    purchase_price DECIMAL(10,2) NOT NULL COMMENT '进货价',
    alert_quantity INT NOT NULL DEFAULT 10 COMMENT '库存预警阈值',
    FOREIGN KEY (drug_id) REFERENCES drug(drug_id)
) COMMENT '库存表';

-- 9. 预警记录表
CREATE TABLE IF NOT EXISTS alert (
    alert_id   INT PRIMARY KEY AUTO_INCREMENT COMMENT '预警编号',
    drug_id    INT NOT NULL COMMENT '药品编号',
    batch_no   VARCHAR(50) NOT NULL COMMENT '批次号',
    alert_type VARCHAR(20) NOT NULL COMMENT '预警类型：LOW_STOCK/EXPIRING',
    message    VARCHAR(200) NOT NULL COMMENT '预警信息',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '预警时间',
    is_read    TINYINT NOT NULL DEFAULT 0 COMMENT '是否已读（0未读/1已读）',
    FOREIGN KEY (drug_id) REFERENCES drug(drug_id)
) COMMENT '预警记录表';


-- ============================================================
-- 二、触发器（成员D负责，已整合）
-- ============================================================

-- 触发器1：库存不足预警
-- 当 inventory 的 quantity 被更新后，如果低于预警阈值，自动写入 alert 表
DELIMITER //
CREATE TRIGGER trg_low_stock
AFTER UPDATE ON inventory
FOR EACH ROW
BEGIN
    IF NEW.quantity < NEW.alert_quantity AND NEW.quantity >= 0 THEN
        INSERT INTO alert(drug_id, batch_no, alert_type, message, created_at, is_read)
        VALUES(NEW.drug_id, NEW.batch_no, 'LOW_STOCK',
               CONCAT('库存不足预警：药品ID=', NEW.drug_id, ' 批次=', NEW.batch_no, ' 当前库存=', NEW.quantity),
               NOW(), 0);
    END IF;
END//
DELIMITER ;

-- 触发器2：过期预警
-- 当 inventory 新增记录时，如果有效期在30天内，自动写入 alert 表
DELIMITER //
CREATE TRIGGER trg_expiry_warn
AFTER INSERT ON inventory
FOR EACH ROW
BEGIN
    IF DATEDIFF(NEW.expiry_date, CURDATE()) <= 30 THEN
        INSERT INTO alert(drug_id, batch_no, alert_type, message, created_at, is_read)
        VALUES(NEW.drug_id, NEW.batch_no, 'EXPIRING',
               CONCAT('过期预警：药品ID=', NEW.drug_id, ' 批次=', NEW.batch_no, ' 将于', NEW.expiry_date, '过期'),
               NOW(), 0);
    END IF;
END//
DELIMITER ;


-- ============================================================
-- 三、存储过程（成员D负责，已整合）
-- ============================================================

-- 存储过程1：按月统计销售额
DELIMITER //
CREATE PROCEDURE sp_monthly_sales(IN p_year INT, IN p_month INT)
BEGIN
    SELECT d.name AS '药品名称',
           SUM(sd.quantity) AS '销售数量',
           SUM(sd.quantity * sd.price) AS '销售额'
    FROM sale_detail sd
    JOIN sale s ON sd.sale_id = s.sale_id
    JOIN drug d ON sd.drug_id = d.drug_id
    WHERE YEAR(s.sale_date) = p_year AND MONTH(s.sale_date) = p_month
    GROUP BY d.drug_id, d.name
    ORDER BY SUM(sd.quantity * sd.price) DESC;
END//
DELIMITER ;

-- 存储过程2：按月统计利润
DELIMITER //
CREATE PROCEDURE sp_profit_report(IN p_year INT, IN p_month INT)
BEGIN
    SELECT d.name AS '药品名称',
           SUM(sd.quantity) AS '销售数量',
           SUM(sd.quantity * sd.price) AS '销售收入',
           SUM(sd.quantity * inv.purchase_price) AS '进货成本',
           SUM(sd.quantity * (sd.price - inv.purchase_price)) AS '利润'
    FROM sale_detail sd
    JOIN sale s ON sd.sale_id = s.sale_id
    JOIN drug d ON sd.drug_id = d.drug_id
    JOIN inventory inv ON sd.drug_id = inv.drug_id AND sd.batch_no = inv.batch_no
    WHERE YEAR(s.sale_date) = p_year AND MONTH(s.sale_date) = p_month
    GROUP BY d.drug_id, d.name
    ORDER BY SUM(sd.quantity * (sd.price - inv.purchase_price)) DESC;
END//
DELIMITER ;


-- ============================================================
-- 四、视图（成员D负责，已整合）
-- ============================================================

-- 视图1：实时库存汇总
CREATE VIEW v_current_stock AS
SELECT inv.inventory_id,
       d.name AS drug_name,
       d.drug_type,
       d.unit,
       inv.batch_no,
       inv.quantity,
       inv.expiry_date,
       inv.purchase_price,
       inv.alert_quantity,
       CASE WHEN inv.quantity < inv.alert_quantity THEN '库存不足' ELSE '正常' END AS stock_status,
       CASE WHEN DATEDIFF(inv.expiry_date, CURDATE()) <= 30 THEN '即将过期'
            WHEN DATEDIFF(inv.expiry_date, CURDATE()) <= 0 THEN '已过期'
            ELSE '正常' END AS expiry_status,
       DATEDIFF(inv.expiry_date, CURDATE()) AS days_remaining
FROM inventory inv
JOIN drug d ON inv.drug_id = d.drug_id;

-- 视图2：即将过期药品清单（30天内）
CREATE VIEW v_expiring_drugs AS
SELECT d.name AS drug_name,
       d.unit,
       inv.batch_no,
       inv.quantity,
       inv.expiry_date,
       DATEDIFF(inv.expiry_date, CURDATE()) AS days_remaining
FROM inventory inv
JOIN drug d ON inv.drug_id = d.drug_id
WHERE DATEDIFF(inv.expiry_date, CURDATE()) <= 30
ORDER BY inv.expiry_date;


-- ============================================================
-- 五、测试数据
-- ============================================================

-- 药品（15条）
INSERT INTO drug (name, drug_type, unit, spec) VALUES
('阿莫西林胶囊',    '处方药',   '盒', '250mg×24粒'),
('布洛芬缓释胶囊',  '非处方药', '盒', '300mg×20粒'),
('复方感冒灵颗粒',  '非处方药', '袋', '10g×12袋'),
('阿奇霉素片',      '处方药',   '盒', '250mg×6片'),
('头孢克肟分散片',  '处方药',   '盒', '100mg×10片'),
('板蓝根颗粒',      '非处方药', '袋', '10g×20袋'),
('维生素C片',       '非处方药', '瓶', '100mg×100片'),
('蒙脱石散',        '非处方药', '盒', '3g×10袋'),
('氯雷他定片',      '非处方药', '盒', '10mg×6片'),
('奥美拉唑肠溶胶囊','处方药',   '盒', '20mg×14粒'),
('硝苯地平缓释片',  '处方药',   '盒', '20mg×30片'),
('二甲双胍片',      '处方药',   '盒', '500mg×20片'),
('止咳糖浆',        '非处方药', '瓶', '120ml'),
('创可贴',          '非处方药', '盒', '100片'),
('碘伏消毒液',      '非处方药', '瓶', '500ml');

-- 供应商（5条）
INSERT INTO supplier (name, contact_person, phone, address) VALUES
('国药集团',     '张经理', '13800138001', '北京市朝阳区国药大厦'),
('华润医药',     '李经理', '13800138002', '深圳市南山区华润中心'),
('上药集团',     '王经理', '13800138003', '上海市浦东新区上药大楼'),
('广药集团',     '陈经理', '13800138004', '广州市天河区广药园区'),
('九州通医药',   '刘经理', '13800138005', '武汉市东西湖区九州通大厦');

-- 客户（5条）
INSERT INTO customer (name, contact_person, phone, address) VALUES
('仁和大药房',       '赵店长', '15900159001', '长沙市岳麓区银杏路88号'),
('百姓缘大药房',     '钱店长', '15900159002', '长沙市雨花区劳动路120号'),
('老百姓大药房',     '孙店长', '15900159003', '长沙市开福区芙蓉路200号'),
('益丰大药房',       '周店长', '15900159004', '长沙市天心区解放路66号'),
('市第一人民医院药房','吴主任', '15900159005', '长沙市芙蓉区人民路1号');

-- 采购单（4笔）
INSERT INTO purchase (supplier_id, purchase_date, total_amount, note) VALUES
(1, '2025-12-01', 5400.00, '常规补货'),
(2, '2025-12-10', 3200.00, '冬季感冒药补货'),
(3, '2026-01-05', 4800.00, '新年备货'),
(1, '2026-01-20', 2600.00, '紧急补货');

-- 采购明细（含不同批次号和有效期 —— 项目亮点）
INSERT INTO purchase_detail (purchase_id, drug_id, batch_no, quantity, price, expiry_date) VALUES
-- 第1笔采购
(1, 1,  'PH20251201A', 100, 12.00, '2027-12-01'),   -- 阿莫西林 批次A
(1, 2,  'PH20251201B', 80,  15.00, '2027-06-01'),    -- 布洛芬 批次B
(1, 4,  'PH20251201C', 50,  28.00, '2027-03-01'),    -- 阿奇霉素 批次C
-- 第2笔采购
(2, 3,  'PH20251210A', 200, 8.00,  '2027-12-10'),    -- 感冒灵
(2, 6,  'PH20251210B', 150, 6.00,  '2027-06-10'),    -- 板蓝根
-- 第3笔采购
(3, 1,  'PH20260105A', 80,  12.50, '2028-01-05'),    -- 阿莫西林 批次B（不同批次！）
(3, 7,  'PH20260105B', 100, 5.00,  '2028-01-05'),    -- 维生素C
(3, 10, 'PH20260105C', 60,  22.00, '2027-07-05'),    -- 奥美拉唑
-- 第4笔采购（含一个即将过期的批次 —— 测试过期预警）
(4, 5,  'PH20260120A', 40,  35.00, '2026-03-01'),    -- 头孢克肟（快过期！）
(4, 8,  'PH20260120B', 120, 4.50,  '2027-07-20');    -- 蒙脱石散

-- 库存（与采购明细对应）
INSERT INTO inventory (drug_id, batch_no, quantity, expiry_date, purchase_price, alert_quantity) VALUES
(1,  'PH20251201A', 85,  '2027-12-01', 12.00, 10),   -- 阿莫西林批次A（已卖15）
(2,  'PH20251201B', 70,  '2027-06-01', 15.00, 10),   -- 布洛芬（已卖10）
(4,  'PH20251201C', 42,  '2027-03-01', 28.00, 10),   -- 阿奇霉素（已卖8）
(3,  'PH20251210A', 180, '2027-12-10', 8.00,  20),   -- 感冒灵（已卖20）
(6,  'PH20251210B', 130, '2027-06-10', 6.00,  20),   -- 板蓝根（已卖20）
(1,  'PH20260105A', 80,  '2028-01-05', 12.50, 10),   -- 阿莫西林批次B（新批次，未卖）
(7,  'PH20260105B', 90,  '2028-01-05', 5.00,  10),   -- 维生素C（已卖10）
(10, 'PH20260105C', 55,  '2027-07-05', 22.00, 10),   -- 奥美拉唑（已卖5）
(5,  'PH20260120A', 8,   '2026-03-01', 35.00, 10),   -- 头孢克肟（库存不足+即将过期！）
(8,  'PH20260120B', 110, '2027-07-20', 4.50,  15);   -- 蒙脱石散（已卖10）

-- 销售单（3笔）
INSERT INTO sale (customer_id, sale_date, total_amount) VALUES
(1, '2025-12-15', 810.00),
(2, '2026-01-10', 1040.00),
(3, '2026-01-18', 535.00);

-- 销售明细
INSERT INTO sale_detail (sale_id, drug_id, batch_no, quantity, price) VALUES
-- 第1笔销售
(1, 1, 'PH20251201A', 15, 18.00),   -- 阿莫西林 卖15盒×18元 = 270
(1, 2, 'PH20251201B', 10, 22.00),   -- 布洛芬 卖10盒×22元 = 220
(1, 3, 'PH20251210A', 20, 12.00),   -- 感冒灵 卖20袋×12元 = 240
(1, 4, 'PH20251201C', 3,  40.00),   -- 阿奇霉素 卖3盒×40元 = 120 -> 总计810 不对，调整下
-- 第2笔销售
(2, 6, 'PH20251210B', 20, 10.00),   -- 板蓝根 卖20袋×10元 = 200
(2, 4, 'PH20251201C', 5,  42.00),   -- 阿奇霉素 卖5盒×42元 = 210
(2, 7, 'PH20260105B', 10, 8.00),    -- 维生素C 卖10瓶×8元 = 80
(2, 10,'PH20260105C', 5,  35.00),   -- 奥美拉唑 卖5盒×35元 = 175 -> 665
-- 第3笔销售
(3, 5, 'PH20260120A', 32, 50.00),   -- 头孢克肟 卖32盒×50元（库存只剩8了）
(3, 8, 'PH20260120B', 10, 7.50);    -- 蒙脱石散 卖10盒×7.5元 = 75

-- 手动插入一些预警记录（模拟触发器效果）
INSERT INTO alert (drug_id, batch_no, alert_type, message, created_at, is_read) VALUES
(5, 'PH20260120A', 'LOW_STOCK',  '库存不足预警：头孢克肟分散片 批次PH20260120A 当前库存=8', '2026-01-18 15:30:00', 0),
(5, 'PH20260120A', 'EXPIRING',   '过期预警：头孢克肟分散片 批次PH20260120A 将于2026-03-01过期', '2026-01-20 10:00:00', 0);

-- 更新销售单总金额
UPDATE sale SET total_amount = (
    SELECT COALESCE(SUM(quantity * price), 0) FROM sale_detail WHERE sale_detail.sale_id = sale.sale_id
);
