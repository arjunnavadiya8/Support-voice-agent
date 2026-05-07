# Suvit Knowledge Base — OCR Module

**Module Overview:**
OCR (Optical Character Recognition) converts scanned documents, PDFs, or images into editable, searchable data for easier access and automation. Suvit uses OCR to automatically extract data from Sales and Purchase invoice images/PDFs.

---

## 1. OCR — Uploading and Processing Sales Bills

Learn how to upload and process Sales/Sales Return images in Suvit using OCR for accurate data extraction and entry.

### How to Upload a Sales Invoice from an Image or PDF:

You can easily upload Sales invoices in Suvit using PDF or image files.

### Step 1: Go to Transactions Section
- Click on the **Transactions** icon from the left menu.
- Hover on **Sales** under the Transactions tab.
- Click on **Sales**.

### Step 2: Click on Upload Image
- On the top-right corner, click on **Upload Image**.

### Step 3: Upload the File
- Either **drag & drop** the file or click **Click to upload Image/PDF**.
- After the file loads, click **Upload**.

### Step 4: Verify Uploaded Entry
- After upload, you will see the list of invoices.
- Click on the invoice row to edit or verify the data.

### Important Notes on File Upload:
- You can upload up to **10 invoices** at a time.
- Maximum file size supported: **5 MB**.
- Supported file types: **.pdf, .jpeg, .jpg, .png, .webp**
- Fields from the uploaded sales invoice will be automatically detected and matched with your sales details. You can review and correct any errors.

### Step 5: How to Select and Verify Data

**1. Review and Select Invoice Type:**
- Choose if the sales invoice data is **"With Item"** or **"Accounting Invoice"**.

**2. Invoice Details:**
- Voucher type, number, and date.
- Customer name and GST number (with additional details if required).
- Sales ledger information.

**3. Item Details:**
- Add items in the table with these fields:
  - Serial number, item name, quantity, rate, and amount.
- You can delete any line item if needed.

**Configuration Options:**
- Use the **Configuration Window** to select the fields displayed during voucher entry.
- Fields include: Voucher Date, Customer Invoice No., Item Narration, etc.
- Save the changes once done.

### Step 6: Ledger, Tax, and Finalization

**4. Ledger Details:**
- Add or edit sales ledger names and their amounts.

**5. Tax Ledger Details:**
- Add tax components like SGST, CGST, and IGST with their descriptions and amounts.

**6. Narration and Totals:**
- Enter any additional notes in the narration field.
- Review subtotal, tax amount, and total amount.

**7. Save and Synchronize:**
- **Save & Close:** Saves the invoice and closes the screen.
- **Save & Sync:** Saves the invoice and syncs it directly with Tally.

### Important Reminders:
- Ensure the Suvit Tally Connector is open during synchronization.
- OCR efficiency for capturing sales data is **50–80%** during the initial entry. Always verify the extracted data before saving.

---

## 2. OCR — Uploading and Processing Purchase Bills

Learn how to upload, verify, and process Purchase/Purchase Return invoices using Suvit's OCR automation for seamless data entry and synchronization with Tally.

### How to Upload a Purchase Invoice from an Image or PDF:

### Step 1: Go to Transactions Section
- Click on the **Transactions** icon from the left menu.
- Hover on **Purchase** under the Transactions tab.
- Click on **Purchase**.

### Step 2: Click on Upload Image
- On the top-right corner, click on **Upload Image**.

### Step 3: Upload the File
- Either **drag & drop** the file or click **Click to upload Image/PDF**.
- After the file loads, click **Upload**.

### Step 4: Verify Uploaded Entry
- After upload, you will see the list of invoices.
- Click on the invoice row to edit or verify the data.

### Important Notes on File Upload:
- You can upload up to **10 invoices** at a time.
- Maximum file size supported: **5 MB**.
- Supported file types: **.pdf, .jpeg, .jpg, .png, .webp**
- Fields from the uploaded purchase invoice will be automatically detected and matched with your purchase details. You can review and correct any errors.

### Step 5: Verify Data

**1. Review and Select Invoice Type:**
- Choose if the purchase invoice data is **"With Item"** or **"Accounting Invoice"**.

**2. Fill in Invoice Details:**
- Voucher Type, Number, and Date
- Supplier Name and GST Number (with additional details if required)
- Purchase Ledger Information

**3. Add Item Details:**
- Add purchased items with these fields:
  - Serial number, item name, quantity, rate, and amount.
- You can delete any line item if needed.

**Configuration Options:**
- Use the **Configuration Window** to select fields displayed during voucher entry.
- Fields include: Voucher Date, Supplier Invoice No., Item Narration, etc.
- Save changes once done.

### Step 6: Ledger, Tax, and Finalization

**4. Edit Ledger Details:**
- Add or modify purchase ledger names and their amounts.

**5. Add Tax Ledger Details:**
- Enter tax components like SGST, CGST, and IGST with descriptions and amounts.

**6. Review Narration and Totals:**
- Add any necessary narration notes.
- Review subtotal, tax amount, and total amount.

**7. Save and Synchronize:**
- **Save & Close:** Saves the purchase invoice and closes the screen.
- **Save & Sync:** Saves the invoice and syncs it directly with Tally.

### Important Reminders:
- Ensure the Suvit Tally Connector is open during synchronization.
- OCR efficiency for capturing purchase data is **50–80%** during initial entry. Always verify the extracted data before saving.

---

## OCR vs Excel Upload — Comparison

| Feature | OCR Upload | Excel Upload |
|---------|-----------|--------------|
| Input type | Image / PDF / Scanned document | Excel (.xlsx) file |
| Max upload at once | 10 invoices at a time | One file with up to 10,000 rows |
| Data extraction accuracy | 50–80% (requires verification) | High (data as entered in Excel) |
| Best for | Individual invoices from images | Large volume of transactions |
| Supported formats | .pdf, .jpeg, .jpg, .png, .webp | .xlsx |
| Max file size | 5 MB per file | 30 MB |

---

## Key Quick Reference for Voice Agent

**Q: What is OCR in Suvit?**
A: OCR (Optical Character Recognition) is a feature that automatically extracts data from scanned documents, PDFs, or images of invoices and converts them into structured data that can be entered into Tally.

**Q: How do I upload a sales invoice image in Suvit?**
A: Go to Transactions → Sales → click "Upload Image" (top right) → drag & drop or click to upload the file → verify the extracted data → Save & Sync to send to Tally.

**Q: How do I upload a purchase invoice image in Suvit?**
A: Go to Transactions → Purchase → click "Upload Image" (top right) → drag & drop or click to upload the file → verify the extracted data → Save & Sync to send to Tally.

**Q: How many invoices can I upload at once using OCR?**
A: Up to 10 invoices at a time, with a maximum file size of 5 MB each.

**Q: What file formats are supported for OCR upload?**
A: PDF, JPEG, JPG, PNG, and WEBP formats are supported.

**Q: How accurate is OCR data extraction?**
A: OCR efficiency is 50–80% during initial entry. Always review and verify the extracted data before saving and syncing to Tally.

**Q: What should I do after uploading an invoice image via OCR?**
A: Review the auto-extracted data carefully. Fix any errors in invoice details, item details, ledger names, and tax amounts. Then click Save & Sync to send to Tally.

**Q: Does the Suvit Tally Connector need to be open when using OCR?**
A: Yes. The Suvit Tally Connector (Desktop Application) must be open and running for the data to sync with Tally successfully.

**Q: What is the difference between Accounting Invoice and Item Invoice in OCR?**
A: Accounting Invoice is used when there are no stock items (service invoices). Item Invoice is used when the invoice includes physical goods with item names, quantities, and rates.
