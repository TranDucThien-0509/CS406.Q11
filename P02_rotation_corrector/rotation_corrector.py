import os
import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Import custom modules
from utils.common import get_list_file_in_folder
from utils.visualize import viz_icdar
from predict import init_box_rectify_model
from utils.utils import rotate_image_bbox_angle
from filter import drop_box, get_mean_horizontal_angle, filter_90_box
from utils.line_angle_correction import rotate_and_crop

def get_boxes_data(img_data, boxes):
    boxes_data = []
    for box_data in boxes:
        if isinstance(box_data, dict):
            box_loc = box_data['coors']
        else:
            box_loc = box_data
        box_loc = np.array(box_loc).astype(np.int32).reshape(-1, 1, 2)
        box_data = rotate_and_crop(
            img_data, box_loc, debug=False, extend=True,
            extend_x_ratio=0.0001,
            extend_y_ratio=0.0001,
            min_extend_y=2, min_extend_x=1
        )
        boxes_data.append(box_data)
    return boxes_data

def calculate_page_orient(box_rectify, img_rotated, boxes_list):
    boxes_data = get_boxes_data(img_rotated, boxes_list)
    rotation_state = {'0': 0, '180': 0}
    for it, img in enumerate(boxes_data):
        _, degr = box_rectify.inference(img, debug=False)
        rotation_state[degr[0]] += 1
    print(rotation_state)
    
    if np.abs(rotation_state['180'] - rotation_state['0']) > 8:
        ret = 180
    else:
        ret = 0
    return ret

def get_list_boxes_from_icdar(anno_path):
    with open(anno_path, 'r', encoding='utf-8') as f:
        anno_txt = f.readlines()
    list_boxes = []
    for anno in anno_txt:
        anno = anno.rstrip('\n')

        idx = -1
        for i in range(0, 8):
            idx = anno.find(',', idx + 1)

        coordinates = anno[:idx]
        coors = [int(f) for f in coordinates.split(',')]
        list_boxes.append({'coors': coors, 'data': anno[idx:]})
    return list_boxes

def write_output(list_boxes, result_file_path):
    result = ''
    for idx, box_data in enumerate(list_boxes):
        if isinstance(box_data, dict):
            box = box_data['coors']
            s = [str(i) for i in box]
            line = ','.join(s) + box_data['data']
        else:
            box = box_data
            s = [str(i) for i in box]
            line = ','.join(s) + ','
        result += line + '\n'
    result = result.rstrip('\n')
    with open(result_file_path, 'w', encoding='utf8') as res:
        res.write(result)

def main():
    # --- CẤU HÌNH ĐƯỜNG DẪN VÀ THAM SỐ ---
    img_dir     = r'C:\Users\Admin\Desktop\CS406 - Final Project\Dataset_Splitted\train'
    anno_dir    = r'C:\Users\Admin\Desktop\CS406 - Final Project\Solution_1\data\text_detector\train\txt'

    output_txt_dir          = r'C:\Users\Admin\Desktop\CS406 - Final Project\Solution_1\data\rotation_corrector\train\txt'
    output_viz_dir          = r'C:\Users\Admin\Desktop\CS406 - Final Project\Solution_1\data\rotation_corrector\train\viz_imgs'
    output_rotated_img_dir  = r'C:\Users\Admin\Desktop\CS406 - Final Project\Solution_1\data\rotation_corrector\train\imgs'
    weight_path             = r'C:\Users\Admin\Desktop\CS406 - Final Project\Solution_1\p02_rotation_corrector\mobilenetv3-Epoch-487-Loss-0.03-Acc-0.99.pth'

    rot_drop_thresh = [.5, 2]
    write_rotated_img = True
    write_file = True
    visualize = True

    # --- TẠO THƯ MỤC NẾU CHƯA TỒN TẠI ---
    os.makedirs(output_txt_dir, exist_ok=True)
    os.makedirs(output_viz_dir, exist_ok=True)
    os.makedirs(output_rotated_img_dir, exist_ok=True)

    # --- KHỞI TẠO MODEL VÀ DANH SÁCH ẢNH ---
    # Khởi tạo model dựa trên hàm đã được import
    box_rectify = init_box_rectify_model(weight_path) 
    
    # Lấy danh sách ảnh (Sử dụng hàm của hệ điều hành hoặc hàm get_list_file_in_folder của bạn)
    list_img_path = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    
    # --- VÒNG LẶP XỬ LÝ CHÍNH ---
    begin = time.time()
    for idx, img_name in enumerate(list_img_path[504:]):
        print('\n', f'[{idx}/{len(list_img_path[504:])}] Inference {img_name}')
        
        # 1. Tải ảnh Gốc (Ảnh A)
        img_path = os.path.join(img_dir, img_name)
        test_img = cv2.imread(img_path)
        if test_img is None:
            print(f"Không thể đọc ảnh: {img_path}")
            continue
        img_original = test_img.copy() 

        # Detect text boxes and rotate image to correct skewed angle
        begin_detector = time.time()
        anno_path = os.path.join(anno_dir, img_name.replace('.jpg', '.txt'))
        
        if not os.path.exists(anno_path):
            print(f"Không tìm thấy file annotation: {anno_path}")
            continue

        # Lấy boxes
        boxes_list = get_list_boxes_from_icdar(anno_path)
        boxes_list_original = boxes_list.copy()

        boxes_list = drop_box(boxes_list, drop_gap=rot_drop_thresh)
        rotation = get_mean_horizontal_angle(boxes_list, False)
        print('Góc xoay trung bình:', rotation)
        
        # 2. Xoay theo góc trung bình (Ảnh B)
        img_rotated_skew, boxes_list_skew = rotate_image_bbox_angle(test_img, boxes_list.copy(), rotation)
        
        # Sử dụng ảnh xoay theo góc nghiêng để tính toán góc lật
        degre = calculate_page_orient(box_rectify, img_rotated_skew, boxes_list_skew)
        print('Góc xoay theo model Effi:', degre)
        
        # 3. Xoay theo model Effi (Ảnh C)
        img_rotated_final, boxes_list_final = rotate_image_bbox_angle(img_rotated_skew, boxes_list_skew.copy(), degre)
        
        # Cập nhật boxes_list cho bước lưu kết quả
        boxes_list = filter_90_box(boxes_list_final)
        
        end_detector = time.time()
        print('Thời gian xoay ảnh:', round(end_detector - begin_detector, 4), 'giây.')
        
        # --- HIỂN THỊ 4 ẢNH TRONG SUBPLOT ---
        # 4. Ảnh đè Boxes List (Ảnh D)
        img_with_boxes = img_rotated_final.copy()
        if boxes_list:
            for box_data in boxes_list:
                if isinstance(box_data, dict):
                    box = np.array(box_data['coors']).reshape((-1, 1, 2)).astype(np.int32)
                else:
                    box = np.array(box_data).reshape((-1, 1, 2)).astype(np.int32)
                cv2.polylines(img_with_boxes, [box], isClosed=True, color=(255, 0, 0), thickness=2)

        # Chuyển ảnh từ BGR sang RGB để Matplotlib hiển thị
        img_original_rgb = cv2.cvtColor(img_original, cv2.COLOR_BGR2RGB)
        img_rotated_skew_rgb = cv2.cvtColor(img_rotated_skew, cv2.COLOR_BGR2RGB)
        img_rotated_final_rgb = cv2.cvtColor(img_rotated_final, cv2.COLOR_BGR2RGB)
        img_with_boxes_rgb = cv2.cvtColor(img_with_boxes, cv2.COLOR_BGR2RGB)

        plt.figure(figsize=(15, 8))
        plt.suptitle(f'Kết quả xử lý ảnh: {img_name}', fontsize=16)

        plt.subplot(2, 2, 1)
        plt.imshow(img_original_rgb)
        plt.title('1. Ảnh Gốc', fontsize=12)
        plt.axis('off')

        plt.subplot(2, 2, 2)
        plt.imshow(img_rotated_skew_rgb)
        plt.title(f'2. Xoay theo Góc Trung bình ({round(rotation, 2)}°)', fontsize=12)
        plt.axis('off')

        plt.subplot(2, 2, 3)
        plt.imshow(img_rotated_final_rgb)
        plt.title(f'3. Xoay theo Model Effi ({degre}°)', fontsize=12)
        plt.axis('off')

        plt.subplot(2, 2, 4)
        plt.imshow(img_with_boxes_rgb)
        plt.title('4. Ảnh Cuối cùng với Bounding Box', fontsize=12)
        plt.axis('off')

        plt.tight_layout(rect=[0, 0, 1, 0.95]) 
        plt.show() 
        
        # --- LƯU KẾT QUẢ ---
        base_name = os.path.basename(img_name)
        name_no_ext = os.path.splitext(base_name)[0]
        
        output_txt_path = os.path.join(output_txt_dir, name_no_ext + '.txt')
        output_viz_path = os.path.join(output_viz_dir, base_name)
        output_rotated_img_path = os.path.join(output_rotated_img_dir, base_name)

        if write_rotated_img:
            cv2.imwrite(output_rotated_img_path, img_rotated_final) 
        if write_file:
            write_output(boxes_list, output_txt_path)
        if visualize:
            viz_icdar(img_rotated_final, output_txt_path, output_viz_path)
            end_visualize = time.time()
            print('Visualize time:', round(end_visualize - end_detector, 4), 'seconds')
        
        end = time.time()
        speed = (end - begin) / (idx + 1)
        print('Tổng thời gian chạy:', round(end - begin, 4), 'giây. Tốc độ trung bình:', round(speed, 4), 'giây/ảnh')
        print('-' * 50)


if __name__ == "__main__":
    main()