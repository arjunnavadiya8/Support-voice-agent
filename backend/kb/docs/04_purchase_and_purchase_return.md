# Suvit Knowledge Base — Purchase and Purchase Return Module

**Module Overview:**
Efficiently manage your Purchase and Purchase Return transactions. Track, record, and organize all your purchase activities in one centralized system.

---

## 1. Mandatory Things to Check Before Using Purchase/Purchase Return Module

One can record export of goods, purchase under different GST rates, nil-rated and exempt purchase, deemed export, etc.

### Excel Sheet Checklist (Before Uploading):

1. **Use the First Sheet Only** — Keep your data in the first worksheet of your Excel file.
2. **Headers Go on Top** — The first row should have titles like: Date, Invoice No., GST, Amount, etc.
3. **No Dots or Dollar Signs in Headings** — Don't use symbols like . or $ in column titles. Don't put extra rows above data.
4. **Invoice Number Must Be Filled** — No blank invoice numbers allowed.
5. **Group Same Invoice Numbers Together** — Sort data A–Z by Invoice Number to keep them lined up.
6. **Avoid Words Like NA / Not Applicable** — If GST isn't available, just leave the cell empty.
7. **Use DD/MM/YYYY for Dates** — Example: 27/05/2022.
8. **Delete Extra Totals or Notes** — Remove rows like "Grand Total" — Tally doesn't need them.
9. **Keep it Under 10,000 Transactions** — Don't exceed 10,000 rows in one sheet.
10. **Add a Ledger Column Based on GST** — Create a column that has Purchase Ledger Name as per the GST rate.
11. **GST Ledgers Must Exist in Tally** — Make sure SGST, CGST, IGST are created under Duties & Taxes in Tally.
12. **Use Correct Excel Formats** — Text fields → TEXT or General format; Numbers → Number format.
13. **Add a Column Named "Particular"** — Fill this with the correct Purchase Ledger Name as per GST rate. Example: If GST is 18%, use the ledger with 18% Purchase defined.
14. **Save as Excel Workbook (.xlsx)** — Not CSV or PDF.

---

## 2. Uploading Purchase/Purchase Return Data Through an Excel Sheet

### Quick Access Links:
- Purchase Upload: https://in.suvit.io/da/purchase/excel
- Purchase Return Upload: https://in.suvit.io/da/purchase-Return/excel

### Step 1: Navigate to Purchase/Purchase Return
- Click on **Data Entry Automation** in menu → **Bulk Upload** → **Purchase** or **Purchase Return**.

### Step 2: Upload File
- Click on **"Upload File"** to upload the Excel sheet.
- Select the file from your system using **Click to Upload**.
- Click on **"Upload"** to upload your document.

### Step 3: Access the Mapping Screen
- After uploading, click on the file to proceed to the mapping screen.

---

## 3. Auto-Mapping Excel Sheet Data with Suvit Configuration (Purchase)

Auto-Mapping is Suvit's smart assistant that automatically connects your Excel sheet to Tally. It reads your column names and suggests the right fields — so you don't need to do everything manually. Suvit remembers your choices for next time.

### Step 1: Field Mapping
- Choose your Data Type: With items or without items? (Example: Select **Without Item**).
- What you'll see:
  - **Mapped Fields:** Suvit auto-matched these with Tally.
  - **Unmapped Fields:** You need to select matching Tally fields for these.
  - **Your Sheet Header:** Your Excel column titles.
  - **Tally Fields:** Tally's fields — link them to your columns.
  - **Your Sheet Data:** Shows 3 sample rows for double-checking.
- Click **Next** to move to GST Mapping step.

#### Use of Configuration:
- You can map special fields like: Voucher Date & Number, Party (Buyer or Consignee), Invoice Date, Carrier Name, Lading Number, Export Details, Tracking Number, Vehicle Number, and Cost Centres.

### Step 2: GST Mapping (Tax Ledger)
- If done earlier, Suvit will apply saved mappings automatically.

#### Option 1: Choose from Tally (set to "No")
- Choose the Tally GST Ledger manually from the dropdown.

#### Option 2: Use Excel Column (set to "Yes")
- Link the column that contains GST Ledger names from Excel.

#### GST Auto Calculation (set to "Yes"):
- Suvit calculates SGST, CGST, and IGST using the settings already in Tally.

#### GST Manual Calculation From Excel (set to "No"):
- Suvit picks GST amounts from the Excel sheet.
- **Note:** Mapping SGST, CGST, and IGST is mandatory. You can also map Round-Off Ledger if needed.

### Step 3: Ledger Mapping
- Here you can link fields like: Round-Off, Discount, Freight / Delivery Charges.
- Choose the right Excel column and the matching Tally ledger.
- Finally, click **Save & Proceed** to move ahead.

---

## 4. How to Process or Push Purchase/Purchase Return Data to Tally

After mapping the purchase data, the next screen displays it in an Excel-like format for review.

### Save & Send Data to Tally:
- **A** → Select your Purchase Transaction (All or Individually).
- **B** → Click on **Save**.
- **C** → Click on **Send to Tally** button.
- **D** → Click on **OK** for confirmation.

> **Instruction:** Ensure all transactions are properly filled, and caution triangles are cleared before proceeding.
> **Warning:** Only selected and saved purchase data will be pushed to Tally. Remaining entries can be sent later.

### Progress Tracking:
- **Gray Stage (1st Stage):** Process has been initiated.
- **Orange Stage (2nd Stage):** Process has started.
- **Green Stage (3rd Stage):** Purchase data has been successfully sent to Tally.

### Processing Screen Overview:
| Field | Description |
|-------|-------------|
| Bulk Selection | Select transactions one by one or in bulk |
| Update Bulk Records | Change or select specific data |
| Reference No | As per the Excel sheet |
| Voucher Type | Default: Purchase (can be changed) |
| Supplier Name | Name of the supplier |
| GST No | As per supplier details |
| Place of Supply | From mapping or from Tally |
| Particulars | Shows Purchase Account |
| Warning Triangle | Indicates missing details |
| Orange data | Unselected fields |
| Blue/Orange | Blue = selected; Orange = not yet selected |

### Error Resolution for Ledger Mismatch:

#### Step 1: Check Existing Ledgers
- Select the records in bulk.
- Use Bulk Selection to update and correct entries.

#### Step 2: Create Missing Ledgers
- If ledgers are missing in Tally, click the **"+" button** next to the supplier name to create them instantly.

### General Filters:
- Hide Tally-sent data
- Blank entries
- Saved records
- Failed records
- Sort by Date

### Bulk Operations:

#### Step 1: Update Bulk Records
- Use Bulk Update to modify: Voucher Type, Supplier A/c Name, and Particulars (Purchase Account Ledger).

#### Step 2: Use Bulk Selection Tools
- Helps with searching, filtering voucher types, and selecting purchase account ledgers.
- Select multiple records for quick filtering, updating, or pushing to Tally.

#### Step 3: Cross-Check and Verify
- Search for Bill numbers or specific supplier names.
- Verify GST numbers and Place of Supply.

---

## 5. Create a Ledger and Stock Item from Purchase Transaction Screen

### Method A: Create One-by-One (Single)

#### Create a Party Name (Ledger):
1. Click the **Create Ledger** button.
2. A new pop-up will open → Add party name, GST number, state, etc.
3. Click **Add** to save the party account.

> **Tip:** Once added, send one transaction to Tally — Suvit will create the ledger and then push the entry.

#### Create a Stock Item (Only for Item Invoices):
1. Click on the **drawer icon** to open stock settings.
2. Select **Create Item**.
3. Add name, unit, GST %, etc. → Click **Add** to save the item.

> **Tip:** Send one invoice to Tally — the item gets created first, then the data is pushed.

### Method B: Bulk Creation (Multiple Entries)

#### Bulk Create Party Names:
- Click the **orange Plus Icon** to add many party names together.
- Once you send data to Tally, the ledger is auto-created there.

#### Bulk Create Stock Items:
- Click the **orange Plus Icon** to add many stock items at once.
- New stock items will be created in Tally as soon as you push the data.

---

## 6. Create Invoice for Purchase and Purchase-Return

### Step 1: Dashboard
- Click on **Data Entry Automation** → **Transaction** → **Purchase/Purchase Return**.

### Step 2: Create Bill
- Click the **Create Bill** button.
- Choose between Purchase or Purchase Return.

### Step 3: Invoice Details

#### Item Invoice:
- Toggle between accounting invoice or item invoice based on your document.

**A. Voucher Details:**
- Type: Choose transaction type (Purchase/Return)
- Invoice No.: Enter invoice number
- Date: Select purchase date
- Party & GST: Enter supplier name and GST
- Ledger: Choose purchase account

**B. Item Details:**
- Serial No., Item Name, Qty, Rate, Amount, Action: Fields to list and calculate item details.

**C. Ledger Details:**
- Serial No., Ledger Name, Amount, Action: Fields for ledger entries.

**Customer Details:**
- Includes customer information: name, phone, email, and address.
- Displays outstanding receivables, credit terms, and recent related invoices.

**Configuration Options:**
- Use the Configuration Window to select fields displayed during voucher entry (e.g., Voucher Date, Supplier Invoice No., Item Narration). Save changes once done.

**D. Tax, Narration, and Totals:**
- Add taxes, notes, and final amounts.

**E. Save the Bill:**
- Click **Save & Close** to save and exit.
- Click **Save & Sync** to save and sync directly with Tally.

> **Note:** If the transaction fails, check the tally.imp file in the Tally installation folder. Fields marked with "*" are mandatory.

---

## 7. Fetch GSTR 2B Data in Purchase from GST Portal

With the **"Get GST Data"** button, users can seamlessly retrieve their GST data directly from the master GST API.

### Step 1: Access the "Get GST Data" Button
- Click on **Data Entry Automation** → **Bulk Upload** → **Purchase** → **"Get GST Data"**.

### Step 2: Selecting the Time Range
- Select a time range using date pickers to specify the desired period for GST data retrieval.
- This allows narrowing down the data to a specific month.

### Step 3: Pop-Up Selection
- A pop-up window will appear prompting the user to enter specific information.
- Once you enter the required information, you will be asked to **enter the OTP**.

### Step 4: Viewing Fetched Data
- Once successfully fetched, the platform will present retrieved files as a listing page.
- Navigate and view the fetched data within this interface.

### Step 5: Saving and Sending
After data retrieval, you can:
- **Save:** Save the mapped data for future reference or reporting.
- **Send:** Send the data to designated recipients (tax authorities, accountants, etc.).

---

## Key Quick Reference for Voice Agent

**Q: How do I upload a purchase Excel file in Suvit?**
A: Go to Data Entry Automation → Bulk Upload → Purchase → Click Upload File → Select file → Click Upload.

**Q: How do I fetch GSTR 2B data?**
A: Go to Data Entry Automation → Bulk Upload → Purchase → Click "Get GST Data" → Select the time range → Enter OTP → View and save the fetched data.

**Q: How do I send purchase data to Tally?**
A: After mapping, select transactions, click Save, then click Send to Tally. Confirm with OK. Both Tally and Suvit Desktop App must be open.

**Q: What if a supplier ledger is missing in Tally?**
A: Click the "+" button next to the supplier name to create the ledger directly from the purchase screen. When you push data, the ledger is auto-created in Tally too.

**Q: What is the maximum rows allowed in a purchase Excel sheet?**
A: Up to 10,000 rows per sheet.

**Q: Can I create a purchase invoice manually without uploading an Excel sheet?**
A: Yes. Go to Data Entry Automation → Transaction → Purchase → Create Bill, then fill in the invoice details and save.
