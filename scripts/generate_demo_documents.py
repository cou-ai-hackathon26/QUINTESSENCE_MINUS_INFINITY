"""
Demo Documents & Synthetic Data Generator for Shongoti Hackathon Judge Showcase.
Generates realistic Bangladeshi MSME documents:
1. Supplier Wholesale Invoice (PDF & PNG) - Demand: BDT 45,000
2. bKash Merchant Payment Receipt (PDF & PNG) - Eligible Payment: BDT 20,000
3. Damaged Goods Return Challan (PDF & PNG) - Accepted Return: BDT 5,000
4. Bangla Supplier Clarification Voice Note (MP3) & Text (TXT)
5. Challenge 2: Cropped / Torn Unreadable Receipt (PNG)
6. Challenge 2: Contradictory Supplier SMS (TXT & MP3)
7. Challenge 1: Multi-Invoice Statement for Lump-Sum Split (PDF & PNG)
"""
import os
import asyncio
from pathlib import Path
import pymupdf
import edge_tts

OUTPUT_DIR = Path("demo_documents")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_BN = "C:/Windows/Fonts/Nirmala.ttc"
FONT_EN_BOLD = "helv-bold" if pymupdf.Font else "helv"


def create_supplier_invoice():
    """1. Wholesale Invoice: BDT 45,000 from Kalam Traders to Rahim Store."""
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)  # A4

    # Top Brand Header
    page.draw_rect(pymupdf.Rect(40, 40, 555, 120), color=None, fill=(0.06, 0.28, 0.38))
    page.insert_text((60, 75), "মেসার্স কালাম ট্রেডার্স", fontfile=FONT_BN, fontsize=22, color=(1, 1, 1))
    page.insert_text((60, 95), "পাইকারি পরিবেশক ও সরবরাহকারী | হোলসেল ট্রেড মার্কেট, চকবাজার, ঢাকা-১২১১", fontfile=FONT_BN, fontsize=10, color=(0.85, 0.95, 0.9))
    page.insert_text((60, 110), "মোবাইল: ০১৭১১-২৩৪৫৬৭ | ইমেইল: kalamtraders.bd@gmail.com", fontfile=FONT_BN, fontsize=9, color=(0.75, 0.88, 0.85))

    # Title & Badge
    page.draw_rect(pymupdf.Rect(400, 55, 535, 95), color=(1, 1, 1), fill=(0.1, 0.35, 0.45), width=1.5)
    page.insert_text((420, 75), "বিক্রয় চালান ও বিল", fontfile=FONT_BN, fontsize=12, color=(1, 1, 1))
    page.insert_text((415, 90), "COMMERCIAL INVOICE", fontsize=8, color=(0.9, 0.9, 0.9))

    # Metadata Grid
    page.draw_rect(pymupdf.Rect(40, 135, 555, 215), color=(0.8, 0.85, 0.85), fill=(0.96, 0.98, 0.98))
    # Customer Info
    page.insert_text((55, 155), "ক্রেতার নাম (Customer):", fontfile=FONT_BN, fontsize=10, color=(0.3, 0.3, 0.3))
    page.insert_text((55, 175), "মেসার্স রহিম স্টোর (প্রো: মো: রহিম উদ্দিন)", fontfile=FONT_BN, fontsize=12, color=(0.05, 0.2, 0.2))
    page.insert_text((55, 192), "ঠিকানা: দোকান নং-১২, মিরপুর-১০ গোলচত্বর, ঢাকা", fontfile=FONT_BN, fontsize=9, color=(0.4, 0.4, 0.4))
    page.insert_text((55, 206), "মোবাইল: ০১৭০০-০০০০০১", fontfile=FONT_BN, fontsize=9, color=(0.4, 0.4, 0.4))

    # Invoice Info
    page.insert_text((360, 155), "ইনভয়েস নং (Invoice No):", fontfile=FONT_BN, fontsize=10, color=(0.3, 0.3, 0.3))
    page.insert_text((360, 175), "INV-2024-8891", fontsize=13, color=(0.06, 0.28, 0.38))
    page.insert_text((360, 192), "তারিখ (Date): ১৫ নভেম্বর ২০২৪", fontfile=FONT_BN, fontsize=10, color=(0.2, 0.2, 0.2))
    page.insert_text((360, 206), "পরিশোধের শর্ত: ৭ দিন (Credit Due)", fontfile=FONT_BN, fontsize=9, color=(0.7, 0.1, 0.1))

    # Table Header
    y_start = 230
    page.draw_rect(pymupdf.Rect(40, y_start, 555, y_start + 25), color=None, fill=(0.15, 0.25, 0.3))
    page.insert_text((50, y_start + 17), "নং", fontfile=FONT_BN, fontsize=10, color=(1, 1, 1))
    page.insert_text((85, y_start + 17), "পণ্যের বিবরণ (Description)", fontfile=FONT_BN, fontsize=10, color=(1, 1, 1))
    page.insert_text((310, y_start + 17), "পরিমাণ (Qty)", fontfile=FONT_BN, fontsize=10, color=(1, 1, 1))
    page.insert_text((395, y_start + 17), "দর (Unit Price)", fontfile=FONT_BN, fontsize=10, color=(1, 1, 1))
    page.insert_text((480, y_start + 17), "মোট টাকা (Total)", fontfile=FONT_BN, fontsize=10, color=(1, 1, 1))

    items = [
        ("১", "রূপচাঁদা খাঁটি সরিষার তেল (৫ লিটার জার)", "২০ কার্টন", "১,২০০ টাকা", "২৪,০০০.০০"),
        ("২", "প্রাণ প্রিমিয়াম মিনিকেট চাল (৫০ কেজি বস্তা)", "১০ বস্তা", "১,৫০০ টাকা", "১৫,০০০.০০"),
        ("৩", "অলিম্পিক এনার্জি প্লাস বিস্কুট (প্যাকেট)", "৫০ কার্টন", "১২০ টাকা", "৬,০০০.০০"),
    ]

    curr_y = y_start + 25
    for i, item in enumerate(items):
        bg = (0.97, 0.98, 0.99) if i % 2 == 1 else (1, 1, 1)
        page.draw_rect(pymupdf.Rect(40, curr_y, 555, curr_y + 35), color=(0.85, 0.88, 0.9), fill=bg)
        page.insert_text((52, curr_y + 22), item[0], fontfile=FONT_BN, fontsize=10, color=(0.2, 0.2, 0.2))
        page.insert_text((85, curr_y + 22), item[1], fontfile=FONT_BN, fontsize=10, color=(0.1, 0.1, 0.1))
        page.insert_text((320, curr_y + 22), item[2], fontfile=FONT_BN, fontsize=10, color=(0.2, 0.2, 0.2))
        page.insert_text((400, curr_y + 22), item[3], fontfile=FONT_BN, fontsize=10, color=(0.2, 0.2, 0.2))
        page.insert_text((485, curr_y + 22), item[4], fontfile=FONT_BN, fontsize=10, color=(0.1, 0.1, 0.1))
        curr_y += 35

    # Total Summary Box
    page.draw_rect(pymupdf.Rect(320, curr_y + 15, 555, curr_y + 70), color=(0.1, 0.35, 0.45), fill=(0.95, 0.98, 0.98), width=1.5)
    page.insert_text((335, curr_y + 40), "সর্বমোট পাওনা (Total Demand):", fontfile=FONT_BN, fontsize=11, color=(0.2, 0.2, 0.2))
    page.insert_text((440, curr_y + 60), "৳ ৪৫,০০০.০০", fontfile=FONT_BN, fontsize=16, color=(0.7, 0.1, 0.1))

    # Words in Bangla
    page.insert_text((45, curr_y + 45), "কথায় (In Words): পঁয়তাল্লিশ হাজার টাকা মাত্র।", fontfile=FONT_BN, fontsize=10, color=(0.3, 0.3, 0.3))

    # Terms & Signature
    page.insert_text((45, curr_y + 140), "শর্তাবলী: বিক্রিত মাল ৭ দিনের মধ্যে কোনো ত্রুটি থাকলে ফেরতযোগ্য।", fontfile=FONT_BN, fontsize=9, color=(0.5, 0.5, 0.5))
    page.draw_line(pymupdf.Point(400, curr_y + 180), pymupdf.Point(540, curr_y + 180), color=(0.4, 0.4, 0.4))
    page.insert_text((410, curr_y + 195), "অনুমোদিত স্বাক্ষর ও সিল", fontfile=FONT_BN, fontsize=10, color=(0.3, 0.3, 0.3))
    page.insert_text((405, curr_y + 210), "(মেসার্স কালাম ট্রেডার্স)", fontfile=FONT_BN, fontsize=9, color=(0.5, 0.5, 0.5))

    pdf_path = OUTPUT_DIR / "01_Supplier_Invoice_INV-8891.pdf"
    png_path = OUTPUT_DIR / "01_Supplier_Invoice_INV-8891.png"
    doc.save(str(pdf_path))
    pix = page.get_pixmap(dpi=150)
    pix.save(str(png_path))
    doc.close()
    print(f"Generated: {pdf_path} and {png_path}")


def create_bkash_receipt():
    """2. bKash Merchant Payment Receipt: BDT 20,000 from Rahim Store to Kalam Traders."""
    doc = pymupdf.open()
    page = doc.new_page(width=380, height=600)  # Smartphone slip size

    # bKash Pink Header
    page.draw_rect(pymupdf.Rect(20, 20, 360, 110), color=None, fill=(0.88, 0.10, 0.37))
    page.insert_text((40, 55), "bKash", fontsize=24, color=(1, 1, 1))
    page.insert_text((115, 55), "মার্চেন্ট পেমেন্ট", fontfile=FONT_BN, fontsize=14, color=(1, 1, 1))
    page.insert_text((40, 85), "পেমেন্ট সফল হয়েছে (Payment Successful)", fontfile=FONT_BN, fontsize=12, color=(1, 0.9, 0.95))
    page.insert_text((40, 100), "১৮ নভেম্বর ২০২৪, বিকাল ০৪:৩২", fontfile=FONT_BN, fontsize=9, color=(1, 0.9, 0.95))

    # Main Amount Display
    page.draw_rect(pymupdf.Rect(20, 125, 360, 210), color=(0.9, 0.9, 0.9), fill=(0.98, 0.98, 0.98))
    page.insert_text((130, 155), "প্রদেয় পরিমাণ (Amount)", fontfile=FONT_BN, fontsize=10, color=(0.5, 0.5, 0.5))
    page.insert_text((105, 192), "৳ ২০,০০০.০০", fontfile=FONT_BN, fontsize=24, color=(0.88, 0.10, 0.37))

    # Transaction Details Card
    y = 230
    page.draw_rect(pymupdf.Rect(20, y, 360, y + 250), color=(0.9, 0.9, 0.9), fill=(1, 1, 1))

    details = [
        ("মার্চেন্ট নাম (Merchant)", "মেসার্স কালাম ট্রেডার্স"),
        ("মার্চেন্ট অ্যাকাউন্ট (A/C)", "01711234567"),
        ("প্রেরক (Sender)", "রহিম স্টোর (01700000001)"),
        ("ট্রানজেকশন আইডি (TrxID)", "9K72JFL18A"),
        ("রেফারেন্স (Reference)", "INV-8891"),
        ("চার্জ (Fee)", "৳ 0.00"),
        ("নতুন ব্যালেন্স (New Balance)", "৳ ৪,৫৫০.০০"),
    ]

    for label, val in details:
        page.insert_text((35, y + 25), label, fontfile=FONT_BN, fontsize=9, color=(0.4, 0.4, 0.4))
        page.insert_text((190, y + 25), val, fontfile=FONT_BN, fontsize=10, color=(0.1, 0.1, 0.1))
        page.draw_line(pymupdf.Point(35, y + 33), pymupdf.Point(345, y + 33), color=(0.93, 0.93, 0.93))
        y += 33

    # Verification Note
    page.insert_text((55, 520), "এটি একটি ডিজিটাল ইলেকট্রনিক রসিদ। কোনো স্বাক্ষরের প্রয়োজন নেই।", fontfile=FONT_BN, fontsize=8, color=(0.6, 0.6, 0.6))

    pdf_path = OUTPUT_DIR / "02_Payment_Receipt_bKash_20k.pdf"
    png_path = OUTPUT_DIR / "02_Payment_Receipt_bKash_20k.png"
    doc.save(str(pdf_path))
    pix = page.get_pixmap(dpi=150)
    pix.save(str(png_path))
    doc.close()
    print(f"Generated: {pdf_path} and {png_path}")


def create_return_challan():
    """3. Damaged Goods Return Challan: BDT 5,000 accepted return to Kalam Traders."""
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=500)

    # Header
    page.draw_rect(pymupdf.Rect(40, 30, 555, 95), color=None, fill=(0.45, 0.15, 0.15))
    page.insert_text((60, 60), "ফেরত ও ড্যামেজ পণ্যের ক্রেডিট চালান", fontfile=FONT_BN, fontsize=18, color=(1, 1, 1))
    page.insert_text((60, 80), "RETURN & DAMAGE CREDIT MEMO | রহিম স্টোর -> কালাম ট্রেডার্স", fontfile=FONT_BN, fontsize=9, color=(0.95, 0.85, 0.85))

    # Challan Details
    page.draw_rect(pymupdf.Rect(40, 110, 555, 175), color=(0.85, 0.8, 0.8), fill=(0.99, 0.97, 0.97))
    page.insert_text((55, 132), "চালান নং (Return Challan): RET-552", fontfile=FONT_BN, fontsize=11, color=(0.2, 0.2, 0.2))
    page.insert_text((55, 150), "মূল ইনভয়েস সূত্র: INV-2024-8891", fontfile=FONT_BN, fontsize=10, color=(0.3, 0.3, 0.3))
    page.insert_text((55, 165), "ফেরতের কারণ: ভাঙা বোতল ও তেল লিকেজ", fontfile=FONT_BN, fontsize=10, color=(0.6, 0.1, 0.1))

    page.insert_text((350, 132), "তারিখ: ১৯ নভেম্বর ২০২৪", fontfile=FONT_BN, fontsize=10, color=(0.2, 0.2, 0.2))
    page.insert_text((350, 150), "গ্রহীতা: মেসার্স কালাম ট্রেডার্স", fontfile=FONT_BN, fontsize=10, color=(0.2, 0.2, 0.2))
    page.insert_text((350, 165), "প্রতিনিধি: মো: কালাম (ডেলিভারি ম্যান)", fontfile=FONT_BN, fontsize=10, color=(0.2, 0.2, 0.2))

    # Item Row
    y = 190
    page.draw_rect(pymupdf.Rect(40, y, 555, y + 25), color=None, fill=(0.3, 0.3, 0.3))
    page.insert_text((55, y + 17), "বিবরণ (Returned Item)", fontfile=FONT_BN, fontsize=10, color=(1, 1, 1))
    page.insert_text((280, y + 17), "পরিমাণ", fontfile=FONT_BN, fontsize=10, color=(1, 1, 1))
    page.insert_text((380, y + 17), "দর", fontfile=FONT_BN, fontsize=10, color=(1, 1, 1))
    page.insert_text((470, y + 17), "মোট ক্রেডিট", fontfile=FONT_BN, fontsize=10, color=(1, 1, 1))

    page.draw_rect(pymupdf.Rect(40, y + 25, 555, y + 65), color=(0.8, 0.8, 0.8), fill=(1, 1, 1))
    page.insert_text((55, y + 50), "রূপচাঁদা সরিষার তেল (ড্যামেজ কার্টন)", fontfile=FONT_BN, fontsize=10, color=(0.1, 0.1, 0.1))
    page.insert_text((290, y + 50), "৪ কার্টন", fontfile=FONT_BN, fontsize=10, color=(0.1, 0.1, 0.1))
    page.insert_text((385, y + 50), "১,২৫০ টাকা", fontfile=FONT_BN, fontsize=10, color=(0.1, 0.1, 0.1))
    page.insert_text((475, y + 50), "৳ ৫,০০০.০০", fontfile=FONT_BN, fontsize=11, color=(0.6, 0.1, 0.1))

    # Total Box
    page.draw_rect(pymupdf.Rect(340, y + 80, 555, y + 125), color=(0.45, 0.15, 0.15), fill=(0.98, 0.94, 0.94), width=1.5)
    page.insert_text((355, y + 105), "মোট সমন্বয়যোগ্য ক্রেডিট:", fontfile=FONT_BN, fontsize=10, color=(0.2, 0.2, 0.2))
    page.insert_text((455, y + 120), "৳ ৫,০০০.০০", fontfile=FONT_BN, fontsize=14, color=(0.6, 0.1, 0.1))

    # Delivery Representative Signature
    page.draw_line(pymupdf.Point(80, y + 160), pymupdf.Point(220, y + 160), color=(0.4, 0.4, 0.4))
    page.insert_text((85, y + 175), "মাল বুঝিয়া পাইলাম (স্বাক্ষর)", fontfile=FONT_BN, fontsize=9, color=(0.3, 0.3, 0.3))
    page.insert_text((85, y + 190), "মো: কালাম (ডেলিভারি প্রতিনিধি)", fontfile=FONT_BN, fontsize=8, color=(0.5, 0.5, 0.5))

    pdf_path = OUTPUT_DIR / "03_Return_Damage_Challan_5k.pdf"
    png_path = OUTPUT_DIR / "03_Return_Damage_Challan_5k.png"
    doc.save(str(pdf_path))
    pix = page.get_pixmap(dpi=150)
    pix.save(str(png_path))
    doc.close()
    print(f"Generated: {pdf_path} and {png_path}")


def create_cropped_unreadable_receipt():
    """5. Challenge 2: Cropped / Torn Unreadable Receipt Photo."""
    doc = pymupdf.open()
    page = doc.new_page(width=380, height=450)

    # Drawn to look like a scanned camera photo that is cropped or ripped
    page.draw_rect(pymupdf.Rect(20, 20, 360, 430), color=(0.7, 0.7, 0.7), fill=(0.96, 0.95, 0.92))
    page.insert_text((40, 55), "ক্যাশ মেমো ও মানি রসিদ", fontfile=FONT_BN, fontsize=16, color=(0.2, 0.2, 0.2))
    page.insert_text((40, 75), "জমা গ্রহণ রসিদ | মেসার্স কালাম ট্রেডার্স", fontfile=FONT_BN, fontsize=9, color=(0.4, 0.4, 0.4))

    page.insert_text((40, 110), "তারিখ: ২০ নভেম্বর ২০২৪", fontfile=FONT_BN, fontsize=10, color=(0.2, 0.2, 0.2))
    page.insert_text((40, 130), "গ্রাহক: রহিম স্টোর", fontfile=FONT_BN, fontsize=10, color=(0.2, 0.2, 0.2))
    page.insert_text((40, 150), "বাবদ: আংশিক বকেয়া বিল পরিশোধ", fontfile=FONT_BN, fontsize=10, color=(0.2, 0.2, 0.2))

    # The receipt amount is torn/blurred/missing
    page.draw_rect(pymupdf.Rect(40, 180, 330, 260), color=(0.8, 0.3, 0.3), fill=(0.9, 0.85, 0.8), stroke_opacity=0.5)
    page.insert_text((55, 210), "পরিশোধিত টাকার পরিমাণ: [ছেঁড়া / অস্পষ্ট]", fontfile=FONT_BN, fontsize=11, color=(0.7, 0.1, 0.1))
    page.insert_text((55, 235), "টাকার অঙ্ক ছেঁড়া থাকায় পড়া যাচ্ছে না...", fontfile=FONT_BN, fontsize=9, color=(0.5, 0.2, 0.2))

    # Big stamp: PHOTO CROPPED / DEFECTIVE
    page.draw_rect(pymupdf.Rect(40, 290, 340, 380), color=(0.7, 0.1, 0.1), fill=(1, 0.92, 0.92), width=2)
    page.insert_text((60, 325), "⚠️ ছবি আংশিক ছেঁড়া বা কাটা (CROPPED RECEIPT)", fontfile=FONT_BN, fontsize=10, color=(0.7, 0.1, 0.1))
    page.insert_text((60, 345), "Shongoti Rule: Never guess missing money amounts.", fontsize=8, color=(0.3, 0.3, 0.3))
    page.insert_text((60, 360), "Confidence capped at 59% (Needs Human Review).", fontsize=8, color=(0.3, 0.3, 0.3))

    png_path = OUTPUT_DIR / "05_Challenge2_Cropped_Unreadable_Receipt.png"
    pix = page.get_pixmap(dpi=150)
    pix.save(str(png_path))
    doc.close()
    print(f"Generated: {png_path}")


def create_multi_invoice_batch():
    """7. Challenge 1 & Direction: Statement with 3 Open Invoices for Lump-Sum Split."""
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=650)

    # Header
    page.draw_rect(pymupdf.Rect(40, 30, 555, 100), color=None, fill=(0.1, 0.2, 0.45))
    page.insert_text((60, 65), "বকেয়া ইনভয়েস বিবরণী ও লাম্প-সাম পেমেন্ট স্প্লিট", fontfile=FONT_BN, fontsize=18, color=(1, 1, 1))
    page.insert_text((60, 85), "SUPPLIER OPEN INVOICE LEDGER & PROPOSED SETTLEMENT SPLIT", fontsize=8, color=(0.85, 0.9, 1))

    # Context Card
    page.draw_rect(pymupdf.Rect(40, 115, 555, 170), color=(0.8, 0.85, 0.9), fill=(0.96, 0.97, 1))
    page.insert_text((55, 135), "সরবরাহকারী: মেসার্স কালাম ট্রেডার্স", fontfile=FONT_BN, fontsize=11, color=(0.1, 0.1, 0.3))
    page.insert_text((55, 155), "খুচরা ব্যবসায়ী: মেসার্স রহিম স্টোর", fontfile=FONT_BN, fontsize=11, color=(0.1, 0.1, 0.3))
    page.insert_text((330, 135), "মোট বকেয়া দাবি (Total Due): ৳ ৫০,০০০.০০", fontfile=FONT_BN, fontsize=11, color=(0.7, 0.1, 0.1))
    page.insert_text((330, 155), "মার্চেন্টের এককালীন পেমেন্ট (Lump Sum): ৳ ৩০,০০০.০০", fontfile=FONT_BN, fontsize=11, color=(0.05, 0.45, 0.2))

    # Table of open invoices
    y = 190
    page.draw_rect(pymupdf.Rect(40, y, 555, y + 25), color=None, fill=(0.2, 0.3, 0.5))
    page.insert_text((50, y + 17), "ইনভয়েস নং", fontfile=FONT_BN, fontsize=10, color=(1, 1, 1))
    page.insert_text((150, y + 17), "তারিখ (বকেয়া মেয়াদ)", fontfile=FONT_BN, fontsize=10, color=(1, 1, 1))
    page.insert_text((290, y + 17), "আসল পাওনা", fontfile=FONT_BN, fontsize=10, color=(1, 1, 1))
    page.insert_text((390, y + 17), "প্রস্তাবিত বরাদ্দ (Oldest-First)", fontfile=FONT_BN, fontsize=10, color=(1, 1, 1))
    page.insert_text((505, y + 17), "অবশিষ্ট বকেয়া", fontfile=FONT_BN, fontsize=10, color=(1, 1, 1))

    invoices = [
        ("INV-101", "০১ নভেম্বর ২০২৪ (মেয়াদোত্তীর্ণ)", "৳ ১৫,০০০.০০", "৳ ১৫,০০০.০০ (১০০% পরিশোধ)", "৳ ০.০০"),
        ("INV-102", "১০ নভেম্বর ২০২৪ (মেয়াদোত্তীর্ণ)", "৳ ২৫,০০০.০০", "৳ ১৫,০০০.০০ (আংশিক পরিশোধ)", "৳ ১০,০০০.০০"),
        ("INV-103", "২০ নভেম্বর ২০২৪ (চলতি মেয়াদ)", "৳ ১০,০০০.০০", "৳ ০.০০ (পরবর্তী কিস্তি)", "৳ ১০,০০০.০০"),
    ]

    curr_y = y + 25
    for inv in invoices:
        page.draw_rect(pymupdf.Rect(40, curr_y, 555, curr_y + 35), color=(0.85, 0.88, 0.92), fill=(1, 1, 1))
        page.insert_text((50, curr_y + 22), inv[0], fontsize=10, color=(0.1, 0.1, 0.1))
        page.insert_text((150, curr_y + 22), inv[1], fontfile=FONT_BN, fontsize=9, color=(0.3, 0.3, 0.3))
        page.insert_text((290, curr_y + 22), inv[2], fontfile=FONT_BN, fontsize=10, color=(0.1, 0.1, 0.1))
        page.insert_text((390, curr_y + 22), inv[3], fontfile=FONT_BN, fontsize=9, color=(0.05, 0.45, 0.2))
        page.insert_text((505, curr_y + 22), inv[4], fontfile=FONT_BN, fontsize=10, color=(0.6, 0.1, 0.1))
        curr_y += 35

    # Strategy Comparison Note
    curr_y += 20
    page.draw_rect(pymupdf.Rect(40, curr_y, 555, curr_y + 110), color=(0.2, 0.5, 0.3), fill=(0.95, 0.99, 0.95), width=1.5)
    page.insert_text((55, curr_y + 25), "🎯 Shongoti AI Split Proposal (চ্যালেঞ্জ ১ ও ডিরেকশন সমাধান):", fontfile=FONT_BN, fontsize=11, color=(0.05, 0.4, 0.15))
    page.insert_text((55, curr_y + 50), "• কৌশল ১ (Oldest First): সবচেয়ে পুরনো বিল INV-101 সম্পূর্ণ পরিশোধ (৳15k), বাকি ৳15k বরাদ্দ INV-102 এ।", fontfile=FONT_BN, fontsize=9.5, color=(0.2, 0.2, 0.2))
    page.insert_text((55, curr_y + 70), "• কৌশল ২ (Proportional Split): প্রতিটি ইনভয়েসে ৬০% হারে বরাদ্দ (INV-101: ৳9k, INV-102: ৳15k, INV-103: ৳6k)।", fontfile=FONT_BN, fontsize=9.5, color=(0.2, 0.2, 0.2))
    page.insert_text((55, curr_y + 90), "• গ্যারান্টি: কোনো ইনভয়েসে অতিরিক্ত বরাদ্দ বা ফ্লোটিং-পয়েন্ট ভগ্নাংশ থাকবে না। ১০০% ইন্টিজার পয়সা।", fontfile=FONT_BN, fontsize=9.5, color=(0.2, 0.2, 0.2))

    pdf_path = OUTPUT_DIR / "07_Challenge1_Multi_Invoice_LumpSum_Batch.pdf"
    png_path = OUTPUT_DIR / "07_Challenge1_Multi_Invoice_LumpSum_Batch.png"
    doc.save(str(pdf_path))
    pix = page.get_pixmap(dpi=150)
    pix.save(str(png_path))
    doc.close()
    print(f"Generated: {pdf_path} and {png_path}")


async def create_audio_and_text_messages():
    """4 & 6. Voice notes and text messages (Bangla speech via edge-tts)."""
    # 4. Standard Supplier Clarification
    text_clarification = (
        "রহিম ভাই, আসসালামু আলাইকুম। কালাম বলছিলাম। "
        "আপনার পাঠানো আগের ২০,০০০ টাকার বিকাশ পেমেন্ট পাইছি। "
        "কিন্তু ৫,০০০ টাকার ফেরত মালের ক্রেডিট এখনও হিসেবে বাদ দেই নাই। "
        "হিসাব মিলায়া বাকি টাকা দ্রুত পাঠায়ে দেন।"
    )
    txt_path_4 = OUTPUT_DIR / "04_Bangla_Supplier_Clarification.txt"
    with open(txt_path_4, "w", encoding="utf-8") as f:
        f.write(text_clarification)
    print(f"Generated: {txt_path_4}")

    audio_path_4 = OUTPUT_DIR / "04_Supplier_Audio_Voice_Note.mp3"
    comm_4 = edge_tts.Communicate(text_clarification, "bn-BD-PradeepNeural")
    await comm_4.save(str(audio_path_4))
    print(f"Generated: {audio_path_4}")

    # 6. Challenge 2: Contradictory Supplier SMS
    text_contradiction = (
        "মেসেজ ১ (২০ নভেম্বর, সকাল ১০:০০):\n"
        "\"রহিম ভাই, আপনার পাঠানো আগের ২০,০০০ টাকার পেমেন্ট পাইছি।\"\n\n"
        "মেসেজ ২ (২২ নভেম্বর, বিকাল ০৩:০০ - দ্বন্দ্বমূলক বার্তা):\n"
        "\"না না রহিম ভাই! খাতা চেক করে দেখলাম ওই ২০,০০০ টাকা তো পাই নাই! ওইটা অন্য কাস্টমারের পেমেন্ট ছিল। আপনার কোনো টাকা জমা হয় নাই!\"\n\n"
        "--- Shongoti Detection ---\n"
        "Status: CONFLICTED / CONTRADICTION DETECTED\n"
        "Action: Previous confirmation contradicted by supplier. Requires owner review."
    )
    txt_path_6 = OUTPUT_DIR / "06_Challenge2_Contradictory_Supplier_SMS.txt"
    with open(txt_path_6, "w", encoding="utf-8") as f:
        f.write(text_contradiction)
    print(f"Generated: {txt_path_6}")

    audio_path_6 = OUTPUT_DIR / "06_Challenge2_Contradictory_Voice.mp3"
    comm_6 = edge_tts.Communicate(
        "না না রহিম ভাই! খাতা চেক করে দেখলাম ওই ২০,০০০ টাকা তো পাই নাই! ওইটা অন্য কাস্টমারের পেমেন্ট ছিল। আপনার কোনো টাকা জমা হয় নাই!",
        "bn-BD-PradeepNeural",
    )
    await comm_6.save(str(audio_path_6))
    print(f"Generated: {audio_path_6}")


async def main():
    print("Generating demo document suite for Shongoti...")
    create_supplier_invoice()
    create_bkash_receipt()
    create_return_challan()
    create_cropped_unreadable_receipt()
    create_multi_invoice_batch()
    await create_audio_and_text_messages()
    print("\nAll demo documents generated in:", OUTPUT_DIR.resolve())


if __name__ == "__main__":
    asyncio.run(main())
