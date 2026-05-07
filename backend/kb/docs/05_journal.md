# Suvit Knowledge Base — Journal Module

**Module Overview:**
Learn how to process and manage journal entries in Suvit. This module offers guides, tips, and steps to handle journal data and sync it seamlessly with Tally.

---

## 1. Checklist for Excel Before Using Journal Module

Record sales and purchase debit/credit using a journal in Suvit. Follow the provided steps to create an Excel sheet for accurate journal data entry.

### Excel Sheet Checklist (Before Uploading):

1. **Put data in the first sheet**
   - Only use **Sheet 1** in your Excel file.

2. **Headers go on the top row**
   - Keep your titles like **Date**, **Journal No.**, **Amount**, etc., in the **first row**.

3. **No dots or dollar signs in column names**
   - Don't use symbols like "." or "$".
   - Don't write anything above your column titles.

4. **Fill Journal Number for every entry**
   - No empty journal numbers allowed.

5. **Keep same invoice/reference numbers together**
   - Use Excel sort to group them.

6. **No NA or Not Applicable**
   - If something is not available, leave the cell **blank**.
   - Don't write NA, Not applicable, etc.

7. **Date format should be DD/MM/YYYY**
   - Example: 27/05/2022.

8. **Delete Grand Total or summary rows**
   - Suvit only needs raw entries — no totals at the bottom.

9. **Keep it short — max 5,000 rows**
   - Don't exceed 5,000 entries in one sheet.

10. **Debit = Credit**
    - Your total **Debit** amount and **Credit** amount must be equal.

11. **Use proper formatting in Excel**
    - Text = **TEXT** or **General** format.
    - Numbers = **Number** format.

12. **Add extra amounts horizontally (if needed)**
    - For the same Invoice or Reference No., you can add more columns to the right (not downwards).

13. **Save file in Excel Workbook format**
    - Save as .xlsx — not CSV or PDF.

> **Note:** Maximum 5,000 rows per sheet (lower than Sales/Purchase limit of 10,000).

---

## 2. Uploading Journal Data Through an Excel Sheet

### Step 1: Go to Bulk Upload → Journal
1. Click on **Bulk Upload** in the left-side menu.
2. In the dropdown, choose **Journal** from the list of document types.

### Step 2: Upload Your Excel File
3. Click on the **Upload** button in the top-right.
4. Drag and drop your Excel file **or** click the upload box to browse and select your file manually.
5. Click the **Upload** button at the bottom to begin the upload.

### Step 3: View the Uploaded Journal File
6. Your uploaded file will now appear in the list. You will see:
   - **File Name**
   - **Invoice Type** (e.g., Accounting Invoice)
   - **Total Records**
   - **Pending Records**
7. This confirms the sheet has been uploaded and is ready for mapping.

---

## 3. Mapping Excel Sheet Data of Journal with Suvit Configuration

After uploading a journal Excel sheet in Suvit, you need to map the data to Tally-required fields.

### Mapping Screen Overview:

1. **Excel Headers**
   - Suvit shows the column names from your uploaded Excel sheet.

2. **Assign Tally Fields**
   - Link your Excel columns with the correct Tally fields.
   - Example mappings:
     - Journal number → Reference no
     - Invoice value / Total value → Amount

3. **Top 3 Values from Sheet**
   - Suvit shows top 3 sample entries to help you confirm the match is correct.
   - If no data shows up, check your Excel format — something might be off.

4. **Other Ledger Mapping**
   - You can also map extra fields like:
     - Round-off
     - Discount
     - Freight Charges
   - Just select the correct column and link it with the right ledger.

5. **Reset Button**
   - Made a mistake? Click this to clear and re-map everything.

6. **Save & Proceed**
   - After mapping, click this button to go to the processing screen.

7. **Save Mapping**
   - Want to save time next time? Save this mapping format and Suvit will remember it.

### Item Allocation in Configuration:
- If your journal has **items**, go to **Configuration**.
- Find and enable the **Item Allocation field**.
- This ensures item-wise details are recorded properly.

---

## 4. How to Process or Push Journal Data to Tally

### General Filters:

1. **Information Button (i)** — Shows total number of transactions and total number of invoices.

2. **General Filters — Three Options:**
   - **Hide Tally Synced Records:** Hides already pushed data from the processing screen.
   - **Saved Records:** Shows only saved data.
   - **Blank Records:** Filters out blank data.

3. **Date Filter** — Filter by specific date range to send data to Tally for that period.

4. **Warning Triangle** — Appears when data is mismatched with Tally data.
   - Click on the triangle to see the unselected field of that particular record.
   - Data in **orange** indicates the data has not been selected.

### Bulk Operations:

5. **Search Bar** — Filter for any specific name.

6. **Select Transaction** — Helps to select individual or bulk entries.

7. **Update Bulk Records** — Select the type of data to update in bulk (e.g., Voucher Type & Particulars).

8. **Particulars** — Search for Party Name according to your Excel data.

### How to Save and Push the Data:

9. **Select Transaction** — Choose individual or bulk entries to send to Tally.

10. After selecting the transactions, click on the **Save** button.

11. **Re-Select Transaction (if needed)** — Choose individual or bulk entries to resend.

12. Click **Send to Tally** to push the data.

---

## 5. How to Sync Journal Data with Item Support in Tally using Suvit

Suvit helps manage financial data by syncing journal entries with item details to Tally. Your data must include item names, quantities, and amounts.

### Step 1: Navigate to Data Entry Automation
- Go to **Data Entry Automation** → **Bulk Upload** → **Journal**.

### Step 2: Select Journal Upload
- Click on the **Upload** button.

### Step 3: Upload File
- Select your file using **Click to upload**.
- Click on **Upload** button.
- Click on the uploaded **File**.

### Step 4: Sheet Preparation — Required Data

You need at least **9 types of data** in your Excel sheet for mapping:

| # | Field | Description |
|---|-------|-------------|
| 1 | Journal No. | Journal entry number |
| 2 | Reference No. | Transaction Number |
| 3 | Date | Date of the invoice bill/entry |
| 4 | Particulars | Name of the Debtor and Creditor |
| 5 | Name of Item | Stock item name as per Tally |
| 6 | Quantity | Total quantity |
| 7 | Rate | Rate of the stock item |
| 8 | Debit/Credit Type | Type of amount (Debit or Credit) |
| 9 | Amount | Value of the stock item or bill |

**Optional (Not Mandatory):**
| # | Field | Description |
|---|-------|-------------|
| 10 | Cost Center | From which department cost was allocated (if applicable) |
| 11 | Total Amount | Grand total including taxes (for verification) |

### Step 5: Configuration
- After uploading, go to the **Mapping Screen** in Suvit.
- Navigate to the **"Configuration"** section.
- Enable **item details** — this is crucial to allow Suvit to sync journal data with item support in Tally.

### Step 6: Mapping
1. **Imported File Header:** Shows headings from your Excel sheet.
2. **Tally Fields:** Fields matched with Tally. You can change them if needed.
3. **Your Sheet Data:** Shows sample data for cross-checking.
4. Press **Next** to move to GST Mapping.

### Step 7: Sync the Data in Tally
- Once the mapping is complete, you are ready to sync the data in Tally.
- Follow Suvit's documentation instructions for syncing journal data.

---

## Key Quick Reference for Voice Agent

**Q: How do I upload journal data in Suvit?**
A: Go to Data Entry Automation → Bulk Upload → Journal → Click Upload → Drag/drop or select your Excel file → Click Upload.

**Q: What is the maximum number of rows for a journal Excel sheet?**
A: Maximum **5,000 rows** per sheet (lower than Sales/Purchase which allows 10,000).

**Q: What must be true about Debit and Credit amounts in the journal?**
A: Total Debit must equal total Credit. They must balance.

**Q: How do I push journal data to Tally?**
A: Select transactions → Click Save → Re-select → Click Send to Tally. Both Tally and Suvit Desktop App must be open.

**Q: What does the orange warning triangle mean in the journal screen?**
A: It means some data is mismatched or not yet selected. Data shown in orange is unselected.

**Q: Can I sync journal entries that include stock items?**
A: Yes. When mapping, go to Configuration and enable the Item Allocation field. Your Excel sheet must include item name, quantity, rate, and debit/credit type.

**Q: How do I save my mapping for future uploads?**
A: Click "Save Mapping" after completing the mapping. Suvit will remember it for future uploads of similar format.

**Q: What is the date format required for journal entries?**
A: DD/MM/YYYY — for example, 27/05/2022.
