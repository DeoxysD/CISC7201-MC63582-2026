# Project 01: Order Event Data Processing

## 0. Introduction

You are given an approximately 1 GB dataset, supplied in `Datasets.zip`.

The dataset is split into 8 CSV files, which together form one event log with 18 columns.

```text
Datasets.zip
└── Datasets/
    ├── events_part1.csv
    ├── events_part2.csv
    ├── events_part3.csv
    ├── ...
    └── events_part8.csv
```

You are asked to inspect the order events for formatting, missing-value, duplicate, and business-logic issues.

You are encouraged to use AI for analysis and coding. However, you are NOT allowed to use agents, harnesses, skills, or similar automation tools.

After your analysis, please submit:

- A `.txt` file containing all problematic original event IDs.
- Your completed `project_01_template.py` file.
- An AI declaration briefly describing how you used AI. (Optional)

Please read the detailed instructions below.

## 1. Read the data

Please refer to [project_01_template.py](project_01_template.py) for the Python code to read the data and export your results. Place `Datasets.zip` in the same folder as the script, and fill in the analysis area for your chosen mode: `USE_CHUNKS = True` reads in batches; `USE_CHUNKS = False` loads all eight files into memory.

Make sure you have enough disk space for the extracted files (approximately 1.2 GB).

Make sure your output: the total rows of this dataset is `9,604,621`.

An order or transaction may appear in different files or batches. Your checks must cover all eight files. In chunked mode, do not keep every batch in a list, as this would load the whole dataset into memory.

## 2. Detail introduction of Dataset columns

**Each row is an event, not an order.** 

An order_id may have creation, payment, shipping, refund, delivery, and cancellation events.

| # | Column | Meaning | Correct Example |
| --- | --- | --- | --- |
| 1 | event_id | 事件编号 / Event ID | EV200101 |
| 2 | order_id | 订单编号 / Order ID | ORD2001 |
| 3 | event_type | 事件类型 / Event type | PAYMENT_SUCCESS |
| 4 | event_time | 业务发生时间 / Time the event occurred | 2025-03-01T09:00:00+08:00 |
| 5 | source_system | 订单所属平台 / Order platform | MEITUAN, JD, TAOBAO, PDD, XIANYU |
| 6 | customer_id | 客户编号 / Customer ID | C2001 |
| 7 | name | 客户姓名 / Customer name | Amy Lee |
| 8 | tel | 联系电话，按字符串保存 / Telephone, stored as text | 13800000001 |
| 9 | product_id | 购买的商品编号 / Product ID | SKU2001 |
| 10 | quantity | 购买数量，正整数 / Quantity, a positive integer | 2 |
| 11 | unit_price | 商品单价 / Unit price | 60.00 |
| 12 | discount_amount | 整笔订单优惠 / Order-level discount | 10.00 |
| 13 | shipping_fee | 整笔订单运费 / Order-level shipping fee | 5.00 |
| 14 | amount | 当前事件对应的金额 / Amount associated with this event | 115.00 |
| 15 | currency | 币种 / Currency | CNY, USD, EUR |
| 16 | payment_method | 支付或退款方式 / Payment or refund method | VISA, MASTERCARD, PAYPAL, ALIPAY, WECHAT_PAY |
| 17 | transaction_id | 一笔支付尝试或退款的编号 / Payment-attempt or refund ID | TX200101, RF200101 |
| 18 | shipment_id | 包裹编号 / Parcel ID | SHP2001 |

### Event types and required fields

Every event requires event_id, order_id, event_type, event_time, and source_system. 

Please note that customer details may be blank on non-creation events, and this event_type may not be incorrect, which means you cannot simply removed the blank units; product details are required only on creation events.

Additional requirements are below. 

| event_type | Meaning of amount | Additional required fields |
| --- | --- | --- |
| ORDER_CREATED | Order total | customer_id, name, tel, product_id, quantity, unit_price, discount_amount, shipping_fee, amount, currency |
| PAYMENT_SUCCESS |  Successful payment | amount, currency, payment_method, transaction_id |
| PAYMENT_FAILED |  Attempted payment, not received funds | amount, currency, payment_method, transaction_id |
| SHIPPED | Not applicable; may be blank | shipment_id |
| DELIVERED | Not applicable; may be blank | shipment_id |
| REFUND |  Completed refund, positive amount | amount, currency, payment_method, transaction_id |
| CANCELLED | Not applicable; may be blank | None |

## 3. Validation rules

Please note that **noncanonical formatting, missing required fields, invalid values, duplicate reports, and business conflicts are reportable, even when repairable.**

Valid failed payments, valid cancellations, and blanks in inapplicable fields are not errors.

### 3.1 Formatting hints

Use the column descriptions and examples in Part 2 as a reference. Some things to look for:

- Inconsistent spelling, capitalization, spacing, or separators in IDs and categories.
- Different ways of writing dates, times, amounts, and currencies.
- Unexpected characters or inconsistent representations in names and telephone numbers.
- Missing values that appear in different forms.

Explore the data to identify these patterns and decide how to handle them. These hints are not an exhaustive list.

### 3.2 Orders and transactions

1. **Scope:** one product, currency and parcel per order. Creation and event times must fall within 2025 in +08:00. Platform, currency and nonempty customer details must agree within an order.
2. **Price:** `creation amount = quantity × unit_price − discount_amount + shipping_fee`. Quantity is a positive integer, unit_price > 0, shipping_fee ≥ 0, and discount is between zero and the product subtotal. Order and transaction amounts are positive.
3. **Payments/refunds:** deduplicate before summing successful payments and refunds. Failed attempts and creation amounts are not receipts. Cumulative refunds cannot exceed cumulative successful payments at any event time.
4. **Sequence:** creation precedes payment; full payment precedes shipping; shipping precedes delivery, with matching parcel IDs. Cancellation is allowed before shipping; refunds may follow cancellation, but payment or shipping may not. An unfinished order is not automatically erroneous.

### 3.3 Which row should be reported?

- Report the row with a **local issue**, including repairable required-field omissions. UNRESOLVED issues are also reportable.
- **Duplicates:** for matching transaction IDs with identical normalized business content except event_id, retain the smallest canonical event ID lexicographically, breaking ties by raw ID. Report redundant rows; report the retained row only for independent issues.
- **Unambiguous violations:** report the excessive refund, pre-creation payment or post-cancellation shipment, not otherwise valid evidence rows. If required creation or shipping evidence is absent, report directly dependent events rather than inventing predecessors.

Do not flag an entire order for one bad event. Decide that evidence is missing only after reading all eight files.

## 4. Sample AI conversation: improving the analysis round by round

The following sample shows one student prompt and one AI reply per round, with a table explaining the findings. The rows are illustrative, not results from a completed analysis of your dataset. Unless stated otherwise, rows are independent examples; omitted fields and business context comply with the rules.

### Round 1: Discover and correct event ID formatting

**Student:**

> I have loaded the data using `project_01_template.py`. Please check the event IDs below, explain which ones have formatting problems, and update the analysis to normalize them while preserving the original IDs for submission.

**AI:**

> Two IDs have noncanonical formatting, as shown below. The revised check keeps the raw IDs for reporting and uses a separate normalized copy for comparisons. Correcting the format does not remove the original issue: report `EV-200102` and `ev200103`, not their normalized versions.

| Original event_id | Normalized value for analysis | Issue and reason |
| --- | --- | --- |
| EV200101 | EV200101 | No: already in canonical format. |
| EV-200102 | EV200102 | Yes: an extra hyphen appears in the ID. |
| ev200103 | EV200103 | Yes: the prefix is lowercase instead of uppercase. |

### Round 2: Handle different amount formats

**Student:**

> The ID check works on my sample. Now converting `amount` directly to numbers fails on some rows below. Please explain the differences and revise the parsing so it preserves raw values and does not treat every blank as an error.

**AI:**

> The revised parsing creates a separate numeric value and records noncanonical formatting as an issue. In these unambiguous examples, `CNY 115` means `115.00` CNY and `€50,00` means `50.00` EUR. A blank shipping amount is permitted. Ambiguous values should remain unresolved rather than being guessed or replaced with zero.

| Original event_id | event_type | Raw amount | currency | Parsed amount | Issue and reason |
| --- | --- | --- | --- | --- | --- |
| EV200201 | PAYMENT_SUCCESS | 115.00 | CNY | 115.00 | No: valid amount format. |
| EV200202 | PAYMENT_SUCCESS | CNY 115 | CNY | 115.00 | Yes: the amount includes a currency prefix and is not in canonical format. |
| EV200203 | REFUND | €50,00 | EUR | 50.00 | Yes: the amount includes a currency symbol and a decimal comma. |
| EV200204 | SHIPPED | blank | blank | Not applicable | No: a shipping event does not require an amount or currency. |

### Round 3: Correct a false positive for failed payments

**Student:**

> My current code flags every `PAYMENT_FAILED` row. Below is one order's event sequence, with a total of 250.00 EUR. Please check whether those flags are justified and correct the payment logic without removing unrelated issues.

**AI:**

> A valid failed attempt is not a data error and is not received money. Remove the rule that flags a row solely because its type is `PAYMENT_FAILED`, but retain required-field and other applicable checks. Here, only `EV200303` is reportable, because its transaction ID is missing. Successful payments total 250.00 EUR; creation amounts and failed attempts do not contribute to that total.

| Original event_id | event_type | amount (EUR) | transaction_id | Issue and reason |
| --- | --- | --- | --- | --- |
| EV200301 | ORDER_CREATED | 250.00 | blank | No: a valid creation event; its amount is not received funds. |
| EV200302 | PAYMENT_FAILED | 250.00 | TX3001 | No: a valid failed payment attempt. |
| EV200303 | PAYMENT_FAILED | 250.00 | blank | Yes: the required transaction ID is missing; the failed status itself is not an error. |
| EV200304 | PAYMENT_SUCCESS | 250.00 | TX3002 | No: a separate successful payment. |

### Round 4: Detect duplicate transactions across files

**Student:**

> The failed-payment check now works. These payment events belong to one order but appear in different files. Please identify duplicate reports, explain which row should be retained, and revise the check so it also works across batches.

**AI:**

> `EV200402` and `EV200404` report the same transaction with identical normalized business content except for the event ID. Retain `EV200402`, the smallest canonical ID lexicographically, and report `EV200404`. Use the raw ID to break ties. Keep comparison state across batches and finalize decisions after reading all files. After deduplication, successful payments total 60.00 + 55.00 = 115.00 CNY. Matching transaction IDs with conflicting business content need separate investigation.

All rows below are `PAYMENT_SUCCESS` events in CNY. Times are on 2025-03-03 in UTC+08:00; omitted business fields match between the duplicate reports.

| Original event_id | File | Time | amount | transaction_id | Issue and reason |
| --- | --- | --- | --- | --- | --- |
| EV200402 | events_part1.csv | 09:02 | 60.00 | TX4001 | No: retain this report of TX4001 because its canonical event ID is smaller. |
| EV200403 | events_part2.csv | 09:05 | 55.00 | TX4002 | No: a separate successful payment. |
| EV200404 | events_part8.csv | 09:02 | 60.00 | TX4001 | Yes: a redundant report of the same transaction as EV200402; exclude it from payment totals. |

Continue the same process for the remaining requirements in Sections 2 and 3. These four rounds illustrate the conversation format, not an exhaustive solution; run each revision and inspect both flagged and unflagged examples.

### Round 5: ... ...

... ...
... ...
... ...

## 5. Expected output of your program

Problematic events (illustrative IDs only; not an answer list):

```text
EV200101
EV200102
EV200104
EV200205
EV200304
EV200307
EV200403
```

## 6. Submission

You should submit your `project_01_template.py` file to our evaluation system, where the accuracy will be displayed after submission, and submit the following files to UMMoodle.

| Item | Required? | Requirements |
| --- | --- | --- |
| Your `project_01_template.py` code | **Required** | You may submit the code used to process the dataset. |
| AI Declaration | Optional | Briefly describe how you used AI in this assignment, such as interpreting the rules, writing code, debugging, or checking results. |

The evaluation system will be opended in the next few days.

## 7. Deadline

25 Oct 2026 23:59:59