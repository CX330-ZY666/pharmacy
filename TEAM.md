# 💊 药品存销信息管理系统 — 团队分工文档

## 项目信息

| 项目       | 说明                                    |
| ---------- | --------------------------------------- |
| 项目名称   | 药品存销信息管理系统                    |
| 技术栈     | MySQL 8.x + Python Flask + Bootstrap    |
| 远程仓库   | GitHub（组长创建，其他人 Clone）        |
| 成员       | A（组长）、B、C、D                      |

---

## 一、环境准备（全员必做）

### 1. 安装 MySQL

- 下载：https://dev.mysql.com/downloads/installer/
- 选「Developer Default」安装
- **root 密码统一设为 `123456`**
- 安装后自带 MySQL Workbench（图形化工具）

### 2. 安装 Python

- 下载：https://www.python.org/downloads/
- **安装时勾选「Add Python to PATH」**
- 验证：打开命令行输入 `python --version`

### 3. 安装项目依赖

```bash
pip install flask pymysql
```

### 4. 安装 Git

- 下载：https://git-scm.com/downloads
- 注册 GitHub 账号：https://github.com

### 5. 克隆项目（组长创建仓库后）

```bash
# 第一次下载代码
git clone https://github.com/你的用户名/pharmacy.git

# 进入项目目录
cd pharmacy

# 创建自己的分支（B/C/D 各自执行）
git checkout -b dev-B    # 成员B
git checkout -b dev-C    # 成员C
git checkout -b dev-D    # 成员D
```

### 6. 导入数据库

打开 MySQL Workbench，执行 `init_db.sql` 文件中的所有 SQL。

### 7. 启动项目

```bash
python app.py
```

然后浏览器打开 http://127.0.0.1:5000 看到首页就成功了。

---

## 二、GitHub 协作流程

### 分支规则

```
main          ← 稳定代码，只有组长能合并
├── dev-B     ← 成员B 的开发分支
├── dev-C     ← 成员C 的开发分支
└── dev-D     ← 成员D 的开发分支
```

### 每日操作三步走

```bash
# 1. 写代码前，先拉最新代码
git pull origin main
git merge main

# 2. 写完代码后，提交并推送
git add .
git commit -m "完成了什么功能"
git push origin dev-X          # X 换成自己的字母

# 3. 去 GitHub 网页提 Pull Request
#    从 dev-X → main，通知组长审核合并
```

### Git 命令速查表

| 命令                            | 作用                   |
| ------------------------------- | ---------------------- |
| `git clone 仓库地址`           | 第一次下载代码到本地   |
| `git checkout -b dev-X`        | 创建并切换到自己的分支 |
| `git add .`                    | 暂存所有修改           |
| `git commit -m "描述"`         | 提交到本地仓库         |
| `git push origin dev-X`        | 推送到 GitHub          |
| `git pull origin main`         | 拉取主分支最新代码     |
| `git merge main`               | 合并主分支到自己分支   |
| `git status`                   | 查看当前修改状态       |
| `git log --oneline -5`         | 查看最近5条提交记录    |

### 重要约定

- **只改自己负责的文件，不要动别人的**
- 遇到问题先在群里说，不要自己瞎改别人代码
- `config.py` 不提交到 GitHub（已在 `.gitignore` 中忽略）
- 变量命名用英文，注释可以写中文

---

## 三、项目文件结构

每个人只需要关注自己负责的文件：

```
pharmacy/
├── app.py                    ← 【成员A】主程序入口
├── config.py                 ← 【成员A】数据库配置（不提交到Git）
├── config.example.py         ← 【成员A】配置示例（提交到Git）
├── init_db.sql               ← 【成员A】建表 + 测试数据
├── .gitignore                ← 【成员A】Git忽略规则
├── README.md                 ← 【成员A】项目说明
├── TEAM.md                   ← 本文件（分工文档）
│
├── templates/                ← HTML 页面
│   ├── base.html             ← 【成员A】公共模板（导航栏）
│   ├── index.html            ← 【成员A】首页
│   │
│   ├── drug/                 ← 【成员B】
│   │   └── list.html
│   ├── supplier/             ← 【成员B】
│   │   └── list.html
│   ├── customer/             ← 【成员B】
│   │   └── list.html
│   │
│   ├── purchase/             ← 【成员C】
│   │   ├── add.html
│   │   └── list.html
│   ├── sale/                 ← 【成员C】
│   │   ├── add.html
│   │   └── list.html
│   │
│   ├── inventory/            ← 【成员D】
│   │   └── list.html
│   ├── alert/                ← 【成员D】
│   │   └── list.html
│   └── report/               ← 【成员D】
│       └── index.html
│
├── routes/                   ← 后端路由（Python文件）
│   ├── __init__.py           ← 【成员A】空文件
│   ├── drug.py               ← 【成员B】
│   ├── supplier.py           ← 【成员B】
│   ├── customer.py           ← 【成员B】
│   ├── purchase.py           ← 【成员C】
│   ├── sale.py               ← 【成员C】
│   ├── inventory.py          ← 【成员D】
│   ├── alert.py              ← 【成员D】
│   └── report.py             ← 【成员D】
│
└── static/
    └── style.css             ← 自定义样式（可选）
```

---

## 四、数据库设计（8 张表）

> 由成员A统一建表，其他人基于此开发。

### drug（药品表）

| 字段      | 类型         | 说明                     |
| --------- | ------------ | ------------------------ |
| drug_id   | INT 主键自增 | 药品编号                 |
| name      | VARCHAR(100) | 药品名称                 |
| drug_type | VARCHAR(20)  | 处方药 / 非处方药        |
| unit      | VARCHAR(20)  | 单位（盒/瓶/支）        |
| spec      | VARCHAR(50)  | 规格（如 250mg×24粒）   |

### supplier（供应商表）

| 字段           | 类型         | 说明     |
| -------------- | ------------ | -------- |
| supplier_id    | INT 主键自增 | 供应商编号 |
| name           | VARCHAR(100) | 供应商名称 |
| contact_person | VARCHAR(50)  | 联系人   |
| phone          | VARCHAR(20)  | 电话     |
| address        | VARCHAR(200) | 地址     |

### customer（客户表）

| 字段           | 类型         | 说明     |
| -------------- | ------------ | -------- |
| customer_id    | INT 主键自增 | 客户编号 |
| name           | VARCHAR(100) | 客户名称 |
| contact_person | VARCHAR(50)  | 联系人   |
| phone          | VARCHAR(20)  | 电话     |
| address        | VARCHAR(200) | 地址     |

### purchase（采购单表）

| 字段          | 类型           | 说明           |
| ------------- | -------------- | -------------- |
| purchase_id   | INT 主键自增   | 采购单编号     |
| supplier_id   | INT 外键       | 关联供应商     |
| purchase_date | DATE           | 采购日期       |
| total_amount  | DECIMAL(10,2)  | 总金额         |
| note          | VARCHAR(200)   | 备注           |

### purchase_detail（采购明细表）⭐ 关键表

| 字段        | 类型          | 说明                       |
| ----------- | ------------- | -------------------------- |
| detail_id   | INT 主键自增  | 明细编号                   |
| purchase_id | INT 外键      | 关联采购单                 |
| drug_id     | INT 外键      | 关联药品                   |
| batch_no    | VARCHAR(50)   | **批次号**（如 PH20250101）|
| quantity    | INT           | 数量                       |
| price       | DECIMAL(10,2) | 进货单价                   |
| expiry_date | DATE          | **有效期**                 |

> ⭐ 项目亮点：同一个药品，不同批次有不同有效期，必须分开记录。

### sale（销售单表）

| 字段         | 类型           | 说明       |
| ------------ | -------------- | ---------- |
| sale_id      | INT 主键自增   | 销售单编号 |
| customer_id  | INT 外键       | 关联客户   |
| sale_date    | DATE           | 销售日期   |
| total_amount | DECIMAL(10,2)  | 总金额     |

### sale_detail（销售明细表）

| 字段      | 类型          | 说明               |
| --------- | ------------- | ------------------ |
| detail_id | INT 主键自增  | 明细编号           |
| sale_id   | INT 外键      | 关联销售单         |
| drug_id   | INT 外键      | 关联药品           |
| batch_no  | VARCHAR(50)   | 批次号（卖的哪批） |
| quantity  | INT           | 数量               |
| price     | DECIMAL(10,2) | 销售单价           |

### inventory（库存表）⭐ 关键表

| 字段           | 类型          | 说明                     |
| -------------- | ------------- | ------------------------ |
| inventory_id   | INT 主键自增  | 库存记录编号             |
| drug_id        | INT 外键      | 关联药品                 |
| batch_no       | VARCHAR(50)   | 批次号                   |
| quantity       | INT           | 当前库存数量             |
| expiry_date    | DATE          | 有效期                   |
| purchase_price | DECIMAL(10,2) | 进货价（用于算利润）     |
| alert_quantity | INT 默认10    | 库存预警阈值             |

> ⭐ 进货加库存，销售减库存。按「药品 + 批次」维度记录。

### alert（预警记录表）

| 字段       | 类型         | 说明                         |
| ---------- | ------------ | ---------------------------- |
| alert_id   | INT 主键自增 | 预警编号                     |
| drug_id    | INT 外键     | 关联药品                     |
| batch_no   | VARCHAR(50)  | 批次号                       |
| alert_type | VARCHAR(20)  | LOW_STOCK / EXPIRING         |
| message    | VARCHAR(200) | 预警信息                     |
| created_at | DATETIME     | 预警时间                     |
| is_read    | TINYINT      | 是否已读（0=未读 / 1=已读） |

---

## 五、分工详情

---

### 成员A — 组长

> 角色：**架构师 + 整合者**。先把骨架搭好，其他人往里填。

#### A 的文档任务

| 章节               | 内容                                   | 字数  |
| ------------------ | -------------------------------------- | ----- |
| 第1章 背景         | 为什么做、系统目标、解决什么问题       | ~500  |
| 第2章 需求分析     | 5个模块的功能点 + 非功能需求           | ~800  |
| 全文整合（最后做） | 统一格式、目录、页码、封面封底         | —     |

**第1章怎么写：**
- 为什么要做这个系统？（手工记账容易出错、药品有效期管理重要等）
- 系统目标是什么？（实现药品进销存信息化管理）
- 能解决什么问题？（库存预警、过期提醒、利润统计等）

**第2章怎么写：**
- 功能需求：列出5个核心模块各自的功能点
  - 基础信息管理：药品、供应商、客户的增删改查
  - 进货管理：采购单录入、批次管理、自动入库
  - 销售管理：销售开单、按批次出库
  - 库存查询：实时库存、过期预警、低库存预警
  - 统计报表：月销售额、利润分析
- 非功能需求：易用性、数据安全性、响应速度

#### A 的代码任务

| 文件                | 做什么                                     |
| ------------------- | ------------------------------------------ |
| `init_db.sql`       | 建库、建表（8张）、触发器、存储过程、视图、测试数据 |
| `config.py`         | 数据库连接配置                             |
| `config.example.py` | 配置示例文件（提交到Git供他人参考）        |
| `app.py`            | Flask入口：创建应用、注册蓝图、数据库连接函数 |
| `templates/base.html` | 公共模板：导航栏 + Bootstrap CDN          |
| `templates/index.html` | 首页                                    |
| `routes/__init__.py` | 空文件                                    |
| `.gitignore`        | Git忽略规则                                |
| 最终合并            | 合并B/C/D的代码，联调，修Bug              |

---

### 成员B

> 角色：**基础信息管理 + 数据分析文档**。逻辑最简单，但页面最多（3套CRUD）。

#### B 的文档任务

| 章节             | 内容                                        | 字数  |
| ---------------- | ------------------------------------------- | ----- |
| 第3章 数据流图   | 顶层DFD + 0层DFD + 1层DFD（共5~6张图）     | —     |
| 第4章 数据字典   | 数据项、数据流、数据存储、加工词条          | ~2000 |

**第3章怎么画**（用 https://draw.io 免费画图）：
1. **顶层DFD**：整个系统是一个大圆圈，外部实体有「供应商」「客户」「管理员」
2. **0层DFD**：拆成5个子功能（基础管理、进货、销售、库存查询、报表统计）
3. **1层DFD-进货流程**：管理员 → 录入采购单 → 更新库存
4. **1层DFD-销售流程**：管理员 → 录入销售单 → 扣减库存 → 检查库存预警
5. **1层DFD-库存查询流程**：管理员 → 查询库存/过期信息

每张图要标注：数据流名称、数据存储、加工处理。

**第4章怎么写**（对照数据流图写词条）：
- 数据项词条：如 `drug_id = 药品编号, INT, 自增, 唯一标识一种药品`
- 数据流词条：如 `采购信息 = 供应商编号 + 药品编号 + 批次号 + 数量 + 进价 + 有效期`
- 数据存储词条：如 `药品信息文件 = 存放所有药品的基本信息`
- 加工词条：如 `录入采购单 = 验证供应商信息 → 填写药品明细 → 计算总金额 → 保存`

#### B 的代码任务

**需要写的文件：**

| 文件                          | 做什么             |
| ----------------------------- | ------------------ |
| `routes/drug.py`              | 药品的增删改查路由 |
| `routes/supplier.py`          | 供应商的增删改查路由 |
| `routes/customer.py`          | 客户的增删改查路由 |
| `templates/drug/list.html`    | 药品管理页面       |
| `templates/supplier/list.html`| 供应商管理页面     |
| `templates/customer/list.html`| 客户管理页面       |

**每个路由文件的接口**（以 drug.py 为例，其他两个一样，换个表名和字段就行）：

| 路由                | 方法 | 功能                       |
| ------------------- | ---- | -------------------------- |
| `/drug`             | GET  | 显示药品列表（支持搜索）   |
| `/drug/add`         | GET  | 显示添加表单               |
| `/drug/add`         | POST | 把表单数据 INSERT 到药品表 |
| `/drug/edit/<id>`   | GET  | 显示编辑表单（预填数据）   |
| `/drug/edit/<id>`   | POST | UPDATE 药品表              |
| `/drug/delete/<id>` | GET  | DELETE 对应记录            |

**页面长什么样：**
- 顶部搜索框（输入药品名 → 模糊查询）
- 一个表格显示所有记录
- 每行有「编辑」「删除」按钮
- 表格上方有「新增」按钮

> 💡 提示：写完 drug 模块后，supplier 和 customer 复制改改字段就行，逻辑完全一样。

---

### 成员C

> 角色：**进销核心业务**。逻辑最复杂，是系统的核心功能。

#### C 的文档任务

| 章节             | 内容                                     | 字数 |
| ---------------- | ---------------------------------------- | ---- |
| 第5章 概念设计   | 各实体E-R图（6张）+ 全局E-R图（1张）    | —    |

**怎么画**（用 https://draw.io）：
1. 药品实体E-R图：矩形(drug) + 椭圆(各属性)
2. 供应商实体E-R图
3. 客户实体E-R图
4. 采购单实体E-R图（含采购明细）
5. 销售单实体E-R图（含销售明细）
6. 库存实体E-R图
7. **全局E-R图**（最重要！）：所有实体放一张图，标注关系：
   - 供应商 —1:N→ 采购单
   - 采购单 —1:N→ 采购明细
   - 药品 —1:N→ 采购明细
   - 客户 —1:N→ 销售单
   - 销售单 —1:N→ 销售明细
   - 药品 —1:N→ 库存（按批次）

#### C 的代码任务

**需要写的文件：**

| 文件                           | 做什么           |
| ------------------------------ | ---------------- |
| `routes/purchase.py`           | 进货管理路由     |
| `routes/sale.py`               | 销售管理路由     |
| `templates/purchase/add.html`  | 采购录入页面     |
| `templates/purchase/list.html` | 采购单列表页面   |
| `templates/sale/add.html`      | 销售录入页面     |
| `templates/sale/list.html`     | 销售单列表页面   |

**routes/purchase.py 核心逻辑：**

| 路由               | 方法 | 功能         |
| ------------------ | ---- | ------------ |
| `/purchase`        | GET  | 采购单列表   |
| `/purchase/add`    | GET  | 显示录入页面 |
| `/purchase/add`    | POST | 保存采购单 ⬇ |
| `/purchase/<id>`   | GET  | 查看详情     |

**POST /purchase/add 核心步骤：**
1. INSERT 到 purchase 表 → 拿到 purchase_id
2. 循环 INSERT 每条明细到 purchase_detail 表
3. 对每条明细更新 inventory 表：
   - 查 inventory 有没有相同 drug_id + batch_no 的记录
   - **有** → `UPDATE quantity = quantity + 新数量`
   - **没有** → `INSERT 新记录`（含 expiry_date, purchase_price）
4. UPDATE purchase 表的 total_amount

**routes/sale.py 核心逻辑：**

| 路由           | 方法 | 功能         |
| -------------- | ---- | ------------ |
| `/sale`        | GET  | 销售单列表   |
| `/sale/add`    | GET  | 显示录入页面 |
| `/sale/add`    | POST | 保存销售单 ⬇ |
| `/sale/<id>`   | GET  | 查看详情     |

**POST /sale/add 核心步骤：**
1. INSERT 到 sale 表
2. 循环 INSERT 每条明细到 sale_detail 表
3. 对每条明细扣减 inventory 表：
   - `UPDATE inventory SET quantity = quantity - 销售数量 WHERE drug_id=? AND batch_no=?`
   - 如果扣减后 quantity < 0 → **拒绝，提示「库存不足」**
4. UPDATE sale 表的 total_amount

**页面注意点：**
- 采购录入页面：需要「动态添加明细行」功能（点 `+` 按钮增加一行输入框，用简单JS实现）
- 销售录入页面：「批次」下拉框只显示有库存的批次

---

### 成员D

> 角色：**SQL高级功能 + 文档收尾**。写触发器、存储过程、视图，以及报表展示。

#### D 的文档任务

| 章节                     | 内容                                     | 字数  |
| ------------------------ | ---------------------------------------- | ----- |
| 第6章 详细设计           | 开发平台 + 各表结构 + 关键SQL说明        | ~1500 |
| 第7章 界面设计           | 所有页面截图 + 功能说明                  | ~1000 |
| 第8章 总结 + 参考文献    | 总结 + 参考文献                          | ~500  |

**第6章怎么写：**
- 6.1 开发平台说明：MySQL 8.x + Python 3.x + Flask + Bootstrap
- 6.2 各表结构说明：把8张表用表格列出（字段名、类型、说明、约束）
- 6.3 关键SQL说明：贴出触发器、存储过程、视图的代码并加注释解释

**第7章怎么写：**
- 收集所有人做好的页面截图
- 每个页面一张截图 + 2~3句功能说明
- 如：「图X 药品管理界面：展示所有药品信息，支持按名称模糊搜索，可进行增删改查操作」

**第8章怎么写：**
- 总结：项目完成情况、遇到的困难、学到了什么
- 参考文献：《数据库系统概论（第5版）》萨师煊 高等教育出版社 等

#### D 的代码任务

**需要写的文件：**

| 文件                            | 做什么               |
| ------------------------------- | -------------------- |
| `routes/inventory.py`           | 库存查询路由         |
| `routes/alert.py`               | 预警信息路由         |
| `routes/report.py`              | 统计报表路由         |
| `templates/inventory/list.html` | 库存查询页面         |
| `templates/alert/list.html`     | 预警信息页面         |
| `templates/report/index.html`   | 统计报表页面         |
| SQL触发器 × 2                   | 交给成员A整合        |
| SQL存储过程 × 2                 | 交给成员A整合        |
| SQL视图 × 2                     | 交给成员A整合        |

**SQL 部分（写好后发给成员A整合进 init_db.sql）：**

**触发器1：trg_low_stock**
```sql
-- 库存数量更新后，检查是否低于预警阈值
CREATE TRIGGER trg_low_stock
AFTER UPDATE ON inventory
FOR EACH ROW
BEGIN
    IF NEW.quantity < NEW.alert_quantity AND NEW.quantity >= 0 THEN
        INSERT INTO alert(drug_id, batch_no, alert_type, message, created_at, is_read)
        VALUES(NEW.drug_id, NEW.batch_no, 'LOW_STOCK',
               CONCAT('库存不足预警：药品ID=', NEW.drug_id,
                      ' 批次=', NEW.batch_no,
                      ' 当前库存=', NEW.quantity),
               NOW(), 0);
    END IF;
END;
```

**触发器2：trg_expiry_warn**
```sql
-- 新增库存记录时，检查有效期是否在30天内
CREATE TRIGGER trg_expiry_warn
AFTER INSERT ON inventory
FOR EACH ROW
BEGIN
    IF DATEDIFF(NEW.expiry_date, CURDATE()) <= 30 THEN
        INSERT INTO alert(drug_id, batch_no, alert_type, message, created_at, is_read)
        VALUES(NEW.drug_id, NEW.batch_no, 'EXPIRING',
               CONCAT('过期预警：药品ID=', NEW.drug_id,
                      ' 批次=', NEW.batch_no,
                      ' 将于', NEW.expiry_date, '过期'),
               NOW(), 0);
    END IF;
END;
```

**存储过程1：sp_monthly_sales**
```sql
-- 按月统计销售额
CREATE PROCEDURE sp_monthly_sales(IN p_year INT, IN p_month INT)
BEGIN
    SELECT d.name AS 药品名称,
           SUM(sd.quantity) AS 销售数量,
           SUM(sd.quantity * sd.price) AS 销售额
    FROM sale_detail sd
    JOIN sale s ON sd.sale_id = s.sale_id
    JOIN drug d ON sd.drug_id = d.drug_id
    WHERE YEAR(s.sale_date) = p_year AND MONTH(s.sale_date) = p_month
    GROUP BY d.drug_id, d.name;
END;
```

**存储过程2：sp_profit_report**
```sql
-- 按月统计利润
CREATE PROCEDURE sp_profit_report(IN p_year INT, IN p_month INT)
BEGIN
    SELECT d.name AS 药品名称,
           SUM(sd.quantity) AS 销售数量,
           SUM(sd.quantity * sd.price) AS 销售收入,
           SUM(sd.quantity * inv.purchase_price) AS 进货成本,
           SUM(sd.quantity * (sd.price - inv.purchase_price)) AS 利润
    FROM sale_detail sd
    JOIN sale s ON sd.sale_id = s.sale_id
    JOIN drug d ON sd.drug_id = d.drug_id
    JOIN inventory inv ON sd.drug_id = inv.drug_id AND sd.batch_no = inv.batch_no
    WHERE YEAR(s.sale_date) = p_year AND MONTH(s.sale_date) = p_month
    GROUP BY d.drug_id, d.name;
END;
```

**视图1：v_current_stock**
```sql
CREATE VIEW v_current_stock AS
SELECT inv.inventory_id, d.name AS 药品名称, inv.batch_no AS 批次号,
       inv.quantity AS 库存数量, inv.expiry_date AS 有效期,
       inv.purchase_price AS 进价, inv.alert_quantity AS 预警阈值,
       CASE WHEN inv.quantity < inv.alert_quantity THEN '⚠ 库存不足' ELSE '正常' END AS 库存状态
FROM inventory inv
JOIN drug d ON inv.drug_id = d.drug_id;
```

**视图2：v_expiring_drugs**
```sql
CREATE VIEW v_expiring_drugs AS
SELECT d.name AS 药品名称, inv.batch_no AS 批次号,
       inv.quantity AS 库存数量, inv.expiry_date AS 有效期,
       DATEDIFF(inv.expiry_date, CURDATE()) AS 剩余天数
FROM inventory inv
JOIN drug d ON inv.drug_id = d.drug_id
WHERE DATEDIFF(inv.expiry_date, CURDATE()) <= 30
ORDER BY inv.expiry_date;
```

**Flask 页面部分：**

| 路由          | 功能                                           |
| ------------- | ---------------------------------------------- |
| GET /inventory| 查询 v_current_stock 视图，展示库存列表（支持搜索）|
| GET /alert    | 查询 alert 表，展示预警信息，提供「标记已读」按钮 |
| GET /report   | 选年月 → 调存储过程 → 展示销售额和利润表格     |

页面注意点：
- 库存页面：用红色背景标记低库存和即将过期的行
- 预警页面：区分「库存不足」和「即将过期」两类
- 报表页面：用 HTML 表格展示即可

---

## 六、时间线（建议3周）

### 第1周：搭基础

| 谁     | 做什么                                                    |
| ------ | --------------------------------------------------------- |
| 全员   | 安装环境（MySQL + Python + Flask + Git）                  |
| 成员A  | 创建 GitHub 仓库 → 完成建表SQL + Flask骨架 → 推送到仓库  |
| 全员   | Clone 仓库 → 导入SQL → `python app.py` 确认能跑          |
| 成员D  | 写好触发器+存储过程+视图的SQL → 提PR给成员A              |

### 第2周：各写各的

| 谁     | 做什么                                                    |
| ------ | --------------------------------------------------------- |
| 成员B  | 写 drug.py + supplier.py + customer.py + 3个HTML → 提PR  |
| 成员C  | 写 purchase.py + sale.py + 4个HTML → 提PR                |
| 成员D  | 写 inventory.py + alert.py + report.py + 3个HTML → 提PR  |
| 成员A  | 写背景+需求分析文档，审核PR，帮其他人解决问题            |
| 全员   | 同步写自己负责的文档章节                                  |

### 第3周：合并收尾

| 谁     | 做什么                                                    |
| ------ | --------------------------------------------------------- |
| 成员A  | 合并所有PR → 联调测试 → 修Bug                            |
| 成员D  | 收集所有页面截图 → 写第7章界面设计                        |
| 成员A  | 整合所有文档 → 统一格式排版 → 生成目录                   |
| 全员   | 互相检查文档，查缺补漏                                    |

---

## 七、分工总览

| 成员 | 文档                          | 代码                                         | 难度特点           |
| ---- | ----------------------------- | -------------------------------------------- | ------------------ |
| A    | 背景+需求分析+全文整合        | 建表SQL+Flask骨架+合并联调                   | 架构把控，整合量大 |
| B    | 数据流图+数据字典             | 药品/供应商/客户 CRUD × 3页面                | 画图多，逻辑简单   |
| C    | E-R图（实体+全局）            | 进货+销售（批次管理）× 4页面                 | 业务逻辑最复杂     |
| D    | 详细设计+界面设计+总结        | 触发器+存储过程+视图+查询/报表 × 3页面       | SQL难度最高        |
