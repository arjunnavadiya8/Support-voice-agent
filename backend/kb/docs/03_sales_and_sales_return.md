# Suvit Knowledge Base — Sales and Sales Return Module

**Module Overview:**
Easily manage your Sales and Sales Return transactions in one place. Track, record, and streamline your sales process for better accuracy and control.

---

## 1. Mandatory Things to Check Before Using the Sales/Sales Return Module

One can record export of goods, sales under different GST rates, exempt sales, deemed export, etc. using a sales voucher through Suvit.

### Excel Sheet Checklist (Before Uploading):

1. **Put Your Data in the First Sheet**
   - All sales data must be in the **first sheet** of your Excel file.

2. **Headers Go on Top**
   - The **first row** should have column names like: Date, Invoice Number, Amount, etc.

3. **Clean Column Titles**
   - No **dots (.)**, no **dollar signs ($)** in your headers.
   - Don't write anything above the column names.

4. **Always Fill the Invoice Number**
   - No empty boxes in the Invoice Number column allowed.

5. **Keep Same Invoice Numbers Together**
   - If one invoice has many items, sort by Invoice Number A–Z to keep them grouped.

6. **Don't Write NA or Not Applicable**
   - If something like GST doesn't apply, just **leave the cell blank**.
   - Do NOT write "NA" or "none".

7. **Use Date Format: DD/MM/YYYY**
   - Example: 27/05/1992 (day/month/year)

8. **No Extra Totals**
   - Delete rows with "Grand Total" or any notes not needed for Tally.

9. **Keep It Short**
   - Only add up to **10,000 rows** per sheet.

10. **Add a Ledger Column**
    - Add a column for **Sales Ledger** or **Purchase Ledger** based on GST rate.

11. **Set Up GST Ledgers in Tally**
    - Make sure **CGST**, **SGST**, and **IGST** ledgers are created under **Duties & Taxes** in Tally.

12. **Format Your Data Correctly**
    - Use **TEXT or General** format for text columns.
    - Use **NUMBER** format for numbers like amount, rate, etc.

13. **Add a Column Called "Particular"**
    - This is for the **Sales Account Ledger** based on GST rate.
    - Example: If GST is 18%, write the ledger name linked to 18% Sales.

14. **Save as Excel Workbook**
    - Save the file in **Excel Workbook format (.xlsx)**.

---

## 2. Uploading Sales/Sales Return Data Through an Excel Sheet

### Quick Access Links:
- Sales Upload Page: https://in.suvit.io/da/sales/excel
- Sales Return Upload Page: https://in.suvit.io/da/sales-Return/excel

### Step 1: Go to Bulk Upload → Sales / Sales Return
- From the left menu, click on **Bulk Upload**.
- Then choose either **Sales** or **Sales Return** from the dropdown.

### Step 2: Click Upload
- Click on the **Upload** button on the top right corner.

### Step 3: Select and Upload Your Excel File
- Click **"Click to upload"** to select your file from the computer.
- Make sure:
  - The file does NOT contain dots (.) or dollar ($) symbols in headers.
  - File size is **under 30MB**.
  - Date format is in **DD/MM/YYYY** (e.g., 05/08/2024).
  - Do NOT upload password-protected Excel files.
  - You have synced the required ledgers.
- Once the file is selected, click **Upload** to proceed.

### Step 4: File Appears in List
- Your file will now appear in the list with its name, type, and transaction count.
- This confirms the file was successfully uploaded.

### Pro Tip for Accountants:
- Double-check that the **Sales Account Ledger** is mapped as per your GST rate.
- Always sort by **Invoice Number A-Z** to avoid mapping issues.

### What's Next?
- Head to the **Data Mapping Screen** by clicking on the uploaded file.

---

## 3. Auto Mapping Sales Excel Sheet Data with Suvit Configuration

Auto-mapping is Suvit's smart feature that automatically matches your Excel sheet data to the right Tally fields. Once you map things once, Suvit remembers it for future uploads.

### Step 1: Field Mapping
- First, choose whether your data has items or not (e.g., **Without Item** if no product details).
- What you'll see:
  - **Mapped Fields** — Suvit found a match for these.
  - **Unmapped Fields** — You need to match these with the correct Tally field.
  - **Your Sheet Header** — Your Excel column titles.
  - **Tally Fields** — From Tally; match them with your data.
  - **Your Sheet Data** — Shows sample values to double-check.
- Click **Next** to go to GST Mapping.

#### Use of Configuration:
- You can also map: Voucher Date & Number, Party (Buyer or Consignee), Invoice Date, Lading No., Shipping No., Cost Centres, and Dispatch Details.

### Step 2: GST Mapping (Tax Ledger)
Suvit will auto-fill this based on your last upload if available.

#### Option 1: Select from Tally (if set to "No")
- Choose your Tally GST Ledger from a dropdown.

#### Option 2: Select From Excel (if set to "Yes")
- Match the column from Excel where GST Ledger Name is written.

#### GST Auto Calculation (if set to "Yes"):
- Suvit calculates **SGST, CGST, and IGST** on its own from Tally settings.
- Tally uses a rate priority system for GST calculation.

#### GST Manual Calculation From Sheet (if set to "No"):
- Suvit picks GST values from the Excel file.
- It uses that data to fill duties & taxes.
- **Note:** SGST, CGST, and IGST Tax Ledgers must be mapped. You can also map the Round-Off Ledger.

### Step 3: Ledger Mapping
- Link other columns like: Freight Amount, Discounts, Round-off.
- Once done, click **Save & Proceed**. You're ready to push to Tally.

---

## 4. How to Process or Push Sales/Sales Return Data to Tally

After mapping, the next screen shows your data in an Excel-like format for review.

### Save & Send to Tally:
- **A** → Select your transactions (choose all or one by one).
- **B** → Click the **Save** button.
- **C** → Click **Send to Tally** to send data into Tally.
- **D** → Hit **OK** when the system asks for confirmation.

> **Instruction:** Make sure all your entries are correct and no caution triangles are left behind before sending.
> **Warning:** Only the data you selected and saved will go to Tally. You can send the rest later.

### Progress Tracking:
- **Gray Stage (1st Stage):** Process has been initiated.
- **Orange Stage (2nd Stage):** Progress has started.
- **Green Stage (3rd Stage):** Data has been sent successfully to Tally.

### Processing Screen Overview:
| Field | Description |
|-------|-------------|
| Bulk Selection | Select transactions one-by-one or in bulk |
| Update Bulk Records | Change or select specific data |
| Reference No | As per Excel sheet |
| Voucher Type | Default: Sales (can be changed) |
| Party Name | Name of the party |
| GST No | As per party name detail |
| Place of Supply | From mapping or from Tally |
| Particulars | Shows Sales Account |
| Warning Triangle | Indicates missing details (spelling mistake or new party name) |
| Orange data | Not selected / not found in Tally |
| Blue data | All good / selected |

### Fixing Ledger Mismatches:

#### Step 1: Bulk Check Records
- Select the records you want to fix.
- Use Bulk Update to fix them together.

#### Step 2: Create Missing Ledgers
- Click the **"+" button** next to the party name to add a new ledger.

### General Filters Available:
- Hide data already sent to Tally.
- View blank, saved, or failed records.
- Filter data by date range.

### Bulk Operations:
- **Voucher Type** — Change the voucher type in bulk.
- **Party Name** — Update party name in bulk.
- **Particulars (Ledger)** — Change ledger in bulk.

---

## 5. Create Ledger and Stock Items from Sales Transaction Screen

Suvit provides an exceptional feature to create stock items and party ledgers in bulk with a single click.

### Method A: One-by-One (Single Entry)

#### Create a Party Name (Ledger):
1. Click the **Create Ledger** button.
2. A pop-up will appear → Fill the name, GST, and other info.
3. Click **Add** to save your party ledger.

> **Tip:** After saving, send one entry to Tally. Suvit will create the ledger in Tally and then post the entry.

#### Create a Stock Item (for invoices with items):
1. Click on the **drawer** icon to open the item list.
2. Click on **Create Item** to add a new product.
3. Fill all details (item name, unit, GST, etc.) and click **Add** to save.

> **Tip:** Send one transaction to Tally. Suvit will first create the stock item in Tally and then post the entry.

### Method B: Bulk Creation (All at Once)

#### Bulk Party Name Creation:
- Click on the **orange Plus Icon** to quickly add many party names.
- When you push data to Tally, the ledger will be auto-created there too.

#### Bulk Stock Item Creation:
- Click the **orange Plus Icon** to quickly add multiple item names.
- Once you send the data, new stock items will be created inside Tally too.

---

## 6. Create Invoice for Sales and Sales-Return

You can create invoices manually in Suvit without uploading an Excel sheet.

### Step 1: Go to Dashboard
- On the dashboard, click **"Explore Now"** under Data Entry Automation.

### Step 2: Create Invoice
- In the Transaction Menu, click **Create Bill**.
- Choose whether this is a **Sales** or **Sales Return** invoice.

### Step 3: Choose Invoice Type
- **Accounting Invoice** = Without Stock Items
- **Item Invoice** = With Stock Items (use when selling goods)

### Step 4: Fill in Invoice Details
- **Voucher Type** (e.g., Sales)
- **Voucher No.** (like invoice number)
- **Voucher Date** (date of invoice)
- **Party Name** (customer name)
- **GST Details** (will auto-fill from Tally)
- **Ledger Name** (like "Sales @ 18%")

### Step 5: Customer Details
- The customer details on the left will show here too.
- Other values will sync from Tally automatically.

### Step 6: Add Items (For "Item Invoice" only)
- Pick your **Stock Items** from the dropdown.
- Enter the **Quantity** (e.g., 5, 10, 50).
- Enter the **Rate** (price per item).
- If you have multiple items, keep adding them one by one.

### Step 7: Taxes, Narration & Amounts
- Select **Tax Ledgers** like SGST, CGST, IGST.
- Add any **narration or comments** (optional).
- Double-check the **Taxable Amount** and **Total Amount**.

### Step 8: Save the Bill
- Click **Save & Close** to finish.
- Click **Save & Sync** if you want to send it to Tally right away.

> **Note:** Fields marked with "*" must be filled in — no skipping!

---

## Key Quick Reference for Voice Agent

**Q: How do I upload a sales Excel file in Suvit?**
A: Go to Data Entry Automation → Bulk Upload → Sales → Click Upload → Select file → Click Upload.

**Q: What is auto-mapping?**
A: Auto-mapping is Suvit's smart feature that automatically matches your Excel sheet columns to the correct Tally fields. Once mapped, Suvit remembers it for future uploads.

**Q: How do I send sales data to Tally?**
A: After mapping, select your transactions, click Save, then click Send to Tally. Confirm with OK. Make sure Tally and Suvit Desktop App are both open.

**Q: What does the orange triangle warning mean?**
A: It means a ledger or party name is missing or not found in Tally — it could be a spelling mistake or a new party name that hasn't been created yet.

**Q: Can I create ledgers directly from the sales screen?**
A: Yes. Click the "+" button next to the party name to create a new ledger. You can do it one by one or in bulk.

**Q: What is the maximum number of rows allowed in a sales Excel sheet?**
A: Up to 10,000 rows per sheet.

**Q: What date format should be used in the Excel sheet?**
A: DD/MM/YYYY — for example, 27/05/2024.

**Q: What are the two types of invoices in Suvit?**
A: Accounting Invoice (without stock items) and Item Invoice (with stock items).
