"""
Complete Demo Transaction Documents Generator for Shongoti Hackathon.
Uses pymupdf.TextWriter with Nirmala font for 100% visible, non-blank Bengali and English text.
Produces:
Set A: The Golden Case Matching the Live UI (মেসার্স হক ট্রেডার্স - চালান নং ৪১)
  1. Haque Traders Invoice #41 (৳25,000)
  2. Bank Deposit Slip (৳4,000)
  3. Goods Return Memo (৳3,000)
  4. Bangla SMS Clarification
Set B: The Commercial Grocery Case (মেসার্স কালাম ট্রেডার্স - INV-8891)
  5. Kalam Traders Wholesale Bill (৳45,000)
  6. bKash Merchant Slip (৳20,000)
  7. Damaged Goods Challan (৳5,000)
  8. Audio Clarification (MP3 + TXT)
Set C: Hackathon Challenges 1 & 2
  9. Challenge 2: Cropped / Unreadable Receipt (Honesty demonstration)
  10. Challenge 2: Contradictory Supplier SMS (Contradiction demonstration)
  11. Challenge 1: Multi-Invoice Statement with Lump-Sum Split Proposal (৳30,000 split across ৳50,000)
"""
import os
import asyncio
from pathlib import Path
import pymupdf
import edge_tts

OUTPUT_DIR = Path("demo_documents")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_FILE = "C:/Windows/Fonts/Nirmala.ttc"


class DocBuilder:
    def __init__(self, width=595, height=842):
        self.doc = pymupdf.open()
        self.page = self.doc.new_page(width=width, height=height)
        self.font = pymupdf.Font("nirmala", fontfile=FONT_FILE)

    def text(self, pos, s, fontsize=11, color=(0, 0, 0)):
        tw = pymupdf.TextWriter(self.page.rect)
        tw.append(pos, str(s), font=self.font, fontsize=fontsize)
        tw.write_text(self.page, color=color)

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
# SET A: MATCHES CURRENT UI GOLDEN CASE
# Supplier: মেসার্স হক ট্রেডার্স (চালান নং ৪১)
# Demand: ৳25,000 | Payment: ৳4,000 | Return: ৳3,000
# ==========================================

def create_haque_traders_invoice():
    b = DocBuilder(595, 842)

    # Header Box
    b.rect(pymupdf.Rect(40, 40, 555, 125), fill=(0.08, 0.25, 0.45))
    b.text((60, 75), "মেসার্স হক ট্রেডার্স (Haque Traders)", fontsize=22, color=(1, 1, 1))
    b.text((60, 95), "পাইকারি মুদি ও স্টেশনারি সরবরাহকারী | বাদামতলী ঘাট, ঢাকা-১১০০", fontsize=10, color=(0.85, 0.92, 1))
    b.text((60, 112), "মোবাইল: ০১৮১৯-৮৭৬৫৪৩ | ট্রেড লাইসেন্স নং: TRAD/DSCC/019284", fontsize=9, color=(0.75, 0.85, 0.95))

    # Badge
    b.rect(pymupdf.Rect(400, 55, 535, 100), fill=(0.15, 0.35, 0.6), color=(1, 1, 1), width=1.5)
    b.text((420, 77), "চালান ও বিল (ইনভয়েস)", fontsize=11, color=(1, 1, 1))
    b.text((435, 93), "INVOICE #41", fontsize=9, color=(1, 1, 1))

    # Details Box
    b.rect(pymupdf.Rect(40, 140, 555, 220), fill=(0.96, 0.98, 1), color=(0.8, 0.85, 0.9))
    b.text((55, 160), "ক্রেতার নাম:", fontsize=10, color=(0.4, 0.4, 0.4))
    b.text((125, 160), "মেসার্স রহিম স্টোর (Rahim Store)", fontsize=11, color=(0.1, 0.1, 0.2))
    b.text((55, 180), "ঠিকানা:", fontsize=10, color=(0.4, 0.4, 0.4))
    b.text((125, 180), "দোকান নং-১২, মিরপুর-১০, ঢাকা | মোবাইল: ০১৭০০-০০০০০১", fontsize=10, color=(0.2, 0.2, 0.2))

    b.text((360, 160), "চালান নং (Challan No):", fontsize=10, color=(0.4, 0.4, 0.4))
    b.text((475, 160), "চালান নং ৪১", fontsize=11, color=(0.08, 0.25, 0.45))
    b.text((360, 180), "তারিখ (Date):", fontsize=10, color=(0.4, 0.4, 0.4))
    b.text((475, 180), "১২ নভেম্বর ২০২৪", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((360, 200), "পরিশোধের মেয়াদ:", fontsize=10, color=(0.4, 0.4, 0.4))
    b.text((475, 200), "বকেয়া (Due: 7 Days)", fontsize=10, color=(0.7, 0.1, 0.1))

    # Table Header
    y = 235
    b.rect(pymupdf.Rect(40, y, 555, y + 25), fill=(0.15, 0.25, 0.4))
    b.text((50, y + 17), "নং", fontsize=10, color=(1, 1, 1))
    b.text((85, y + 17), "পণ্যের বিবরণ (Description)", fontsize=10, color=(1, 1, 1))
    b.text((300, y + 17), "পরিমাণ (Qty)", fontsize=10, color=(1, 1, 1))
    b.text((390, y + 17), "দর (Unit Price)", fontsize=10, color=(1, 1, 1))
    b.text((480, y + 17), "মোট টাকা", fontsize=10, color=(1, 1, 1))

    items = [
        ("১", "তীর সয়াবিন তেল (৫ লিটার বোতল)", "১০ কার্টন", "১,২০০ টাকা", "১২,০০০.০০"),
        ("২", "চাষী চিনিগুঁড়া সুগন্ধি চাল (২৫ কেজি)", "৪ বস্তা", "২,০০০ টাকা", "৮,০০০.০০"),
        ("৩", "ড্যানিশ কনডেন্সড মিল্ক (টিন)", "২ কার্টন", "২,৫০০ টাকা", "৫,০০০.০০"),
    ]

    curr_y = y + 25
    for i, it in enumerate(items):
        bg = (0.97, 0.98, 1) if i % 2 == 1 else (1, 1, 1)
        b.rect(pymupdf.Rect(40, curr_y, 555, curr_y + 35), fill=bg, color=(0.85, 0.88, 0.92))
        b.text((55, curr_y + 22), it[0], fontsize=10, color=(0.2, 0.2, 0.2))
        b.text((85, curr_y + 22), it[1], fontsize=10, color=(0.1, 0.1, 0.1))
        b.text((310, curr_y + 22), it[2], fontsize=10, color=(0.2, 0.2, 0.2))
        b.text((395, curr_y + 22), it[3], fontsize=10, color=(0.2, 0.2, 0.2))
        b.text((485, curr_y + 22), it[4], fontsize=10, color=(0.1, 0.1, 0.1))
        curr_y += 35

    # Total Due Box
    b.rect(pymupdf.Rect(320, curr_y + 15, 555, curr_y + 75), fill=(0.95, 0.97, 1), color=(0.08, 0.25, 0.45), width=1.5)
    b.text((335, curr_y + 40), "মহাজনের মোট দাবি (Claimed Due):", fontsize=11, color=(0.2, 0.2, 0.2))
    b.text((435, curr_y + 65), "৳ ২৫,০০০.০০", fontsize=18, color=(0.7, 0.1, 0.1))

    b.text((45, curr_y + 45), "কথায়: পঁচিশ হাজার টাকা মাত্র।", fontsize=10, color=(0.3, 0.3, 0.3))
    b.text((45, curr_y + 65), "স্টেটাস: বকেয়া পাওনা (Unpaid Demand)", fontsize=10, color=(0.6, 0.1, 0.1))

    # Signature
    b.line(pymupdf.Point(400, curr_y + 170), pymupdf.Point(540, curr_y + 170))
    b.text((415, curr_y + 185), "অনুমোদিত প্রতিনিধি স্বাক্ষর", fontsize=9, color=(0.3, 0.3, 0.3))
    b.text((420, curr_y + 200), "মেসার্স হক ট্রেডার্স", fontsize=9, color=(0.5, 0.5, 0.5))

    b.save("SetA_01_Haque_Traders_Invoice_41_Tk25k")


def create_haque_payment_slip():
    b = DocBuilder(420, 580)

    # Header Box
    b.rect(pymupdf.Rect(25, 25, 395, 105), fill=(0.1, 0.45, 0.3))
    b.text((45, 60), "ইসলামী ব্যাংক বাংলাদেশ পিএলসি", fontsize=18, color=(1, 1, 1))
    b.text((45, 80), "অনলাইন ক্যাশ ডিপোজিট স্লিপ (Deposit Slip)", fontsize=10, color=(0.9, 1, 0.95))
    b.text((45, 96), "শাখা: মিরপুর শাখা, ঢাকা | ট্রানজেকশন সফল", fontsize=9, color=(0.8, 0.95, 0.85))

    # Amount Card
    b.rect(pymupdf.Rect(25, 120, 395, 205), fill=(0.95, 0.99, 0.96), color=(0.8, 0.9, 0.85))
    b.text((145, 150), "জমার পরিমাণ (Deposited Amount)", fontsize=10, color=(0.3, 0.5, 0.4))
    b.text((130, 185), "৳ ৪,০০০.০০", fontsize=24, color=(0.1, 0.45, 0.3))

    # Details
    y = 220
    b.rect(pymupdf.Rect(25, y, 395, y + 240), fill=(1, 1, 1), color=(0.85, 0.9, 0.88))

    details = [
        ("প্রাপকের হিসাব (A/C Name):", "মেসার্স হক ট্রেডার্স (Haque Traders)"),
        ("হিসাব নং (A/C Number):", "2050148020198765"),
        ("জমাকারী (Depositor):", "রহিম স্টোর (মো: রহিম উদ্দিন)"),
        ("রেফারেন্স (Reference):", "চালান নং ৪১ (Challan 41)"),
        ("তারিখ ও সময়:", "১৪ নভেম্বর ২০২৪, দুপুর ১২:১৫"),
        ("ভাউচার নং (Voucher No):", "IBBL-DEP-994182"),
        ("কথায়:", "চার হাজার টাকা মাত্র"),
    ]

    for label, val in details:
        b.text((40, y + 25), label, fontsize=9, color=(0.4, 0.4, 0.4))
        b.text((170, y + 25), val, fontsize=9.5, color=(0.1, 0.1, 0.1))
        b.line(pymupdf.Point(40, y + 33), pymupdf.Point(380, y + 33), color=(0.92, 0.94, 0.92))
        y += 33

    b.text((45, 480), "ব্যাংক কর্মকর্তা সিল ও স্বাক্ষর: [VERIFIED CASH DEPOSIT]", fontsize=8, color=(0.3, 0.5, 0.3))
    b.text((45, 495), "নোট: এটি আমাদের পূর্বের পরিশোধিত ৪,০০০ টাকা যা দাবির সাথে সমন্বয়যোগ্য।", fontsize=8, color=(0.5, 0.5, 0.5))

    b.save("SetA_02_Bank_Deposit_Slip_Tk4k")


def create_haque_return_memo():
    b = DocBuilder(520, 450)

    # Header Box
    b.rect(pymupdf.Rect(30, 30, 490, 95), fill=(0.55, 0.15, 0.15))
    b.text((50, 60), "পণ্য ফেরত চালান (Goods Return Memo)", fontsize=18, color=(1, 1, 1))
    b.text((50, 80), "ক্রেতা: রহিম স্টোর  ->  সরবরাহকারী: মেসার্স হক ট্রেডার্স", fontsize=10, color=(0.95, 0.85, 0.85))

    # Meta
    b.rect(pymupdf.Rect(30, 110, 490, 175), fill=(0.99, 0.96, 0.96), color=(0.85, 0.8, 0.8))
    b.text((45, 132), "ফেরত চালান নং: RET-41-01", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((45, 150), "মূল চালানের সূত্র: চালান নং ৪১", fontsize=10, color=(0.55, 0.15, 0.15))
    b.text((45, 165), "ফেরতের কারণ: ভাঙা টিন ও মেয়াদোত্তীর্ণ পণ্য", fontsize=9.5, color=(0.4, 0.4, 0.4))

    b.text((310, 132), "তারিখ: ১৬ নভেম্বর ২০২৪", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((310, 150), "গ্রহীতা প্রতিনিধি: হক ট্রেডার্স ডেলিভারি", fontsize=10, color=(0.2, 0.2, 0.2))

    # Table
    y = 190
    b.rect(pymupdf.Rect(30, y, 490, y + 25), fill=(0.25, 0.25, 0.25))
    b.text((45, y + 17), "বিবরণ (Returned Item)", fontsize=9.5, color=(1, 1, 1))
    b.text((250, y + 17), "পরিমাণ", fontsize=9.5, color=(1, 1, 1))
    b.text((340, y + 17), "দর", fontsize=9.5, color=(1, 1, 1))
    b.text((420, y + 17), "মোট ক্রেডিট", fontsize=9.5, color=(1, 1, 1))

    b.rect(pymupdf.Rect(30, y + 25, 490, y + 60), fill=(1, 1, 1), color=(0.8, 0.8, 0.8))
    b.text((45, y + 48), "ড্যানিশ কনডেন্সড মিল্ক (ড্যামেজ টিন)", fontsize=9.5, color=(0.1, 0.1, 0.1))
    b.text((260, y + 48), "২৪ টিন", fontsize=9.5, color=(0.1, 0.1, 0.1))
    b.text((345, y + 48), "১২৫ টাকা", fontsize=9.5, color=(0.1, 0.1, 0.1))
    b.text((425, y + 48), "৳ ৩,০০০.০০", fontsize=10.5, color=(0.6, 0.1, 0.1))

    # Total
    b.rect(pymupdf.Rect(280, y + 75, 490, y + 120), fill=(0.98, 0.94, 0.94), color=(0.55, 0.15, 0.15), width=1.5)
    b.text((295, y + 98), "মোট ফেরত সমন্বয়:", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((400, y + 112), "৳ ৩,০০০.০০", fontsize=14, color=(0.6, 0.1, 0.1))

    # Signature
    b.line(pymupdf.Point(60, y + 155), pymupdf.Point(200, y + 155))
    b.text((65, y + 170), "মাল বুঝিয়া পাইলাম (হক ট্রেডার্স প্রতিনিধি)", fontsize=8.5, color=(0.3, 0.3, 0.3))

    b.save("SetA_03_Goods_Return_Memo_Tk3k")


def create_haque_sms_clarification():
    text = (
        "মেসার্স হক ট্রেডার্স (মহাজনের বার্তা):\n"
        "তারিখ: ১৮ নভেম্বর ২০২৪\n\n"
        "\"রহিম ভাই, আপনার ৪,০০০ টাকার ব্যাংক জমা পাইছি এবং খাতায় জমা দিয়েছি। "
        "কিন্তু ৩,০০০ টাকার ফেরত মালপত্র এখনও আমার গোডাউন ম্যানেজার যাচাই করে খাতায় বাদ দেয় নাই। "
        "তাই মোট ২৫,০০০ থেকে ৪,০০০ বাদ দিয়ে আপাতত ২১,০০০ টাকা পাঠান। ফেরত মাল নিশ্চিত হলে বাকি ৩,০০০ সমন্বয় করব।\"\n\n"
        "--- Shongoti AI Reconciliation Result ---\n"
        "Hypothesis Isolated: REC-003 (Payment Included, Return Excluded)\n"
        "Calculation: ৳25,000 (Demand) - ৳4,000 (Payment) = ৳21,000\n"
        "Remaining Question: 'whether accepted return of ৳3,000 is included in current demand'"
    )
    path = OUTPUT_DIR / "SetA_04_Haque_Traders_Bangla_Clarification.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Generated: {path.name}")


# ==========================================
# SET B: WHOLESALE GROCERY INVOICE CASE
# Supplier: কালাম ট্রেডার্স (INV-2024-8891)
# Demand: ৳45,000 | bKash: ৳20,000 | Return: ৳5,000
# ==========================================

def create_kalam_invoice():
    b = DocBuilder(595, 842)

    # Header
    b.rect(pymupdf.Rect(40, 40, 555, 125), fill=(0.06, 0.28, 0.38))
    b.text((60, 75), "মেসার্স কালাম ট্রেডার্স (Kalam Traders)", fontsize=22, color=(1, 1, 1))
    b.text((60, 95), "পাইকারি পরিবেশক ও সরবরাহকারী | হোলসেল মার্কেট, চকবাজার, ঢাকা-১২১১", fontsize=10, color=(0.85, 0.95, 0.9))
    b.text((60, 112), "মোবাইল: ০১৭১১-২৩৪৫৬৭ | ইমেইল: kalamtraders.bd@gmail.com", fontsize=9, color=(0.75, 0.88, 0.85))

    b.rect(pymupdf.Rect(400, 55, 535, 100), fill=(0.1, 0.35, 0.45), color=(1, 1, 1), width=1.5)
    b.text((420, 77), "বিক্রয় চালান ও বিল", fontsize=12, color=(1, 1, 1))
    b.text((425, 93), "INV-2024-8891", fontsize=9, color=(1, 1, 1))

    # Meta
    b.rect(pymupdf.Rect(40, 140, 555, 220), fill=(0.96, 0.98, 0.98), color=(0.8, 0.85, 0.85))
    b.text((55, 160), "ক্রেতার নাম:", fontsize=10, color=(0.3, 0.3, 0.3))
    b.text((130, 160), "মেসার্স রহিম স্টোর (প্রো: মো: রহিম উদ্দিন)", fontsize=11, color=(0.05, 0.2, 0.2))
    b.text((55, 180), "ঠিকানা:", fontsize=10, color=(0.3, 0.3, 0.3))
    b.text((130, 180), "দোকান নং-১২, মিরপুর-১০ গোলচত্বর, ঢাকা | ০১৭০০-০০০০০১", fontsize=9.5, color=(0.4, 0.4, 0.4))

    b.text((360, 160), "ইনভয়েস নং:", fontsize=10, color=(0.3, 0.3, 0.3))
    b.text((450, 160), "INV-2024-8891", fontsize=11, color=(0.06, 0.28, 0.38))
    b.text((360, 180), "তারিখ (Date):", fontsize=10, color=(0.3, 0.3, 0.3))
    b.text((450, 180), "১৫ নভেম্বর ২০২৪", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((360, 200), "পরিশোধের শর্ত:", fontsize=10, color=(0.3, 0.3, 0.3))
    b.text((450, 200), "৭ দিন (বকেয়া ক্রেডিট)", fontsize=10, color=(0.7, 0.1, 0.1))

    # Items Table
    y = 235
    b.rect(pymupdf.Rect(40, y, 555, y + 25), fill=(0.15, 0.25, 0.3))
    b.text((50, y + 17), "নং", fontsize=10, color=(1, 1, 1))
    b.text((85, y + 17), "পণ্যের বিবরণ (Description)", fontsize=10, color=(1, 1, 1))
    b.text((310, y + 17), "পরিমাণ (Qty)", fontsize=10, color=(1, 1, 1))
    b.text((395, y + 17), "দর (Unit Price)", fontsize=10, color=(1, 1, 1))
    b.text((480, y + 17), "মোট টাকা", fontsize=10, color=(1, 1, 1))

    items = [
        ("১", "রূপচাঁদা খাঁটি সরিষার তেল (৫ লিটার জার)", "২০ কার্টন", "১,২০০ টাকা", "২৪,০০০.০০"),
        ("২", "প্রাণ প্রিমিয়াম মিনিকেট চাল (৫০ কেজি বস্তা)", "১০ বস্তা", "১,৫০০ টাকা", "১৫,০০০.০০"),
        ("৩", "অলিম্পিক এনার্জি প্লাস বিস্কুট (প্যাকেট)", "৫০ কার্টন", "১২০ টাকা", "৬,০০০.০০"),
    ]

    curr_y = y + 25
    for i, it in enumerate(items):
        bg = (0.97, 0.98, 0.99) if i % 2 == 1 else (1, 1, 1)
        b.rect(pymupdf.Rect(40, curr_y, 555, curr_y + 35), fill=bg, color=(0.85, 0.88, 0.9))
        b.text((55, curr_y + 22), it[0], fontsize=10, color=(0.2, 0.2, 0.2))
        b.text((85, curr_y + 22), it[1], fontsize=10, color=(0.1, 0.1, 0.1))
        b.text((320, curr_y + 22), it[2], fontsize=10, color=(0.2, 0.2, 0.2))
        b.text((400, curr_y + 22), it[3], fontsize=10, color=(0.2, 0.2, 0.2))
        b.text((485, curr_y + 22), it[4], fontsize=10, color=(0.1, 0.1, 0.1))
        curr_y += 35

    # Total
    b.rect(pymupdf.Rect(320, curr_y + 15, 555, curr_y + 75), fill=(0.95, 0.98, 0.98), color=(0.1, 0.35, 0.45), width=1.5)
    b.text((335, curr_y + 40), "সর্বমোট পাওনা (Total Demand):", fontsize=11, color=(0.2, 0.2, 0.2))
    b.text((440, curr_y + 65), "৳ ৪৫,০০০.০০", fontsize=18, color=(0.7, 0.1, 0.1))

    b.text((45, curr_y + 45), "কথায়: পঁয়তাল্লিশ হাজার টাকা মাত্র।", fontsize=10, color=(0.3, 0.3, 0.3))

    b.line(pymupdf.Point(400, curr_y + 170), pymupdf.Point(540, curr_y + 170))
    b.text((415, curr_y + 185), "অনুমোদিত স্বাক্ষর ও সিল", fontsize=9, color=(0.3, 0.3, 0.3))
    b.text((410, curr_y + 200), "(মেসার্স কালাম ট্রেডার্স)", fontsize=9, color=(0.5, 0.5, 0.5))

    b.save("SetB_01_Kalam_Traders_Invoice_INV-8891_Tk45k")


def create_bkash_slip():
    b = DocBuilder(380, 580)

    # Header
    b.rect(pymupdf.Rect(20, 20, 360, 110), fill=(0.88, 0.10, 0.37))
    b.text((40, 55), "bKash", fontsize=24, color=(1, 1, 1))
    b.text((120, 55), "মার্চেন্ট পেমেন্ট", fontsize=14, color=(1, 1, 1))
    b.text((40, 85), "পেমেন্ট সফল হয়েছে (Payment Successful)", fontsize=11, color=(1, 0.9, 0.95))
    b.text((40, 100), "১৮ নভেম্বর ২০২৪, বিকাল ০৪:৩২", fontsize=9, color=(1, 0.9, 0.95))

    # Amount
    b.rect(pymupdf.Rect(20, 125, 360, 210), fill=(0.98, 0.98, 0.98), color=(0.9, 0.9, 0.9))
    b.text((130, 155), "প্রদেয় পরিমাণ (Amount)", fontsize=10, color=(0.5, 0.5, 0.5))
    b.text((105, 192), "৳ ২০,০০০.০০", fontsize=24, color=(0.88, 0.10, 0.37))

    y = 230
    b.rect(pymupdf.Rect(20, y, 360, y + 240), fill=(1, 1, 1), color=(0.9, 0.9, 0.9))

    details = [
        ("মার্চেন্ট নাম (Merchant):", "মেসার্স কালাম ট্রেডার্স"),
        ("মার্চেন্ট নম্বর (A/C):", "01711234567"),
        ("প্রেরক (Sender):", "রহিম স্টোর (01700000001)"),
        ("ট্রানজেকশন আইডি:", "9K72JFL18A"),
        ("রেফারেন্স (Ref):", "INV-8891"),
        ("চার্জ (Fee):", "৳ 0.00"),
        ("পেমেন্ট চ্যানেল:", "bKash Business App"),
    ]

    for label, val in details:
        b.text((35, y + 25), label, fontsize=9, color=(0.4, 0.4, 0.4))
        b.text((180, y + 25), val, fontsize=9.5, color=(0.1, 0.1, 0.1))
        b.line(pymupdf.Point(35, y + 33), pymupdf.Point(345, y + 33), color=(0.93, 0.93, 0.93))
        y += 33

    b.text((55, 500), "এটি একটি ডিজিটাল ইলেকট্রনিক রসিদ। কোনো স্বাক্ষরের প্রয়োজন নেই।", fontsize=8, color=(0.6, 0.6, 0.6))

    b.save("SetB_02_bKash_Payment_Receipt_Tk20k")


def create_kalam_return():
    b = DocBuilder(520, 450)

    b.rect(pymupdf.Rect(30, 30, 490, 95), fill=(0.45, 0.15, 0.15))
    b.text((50, 60), "ফেরত ও ড্যামেজ পণ্যের চালান", fontsize=18, color=(1, 1, 1))
    b.text((50, 80), "RETURN MEMO | রহিম স্টোর -> মেসার্স কালাম ট্রেডার্স", fontsize=9.5, color=(0.95, 0.85, 0.85))

    b.rect(pymupdf.Rect(30, 110, 490, 175), fill=(0.99, 0.97, 0.97), color=(0.85, 0.8, 0.8))
    b.text((45, 132), "চালান নং: RET-552", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((45, 150), "মূল ইনভয়েস সূত্র: INV-2024-8891", fontsize=10, color=(0.3, 0.3, 0.3))
    b.text((45, 165), "ফেরতের কারণ: ভাঙা বোতল ও তেল লিকেজ", fontsize=9.5, color=(0.6, 0.1, 0.1))

    b.text((310, 132), "তারিখ: ১৯ নভেম্বর ২০২৪", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((310, 150), "গ্রহীতা প্রতিনিধি: কালাম (ডেলিভারি ম্যান)", fontsize=10, color=(0.2, 0.2, 0.2))

    y = 190
    b.rect(pymupdf.Rect(30, y, 490, y + 25), fill=(0.3, 0.3, 0.3))
    b.text((45, y + 17), "বিবরণ (Returned Item)", fontsize=9.5, color=(1, 1, 1))
    b.text((250, y + 17), "পরিমাণ", fontsize=9.5, color=(1, 1, 1))
    b.text((340, y + 17), "দর", fontsize=9.5, color=(1, 1, 1))
    b.text((420, y + 17), "মোট ক্রেডিট", fontsize=9.5, color=(1, 1, 1))

    b.rect(pymupdf.Rect(30, y + 25, 490, y + 60), fill=(1, 1, 1), color=(0.8, 0.8, 0.8))
    b.text((45, y + 48), "রূপচাঁদা সরিষার তেল (ড্যামেজ কার্টন)", fontsize=9.5, color=(0.1, 0.1, 0.1))
    b.text((260, y + 48), "৪ কার্টন", fontsize=9.5, color=(0.1, 0.1, 0.1))
    b.text((345, y + 48), "১,২৫০ টাকা", fontsize=9.5, color=(0.1, 0.1, 0.1))
    b.text((425, y + 48), "৳ ৫,০০০.০০", fontsize=10.5, color=(0.6, 0.1, 0.1))

    b.rect(pymupdf.Rect(280, y + 75, 490, y + 120), fill=(0.98, 0.94, 0.94), color=(0.45, 0.15, 0.15), width=1.5)
    b.text((295, y + 98), "মোট সমন্বয়যোগ্য ক্রেডিট:", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((400, y + 112), "৳ ৫,০০০.০০", fontsize=14, color=(0.6, 0.1, 0.1))

    b.line(pymupdf.Point(60, y + 155), pymupdf.Point(200, y + 155))
    b.text((65, y + 170), "মাল বুঝিয়া পাইলাম (কালাম ট্রেডার্স ডেলিভারি)", fontsize=8.5, color=(0.3, 0.3, 0.3))

    b.save("SetB_03_Damage_Return_Challan_Tk5k")


# ==========================================
# SET C: HACKATHON CHALLENGES 1 & 2
# ==========================================

def create_cropped_receipt():
    b = DocBuilder(380, 450)

    b.rect(pymupdf.Rect(20, 20, 360, 430), fill=(0.96, 0.95, 0.92), color=(0.7, 0.7, 0.7))
    b.text((40, 55), "ক্যাশ মেমো ও মানি রসিদ (Cash Memo)", fontsize=16, color=(0.2, 0.2, 0.2))
    b.text((40, 75), "জমা গ্রহণ রসিদ | মেসার্স কালাম ট্রেডার্স", fontsize=9, color=(0.4, 0.4, 0.4))

    b.text((40, 110), "তারিখ: ২০ নভেম্বর ২০২৪", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((40, 130), "গ্রাহক: রহিম স্টোর", fontsize=10, color=(0.2, 0.2, 0.2))
    b.text((40, 150), "বাবদ: আংশিক বকেয়া বিল পরিশোধ", fontsize=10, color=(0.2, 0.2, 0.2))

    # Torn amount box
    b.rect(pymupdf.Rect(40, 180, 330, 260), fill=(0.92, 0.85, 0.8), color=(0.8, 0.3, 0.3))
    b.text((55, 210), "পরিশোধিত টাকার পরিমাণ: [ছেঁড়া / অস্পষ্ট অংশ]", fontsize=10.5, color=(0.7, 0.1, 0.1))
    b.text((55, 235), "রসিদের নিচের অংশ ছেঁড়া থাকায় টাকার অঙ্ক দেখা যাচ্ছে না...", fontsize=9, color=(0.5, 0.2, 0.2))

    # Stamp
    b.rect(pymupdf.Rect(35, 290, 345, 385), fill=(1, 0.92, 0.92), color=(0.7, 0.1, 0.1), width=2.0)
    b.text((50, 320), "⚠️ ছবি আংশিক ছেঁড়া বা কাটা (CROPPED RECEIPT)", fontsize=10, color=(0.7, 0.1, 0.1))
    b.text((50, 340), "Shongoti Rule: Never guess or hallucinate missing money.", fontsize=8.5, color=(0.3, 0.3, 0.3))
    b.text((50, 355), "Confidence Capped: 59% (Needs Owner Review)", fontsize=8.5, color=(0.3, 0.3, 0.3))
    b.text((50, 370), "Status: missing_fact = 'eligible_payment.amount_paisa'", fontsize=8, color=(0.6, 0.1, 0.1))

    b.save("SetC_01_Challenge2_Cropped_Unreadable_Receipt")


def create_lump_sum_split_statement():
    b = DocBuilder(595, 650)

    b.rect(pymupdf.Rect(40, 30, 555, 100), fill=(0.1, 0.2, 0.45))
    b.text((60, 65), "বকেয়া ইনভয়েস বিবরণী ও লাম্প-সাম পেমেন্ট স্প্লিট", fontsize=18, color=(1, 1, 1))
    b.text((60, 85), "SUPPLIER OPEN INVOICES & PROPOSED SETTLEMENT SPLIT", fontsize=8.5, color=(0.85, 0.9, 1))

    # Meta
    b.rect(pymupdf.Rect(40, 115, 555, 170), fill=(0.96, 0.97, 1), color=(0.8, 0.85, 0.9))
    b.text((55, 135), "সরবরাহকারী: মেসার্স কালাম ট্রেডার্স", fontsize=11, color=(0.1, 0.1, 0.3))
    b.text((55, 155), "খুচরা ব্যবসায়ী: মেসার্স রহিম স্টোর", fontsize=11, color=(0.1, 0.1, 0.3))
    b.text((330, 135), "মোট বকেয়া দাবি (Total Due): ৳ ৫০,০০০.০০", fontsize=11, color=(0.7, 0.1, 0.1))
    b.text((330, 155), "এককালীন পেমেন্ট (Lump-Sum): ৳ ৩০,০০০.০০", fontsize=11, color=(0.05, 0.45, 0.2))

    # Table
    y = 190
    b.rect(pymupdf.Rect(40, y, 555, y + 25), fill=(0.2, 0.3, 0.5))
    b.text((50, y + 17), "ইনভয়েস নং", fontsize=10, color=(1, 1, 1))
    b.text((140, y + 17), "তারিখ (বকেয়া মেয়াদ)", fontsize=10, color=(1, 1, 1))
    b.text((280, y + 17), "আসল দাবি", fontsize=10, color=(1, 1, 1))
    b.text((375, y + 17), "প্রস্তাবিত বরাদ্দ (Oldest-First)", fontsize=10, color=(1, 1, 1))
    b.text((495, y + 17), "অবশিষ্ট বকেয়া", fontsize=10, color=(1, 1, 1))

    invoices = [
        ("INV-101", "০১ নভেম্বর ২০২৪ (মেয়াদোত্তীর্ণ)", "৳ ১৫,০০০.০০", "৳ ১৫,০০০.০০ (১০০% পরিশোধ)", "৳ ০.০০"),
        ("INV-102", "১০ নভেম্বর ২০২৪ (মেয়াদোত্তীর্ণ)", "৳ ২৫,০০০.০০", "৳ ১৫,০০০.০০ (আংশিক পরিশোধ)", "৳ ১০,০০০.০০"),
        ("INV-103", "২০ নভেম্বর ২০২৪ (চলতি মেয়াদ)", "৳ ১০,০০০.০০", "৳ ০.০০ (পরবর্তী কিস্তি)", "৳ ১০,০০০.০০"),
    ]

    curr_y = y + 25
    for inv in invoices:
        b.rect(pymupdf.Rect(40, curr_y, 555, curr_y + 35), fill=(1, 1, 1), color=(0.85, 0.88, 0.92))
        b.text((50, curr_y + 22), inv[0], fontsize=10, color=(0.1, 0.1, 0.1))
        b.text((140, curr_y + 22), inv[1], fontsize=9, color=(0.3, 0.3, 0.3))
        b.text((280, curr_y + 22), inv[2], fontsize=10, color=(0.1, 0.1, 0.1))
        b.text((375, curr_y + 22), inv[3], fontsize=9, color=(0.05, 0.45, 0.2))
        b.text((495, curr_y + 22), inv[4], fontsize=10, color=(0.6, 0.1, 0.1))
        curr_y += 35

    curr_y += 20
    b.rect(pymupdf.Rect(40, curr_y, 555, curr_y + 115), fill=(0.95, 0.99, 0.95), color=(0.2, 0.5, 0.3), width=1.5)
    b.text((55, curr_y + 25), "🎯 Shongoti AI Split Proposal (চ্যালেঞ্জ ১ ও ডিরেকশন সমাধান):", fontsize=11, color=(0.05, 0.4, 0.15))
    b.text((55, curr_y + 50), "• কৌশল ১ (Oldest First): সবচেয়ে পুরনো বিল INV-101 সম্পূর্ণ পরিশোধ (৳15k), বাকি ৳15k বরাদ্দ INV-102 এ।", fontsize=9.5, color=(0.2, 0.2, 0.2))
    b.text((55, curr_y + 70), "• কৌশল ২ (Proportional Split): প্রতিটি ইনভয়েসে ৬০% হারে বরাদ্দ (INV-101: ৳9k, INV-102: ৳15k, INV-103: ৳6k)।", fontsize=9.5, color=(0.2, 0.2, 0.2))
    b.text((55, curr_y + 90), "• গ্যারান্টি: কোনো ইনভয়েসে অতিরিক্ত বরাদ্দ বা ফ্লোটিং-পয়েন্ট ভগ্নাংশ থাকবে না। ১০০% ইন্টিজার পয়সা।", fontsize=9.5, color=(0.2, 0.2, 0.2))

    b.save("SetC_02_Challenge1_Multi_Invoice_LumpSum_Batch")


async def create_audio_files():
    kalam_text = (
        "রহিম ভাই, আসসালামু আলাইকুম। কালাম বলছিলাম। "
        "আপনার পাঠানো আগের ২০,০০০ টাকার বিকাশ পেমেন্ট পাইছি। "
        "কিন্তু ৫,০০০ টাকার ফেরত মালের ক্রেডিট এখনও হিসেবে বাদ দেই নাই। "
        "হিসাব মিলায়া বাকি টাকা দ্রুত পাঠায়ে দেন।"
    )
    p4 = OUTPUT_DIR / "SetB_04_Kalam_Supplier_Clarification.mp3"
    comm = edge_tts.Communicate(kalam_text, "bn-BD-PradeepNeural")
    await comm.save(str(p4))
    print(f"Generated: {p4.name}")

    contra_text = (
        "না না রহিম ভাই! খাতা চেক করে দেখলাম ওই ২০,০০০ টাকা তো পাই নাই! "
        "ওইটা অন্য কাস্টমারের পেমেন্ট ছিল। আপনার কোনো টাকা জমা হয় নাই!"
    )
    p6 = OUTPUT_DIR / "SetC_03_Challenge2_Contradictory_Voice.mp3"
    comm2 = edge_tts.Communicate(contra_text, "bn-BD-PradeepNeural")
    await comm2.save(str(p6))
    print(f"Generated: {p6.name}")


async def main():
    print("=== Generating 100% Legible Non-Blank Demo Transaction Documents ===")
    create_haque_traders_invoice()
    create_haque_payment_slip()
    create_haque_return_memo()
    create_haque_sms_clarification()

    create_kalam_invoice()
    create_bkash_slip()
    create_kalam_return()

    create_cropped_receipt()
    create_lump_sum_split_statement()
    await create_audio_files()
    print("\nAll files successfully generated with zero blank glyphs!")


if __name__ == "__main__":
    asyncio.run(main())
