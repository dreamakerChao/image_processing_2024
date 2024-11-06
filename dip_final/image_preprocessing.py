from PIL import Image

def convert_to_8bit_rgb(input_path, output_path):
    # 打開 PNG 圖像
    image = Image.open(input_path)

    # 確保圖像為 8 位色深，並去掉 Alpha 通道
    if image.mode == 'RGBA':
        # 去掉 Alpha 通道並轉換為 RGB
        image = image.convert('RGB')
    elif image.mode == 'LA':
        # 如果是灰度圖像且帶有 Alpha 通道，先轉為 RGB
        image = image.convert('RGB')
    elif image.mode == 'P' or image.mode == 'L':
        # 如果是調色板或灰度圖像，轉換為 RGB
        image = image.convert('RGB')

    # 保存為 8 位色深的 RGB 格式 PNG
    image.save(output_path, format='PNG')
    print(f"Saved the 8-bit RGB image without alpha to {output_path}")

# 使用示例
input_path = './images/Lena.png'
output_path = './output_img/Lena_after.png'
convert_to_8bit_rgb(input_path, output_path)
