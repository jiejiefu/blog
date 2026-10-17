import os
from PIL import Image, ImageDraw, ImageFont

def add_anti_theft_watermark(input_image_path, output_image_path, text="© Unauthorised Use Prohibited"):
    # 1. 讀取圖片並轉為 RGBA 模式（才能處理透明度）
    img = Image.open(input_image_path).convert("RGBA")
    width, height = img.size
    
    # 2. 建立一個與原圖一樣大的透明圖層用來畫浮水印
    watermark_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_layer)
    
    # 3. 設定字型與大小（Mac 內建有 Helvetica 或 Arial，可自行替換路徑）
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(width * 0.025))
    except IOError:
        font = ImageFont.load_default()
        
    # 使用 font.getbbox() 獲取文字寬高
    text_bbox = draw.textstring_bbox((0, 0), text, font=font) if hasattr(draw, 'textstring_bbox') else font.getbbox(text)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # 4. 以網格狀（Grid）在透明圖層上寫滿文字，間距為文字寬高的 1.5 倍
    x_spacing = int(text_width * 1.5)
    y_spacing = int(text_height * 3.0)
    
    # 故意將範圍擴大，確保旋轉後邊角也能被字蓋到
    for x in range(-width, width * 2, x_spacing):
        for y in range(-height, height * 2, y_spacing):
            # 設定顏色與透明度：(紅, 綠, 藍, 透明度) 
            # 透明度 35 (範圍0-255) 呈現若隱若現的灰色，極難被 AI 完整去背
            draw.text((x, y), text, font=font, fill=(200, 200, 200, 35))
            
    # 5. 將浮水印圖層旋轉 45 度（增加修圖難度）
    watermark_layer = watermark_layer.rotate(45, resample=Image.BICUBIC)
    
    # 6. 將原圖與浮水印圖層合併
    final_img = Image.alpha_composite(img, watermark_layer)
    
    # 7. 轉回 RGB 並儲存（若原圖是 PNG 可直接存為 RGBA）
    final_img.convert("RGB").save(output_image_path, "JPEG", quality=90)
    print(f"成功生成防盜圖片：{output_image_path}")


# 使用範例
# add_anti_theft_watermark("my_photo.jpg", "protected_photo.jpg", "© 2026 MyName Mini Studio")

"""
這是一份為你量身打造的專業級全螢幕網格防盜浮水印腳本。此腳本結合了工程級的防錯設計、跨平台字型自動適配、命令列參數（argparse）完整支援，以及資料夾批次處理與絕對不覆蓋原檔的安全防呆機制。

網格狀且半透明（Opacity 35）旋轉 45 度的設計，能夠有效抵抗現代 AI 圖像修復與去背工具的清除嘗試。

💻 完整 Python 腳本 (anti_theft_watermark.py)
請建立一個名為 anti_theft_watermark.py 的檔案，並貼入以下程式碼：

🚀 指令操作範例指南
使用終端機執行此腳本時，支援以下豐富的參數代入方式：

1. 處理單張圖片（使用預設文字與同路徑防覆蓋輸出）
Bash

python anti_theft_watermark.py -i my_photo.jpg
- 結果：會在同一個資料夾下自動生成 my_photo_protected.jpg，絕對不會覆蓋原圖。
- 
2. 自訂浮水印文字與透明度（單張）
Bash

python anti_theft_watermark.py -i images/sample.png -t "© 2026 MyStudio - Strictly Confidential" --opacity 45
3. 批次處理整個資料夾（指定特定副檔名如 .png）
Bash

python anti_theft_watermark.py -i ./raw_photos --ext .png .jpg -t "© Proprietary Asset"
- 說明：腳本會掃描 ./raw_photos 內所有符合 .png 與 .jpg 的圖片，並自動在同路徑產出對應的保護後檔案。
- 
4. 批次處理並指定輸出到另一個資料夾
Bash

python anti_theft_watermark.py -i ./raw_photos -o ./protected_output -t "© 2026 Protected"
💡 工程亮點解析
- 跨平台字型容錯：內建 get_system_font 函式，會自動依序偵測 macOS (Helvetica.ttc)、Windows (arial.ttf) 或 Linux 的常見字型路徑，若找不到會自動降級為 Pillow 內建預設字型，不會因系統環境不同而報錯。
- 
- 絕對防覆蓋防呆：get_safe_output_path 會比對絕對路徑。若輸入與輸出檔名相撞，會自動加上 _protected 或 _protected_new 字尾。
- 
- 動態網格計算：利用 font.getbbox() 精確測量文字寬高，並以 1.5 倍字寬、3.0 倍字高作網格間距，再透過 45 度旋轉撐滿整張圖的對角線死角。
"""
import os
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def get_system_font(font_size):
    """跨平台自動尋找可用字型，若找不到則回退至系統預設字型"""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "/Library/Fonts/Arial.ttf",              # macOS / Windows
        "C:\\Windows\\Fonts\\arial.ttf",         # Windows
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" # Linux
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, font_size)
            except Exception:
                continue
    return ImageFont.load_default()

def add_anti_theft_watermark(input_image_path, output_image_path, text="© Unauthorised Use Prohibited", opacity=35, angle=45):
    """單張圖片加上防盜網格浮水印核心函式"""
    try:
        # 1. 讀取圖片並轉為 RGBA 模式（才能處理透明度）
        img = Image.open(input_image_path).convert("RGBA")
        width, height = img.size
        
        # 2. 建立一個與原圖一樣大的透明圖層用來畫浮水印
        watermark_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        # 3. 設定字型與大小（動態計算比例）
        font_size = int(width * 0.025)
        font = get_system_font(font_size)
        
        # 獲取文字寬高
        text_bbox = font.getbbox(text) if hasattr(font, 'getbbox') else draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # 4. 以網格狀（Grid）在透明圖層上寫滿文字
        x_spacing = int(text_width * 1.5)
        y_spacing = int(text_height * 3.0)
        
        # 故意將範圍擴大，確保旋轉後邊角也能被字蓋到
        for x in range(-width, width * 2, x_spacing):
            for y in range(-height, height * 2, y_spacing):
                # 設定顏色與透明度：(紅, 綠, 藍, 透明度)
                draw.text((x, y), text, font=font, fill=(128, 128, 128, opacity))
                
        # 5. 將浮水印圖層旋轉指定角度（預設 45 度）
        watermark_layer = watermark_layer.rotate(angle, resample=Image.BICUBIC)
        
        # 6. 將原圖與浮水印圖層合併
        final_img = Image.alpha_composite(img, watermark_layer)
        
        # 7. 根據副檔名安全儲存
        ext = os.path.splitext(output_image_path)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            final_img.convert("RGB").save(output_image_path, "JPEG", quality=95)
        else:
            final_img.save(output_image_path)
            
        print(f"[成功] 防盜圖片已生成：{output_image_path}")
        return True
    except Exception as e:
        print(f"[錯誤] 處理圖片 {input_image_path} 失敗: {e}")
        return False

def get_safe_output_path(input_path, output_arg=None):
    """確保輸出路徑安全，預設同路徑且絕對不覆蓋原檔"""
    input_p = Path(input_path)
    
    if output_arg:
        output_p = Path(output_arg)
        if output_p.is_dir():
            output_p = output_p / f"{input_p.stem}_protected{input_p.suffix}"
    else:
        # 預設同路徑，加上 _protected 字尾避免覆蓋
        output_p = input_p.parent / f"{input_p.stem}_protected{input_p.suffix}"
        
    # 如果路徑不幸與原檔完全相同，自動加上流水號字尾
    if output_p.resolve() == input_p.resolve():
        output_p = input_p.parent / f"{input_p.stem}_protected_new{input_p.suffix}"
        
    return str(output_p)

def main():
    parser = argparse.ArgumentParser(description="專業級 Python 網格全螢幕防盜浮水印工具")
    parser.add_argument("-i", "--input", required=True, help="輸入的圖片檔案路徑或資料夾路徑")
    parser.add_argument("-o", "--output", help="輸出的圖片檔案路徑或資料夾路徑（預設同路徑，自動防覆蓋）")
    parser.add_argument("-t", "--text", default="© Unauthorised Use Prohibited", help="浮水印文字內容")
    parser.add_argument("--opacity", type=int, default=50, help="浮水印透明度 (0-255，預設 50)")
    parser.add_argument("--angle", type=int, default=45, help="浮水印旋轉角度（預設 45）")
    parser.add_argument("--ext", nargs="+", default=[".jpg", ".jpeg", ".png", ".webp"], help="處理資料夾時支援的副檔名列表")
    
    args = parser.parse_args()
    input_path = Path(args.input)
    
    # 模式 A：單張圖片處理
    if input_path.is_file():
        output_path = get_safe_output_path(input_path, args.output)
        add_anti_theft_watermark(str(input_path), output_path, args.text, args.opacity, args.angle)
        
    # 模式 B：整個資料夾批次處理
    elif input_path.is_dir():
        output_dir = Path(args.output) if args.output else input_path
        output_dir.mkdir(parents=True, exist_ok=True)
        
        supported_exts = tuple(e.lower() for e in args.ext)
        files = [f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() in supported_exts]
        
        if not files:
            print(f"[提示] 在資料夾 {input_path} 中找不到指定的副檔名檔案 ({args.ext})。")
            return
            
        print(f"[*] 開始批量處理資料夾，共找到 {len(files)} 張符合的圖片...")
        success_count = 0
        for file_path in files:
            if args.output:
                out_file = output_dir / f"{file_path.stem}_protected{file_path.suffix}"
            else:
                out_file = file_path.parent / f"{file_path.stem}_protected{file_path.suffix}"
            
            # 防覆蓋防呆檢查
            if out_file.resolve() == file_path.resolve():
                out_file = file_path.parent / f"{file_path.stem}_protected_new{file_path.suffix}"
                
            if add_anti_theft_watermark(str(file_path), str(out_file), args.text, args.opacity, args.angle):
                success_count += 1
                
        print(f"[✨] 批次處理完成！成功處理 {success_count} / {len(files)} 張圖片。")
    else:
        print(f"[錯誤] 輸入的路徑不存在或不合法：{args.input}")

if __name__ == "__main__":
    main()