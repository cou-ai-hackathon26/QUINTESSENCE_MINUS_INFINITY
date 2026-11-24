"""
Generate Complete English Demo Transaction Documents for Shongoti Hackathon Showcase.
Clean typography using standard Helvetica / Arial vector fonts in PyMuPDF.
Produces:
Set A: The Golden Case (Haque Traders Invoice #41)
  1. Haque Traders Invoice #41 (BDT 25,000)
  2. Bank Deposit Slip (BDT 4,000)
  3. Goods Return Memo (BDT 3,000)
  4. Supplier Clarification Message (TXT)
Set B: Commercial Wholesale Case (Kalam Traders INV-8891)
  5. Kalam Traders Wholesale Bill (BDT 45,000)
  6. bKash Merchant Slip (BDT 20,000)
  7. Damaged Goods Challan (BDT 5,000)
  8. Audio Clarification (MP3 + TXT)
Set C: Hackathon Challenges 1 & 2
  9. Challenge 2: Cropped / Unreadable Receipt (Honesty demonstration)
  10. Challenge 2: Contradictory Supplier Messages (TXT + MP3)
  11. Challenge 1: Multi-Invoice Statement with Lump-Sum Split Proposal (BDT 30,000 split across BDT 50,000)
"""
import os
import asyncio
from pathlib import Path
import pymupdf
import edge_tts

OUTPUT_DIR = Path("demo_documents")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class EnglishDocBuilder:
    def __init__(self, width=595, height=842):
        self.doc = pymupdf.open()
        self.page = self.doc.new_page(width=width, height=height)

    def text(self, pos, s, fontsize=11, color=(0, 0, 0), bold=False):
        fontname = "hebo" if bold else "helv"
        self.page.insert_text(pos, str(s), fontname=fontname, fontsize=fontsize, color=color)

    def rect(self, r, fill=None, color=None, width=1.0):
        self.page.draw_rect(r, color=color, fill=fill, width=width)

    def line(self, p1, p2, color=(0.4, 0.4, 0.4), width=1.0):
        self.page.draw_line(p1, p2, color=color, width=width)

    def save(self, base_name):
        pdf_path = OUTPUT_DIR / f"{base_name}.pdf"
        png_path = OUTPUT_DIR / f"{base_name}.png"
        self.doc.save(str(pdf_path))
        pix = self.page.get_pixmap(dpi=150)
        pix.save(str(png_path))
        self.doc.close()
        print(f"Generated: {pdf_path.name} & {png_path.name} ({pix.width}x{pix.height})")


# ==========================================
# SET A: GOLDEN CASE (Matches UI Reconciliation)
# Haque Traders - Invoice #41 (BDT 25,000)
# ==========================================

def create_haque_invoice_en():
    b = EnglishDocBuilder(595, 842)

    # Top Brand Header Box
    b.rect(pymupdf.Rect(40, 40, 555, 125), fill=(0.08, 0.25, 0.45))
    b.text((60, 75), "HAQUE TRADERS WHOLESALE CO.", fontsize=22, color=(1, 1, 1), bold=True)
    b.text((60, 96), "Wholesale Groceries & FMCG Distributor | Badamtoli Ghat, Dhaka-1100", fontsize=10, color=(0.85, 0.92, 1))
    b.text((60, 112), "Phone: +880 1819-876543 | Trade License: TRAD/DSCC/019284 | BIN: 001928472-0101", fontsize=9, color=(0.75, 0.85, 0.95))

    # Badge Box
    b.rect(pymupdf.Rect(390, 55, 535, 105), fill=(0.15, 0.35, 0.6), color=(1, 1, 1), width=1.5)
    b.text((410, 78), "COMMERCIAL BILL", fontsize=11, color=(1, 1, 1), bold=True)
    b.text((422, 96), "INVOICE #41", fontsize=11, color=(1, 1, 1), bold=True)

    # Details Box
    b.rect(pymupdf.Rect(40, 140, 555, 225), fill=(0.96, 0.98, 1), color=(0.8, 0.85, 0.9))
    b.text((55, 162), "BILL TO (CUSTOMER):", fontsize=9, color=(0.4, 0.4, 0.4), bold=True)
    b.text((55, 180), "Rahim Store (Proprietor: Md. Rahim Uddin)", fontsize=11, color=(0.1, 0.1, 0.2), bold=True)
    b.text((55, 196), "Shop #12, Mirpur-10 Circle, Dhaka-1216", fontsize=9.5, color=(0.25, 0.25, 0.25))
    b.text((55, 210), "Contact: +880 1700-000001 | Customer Code: RAH-0091", fontsize=9, color=(0.35, 0.35, 0.35))

    b.text((360, 162), "INVOICE NUMBER:", fontsize=9, color=(0.4, 0.4, 0.4), bold=True)
    b.text((460, 162), "INV-2024-41", fontsize=11, color=(0.08, 0.25, 0.45), bold=True)
    b.text((360, 180), "INVOICE DATE:", fontsize=9, color=(0.4, 0.4, 0.4), bold=True)
    b.text((460, 180), "12 November 2024", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((360, 198), "PAYMENT TERMS:", fontsize=9, color=(0.4, 0.4, 0.4), bold=True)
    b.text((460, 198), "Net 7 Days (Unpaid Due)", fontsize=10, color=(0.7, 0.1, 0.1), bold=True)
    b.text((360, 214), "DUE DATE:", fontsize=9, color=(0.4, 0.4, 0.4), bold=True)
    b.text((460, 214), "19 November 2024", fontsize=9.5, color=(0.2, 0.2, 0.2))

    # Items Table Header
    y = 240
    b.rect(pymupdf.Rect(40, y, 555, y + 25), fill=(0.15, 0.25, 0.4))
    b.text((50, y + 17), "#", fontsize=10, color=(1, 1, 1), bold=True)
    b.text((80, y + 17), "Item Description", fontsize=10, color=(1, 1, 1), bold=True)
    b.text((310, y + 17), "Quantity", fontsize=10, color=(1, 1, 1), bold=True)
    b.text((395, y + 17), "Unit Price", fontsize=10, color=(1, 1, 1), bold=True)
    b.text((475, y + 17), "Total Amount", fontsize=10, color=(1, 1, 1), bold=True)

    items = [
        ("1", "Teer Pure Fortified Soybean Oil (5 Liter Bottle)", "10 Cartons", "BDT 1,200.00", "BDT 12,000.00"),
        ("2", "Chashi Premium Chinigura Aromatic Rice (25kg Bag)", "4 Bags", "BDT 2,000.00", "BDT 8,000.00"),
        ("3", "Danish Sweetened Condensed Milk (Full Cream Tin)", "2 Cartons", "BDT 2,500.00", "BDT 5,000.00"),
    ]

    curr_y = y + 25
    for i, it in enumerate(items):
        bg = (0.97, 0.98, 1) if i % 2 == 1 else (1, 1, 1)
        b.rect(pymupdf.Rect(40, curr_y, 555, curr_y + 35), fill=bg, color=(0.85, 0.88, 0.92))
        b.text((52, curr_y + 22), it[0], fontsize=10, color=(0.2, 0.2, 0.2))
        b.text((80, curr_y + 22), it[1], fontsize=10, color=(0.1, 0.1, 0.1))
        b.text((315, curr_y + 22), it[2], fontsize=10, color=(0.2, 0.2, 0.2))
        b.text((395, curr_y + 22), it[3], fontsize=10, color=(0.2, 0.2, 0.2))
        b.text((470, curr_y + 22), it[4], fontsize=10, color=(0.1, 0.1, 0.1), bold=True)
        curr_y += 35

    # Total Due Box
    b.rect(pymupdf.Rect(310, curr_y + 15, 555, curr_y + 75), fill=(0.95, 0.97, 1), color=(0.08, 0.25, 0.45), width=1.5)
    b.text((325, curr_y + 38), "TOTAL CLAIMED DEMAND:", fontsize=10, color=(0.3, 0.3, 0.3), bold=True)
    b.text((420, curr_y + 65), "BDT 25,000.00", fontsize=18, color=(0.7, 0.1, 0.1), bold=True)

    b.text((45, curr_y + 40), "In Words: Twenty Five Thousand Bangladeshi Taka Only.", fontsize=9.5, color=(0.3, 0.3, 0.3), bold=True)
    b.text((45, curr_y + 60), "Status: OUTSTANDING SUPPLIER DEMAND (Awaiting Settlement)", fontsize=9.5, color=(0.6, 0.1, 0.1))

    # Signatures
    b.line(pymupdf.Point(400, curr_y + 160), pymupdf.Point(540, curr_y + 160))
    b.text((410, curr_y + 175), "Authorized Representative Signature", fontsize=8.5, color=(0.4, 0.4, 0.4))
    b.text((435, curr_y + 190), "Haque Traders Wholesale", fontsize=9, color=(0.2, 0.2, 0.2), bold=True)

    b.save("SetA_01_Haque_Traders_Invoice_41_Tk25k_EN")


def create_haque_payment_slip_en():
    b = EnglishDocBuilder(420, 580)

    # Header Box
    b.rect(pymupdf.Rect(25, 25, 395, 105), fill=(0.1, 0.45, 0.3))
    b.text((45, 58), "ISLAMI BANK BANGLADESH PLC", fontsize=18, color=(1, 1, 1), bold=True)
    b.text((45, 78), "Official Cash Deposit Receipt (Bank Counter Slip)", fontsize=9.5, color=(0.9, 1, 0.95))
    b.text((45, 95), "Branch: Mirpur Branch, Dhaka | Status: SUCCESSFUL TRANSACTION", fontsize=8.5, color=(0.8, 0.95, 0.85))

    # Amount Card
    b.rect(pymupdf.Rect(25, 120, 395, 205), fill=(0.95, 0.99, 0.96), color=(0.8, 0.9, 0.85))
    b.text((135, 148), "DEPOSITED AMOUNT", fontsize=10, color=(0.3, 0.5, 0.4), bold=True)
    b.text((120, 185), "BDT 4,000.00", fontsize=24, color=(0.1, 0.45, 0.3), bold=True)

    # Details Grid
    y = 220
    b.rect(pymupdf.Rect(25, y, 395, y + 245), fill=(1, 1, 1), color=(0.85, 0.9, 0.88))

    details = [
        ("Beneficiary Name:", "Haque Traders (Wholesale Account)"),
        ("Account Number:", "2050-1480-2019-8765"),
        ("Deposited By:", "Rahim Store (Md. Rahim Uddin)"),
        ("Reference Invoice:", "Invoice #41 (Challan 41)"),
        ("Date & Timestamp:", "14 November 2024, 12:15 PM"),
        ("Transaction / Voucher ID:", "IBBL-DEP-99418274"),
        ("Amount in Words:", "Four Thousand Taka Only"),
    ]

    for label, val in details:
        b.text((40, y + 25), label, fontsize=9, color=(0.4, 0.4, 0.4), bold=True)
        b.text((170, y + 25), val, fontsize=9.5, color=(0.1, 0.1, 0.1))
        b.line(pymupdf.Point(40, y + 33), pymupdf.Point(380, y + 33), color=(0.92, 0.94, 0.92))
        y += 33

    b.text((45, 485), "[BANK TELLER CASHIER STAMP & SIGNATURE VERIFIED]", fontsize=8, color=(0.2, 0.5, 0.3), bold=True)
    b.text((45, 500), "Note: Eligible payment record towards settling Haque Traders Invoice #41.", fontsize=8, color=(0.45, 0.45, 0.45))

    b.save("SetA_02_Bank_Deposit_Slip_Tk4k_EN")


def create_haque_return_memo_en():
    b = EnglishDocBuilder(520, 450)

    # Header Box
    b.rect(pymupdf.Rect(30, 30, 490, 95), fill=(0.55, 0.15, 0.15))
    b.text((50, 60), "GOODS RETURN CREDIT MEMO", fontsize=18, color=(1, 1, 1), bold=True)
    b.text((50, 80), "Buyer: Rahim Store  ->  Supplier: Haque Traders Wholesale", fontsize=9.5, color=(0.95, 0.85, 0.85))

    # Meta
    b.rect(pymupdf.Rect(30, 110, 490, 175), fill=(0.99, 0.96, 0.96), color=(0.85, 0.8, 0.8))
    b.text((45, 132), "Return Memo #: RET-41-01", fontsize=10, color=(0.2, 0.2, 0.2), bold=True)
    b.text((45, 150), "Original Invoice Ref: Invoice #41", fontsize=10, color=(0.55, 0.15, 0.15), bold=True)
    b.text((45, 165), "Return Reason: Damaged tins and packaging leaks", fontsize=9.5, color=(0.4, 0.4, 0.4))

    b.text((310, 132), "Date: 16 November 2024", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((310, 150), "Received By: Delivery Rep (Haque Traders)", fontsize=9.5, color=(0.2, 0.2, 0.2))

    # Table
    y = 190
    b.rect(pymupdf.Rect(30, y, 490, y + 25), fill=(0.25, 0.25, 0.25))
    b.text((45, y + 17), "Returned Item Description", fontsize=9.5, color=(1, 1, 1), bold=True)
    b.text((250, y + 17), "Quantity", fontsize=9.5, color=(1, 1, 1), bold=True)
    b.text((330, y + 17), "Unit Rate", fontsize=9.5, color=(1, 1, 1), bold=True)
    b.text((410, y + 17), "Credit Total", fontsize=9.5, color=(1, 1, 1), bold=True)

    b.rect(pymupdf.Rect(30, y + 25, 490, y + 60), fill=(1, 1, 1), color=(0.8, 0.8, 0.8))
    b.text((45, y + 48), "Danish Sweetened Condensed Milk (Damaged)", fontsize=9.5, color=(0.1, 0.1, 0.1))
    b.text((260, y + 48), "24 Tins", fontsize=9.5, color=(0.1, 0.1, 0.1))
    b.text((335, y + 48), "BDT 125.00", fontsize=9.5, color=(0.1, 0.1, 0.1))
    b.text((415, y + 48), "BDT 3,000.00", fontsize=10.5, color=(0.6, 0.1, 0.1), bold=True)

    # Total
    b.rect(pymupdf.Rect(270, y + 75, 490, y + 120), fill=(0.98, 0.94, 0.94), color=(0.55, 0.15, 0.15), width=1.5)
    b.text((285, y + 98), "TOTAL RETURN CREDIT:", fontsize=9.5, color=(0.2, 0.2, 0.2), bold=True)
    b.text((385, y + 112), "BDT 3,000.00", fontsize=14, color=(0.6, 0.1, 0.1), bold=True)

    # Signature
    b.line(pymupdf.Point(60, y + 155), pymupdf.Point(220, y + 155))
    b.text((65, y + 170), "Goods Received & Acknowledged (Delivery Agent)", fontsize=8.5, color=(0.3, 0.3, 0.3))

    b.save("SetA_03_Goods_Return_Memo_Tk3k_EN")


def create_haque_clarification_en():
    text = (
        "SUPPLIER CLARIFICATION MESSAGE (HAQUE TRADERS)\n"
        "Date: 18 November 2024\n"
        "From: Haque Traders Accounts Desk\n"
        "To: Rahim Store (Md. Rahim Uddin)\n\n"
        "\"Hello Rahim Bhai. We verified and received your BDT 4,000 bank deposit, and we have already "
        "credited it towards your account. However, our warehouse supervisor has NOT yet verified or deducted "
        "the BDT 3,000 damaged goods return slip from our billing records.\n\n"
        "Therefore, out of our BDT 25,000 demand, after deducting your BDT 4,000 payment, please settle the net "
        "payable of BDT 21,000 immediately. Once the return credit note is processed, the remaining BDT 3,000 will be adjusted.\"\n\n"
        "---------------------------------------------------\n"
        "SHONGOTI AUTOMATED RECONCILIATION RESULT:\n"
        "Hypothesis Isolated: REC-003 (Payment Included: True, Return Included: False)\n"
        "Arithmetic: BDT 25,000 (Demand) - BDT 4,000 (Payment) = BDT 21,000.00\n"
        "Unresolved Fact: Return deduction pending warehouse verification."
    )
    path = OUTPUT_DIR / "SetA_04_Haque_Traders_Supplier_Clarification_EN.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Generated: {path.name}")


# ==========================================
# SET B: WHOLESALE GROCERY INVOICE CASE
# Kalam Traders - INV-8891 (BDT 45,000)
# ==========================================

def create_kalam_invoice_en():
    b = EnglishDocBuilder(595, 842)

    # Header Box
    b.rect(pymupdf.Rect(40, 40, 555, 125), fill=(0.06, 0.28, 0.38))
    b.text((60, 75), "KALAM WHOLESALE TRADERS & SUPPLIES", fontsize=21, color=(1, 1, 1), bold=True)
    b.text((60, 96), "Primary Wholesale Distributor | Wholesale Market, Chawkbazar, Dhaka-1211", fontsize=10, color=(0.85, 0.95, 0.9))
    b.text((60, 112), "Phone: +880 1711-234567 | Email: kalamtraders.bd@gmail.com | BIN: 002345671-0202", fontsize=9, color=(0.75, 0.88, 0.85))

    b.rect(pymupdf.Rect(390, 55, 535, 105), fill=(0.1, 0.35, 0.45), color=(1, 1, 1), width=1.5)
    b.text((410, 78), "COMMERCIAL BILL", fontsize=11, color=(1, 1, 1), bold=True)
    b.text((410, 96), "INV-2024-8891", fontsize=11, color=(1, 1, 1), bold=True)

    # Details
    b.rect(pymupdf.Rect(40, 140, 555, 225), fill=(0.96, 0.98, 0.98), color=(0.8, 0.85, 0.85))
    b.text((55, 162), "BUYER / CUSTOMER:", fontsize=9, color=(0.3, 0.3, 0.3), bold=True)
    b.text((55, 180), "Rahim Store (Prop: Md. Rahim Uddin)", fontsize=11, color=(0.05, 0.2, 0.2), bold=True)
    b.text((55, 196), "Shop #12, Mirpur-10 Circle, Dhaka-1216", fontsize=9.5, color=(0.4, 0.4, 0.4))
    b.text((55, 210), "Mobile: +880 1700-000001 | A/C Code: RAH-8891", fontsize=9, color=(0.4, 0.4, 0.4))

    b.text((360, 162), "INVOICE NUMBER:", fontsize=9, color=(0.3, 0.3, 0.3), bold=True)
    b.text((460, 162), "INV-2024-8891", fontsize=11, color=(0.06, 0.28, 0.38), bold=True)
    b.text((360, 180), "DATE OF ISSUE:", fontsize=9, color=(0.3, 0.3, 0.3), bold=True)
    b.text((460, 180), "15 November 2024", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((360, 198), "PAYMENT TERMS:", fontsize=9, color=(0.3, 0.3, 0.3), bold=True)
    b.text((460, 198), "Credit Due (7 Days)", fontsize=10, color=(0.7, 0.1, 0.1), bold=True)

    # Table
    y = 240
    b.rect(pymupdf.Rect(40, y, 555, y + 25), fill=(0.15, 0.25, 0.3))
    b.text((50, y + 17), "#", fontsize=10, color=(1, 1, 1), bold=True)
    b.text((80, y + 17), "Product Description", fontsize=10, color=(1, 1, 1), bold=True)
    b.text((310, y + 17), "Quantity", fontsize=10, color=(1, 1, 1), bold=True)
    b.text((395, y + 17), "Unit Price", fontsize=10, color=(1, 1, 1), bold=True)
    b.text((475, y + 17), "Total (BDT)", fontsize=10, color=(1, 1, 1), bold=True)

    items = [
        ("1", "Rupchanda Pure Mustard Oil (5 Liter Jar)", "20 Cartons", "BDT 1,200.00", "BDT 24,000.00"),
        ("2", "Pran Premium Miniket Rice (50kg Bag)", "10 Bags", "BDT 1,500.00", "BDT 15,000.00"),
        ("3", "Olympic Energy Plus Biscuits (Export Pack)", "50 Cartons", "BDT 120.00", "BDT 6,000.00"),
    ]

    curr_y = y + 25
    for i, it in enumerate(items):
        bg = (0.97, 0.98, 0.99) if i % 2 == 1 else (1, 1, 1)
        b.rect(pymupdf.Rect(40, curr_y, 555, curr_y + 35), fill=bg, color=(0.85, 0.88, 0.9))
        b.text((52, curr_y + 22), it[0], fontsize=10, color=(0.2, 0.2, 0.2))
        b.text((80, curr_y + 22), it[1], fontsize=10, color=(0.1, 0.1, 0.1))
        b.text((315, curr_y + 22), it[2], fontsize=10, color=(0.2, 0.2, 0.2))
        b.text((395, curr_y + 22), it[3], fontsize=10, color=(0.2, 0.2, 0.2))
        b.text((470, curr_y + 22), it[4], fontsize=10, color=(0.1, 0.1, 0.1), bold=True)
        curr_y += 35

    # Total
    b.rect(pymupdf.Rect(310, curr_y + 15, 555, curr_y + 75), fill=(0.95, 0.98, 0.98), color=(0.1, 0.35, 0.45), width=1.5)
    b.text((325, curr_y + 38), "TOTAL INVOICE DEMAND:", fontsize=10, color=(0.2, 0.2, 0.2), bold=True)
    b.text((420, curr_y + 65), "BDT 45,000.00", fontsize=18, color=(0.7, 0.1, 0.1), bold=True)

    b.text((45, curr_y + 40), "In Words: Forty Five Thousand Taka Only.", fontsize=9.5, color=(0.3, 0.3, 0.3), bold=True)
    b.text((45, curr_y + 60), "Status: UNSETTLED WHOLESALE DEMAND", fontsize=9.5, color=(0.6, 0.1, 0.1))

    b.line(pymupdf.Point(400, curr_y + 160), pymupdf.Point(540, curr_y + 160))
    b.text((410, curr_y + 175), "Authorized Signature & Stamp", fontsize=8.5, color=(0.3, 0.3, 0.3))
    b.text((410, curr_y + 190), "Kalam Wholesale Traders", fontsize=9, color=(0.5, 0.5, 0.5), bold=True)

    b.save("SetB_01_Kalam_Traders_Invoice_INV-8891_Tk45k_EN")


def create_bkash_slip_en():
    b = EnglishDocBuilder(380, 580)

    # Header
    b.rect(pymupdf.Rect(20, 20, 360, 110), fill=(0.88, 0.10, 0.37))
    b.text((40, 55), "bKash", fontsize=24, color=(1, 1, 1), bold=True)
    b.text((120, 55), "MERCHANT PAYMENT", fontsize=12, color=(1, 1, 1), bold=True)
    b.text((40, 85), "Payment Successful", fontsize=13, color=(1, 1, 1), bold=True)
    b.text((40, 102), "18 November 2024, 04:32 PM", fontsize=9, color=(1, 0.9, 0.95))

    # Amount
    b.rect(pymupdf.Rect(20, 125, 360, 210), fill=(0.98, 0.98, 0.98), color=(0.9, 0.9, 0.9))
    b.text((130, 155), "PAID AMOUNT", fontsize=10, color=(0.5, 0.5, 0.5), bold=True)
    b.text((100, 192), "BDT 20,000.00", fontsize=22, color=(0.88, 0.10, 0.37), bold=True)

    y = 230
    b.rect(pymupdf.Rect(20, y, 360, y + 240), fill=(1, 1, 1), color=(0.9, 0.9, 0.9))

    details = [
        ("Merchant Name:", "Kalam Wholesale Traders"),
        ("Merchant Account:", "01711-234567"),
        ("Sender (Customer):", "Rahim Store (01700-000001)"),
        ("Transaction ID (TrxID):", "9K72JFL18A"),
        ("Reference Code:", "INV-8891"),
        ("Convenience Fee:", "BDT 0.00"),
        ("Payment Channel:", "bKash Business QR / App"),
    ]

    for label, val in details:
        b.text((35, y + 25), label, fontsize=9, color=(0.4, 0.4, 0.4), bold=True)
        b.text((175, y + 25), val, fontsize=9.5, color=(0.1, 0.1, 0.1))
        b.line(pymupdf.Point(35, y + 33), pymupdf.Point(345, y + 33), color=(0.93, 0.93, 0.93))
        y += 33

    b.text((45, 500), "Official electronic transaction receipt. No signature required.", fontsize=8, color=(0.55, 0.55, 0.55))

    b.save("SetB_02_bKash_Payment_Receipt_Tk20k_EN")


def create_kalam_return_en():
    b = EnglishDocBuilder(520, 450)

    b.rect(pymupdf.Rect(30, 30, 490, 95), fill=(0.45, 0.15, 0.15))
    b.text((50, 60), "GOODS RETURN CHALLAN", fontsize=18, color=(1, 1, 1), bold=True)
    b.text((50, 80), "Customer: Rahim Store  ->  Supplier: Kalam Wholesale Traders", fontsize=9.5, color=(0.95, 0.85, 0.85))

    b.rect(pymupdf.Rect(30, 110, 490, 175), fill=(0.99, 0.97, 0.97), color=(0.85, 0.8, 0.8))
    b.text((45, 132), "Challan No: RET-552", fontsize=10, color=(0.2, 0.2, 0.2), bold=True)
    b.text((45, 150), "Original Bill Ref: INV-2024-8891", fontsize=10, color=(0.45, 0.15, 0.15), bold=True)
    b.text((45, 165), "Return Reason: Broken jars & packaging leakages", fontsize=9.5, color=(0.5, 0.1, 0.1))

    b.text((310, 132), "Date: 19 November 2024", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((310, 150), "Received By: Delivery Rep (Kalam Traders)", fontsize=9.5, color=(0.2, 0.2, 0.2))

    y = 190
    b.rect(pymupdf.Rect(30, y, 490, y + 25), fill=(0.3, 0.3, 0.3))
    b.text((45, y + 17), "Item Description", fontsize=9.5, color=(1, 1, 1), bold=True)
    b.text((250, y + 17), "Quantity", fontsize=9.5, color=(1, 1, 1), bold=True)
    b.text((330, y + 17), "Unit Price", fontsize=9.5, color=(1, 1, 1), bold=True)
    b.text((410, y + 17), "Credit Amount", fontsize=9.5, color=(1, 1, 1), bold=True)

    b.rect(pymupdf.Rect(30, y + 25, 490, y + 60), fill=(1, 1, 1), color=(0.8, 0.8, 0.8))
    b.text((45, y + 48), "Rupchanda Mustard Oil (Damaged)", fontsize=9.5, color=(0.1, 0.1, 0.1))
    b.text((260, y + 48), "4 Cartons", fontsize=9.5, color=(0.1, 0.1, 0.1))
    b.text((335, y + 48), "BDT 1,250.00", fontsize=9.5, color=(0.1, 0.1, 0.1))
    b.text((415, y + 48), "BDT 5,000.00", fontsize=10.5, color=(0.6, 0.1, 0.1), bold=True)

    b.rect(pymupdf.Rect(270, y + 75, 490, y + 120), fill=(0.98, 0.94, 0.94), color=(0.45, 0.15, 0.15), width=1.5)
    b.text((285, y + 98), "TOTAL RETURN CREDIT:", fontsize=9.5, color=(0.2, 0.2, 0.2), bold=True)
    b.text((385, y + 112), "BDT 5,000.00", fontsize=14, color=(0.6, 0.1, 0.1), bold=True)

    b.line(pymupdf.Point(60, y + 155), pymupdf.Point(220, y + 155))
    b.text((65, y + 170), "Goods Received & Accepted (Delivery Agent Signature)", fontsize=8.5, color=(0.3, 0.3, 0.3))

    b.save("SetB_03_Damage_Return_Challan_Tk5k_EN")


# ==========================================
# SET C: HACKATHON CHALLENGES 1 & 2
# ==========================================

def create_cropped_receipt_en():
    b = EnglishDocBuilder(380, 450)

    b.rect(pymupdf.Rect(20, 20, 360, 430), fill=(0.96, 0.95, 0.92), color=(0.7, 0.7, 0.7))
    b.text((40, 55), "OFFICIAL CASH PAYMENT RECEIPT", fontsize=15, color=(0.2, 0.2, 0.2), bold=True)
    b.text((40, 75), "Supplier Money Receipt | Kalam Wholesale Traders", fontsize=9, color=(0.4, 0.4, 0.4))

    b.text((40, 110), "Date: 20 November 2024", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((40, 130), "Customer: Rahim Store", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((40, 150), "Payment For: Partial invoice settlement", fontsize=10, color=(0.2, 0.2, 0.2))

    # Torn amount box
    b.rect(pymupdf.Rect(40, 180, 330, 260), fill=(0.92, 0.85, 0.8), color=(0.8, 0.3, 0.3))
    b.text((55, 210), "PAID AMOUNT: [PORTION TORN / CROPPED]", fontsize=10, color=(0.7, 0.1, 0.1), bold=True)
    b.text((55, 235), "Amount numbers are sliced off in receipt photo...", fontsize=9, color=(0.5, 0.2, 0.2))

    # Stamp
    b.rect(pymupdf.Rect(35, 290, 345, 390), fill=(1, 0.92, 0.92), color=(0.7, 0.1, 0.1), width=2.0)
    b.text((50, 320), "⚠️ CROPPED / UNREADABLE RECEIPT PHOTO", fontsize=10, color=(0.7, 0.1, 0.1), bold=True)
    b.text((50, 340), "Shongoti Integrity Rule: Never guess or hallucinate missing money.", fontsize=8, color=(0.3, 0.3, 0.3))
    b.text((50, 355), "Confidence Assessment: CAPPED AT 59% (Needs Owner Review)", fontsize=8, color=(0.3, 0.3, 0.3), bold=True)
    b.text((50, 370), "Status: missing_fact = 'eligible_payment.amount_paisa'", fontsize=8, color=(0.6, 0.1, 0.1))

    b.save("SetC_01_Challenge2_Cropped_Unreadable_Receipt_EN")


def create_lump_sum_split_statement_en():
    b = EnglishDocBuilder(595, 650)

    b.rect(pymupdf.Rect(40, 30, 555, 100), fill=(0.1, 0.2, 0.45))
    b.text((60, 65), "OPEN SUPPLIER INVOICES & PROPOSED SETTLEMENT SPLIT", fontsize=16, color=(1, 1, 1), bold=True)
    b.text((60, 85), "HACKATHON CHALLENGE 1 & DIRECTION DEMONSTRATION", fontsize=9, color=(0.85, 0.9, 1))

    # Meta
    b.rect(pymupdf.Rect(40, 115, 555, 170), fill=(0.96, 0.97, 1), color=(0.8, 0.85, 0.9))
    b.text((55, 135), "Supplier: Kalam Wholesale Traders", fontsize=11, color=(0.1, 0.1, 0.3), bold=True)
    b.text((55, 155), "Merchant: Rahim Store (Retail Grocery)", fontsize=11, color=(0.1, 0.1, 0.3))
    b.text((320, 135), "Total Outstanding Due: BDT 50,000.00", fontsize=11, color=(0.7, 0.1, 0.1), bold=True)
    b.text((320, 155), "Merchant Lump-Sum Payment: BDT 30,000.00", fontsize=11, color=(0.05, 0.45, 0.2), bold=True)

    # Table
    y = 190
    b.rect(pymupdf.Rect(40, y, 555, y + 25), fill=(0.2, 0.3, 0.5))
    b.text((50, y + 17), "Invoice #", fontsize=10, color=(1, 1, 1), bold=True)
    b.text((140, y + 17), "Due Date & Age", fontsize=10, color=(1, 1, 1), bold=True)
    b.text((270, y + 17), "Original Due", fontsize=10, color=(1, 1, 1), bold=True)
    b.text((375, y + 17), "Proposed Allocation (Oldest-First)", fontsize=10, color=(1, 1, 1), bold=True)
    b.text((495, y + 17), "Remaining Due", fontsize=10, color=(1, 1, 1), bold=True)

    invoices = [
        ("INV-101", "01 Nov 2024 (Overdue 23 Days)", "BDT 15,000.00", "BDT 15,000.00 (100% Cleared)", "BDT 0.00"),
        ("INV-102", "10 Nov 2024 (Overdue 14 Days)", "BDT 25,000.00", "BDT 15,000.00 (Partial Payment)", "BDT 10,000.00"),
        ("INV-103", "20 Nov 2024 (Current Term)", "BDT 10,000.00", "BDT 0.00 (Next Settlement)", "BDT 10,000.00"),
    ]

    curr_y = y + 25
    for inv in invoices:
        b.rect(pymupdf.Rect(40, curr_y, 555, curr_y + 35), fill=(1, 1, 1), color=(0.85, 0.88, 0.92))
        b.text((50, curr_y + 22), inv[0], fontsize=10, color=(0.1, 0.1, 0.1), bold=True)
        b.text((140, curr_y + 22), inv[1], fontsize=9, color=(0.3, 0.3, 0.3))
        b.text((270, curr_y + 22), inv[2], fontsize=10, color=(0.1, 0.1, 0.1))
        b.text((375, curr_y + 22), inv[3], fontsize=9, color=(0.05, 0.45, 0.2), bold=True)
        b.text((495, curr_y + 22), inv[4], fontsize=10, color=(0.6, 0.1, 0.1), bold=True)
        curr_y += 35

    curr_y += 20
    b.rect(pymupdf.Rect(40, curr_y, 555, curr_y + 115), fill=(0.95, 0.99, 0.95), color=(0.2, 0.5, 0.3), width=1.5)
    b.text((55, curr_y + 25), "🎯 SHONGOTI AI SPLIT PROPOSAL (Challenge 1 & Direction Solution):", fontsize=11, color=(0.05, 0.4, 0.15), bold=True)
    b.text((55, curr_y + 48), "• Strategy 1 (Oldest Due First): Fully clears oldest overdue bill INV-101 (15k), remaining 15k applied to INV-102.", fontsize=9, color=(0.2, 0.2, 0.2))
    b.text((55, curr_y + 68), "• Strategy 2 (Proportional Split): 60% flat allocation across all bills (INV-101: 9k, INV-102: 15k, INV-103: 6k).", fontsize=9, color=(0.2, 0.2, 0.2))
    b.text((55, curr_y + 88), "• Financial Rule D001: Integer paisa precision strictly enforced. Zero floating-point rounding errors.", fontsize=9, color=(0.2, 0.2, 0.2))

    b.save("SetC_02_Challenge1_Multi_Invoice_LumpSum_Batch_EN")


async def create_english_audio_and_text():
    # Kalam clarification
    kalam_text = (
        "SUPPLIER CLARIFICATION MESSAGE (KALAM TRADERS)\n"
        "Date: 19 November 2024\n"
        "From: Kalam Wholesale Traders Accounts\n"
        "To: Rahim Store\n\n"
        "\"Hello Rahim Bhai, Kalam here. We received your BDT 20,000 bKash payment. "
        "However, our warehouse accounts have NOT yet credited or deducted the BDT 5,000 damaged goods return. "
        "Please calculate the net payable after deducting the payment and send the remaining balance promptly.\""
    )
    p4 = OUTPUT_DIR / "SetB_04_Kalam_Supplier_Clarification_EN.txt"
    with open(p4, "w", encoding="utf-8") as f:
        f.write(kalam_text)
    print(f"Generated: {p4.name}")

    audio_p4 = OUTPUT_DIR / "SetB_04_Kalam_Supplier_Clarification_EN.mp3"
    comm1 = edge_tts.Communicate(
        "Hello Rahim Bhai, Kalam here. We received your twenty thousand taka bKash payment. "
        "However, our accounts have not yet credited the five thousand taka damaged goods return. "
        "Please calculate the net payable and send the remaining balance promptly.",
        "en-US-GuyNeural"
    )
    await comm1.save(str(audio_p4))
    print(f"Generated: {audio_p4.name}")

    # Challenge 2 Contradiction
    contra_text = (
        "CHALLENGE 2: SUPPLIER CONTRADICTORY STATEMENTS\n\n"
        "Message 1 (20 November, 10:00 AM):\n"
        "\"Rahim Bhai, we verified and received your BDT 20,000 payment. It is credited.\"\n\n"
        "Message 2 (22 November, 03:00 PM - Contradictory denial):\n"
        "\"No no Rahim Bhai! I checked our bank book again and we never received that BDT 20,000! "
        "That payment was from another retail shop! You have zero payment deposited!\"\n\n"
        "---------------------------------------------------\n"
        "SHONGOTI CONTRADICTION DETECTION:\n"
        "System State: CONFLICTED\n"
        "Action: Conflicting claim detected between Message 1 and Message 2. Blocks automatic settlement."
    )
    p6 = OUTPUT_DIR / "SetC_03_Challenge2_Contradictory_Supplier_SMS_EN.txt"
    with open(p6, "w", encoding="utf-8") as f:
        f.write(contra_text)
    print(f"Generated: {p6.name}")

    audio_p6 = OUTPUT_DIR / "SetC_03_Challenge2_Contradictory_Voice_EN.mp3"
    comm2 = edge_tts.Communicate(
        "No no Rahim Bhai! I checked our bank book again and we never received that twenty thousand taka! "
        "That payment was from another retail shop! You have zero payment deposited!",
        "en-US-GuyNeural"
    )
    await comm2.save(str(audio_p6))
    print(f"Generated: {audio_p6.name}")


async def main():
    print("=== Generating 100% English Demo Transaction Documents ===")
    create_haque_invoice_en()
    create_haque_payment_slip_en()
    create_haque_return_memo_en()
    create_haque_clarification_en()

    create_kalam_invoice_en()
    create_bkash_slip_en()
    create_kalam_return_en()

    create_cropped_receipt_en()
    create_lump_sum_split_statement_en()
    await create_english_audio_and_text()
    print("\nAll English demo files successfully generated!")


if __name__ == "__main__":
    asyncio.run(main())
