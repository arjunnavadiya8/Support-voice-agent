# Suvit Knowledge Base — Banking Module

**Module Overview:**
Suvit's Banking Module automates bank imports, categorization, and Tally sync — making banking tasks faster, easier, and reducing manual work.

---

## 1. Import the Bank Statement

This guide explains how to import a bank statement from Suvit to Tally.

### Step 1: Sign In
- Visit https://in.suvit.io
- Enter your Email and Password.
- Click **Sign In**.

### Step 2: Navigate to Bulk Upload → Banking
- From the sidebar (Data Entry Automation), click on **Bulk Upload**.
- Under the Bulk Upload section, choose **Banking** from the dropdown list.

### Step 3: Choose the Company
- Click on the top-right corner dropdown to view available companies.
- Use the search bar to type part of your company name.
- Select the box beside the desired company.

### Step 4: Import the Statement
- Click the **Import** button located in the top-right section of the Banking screen.

### Step 5: Select Bank & Attach File
- From the pop-up window, choose the relevant **Bank** (e.g., SBI Bank, UCO Bank).

### Step 6: Upload the File
- Drag and drop the file or click to upload.
- Ensure the correct bank and file are selected.
- Click the **Upload** button at the bottom-right.
- ⚠️ If a document with the same name already exists, a warning about duplication will appear.

### Step 7: Processing Status
- After clicking Upload, the file will appear in the **Processing** state.
- Wait until the status changes to **Complete** or **Failed**.
- 🕒 If the processing takes too long, try refreshing the page using Ctrl + Shift + R.

### Document Processing Times:
| File Type | Processing Time |
|-----------|----------------|
| Excel Sheet | Up to 30 minutes |
| Original PDF | Up to 1 hour |
| Scanned PDF | Up to 12 hours |

### Unsupported File Types (Do NOT Upload):
- ❌ Passbooks
- ❌ Share Market Statements
- ❌ Loan Statements
- ❌ Password-Protected PDFs
- ❌ RTP/TXT formats
- ❌ Dot Matrix font formats

---

## 2. "Complete" Status After Processing the Statement

When the status **"Complete"** appears, the statement has been successfully processed.

### What To Do After Complete Status:
- Click on the statement to open the extracted data.
- Begin by **selecting and saving ledgers** for your transactions.
- Once ledgers have been saved, send the data to Tally.
- You can select ledgers both **individually** and **in bulk**.
- Use various filters to make ledger selection easier and faster.

### Steps:

#### Step 1: Select and Save Ledgers
- How to select Party Name: See Ledger Selection section below.
- How to use General Filters: See Filters section below.
- Once done selecting ledgers, save them.

#### Step 2: Send Transactions to Tally
- After saving, send the transactions to Tally.
- ⚠️ Make sure Tally and Suvit Desktop Application are both open.

#### Step 3: Verify in Tally
- Once data is sent successfully, open Tally and check the entries to ensure everything has been synchronized correctly.

---

## 3. How to Select Ledgers

Once the bank statement is successfully uploaded in Suvit, you can select ledgers individually or in bulk.

### Method 1: Choose Specific Ledgers for Each Transaction (One-by-One)
- Click on the **"Select Ledger"** option at the end of every transaction row.
- Search for and select the appropriate party name/ledger.

### Method 2: Select Ledgers in Bulk for Same Transactions
- Filter out the transactions you wish to post in a single ledger.
- Example: Search keyword **"charges"** in the narration field (can also use: Cash, EMI, UPI, NEFT, SMS charges, etc.)
- Select all filtered transactions.
- Search for the Party Name in the LEDGER box and select it.

### Contra Entry:

#### Change Individual Transaction Type:
- Click on **"Payment"** or **"Receipt"** beside the transaction.
- A drop-down will appear with: **"Contra Withdraw"** and **"Contra Deposit"**.
- Select as per your requirement and save.

#### Change Transaction Type in Bulk:
- Use the **"Transaction Type"** option under bulk operations.
- If ledgers are not available in Tally, you can Create Ledger directly from Suvit.

### Step: Send Transactions to Tally
- ⚠️ Make sure Tally and Suvit Desktop Application are open.
- After saving, send the transactions to Tally.

### Step: Verify in Tally
- Open Tally and check that all entries are synchronized correctly.

---

## 4. Use of General Filters

Suvit provides multiple filters to make ledger selection faster and more organized.

### Available Filters:

#### 1. Date Filter
- Filter the data by a date range you wish to work on.
- If you don't need particular date range data sent to Tally, filter that date range and delete it from Suvit.

#### 2. Narration/Description Filter
- For common transactions that need to be posted in the same ledger, search the common keyword in narration (e.g., "SMS Alert Charges", "G-pay").
- Once filtered, select all → from bulk operations, set the desired ledger → save.
- Example: Search "neft" → select all → pick ledger from LEDGER box.

#### 3. Payment/Receipt Filter
- Use this filter to work on specific transaction types: **Receipts** or **Payments**.

#### 4. Amount Filter
- Filter transactions within a specific amount range.

#### 5. Hide Tally Pushed
- Selecting this filter hides transactions already sent to Tally, helping you focus on pending ones.

#### 6. Blank Records
- Displays transactions where ledgers are yet to be selected and saved.

#### 7. Saved Records
- Lists transactions with ledgers assigned but not yet sent to Tally.

#### 8. Unsaved Records
- Shows transactions where ledgers were selected but not saved.

### Configuration Settings (via Settings → Configuration):

#### Configure Bank Allocation
- Enable Bank Allocation feature to manage bank-related details in transactions.
- Ensures bank accounts are accurately mapped for ledger entries.

#### Set Cheque/Instrument Number
- Enable the Cheque/Instrument Number field to record details of cheques or instruments used for payments or receipts.
- Input cheque numbers, transaction IDs, or instrument details for better tracking.

#### Supplier/Reference Number
- Activate Supplier/Reference Number option to record the supplier invoice number or reference ID for purchases.
- Ensures proper identification of invoices during reconciliation or reporting.

#### Enable Cost Centre Tracking
- Turn on the Cost Centre feature to allocate expenses and revenues to specific departments, projects, or units.
- Helps in tracking profitability and controlling budgets effectively.

#### Set Voucher Numbering
- Configure the Voucher Number field to manage the sequence of transaction entries in Tally.
- Choose between manual or automatic numbering.

#### Save Changes
- After enabling the required fields, click **"Save"** to apply the configuration settings.

> **Note:** Suvit also offers a unique feature for **Suggested Ledgers** which auto-suggests appropriate ledgers based on past patterns.

---

## 5. "Failed" Status After Processing the Statement

When the status shows **"Failed"**, the statement could not be processed due to one or more issues.

### What To Do If Failed:
- Check the **reason for failure** shown in the status.
- Make corrections in the document.
- Re-upload the corrected file.

### Common Reasons for Failure:
1. Unsupported format
2. Closing Balance mismatch
3. Missing column headers
4. Handwritten or punching marks on the statement
5. Password-protected file

### Tips to Avoid Document Failure:

#### 1. Ensure Proper Alignment:
- Data should be well-aligned and not merged.
- The date line should not merge with the narration, and narration should not overflow into the amount column.

#### 2. Complete Transaction Data:
- Ensure no transaction is missing or incomplete.

#### 3. Date Continuity:
- Transactions should be in date-wise chronological order.

#### 4. Column Headers:
- Statement must include headers: **Date**, **Narration**, **Debit Amount**, and **Credit Amount**.
- If splitting the bank statement, ensure headers are included on each part.

#### 5. Scanned PDFs:
- Ensure the scanned PDF is:
  - Aligned and maintains continuity across all pages.
  - Not too blurred or dark.
  - Free from punching marks, pen/ink marks, or handwritten notes on data.
  - Clear, without overlapping narration in the amount fields.
  - Free from cropped or incomplete data.

#### 6. Excel Sheets:
- Ensure data is in the **first sheet** of the workbook.
- Include columns for: **Date**, **Narration**, **Debit Amount**, and **Credit Amount**.

### Helpful Links:
- To remove password from a protected file, follow the Suvit guide on removing passwords.

---

## Key Quick Reference for Voice Agent

**Q: How do I upload a bank statement in Suvit?**
A: Go to Data Entry Automation → Bulk Upload → Banking → Click Import → Select your Bank → Upload the file.

**Q: How long does processing take?**
A: Excel sheet: up to 30 minutes. Original PDF: up to 1 hour. Scanned PDF: up to 12 hours.

**Q: What does "Complete" status mean?**
A: It means the statement was successfully processed. You can now select ledgers and send data to Tally.

**Q: What does "Failed" status mean?**
A: The file could not be processed. Check the reason (e.g., unsupported format, missing headers, password protection), fix the file, and re-upload.

**Q: How do I select ledgers in bulk?**
A: Use the narration filter to search a keyword (like "charges" or "upi"), select all filtered transactions, then assign a ledger from the LEDGER box.

**Q: What files are NOT supported for bank upload?**
A: Passbooks, Share Market Statements, Loan Statements, Password-Protected PDFs, RTP/TXT formats, and Dot Matrix fonts are not supported.

**Q: What should I do before sending data to Tally?**
A: Make sure both Tally software and the Suvit Desktop Application are open.
