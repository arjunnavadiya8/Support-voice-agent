# Suvit Knowledge Base — GST Automation Module

**Module Overview:**
Use GST Reconciliation in Suvit along with Tally data reports. This module includes GST Reconciliation (GSTR-1 & GSTR-2B), GST Dashboard, Company Summary, IMS (Invoice Matching System), and GST Notice & Order tracking.

---

## 1. GST Reconciliation

GSTR-1 Reconciliation & Voucher Entry — Check differences in GSTR-1 and Sales Register and fix mismatches by adding missing vouchers directly from Suvit.

### Step 1: Check Monthly Differences
- Go to the **Month View** under GSTR1 → Transaction.
- You'll see differences in **Total Invoice**, **Taxable Amount**, and **Tax Amount** for each month.
- This helps quickly identify which months have mismatched or missing data.
- Click on the desired **Month** to check the Transactions.

### Step 2: Filter by Reco Status
- Use the **Reco Status** filter in **Voucher View**.
- Filter vouchers by:
  - **Matched** — Data matches perfectly
  - **Manual-Matched** — Entries matched manually
  - **Partially-Matched** — Partial data mismatch
  - **Not In Tally** — Found in portal but missing in books
  - **Not In Portal** — Present in books but not on the portal
- This helps focus only on problematic entries.

### Step 3: Add Voucher (For "Not In Tally" entries)
- For vouchers marked **Not In Tally**, click the ➕ **Add Voucher** button in the **Action** column.
- This lets you manually create missing entries right inside Suvit.

### Step 4: Fill Voucher Details
- A popup form will appear with:
  - **Voucher No., Date, Party Name, GSTIN**
  - **Item Details:** Item Name, Ledger, HSN, Quantity, Rate
  - **Ledger Details:** Add Sales Account & Tax Ledgers like SGST, CGST
- Double-check all amounts before saving.
- Click the **Save & Close** button at the bottom of the form.
- The entry is now matched and synced with your records.

### Step 5: Sync with Suvit
- After saving, click the **Saved & Synced** button to ensure the new voucher reflects in GSTR1.
- This will update the match status from "Not in Tally" to "Matched".
- Continue doing this for all missing records.

> **Note:** The same flow applies for GSTR2B reconciliation as well.

---

## 2. GST Reconciliation Summary: A Step-by-Step Overview

Use Suvit's GST Reconciliation to track returns, compare Eligible vs. Claimed ITC, and match GSTR-1 with your sales register using Tally data reports.

### Important Notes Before Starting:

#### A. Sync Voucher
- Click on **Sync Voucher** to fetch the latest (Sales/Purchase) data from Tally.
- Suvit will display the data available in Tally up to the time you clicked Sync Voucher.

#### B. GST Data
- Suvit displays the data available on the **GST Portal**.
- Data will be up to date as of the time you clicked **Sync**.

### Step 1: Select Company & Period
- Choose your desired company from the top dropdown.
- Select the financial year period (e.g., Apr 2024 – Mar 2025) to fetch data for the correct duration.
- Click **Login to GST Portal** to connect Suvit with the GST portal.

### Step 2: Login to GST Portal
- Fill in the **GST Number** and **Username** used for the portal login.
- Click **Get OTP** to receive an authentication code.
- This login is required to fetch return filing data securely.

### Step 3: Enter OTP
- Enter the OTP received on the registered mobile/email.
- Click **Get Data** to allow Suvit to fetch GST filings and sales details.

### Step 4: View GSTR-1 Summary
- The **Summary Tab** gives you a bird's eye view of matching status:

| Category | Description |
|----------|-------------|
| Matched | Entries perfectly match between portal & books |
| Manual Matched | Entries matched manually |
| Partially Matched | Partial data mismatch |
| Not in Tally/SR | Found in portal but missing in your books |
| Not in Portal/GSTIN | Present in your books but not on the portal |

### Step 5: Monthly Transaction Reconciliation
- Navigate to the **Transaction → Month View** tab.
- It compares monthly totals for:
  - GSTR-1: Invoice Count, Taxable Amount, Tax Amount
  - Sales Register: Invoice Count, Taxable Amount, Tax Amount
  - **Difference** is highlighted clearly in each row.
- Helps detect month-wise mismatch in data.

### Step 6: Voucher-Level View
- Go to the **Transaction → Voucher View** tab.
- Each voucher entry is listed with:
  - Party name (as per GST Portal & Sales Register)
  - GSTIN match status
  - Invoice dates comparison
- Use this view for verifying invoice-level entries line by line.

### Step 7: Vendor-Level View
- Use **Vendor View** to check reconciliation by vendor.
- Shows GSTR-1 vs. Sales Register for each vendor:
  - Invoice Count
  - Taxable & Tax Amount
  - Status: Matched / Partially Matched / Not Found
- Helps accountants quickly pinpoint vendor-specific mismatches.

---

## 3. GST Dashboard and Company Summary

This dashboard is built for busy accountants and firms to quickly view compliance across all their clients, GSTINs, and filing timelines — in a single glance.

### Dashboard Header (Top Navigation)
- **Dashboard label** showing your current view
- **Filing Period selector** (e.g., Apr 2025 – Mar 2026)
- **Company stats:**
  - Total Companies: Number of registered companies
  - Unsynced Companies: Data needs syncing

### 1. GSTIN Summary (Top Widget Bar)
Colored blocks with quick stats:
- **Total GSTIN** — All GSTINs tracked
- **Valid GSTIN** — GSTINs verified as active
- **Invalid GSTIN** — Marked as incorrect
- **Active / Suspended / Cancelled** — Status-wise GSTIN count

### 2. Filing Status: Month and Year
A clear table showing:
- GSTR-1 & GSTR-3B returns
- Number of returns: Total to be filed, Pending (still due), Completed (already filed)
- Due dates for upcoming filings

### 3. Filing Summary (Total Filing Chart)
A donut chart visualizing:
- Total Filings
- Breakdown: ✅ OnTime Filing vs ⚠️ Late Filing

### 4. GSTR-1 & GSTR-3B Detailed Charts
Return-wise filing for each return type:
- Total GSTINs considered
- Status: OnTime, Late, or Not Filed
- Visual representation to spot delay trends instantly

### 5. Notices & Alerts
- Placeholder widgets for: Notices Received, Filing Alerts & System Notices (actively being improved)

---

## 4. Company Summary

The Company Summary view helps CAs and tax professionals keep each client company's filings, mismatches, and liabilities in check — month by month.

### 1. Top Section — Company Name & Period Selection
- Company Name and GSTIN
- Period Dropdown (e.g., Apr 2024 – Mar 2025) to pick the financial year

### 2. Return Filing Tracker
Tracks both GSTR1 and GSTR3B for each month:
- ✔️ Green Check = On-time Filing
- 🕓 Orange Clock = Late Filing
- 🔄 Blue Circular Arrows = Processing
- — Dash = No Filing or Not Applicable

### 3. GSTR1 Table
Monthly summary of outward supplies:
- **Month:** Filing month
- **Total Invoice:** Number of invoices reported
- **Taxable Amount:** Value before GST
- **Total Tax Amount:** GST value (CGST + SGST + IGST)

### 4. GSTR3B Table
Monthly summary of summary return:
- **Total Tax Liability:** GST to be paid
- **ITC:** Input Tax Credit claimed
- **Total Tax Paid:** Actual payment done

### 5. GSTR1 vs GSTR3B Chart
Visual comparison of outward liability:
- Line 1: GSTR1 Tax Liability (sales data)
- Line 2: GSTR3B Tax Liability (actual filed)
- Useful for spotting mismatch in reporting

### 6. GSTR2B vs GSTR3B Chart
Compare ITC vs filed liability:
- Line 1: GSTR2B Tax Liability (vendor data)
- Line 2: GSTR3B Tax Liability (filed amount)
- Helpful for input credit tracking and under/over claiming alerts

---

## 5. IMS — Invoice Matching System

IMS (Invoice Matching System) in Suvit helps you compare GST Portal data with your Purchase Register (PR) to spot and fix mismatches.

### Document Summary Tab (First Screen in IMS)
This is the first view when you open the IMS module. It shows the summary of documents sorted by Document Type (like B2B or CN Credit Note).

**What it shows:**
- **Document Type:** Type of documents (B2B, CN, etc.)
- **Total Invoices:** Total number of GST invoices under each type
- **Tax Value:** Combined taxable value of all invoices

### 1. Reco Summary — Match Overview
Starting point to check what's matched and what's not:
- **Matched** — Data perfectly matches between GST and PR
- **Manual Matched** — You've manually linked the entries
- **Partially Matched** — Some values differ
- **Not In Tally/PR** — Missing in your Purchase Register or Tally data

### Voucher View — Check Row-Wise Mismatches
- Shows invoice-level details under the **Action** tab.
- Click the **eye icon (👁️)** to view full mismatch details.

### Link Mismatched Invoices
- Click **Link** under the PR column for the mismatched row.
- This opens a panel showing the GST invoice and lets you match it to an existing PR invoice.

### Sync Tally If No Invoice Found
- Go to the **Sync Invoice** tab.
- Click **Sync** to pull the latest data from Tally.
- Then try linking again.

### 2. Take Action on Entries
Use the **Take Action** dropdown:
- **Accept** — Confirm the invoice is fine
- **Reject** — Not acceptable due to mismatch
- **Pending** — Yet to take action

### Understand Upload Status (TBS)
- **TBS = To Be Submitted**
- This tag appears after you've matched or accepted the invoice.
- Signals that the invoice is ready for submission.

### 3. Add Missing Voucher to PR
- For GST Portal invoices not in your PR, click the **plus (➕) icon** → select **Add Voucher**.
- Add full voucher info: Supplier Invoice No, Date, Party Name, GST No, Ledger Details, Tax Breakdown.
- Click **Save & Close**.

### 4. Track Who Took Action
- Click the **clock icon** under the Action column.
- Shows who accepted/rejected the invoice and when.

### 5. Vendor View
Gives a vendor-wise breakdown of how GST Portal data matches with Purchase Register:
- **Vendor:** Name of the supplier and GSTIN
- **IMS Section:** Invoices and tax value from GST portal
- **Purchase Register Section:** Entries found in PR data
- **Status Columns:** Matched, Partially Matched, Not in PR, Not in Portal

**Use Case Example:**
If vendor "DIPAK KIRYANA STORES" has 4 invoices "Not in PR," that means invoices exist in GST portal but not in your purchase register — so you can add missing vouchers or link existing ones.

---

## 6. How to Track GST Notices & Orders in Suvit

Suvit's Notice & Order dashboard offers a centralized view to track all GST-related notices received across your companies.

### Overview
- Helps identify the status of each notice
- Monitors deadlines
- Categorizes notices into general or additional types
- Helps stay compliant with GST regulations and respond on time

### Step-by-Step Guide:

#### 1. Time Period Selection
- Use the **Time Period** dropdown to filter notices by financial year (e.g., Apr 2025 – Mar 2026).
- Helps isolate notices for a specific period.

#### 2. Toggle View: Calendar vs Company
- **Calendar View:** Displays notice activities date-wise.
- **Company View:** Displays company-wise notice status.

#### 3. Sync Status of Companies
- **Total Companies** using Suvit
- **Unsynced Companies** whose notice data is not yet imported
- Helps identify companies needing attention.

#### 4. Notices Received Breakdown
- **All Notices:** Total GST notices imported in Suvit.
- **Open & Order Pending:** Notices acknowledged but awaiting reply/action.
- **Open & Order Issued:** Response submitted and order issued.
- **Closed:** Action completed, and the case is resolved.

#### 5. Notice Types
- **General Notices:** Standard GST notices from the department.
- **Additional Notices:** Extra or follow-up notices requiring attention.

#### Calendar View Color Codes:
- 🔵 **Blue Dot** = Issued Today
- 🔴 **Red Dot** = Due Today
- 🟢 **Green Dot** = Order Closed

### Why Use This Feature?
- Stay compliant with GST timelines
- Avoid penalties for delayed responses
- Keep all notice-related actions organized and accessible
- Assign responsibility and track completion status internally

---

## Key Quick Reference for Voice Agent

**Q: What is GST Reconciliation in Suvit?**
A: It's a feature that compares your Tally/Sales Register data with the GST Portal data to identify mismatches in invoices, amounts, and tax values across GSTR-1 and GSTR-2B.

**Q: How do I fix a "Not In Tally" invoice in GST Reconciliation?**
A: Go to Voucher View → filter by "Not In Tally" → click the "+" Add Voucher button → fill voucher details → Save & Close → click Saved & Synced to update the match status.

**Q: What does the GST Dashboard show?**
A: It shows a complete overview of all GSTINs (valid, invalid, active, cancelled), GSTR-1 and GSTR-3B filing status, on-time vs late filings, and notices received across all companies.

**Q: What is IMS in Suvit?**
A: IMS stands for Invoice Matching System. It compares GST Portal invoices with your Purchase Register to find and fix mismatches. You can accept, reject, link, or add missing vouchers.

**Q: How do I check GST notices in Suvit?**
A: Go to the Notice & Order dashboard. Select the time period, choose Calendar or Company view, and check the notices received breakdown (Open, Pending, Closed, etc.).

**Q: What is the difference between GSTR-1 and GSTR-2B reconciliation?**
A: GSTR-1 reconciliation compares outward supplies (sales) between your books and the GST portal. GSTR-2B reconciliation compares inward supplies (purchases/ITC) between GST portal data and your Purchase Register.

**Q: What do the calendar dot colors mean in the Notice dashboard?**
A: Blue dot = Issued Today; Red dot = Due Today; Green dot = Order Closed.

**Q: What is "Sync Voucher" in GST Reconciliation?**
A: It fetches the latest Sales/Purchase data from Tally into Suvit so you can compare it with the GST Portal data for reconciliation.
