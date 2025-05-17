import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
import cv2
import pyzbar.pyzbar as pyzbar
import warnings
import ctypes

def verify_qr_code(image_path, expected_data):
    """驗證QR碼的輔助函數"""
    try:
        # 使用ctypes來處理底層錯誤
        ERROR_HANDLER = ctypes.CFUNCTYPE(None, ctypes.c_char_p)(lambda x: None)
        
        test_image = cv2.imread(image_path)
        if test_image is None:
            return False, "無法讀取QR碼圖片"
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            decoded_objects = pyzbar.decode(test_image)
            
        if not decoded_objects:
            return False, "QR碼可能無法被正確識別"
            
        decoded_data = decoded_objects[0].data.decode('utf-8')
        if expected_data not in decoded_data:
            return False, "QR碼內容可能不完整"
            
        return True, "成功"
    except Exception as e:
        return False, f"驗證過程發生錯誤: {str(e)}"

def generate_qrcode(code, name, spec, unit, output_dir):
    """生成QR碼並在下方添加完整文字（置中對齊）"""
    try:
        # 準備QR碼內容
        qr_data = f"編碼:{code}|品名:{name}|規格:{spec}|單位:{unit}"
        
        qr = qrcode.QRCode(
            version=None,  # 自動選擇最小的版本
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # 提高容錯率
            box_size=12,  # 增加方塊大小
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # 將QR碼轉換為PIL圖像
        qr_image = qr_image.convert('RGB')
        
        # 使用默認字體
        try:
            # 嘗試使用微軟正黑體（如果系統中有的話）
            info_font = ImageFont.truetype("msjh.ttc", 30)  # 信息文字字體
        except:
            # 如果沒有找到指定字體，使用默認字體
            info_font = ImageFont.load_default()
        
        # 準備要顯示的文字
        info_text = f"編碼:{code}\n品名:{name}\n規格:{spec}\n單位:{unit}"
        
        # 創建臨時繪圖對象來計算文字尺寸
        temp_draw = ImageDraw.Draw(qr_image)
        info_bbox = temp_draw.multiline_textbbox((0, 0), info_text, font=info_font, align="center")
        
        info_w = info_bbox[2] - info_bbox[0]
        info_h = info_bbox[3] - info_bbox[1]
        
        # 獲取QR碼尺寸
        qr_w, qr_h = qr_image.size
        
        # 計算新圖片的尺寸
        padding = 20
        new_width = max(qr_w, info_w) + padding * 2
        new_height = qr_h + info_h + padding * 3
        
        # 創建新的白色背景圖片
        new_image = Image.new('RGB', (new_width, new_height), 'white')
        
        # 計算各元素的位置
        qr_x = (new_width - qr_w) // 2
        qr_y = padding
        
        # 計算文字的中心位置
        info_x = (new_width - info_w) // 2
        info_y = qr_h + padding * 2
        
        # 將QR碼貼到新圖片上
        new_image.paste(qr_image, (qr_x, qr_y))
        
        # 在新圖片上創建繪圖對象
        draw = ImageDraw.Draw(new_image)
        
        # 繪製信息文字（置中對齊）
        draw.multiline_text((info_x, info_y), info_text, font=info_font, fill="black", align="center")
        
        # 保存為高質量圖片
        filename = os.path.join(output_dir, f"qrcode_{code}.png")
        new_image.save(filename, "PNG", quality=95, optimize=False)
        
        # 驗證QR碼
        success, message = verify_qr_code(filename, qr_data)
        if not success:
            print(f"警告: QR碼 {code} - {message}")
        
        return filename
    except Exception as e:
        print(f"生成 QR碼 {code} 時發生錯誤: {str(e)}")
        return None

def merge_images_to_pdf(image_dir, output_pdf, items_per_page=4):
    print("正在將QR碼合併為PDF...")
    """將目錄中的所有PNG圖片合併成一個PDF文件
    
    Args:
        image_dir: 包含PNG圖片的目錄路徑
        output_pdf: 輸出PDF文件的路徑
        items_per_page: 每頁顯示的圖片數量，默認為4（2x2排列）
    """
    # 獲取所有PNG文件並按編號排序
    png_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]
    png_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    
    if not png_files:
        print("沒有找到PNG文件")
        return
    
    # 讀取第一張圖片來獲取尺寸
    first_image = Image.open(os.path.join(image_dir, png_files[0]))
    img_width, img_height = first_image.size
    
    # 設定PDF頁面大小（A4）
    a4_width = 2480  # 約210mm at 300dpi
    a4_height = 3508  # 約297mm at 300dpi
    
    # 計算縮放比例和間距
    margin = 150  # 增加頁面邊距
    spacing = 100  # 增加圖片之間的間距
    cols = 2  # 每行圖片數
    rows = 2  # 每列圖片數
    
    # 計算縮放後的圖片尺寸
    scaled_width = (a4_width - 2 * margin - spacing * (cols - 1)) // cols
    scaled_height = (a4_height - 2 * margin - spacing * (rows - 1)) // rows
    
    # 保持縱橫比
    scale = min(scaled_width / img_width, scaled_height / img_height)
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    
    # 創建PDF頁面
    pdf_pages = []
    
    for i in range(0, len(png_files), items_per_page):
        # 創建新的空白頁面
        page = Image.new('RGB', (a4_width, a4_height), 'white')
        
        # 在頁面上放置圖片
        for j, png_file in enumerate(png_files[i:i + items_per_page]):
            # 計算在頁面上的位置
            row = j // cols
            col = j % cols
            
            # 計算中心對齊的位置
            x = margin + col * (new_width + spacing) + (scaled_width - new_width) // 2
            y = margin + row * (new_height + spacing) + (scaled_height - new_height) // 2
            
            # 打開並縮放圖片
            img = Image.open(os.path.join(image_dir, png_file))
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 貼上圖片
            page.paste(img, (x, y))
        
        pdf_pages.append(page)
    
    # 保存為PDF
    if pdf_pages:
        pdf_pages[0].save(
            output_pdf,
            save_all=True,
            append_images=pdf_pages[1:],
            resolution=300
        )
        print(f"PDF文件已保存至: {output_pdf}")
    else:
        print("沒有生成PDF頁面")