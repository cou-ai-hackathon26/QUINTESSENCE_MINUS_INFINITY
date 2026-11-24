import os
from PIL import Image, ImageDraw, ImageFont

font_dir = 'C:/Windows/Fonts/'
f_title = ImageFont.truetype(font_dir + 'arialbd.ttf', 24)
f_h2 = ImageFont.truetype(font_dir + 'arialbd.ttf', 18)
f_bold = ImageFont.truetype(font_dir + 'arialbd.ttf', 15)
f_reg = ImageFont.truetype(font_dir + 'arial.ttf', 15)
f_small = ImageFont.truetype(font_dir + 'arial.ttf', 12)

os.makedirs('demo_evidence', exist_ok=True)

# 1. Cropped invoice where amount and bottom total are cropped off
img_crop = Image.new('RGB', (650, 420), color='#FDFDFD')
draw = ImageDraw.Draw(img_crop)

# Border with torn/crop effect at bottom
draw.rectangle([(10, 10), (640, 410)], outline='#CCCCCC', width=1)
draw.rectangle([(15, 15), (635, 75)], fill='#2D3748')
draw.text((30, 25), "RAHMAN TRADERS", fill='#FFFFFF', font=f_title)
draw.text((30, 52), "Wholesale and Commission Agent - Dilkusha C/A, Dhaka", fill='#E2E8F0', font=f_small)

draw.text((30, 95), "BILL TO:", fill='#718096', font=f_small)
draw.text((30, 115), "Mina Store (Judge Workspace)", fill='#1A202C', font=f_bold)
draw.text((30, 135), "Shop #4, Karwan Bazar, Dhaka", fill='#4A5568', font=f_reg)

draw.text((420, 95), "MEMO / CHALLAN DETAILS:", fill='#718096', font=f_small)
draw.text((420, 115), "Invoice Ref: INV-101", fill='#1A202C', font=f_bold)
draw.text((420, 135), "Date: 24-Nov-2026", fill='#4A5568', font=f_reg)

# Table Header
draw.rectangle([(25, 175), (625, 205)], fill='#EDF2F7')
draw.text((35, 182), "Item Description", fill='#2D3748', font=f_bold)
draw.text((320, 182), "Quantity", fill='#2D3748', font=f_bold)
draw.text((440, 182), "Unit Price", fill='#2D3748', font=f_bold)
draw.text((540, 182), "Amount", fill='#2D3748', font=f_bold)

# Table Rows
rows = [
    ("1. ACI Pure Salt 1kg Pack", "50 Bags", "BDT 38.00", "BDT 1,900.00"),
    ("2. Teer Fortified Soybean Oil 5L", "10 Cans", "BDT 850.00", "BDT 8,500.00"),
    ("3. Miniket Premium Rice 50kg", "5 Sacks", "BDT 3,400.00", "BDT 17,000.00"),
]
y = 215
for item, qty, price, amt in rows:
    draw.text((35, y), item, fill='#1A202C', font=f_reg)
    draw.text((320, y), qty, fill='#1A202C', font=f_reg)
    draw.text((440, y), price, fill='#1A202C', font=f_reg)
    draw.text((540, y), amt, fill='#1A202C', font=f_reg)
    y += 28

# Notice indicating crop / tear
draw.line([(15, 335), (635, 335)], fill='#E2E8F0', width=1)
draw.rectangle([(15, 345), (635, 405)], fill='#FFF5F5')
draw.text((35, 355), "[ PHOTO CROPPED HERE - BOTTOM SECTION TORN & UNREADABLE ]", fill='#E53E3E', font=f_bold)
draw.text((35, 380), "Total Payable / Signature / Paid Amount: [NOT VISIBLE / CUT OFF]", fill='#C53030', font=f_reg)

img_crop.save('demo_evidence/cropped_challan_unreadable.png')
print('Created demo_evidence/cropped_challan_unreadable.png')

# 2. Contradictory Supplier WhatsApp Message
img_chat = Image.new('RGB', (650, 480), color='#ECE5DD')
d_chat = ImageDraw.Draw(img_chat)

# Header
d_chat.rectangle([(0, 0), (650, 70)], fill='#075E54')
d_chat.ellipse([(20, 15), (60, 55)], fill='#25D366')
d_chat.text((33, 20), "R", fill='#FFFFFF', font=f_title)
d_chat.text((75, 18), "Rahman Traders (Supplier)", fill='#FFFFFF', font=f_h2)
d_chat.text((75, 42), "online · WhatsApp Business", fill='#D1E7DD', font=f_small)

# Bubble 1 (Earlier message context)
d_chat.rectangle([(30, 95), (550, 185)], fill='#FFFFFF')
d_chat.text((45, 105), "Rahman Traders", fill='#075E54', font=f_bold)
d_chat.text((45, 128), "Salam bhai, as per previous talk, INV-101 was BDT 3,000.", fill='#202124', font=f_reg)
d_chat.text((45, 150), "Pls send payment soon.", fill='#202124', font=f_reg)
d_chat.text((480, 165), "09:15 AM", fill='#8C8C8C', font=f_small)

# Bubble 2 (New contradictory reply)
d_chat.rectangle([(30, 205), (610, 375)], fill='#FFFFFF')
d_chat.text((45, 215), "Rahman Traders", fill='#075E54', font=f_bold)
d_chat.text((45, 240), "Wait bhai! Big mistake in earlier message!!", fill='#D93025', font=f_bold)
d_chat.text((45, 268), "I just re-checked our ledger book with accountant.", fill='#202124', font=f_reg)
d_chat.text((45, 292), "For Invoice INV-101, net balance is actually BDT 4,500 (not 3,000).", fill='#B31B1B', font=f_bold)
d_chat.text((45, 318), "Please correct your records: INV-101 due amount is BDT 4,500.", fill='#202124', font=f_reg)
d_chat.text((45, 342), "Do not pay 3,000. Balance is 4,500 BDT.", fill='#202124', font=f_reg)
d_chat.text((540, 355), "10:30 AM", fill='#8C8C8C', font=f_small)

# Bottom input bar
d_chat.rectangle([(0, 420), (650, 480)], fill='#F0F0F0')
d_chat.rectangle([(20, 430), (560, 470)], fill='#FFFFFF', outline='#E0E0E0')
d_chat.text((35, 442), "Type a message...", fill='#9E9E9E', font=f_reg)

img_chat.save('demo_evidence/supplier_message_contradictory.png')
print('Created demo_evidence/supplier_message_contradictory.png')
