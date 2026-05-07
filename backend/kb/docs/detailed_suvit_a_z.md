# Detailed Suvit A to Z Knowledge Base Dataset

This document contains a comprehensive and exhaustive reference manual of all available features, processes, workflows, and modules in Suvit, extracted directly from the Suvit Help Center (https://help.suvit.io/).

## 1. Getting Started and Account Activation
*   **Registration:** Visit [in.suvit.io/signUp](https://in.suvit.io/signUp) directly. Enter your mobile number, verify via OTP, and proceed to fill in personal and organization details.
*   **Account Verification:** Email and Mobile ID must both be verified via the "My Profile" section for full account activation and access to advanced features.
*   **Tally Connector Installation:** Suvit uses a desktop application ("Tally Connector") to bridge the Tally software with the cloud. Downloads are available for both 64-bit and 32-bit systems in the "Help & Resources" section.
*   **Company Sync:** Once the Tally Connector desktop app is installed, open your company in Tally, add it to Suvit, and click the synchronize ledgers button to upload your accounting masters.
*   **Subscription & Billing:** Plans can be purchased directly from the website. They include unlimited document uploads, banking automation, sales/purchase modules, and client management.

---

## 2. Banking Module and Automations
*   **Importing Bank Statements:** Bulk upload of your bank statements is fully supported. Navigate to "Bulk Upload > Banking", select your company and bank ledger, and upload the statement file (Excel or PDF).
*   **Transaction Processing:** Once uploaded, wait for the processing status to say "Complete". Then select matching ledgers for each individual transaction or use checkboxes to process multiple transactions in bulk.
*   **Filters & Configurations:** Includes advanced filtering by date range, narration searches, and amount. You can hide "Tally Pushed" records. Advanced settings allow for tracking cheque numbers/dates ("Bank Allocation") and cost center tracking.
*   **Contra Entries:** The system automatically identifies transfers between your linked bank or cash accounts and allows recording them as contra entries.

---

## 3. Sales & Sales Return Module
*   **Excel Guidelines:** Source spreadsheets must have data on the very first sheet, headers in the first row, and mandatory invoice numbers. The supported date format is strictly `DD/MM/YYYY`.
*   **Auto-Mapping Field Headers:** A smart mapping algorithm allows linking Excel headers to Tally fields and matching GST rates directly to specific tax ledgers.
*   **Pushing to Tally:** Review mapped data, save any manual edits, and click "Send to Tally" for instant synchronization.
*   **Inventory Integration:** Supports both "With Item" (Sales with Inventory) and "Ledger only" (Sales without Inventory) workflows.

---

## 4. Purchase & Purchase Return Module
*   **Standard Workflow:** Mirroring the Sales module, you upload purchase registers in Excel or CSV format, map fields, verify data, and sync with Tally.
*   **System Checklist:** Ensure your data is cleaned, multi-line entries have identical invoice numbers, and required GST ledgers are already created in Tally before starting the import.

---

## 5. Journal & Voucher Modules
*   **Data Preparation:** Supports multi-debit/multi-credit entries within a single voucher. For a voucher to sync successfully, total debits MUST balance with total credits.
*   **Mapping:** Requires mapping of voucher numbers and reference numbers to ensure accounting accuracy in Tally.

---

## 6. Bulk Master Creation
*   **Accounting Ledgers:** Bulk create accounting ledgers (Parties, Expenses, etc.) directly via Excel. You can automatically fetch correct party details from the GST Portal using their GSTIN.
*   **Stock Items:** Supports bulk creation of inventory items with parameters like HSN/SAC, Unit of Measure (UOM), and GST rates.

---

## 7. Client, User, & Permission Management
*   **User Roles & Permissions:** Primary accounts can create sub-users (staff) and assign specific permissions (View/Create/Edit/Delete) on a module-by-module basis.
*   **Client Access:** Practitioners can provide clients with their own login to upload documents directly to the practitioner's workspace.
*   **Suvit Drive:** A secure cloud storage feature for transferring, tracking, and approving documents between accountants and clients.

---

## 8. GST Automation & Reconciliation Tools
*   **GSTR-2A/2B Reconciliation:** Compares your Tally purchase data with GST Portal data to detect matched, mismatched, or completely missing entries.
*   **GST Dashboard:** Shows filing status (GSTR-1, GSTR-3B) for all managed companies, tax liability, and Input Tax Credit (ITC) trends.
*   **Search Taxpayer:** Integrated search tool to check GSTIN status (Active/Suspended/Cancelled) and filing history.

---

## 9. Advanced Features & System Shortcuts
*   **OCR (Optical Character Recognition):** Upload images (`.png`, `.jpeg`, `.jpg`) or PDFs of physical bills. Suvit extracts all essential data fields (Invoice #, Date, Amount, GST) directly into the verification screen without Excel.
*   **WhatsApp Integration:** Automates document collection by sending reminders to clients via WhatsApp to upload their pending files.
*   **Vyapar Integration:** Direct integration with Vyapar app to easily sync sales and purchase entries into Tally through Suvit.
*   **Shortcut Keys:**
    *   `ALT + S`: Save Transaction
    *   `ALT + T`: Sync to Tally
    *   `ALT + C`: Create Ledger
    *   `CTRL + M`: Open Menu Drawer
