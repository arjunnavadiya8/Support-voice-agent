# Suvit Knowledge Base — Bulk Master Creation Module

**Module Overview:**
Create stock items and ledgers in bulk with ease. Just prepare your Excel sheet and upload it using "Bulk Upload". This module covers creating hundreds or thousands of ledgers and stock items at once.

---

## 1. Create Bulk Stock Items in Suvit

Suvit lets you create stock items in bulk. Just prepare your Excel sheet as required and use the "Item" option under Bulk Upload.

### Step-by-Step Guide to Upload Stock Items in Bulk:

#### Step 1: Navigate to Bulk Upload
- Go to **Data Entry Automation** → **Bulk Upload** → **Item**.

#### Step 2: Download the Sample Excel Sheet
- On the **Item Excel page**, you will find an option to download a sample sheet or upload an existing Excel file.
- Click on **"Download Sample"** to get the template.

#### Step 3: Fill in the Required Details
- Open the excel sheet, fill in the required details, and save it.
- **Mandatory fields:** "Name", "Under", and "Unit".

#### Step 4: Upload the Excel Sheet
- Go back to the **Item Excel page**.
- Click on **"Upload"**.
- Select the appropriate company.
- Browse your stock item Excel file and upload it.
- If any item fails to upload, you will see an error log showing the reason for the failure.
- Click on the file for the next step.

#### Step 5 (formerly Step 6): Map the Fields
- Once uploaded, you will be redirected to the **Mapping Field** page.
- Map the relevant data fields correctly.
- After completing the mapping, click on **Save & Proceed**.
- If there's a mistake in the sheet, you will get an error popup — you can see the error in the popup or **Download excel error ledger log**.

#### Step 6 (formerly Step 7): Check for Remarks
- On the **item transaction screen**, you will get the remark **"failed reason"** if any item has issues.

#### Step 7 (formerly Step 8): Save the Transaction
- Go to the **Ledger Transaction** page.
- Select the record.
- Click **Save**.
- Then click **"Send to Tally"** in the drawer's right corner.

#### Step 8 (formerly Step 9): Send the Transaction to Tally
- A confirmation popup will appear → click **OK** to proceed or **Cancel** to stop.
- The **data synchronization** with Tally will complete successfully.

#### Step 9 (formerly Step 10): Verify in Tally
- Check those item ledgers in Tally.
- You will find that the stock item masters are created in your Tally.

---

## 2. Create Bulk Ledger in Suvit

Suvit helps in creating 1000s of ledgers in bulk within minutes. You can also utilize the GST Mapping feature to create ledgers using the GST Portal.

### Step 1: Login to Suvit
- Go to https://in.suvit.io and log in with your registered credentials.

### Step 2: Go to Bulk Upload Section
- From the left sidebar, click on the **Bulk Upload** icon under **Data Entry Automation**.
- Select **Ledger** under Bulk Upload.

### Step 3: Sample Sheet
- You can use Suvit's sample sheet or upload your own Excel sheet. The method is the same for both.

### Step 4: Fill the Sample Excel
- Open the downloaded file and fill in the ledger details.
- **Important Note:** Properly mention the "Under" type (ledger group) of the party name.

### Step 5: Upload Excel Sheet
- On the top right, click the **Upload** icon to upload the file.

### Step 6: Upload the Filled Excel File
- Click on **Upload**.
- Drag and drop your file or click to select.
- Press the **Upload** button to complete the process.

### Step 7: Verify the Upload
- Once uploaded, view your file in the ledger list.
- Click on the file to open it.

### Step 8: Map Fields for Ledgers

#### Method 1: GST Mapping for Party Creation
- Select the **GST Field** in the uploaded Excel sheet.
- Click **GST MAPPING** to fetch details from the GST Portal.
- The system retrieves **Party Name, State, and Tax Information** based on the GST Number.
- Choose the name: either **"Trade Name"** or **"Business Name"** for ledger creation.
- Proceed to **Save & Proceed**.

#### Method 2: Map Fields for Party Creation (Manual Mapping)
- After uploading, you will be taken to the **Mapping Field Page**.
- Map the Excel sheet fields with the system fields.
- Click **"Save & Proceed"** to finalize the ledger creation.

### Step 9: Confirmation
- If there are any issues, a **popup** will display the errors.
- You can view the **errors** directly or download the **Excel error log** for reference.

### Step 10: Save & Send
- Go back to the **Ledger Transaction Page**.
- Select the record you want to import.
- Click **Save**.
- Click on the right-side option **"Send to Tally"**.

### Step 11: Send to Tally
- A confirmation **popup** will appear.
- Click **OK** to proceed or **Cancel** to stop.
- The system will sync data with Tally, ensuring successful synchronization.

### Step 12: Verify in Tally
- After receiving the message **"Your data process has been completed"**, check Tally.
- The **ledger masters** will now be available in Tally.

---

## GST Mapping Feature for Ledger Creation — Special Feature

When creating bulk ledgers, Suvit provides a special **GST Mapping** feature:

1. Include a GST Number column in your Excel sheet.
2. Click **GST MAPPING** on the mapping screen.
3. Suvit will automatically fetch from the GST Portal:
   - Party Name
   - State
   - Tax Information
4. Choose whether to use **Trade Name** or **Business Name** for the ledger.
5. This eliminates the need to manually enter all party details.

---

## Key Quick Reference for Voice Agent

**Q: How do I create bulk stock items in Suvit?**
A: Go to Data Entry Automation → Bulk Upload → Item → Download Sample → Fill in Name, Under, and Unit fields → Upload the file → Map fields → Save & Proceed → Send to Tally.

**Q: What are the mandatory fields for bulk stock item creation?**
A: Name, Under (ledger group), and Unit are mandatory. Other fields like GST rate, HSN code, etc., are optional.

**Q: How do I create bulk ledgers in Suvit?**
A: Go to Data Entry Automation → Bulk Upload → Ledger → Download Sample or use your own Excel → Fill ledger details → Upload → Map fields → Save & Proceed → Send to Tally.

**Q: Can I create ledgers using GST numbers?**
A: Yes! Suvit has a GST Mapping feature. Include GST numbers in your Excel, click GST MAPPING, and Suvit will automatically fetch Party Name, State, and Tax Information from the GST Portal.

**Q: What is the "Under" field when creating ledgers?**
A: "Under" refers to the ledger group in Tally (e.g., Sundry Debtors, Sundry Creditors, Bank Accounts). It is mandatory and must be correctly specified.

**Q: What happens if my bulk upload has errors?**
A: You will see an error popup and can download the Excel error log to identify which records failed and why. Fix the errors and re-upload.

**Q: How do I verify that ledgers/stock items were created in Tally?**
A: After sending to Tally, open your Tally software and check the respective master list. The items/ledgers will now appear there.

**Q: Can I create thousands of ledgers at once?**
A: Yes, Suvit can create thousands of ledgers in bulk within minutes using the Bulk Upload → Ledger feature.
