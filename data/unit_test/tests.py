import json

def check_file(task_id):
    '''
    根据task_id，判断是否需要输出文件，
    如果需要，则检测输出文件是否在output文件夹内，模糊匹配，返回匹配的文件名称
        如果没有输出文件，则直接failed
    如果不需要，这一环节直接pass
    好像不是很必要
    '''

    pass


import json
import os
import fnmatch
import pandas as pd
import cv2
import pickle
from PIL import Image,ImageChops
import numpy as np
from PIL import Image


def are_images_similar(image_path1, image_path2, threshold=0.75):
    """
    判断两张图片是否相似，使用ORB特征匹配。

    :param image_path1: 第一张图片的文件路径
    :param image_path2: 第二张图片的文件路径
    :param threshold: 匹配特征点的阈值，默认为0.75
    :return: 如果图片相似，返回True；否则返回False
    """
    # 读取图片
    img1 = cv2.imread(image_path1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image_path2, cv2.IMREAD_GRAYSCALE)

    # 检查图片是否读取成功
    if img1 is None or img2 is None:
        raise ValueError("One or both images could not be read.")

    # 初始化ORB检测器
    orb = cv2.ORB_create()

    # 寻找关键点和描述符
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    # 创建BFMatcher对象
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # 进行特征点匹配
    matches = bf.match(des1, des2)

    # 根据距离排序
    matches = sorted(matches, key=lambda x: x.distance)

    # 计算好的匹配数量
    good_matches = [m for m in matches if m.distance < threshold * max(matches, key=lambda x: x.distance).distance]

    # 定义一个阈值，判断图片是否相似
    similarity_threshold = 0.9  # 可以根据实际情况调整

    # 如果好的匹配数量占总匹配数量的比例超过阈值，则认为图片相似
    if len(good_matches) / len(matches) > similarity_threshold:
        return True
    else:
        return False

def are_two_images_same(img1, img2,threshold=0.4,tolerance=0.5):
    """
    比较两张图片的相似程度是否超过给定阈值。

    参数:
    img1: PIL.Image.Image - 第一张图片
    img2: PIL.Image.Image - 第二张图片
    threshold: float - 相似度阈值，默认是0.9（即90%）

    返回:
    bool - 如果两张图片的相似度超过阈值则返回True，否则返回False
    """
    # 如果尺寸不同，将img2放缩到img1的尺寸
    if img1.size != img2.size:
        img2 = img2.resize(img1.size)
    
    # 如果模式不同，将img2转换为img1的模式
    if img1.mode != img2.mode:
        img2 = img2.convert(img1.mode)
    
    # 将图像转换为numpy数组
    img1_np = np.array(img1)
    img2_np = np.array(img2)
    
    # 计算每个像素的差异
    diff_np = np.abs(img1_np - img2_np)
    
    # 计算允许的误差范围
    tolerance_value = 255 * tolerance
    
    # 计算在误差范围内的像素数量
    within_tolerance = np.all(diff_np <= tolerance_value, axis=-1)
    similar_pixels = np.count_nonzero(within_tolerance)
    
    # 计算总像素数量
    total_pixels = img1_np.shape[0] * img1_np.shape[1]
    
    # 计算相似度
    similarity = similar_pixels / total_pixels
    print(similarity)
    # 判断相似度是否超过阈值
    return similarity >= threshold

def is_proportionally_similar(img1, img2, tolerance=0.1):
    """
    比较两张图片的尺寸比例是否在允许的误差范围内。
    """
    # 获取图片尺寸
    width1, height1 = img1.size
    width2, height2 = img2.size
    print("Img1",img1.size)
    print("Img2",img2.size)
    # 计算图片的宽高比例
    ratio1 = width1 / height1
    ratio2 = width2 / height2
    
    # 计算比例差异
    ratio_diff = abs(ratio1 - ratio2)
    
    # 判断比例差异是否在容忍范围内
    return ratio_diff <= tolerance


# Function to identify string-type numeric columns
def identify_numeric_columns(df):
    numeric_columns = []
    for column in df.columns:
        if df[column].dtype == 'object':
            try:
                pd.to_numeric(df[column].str.replace(',', '').replace('$', ''), errors='raise')
                numeric_columns.append(column)
            except ValueError:
                pass  # If conversion fails, it's not a numeric column
    return numeric_columns

def calculate_sharpness(image_path):
    # 打开图像并转换为灰度图
    image = Image.open(image_path).convert('L')
    image_array = np.array(image)
    
    # 使用拉普拉斯算子计算图像的清晰度
    laplacian = cv2.Laplacian(image_array, cv2.CV_64F)
    sharpness = laplacian.var()
    
    return sharpness

def test_task_2(trajectory):
    df=pd.read_csv('./output/2.csv')
    duplicates = df.duplicated().sum()
    #print(type(duplicates))
    print(duplicates==0)
    assert duplicates==0

def test_task_3(trajectory):
    df=pd.read_csv('./output/3.csv')
    duplicates = df.duplicated().sum()
    assert duplicates==0

def test_task_4(trajectory):
    df=pd.read_csv('./output/4.csv')
    null_value = df.isnull().sum().sum()
    assert null_value==0

def test_task_5(trajectory):
    df=pd.read_csv("./output/5.csv")
    null_value = df.isnull().sum().sum()
    assert null_value==0

def test_task_6(trajectory):
    #print("in6")
    df = pd.read_csv("./output/6.csv")
    #print(df)
    #print("CheckPoint")
    for column in df.select_dtypes(include=['float64',"int"]).columns:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = ((df[column] < lower_bound) | (df[column] > upper_bound)).sum()
        #print("Outline",outliers,"===")
        assert outliers == 0

def test_task_7(trajectory):
    '''
    <Region>:<count>\n
    Africa: 48
- Latin America: 38
- Asiatic Region: 32
- Western Europe: 26
- Eastern Europe: 23
- Middle East: 15
- Pacific Region: 10
- Northern America: 2 
- Africa/Middle East (combined region): 1
Test whether each answer
    '''
    final_answer=trajectory[-1]['content']
    answer_list=["48","38","32","26","23","15","10","2","1"]
    for ans in answer_list:
        if ans not in final_answer:
            raise ValueError


def test_task_8(trajectory):
    # 读取数据
    df = pd.read_csv('./output/8.csv')
    
    # 检查空值和缺失值
    null_value = df.isnull().sum().sum()  # 总和，检查整个 DataFrame 中的空值数量
    #print("null value",null_value)
    assert null_value == 0

    # 检查重复值
    duplicate_rows = df.duplicated().sum()  # 检查重复行的数量
    #print("duplicate_rows value",duplicate_rows)
    assert duplicate_rows == 0


# Test function
def test_task_9(trajectory):
    df = pd.read_excel("./output/9_1.xlsx")
    df2 = pd.read_csv("./output/9_2.csv")

    # Identify numeric columns in both dataframes
    numeric_columns_df = identify_numeric_columns(df)
    numeric_columns_df2 = identify_numeric_columns(df2)

   
    # Assert that the identified numeric columns match the expected columns
    assert len(numeric_columns_df) == 0
    assert len(numeric_columns_df2) == 0

# Example usage (remove or comment out in actual test file)
# test_task_9()

def test_task_10(trajectory):
    df=pd.read_csv("./output/10.csv")
    date_format_correct = all(pd.to_datetime(df['Start Date'], errors='coerce').notnull())
    assert date_format_correct==True

def test_task_11(trajectory):
    try:
        df=pd.read_excel("./output/11.xls")
    except:
        df=pd.read_excel("./output/11.xlsx")

    assert df


def test_task_12(trajectory):
    df=pd.read_csv("./output/12.csv")
    num_rows = df.shape[0]
    assert num_rows==4

def test_task_13(trajectory):
    df=pd.read_csv("./output/13.csv")
    num_rows = df.shape[0]
    assert num_rows==30

def test_task_14(trajectory):
    df = pd.read_csv("./output/14.csv")
    sorted_df = df.sort_values(by='avg_us_viewers', ascending=False)
    assert df.equals(sorted_df)

def test_task_15(trajectory):
    df = pd.read_csv("./output/15.csv")
    sorted_df = df.sort_values(by=['avg_us_viewers', 'ad_cost'], ascending=[False, True])
    assert df.equals(sorted_df)

    
def test_task_16(trajectory):
    key_path="./output/16.png"
    reference_path="./gpt4_output/wisconsin_sales_by_gender_pie_chart.png"
    assert are_images_similar(reference_path,key_path)

def test_task_17(trajectory):
    # key: "142"
    final_answer=trajectory[-1]['content']
    assert "142" in final_answer

def test_task_18(trajectory):
    final_answer=trajectory[-1]['content']
    assert "2526" in final_answer
    assert "1506614" in final_answer

def test_task_19(trajectory):    
    final_answer=trajectory[-1]['content']
    answer_list=["-346","2504"]
    for ans in answer_list:
        assert ans in final_answer
    
def test_task_20(trajectory):    
    ans_path="./output/20.png"
    reference_path="./gpt4_output/radar_chart.png"
    assert are_images_similar(ans_path,reference_path)


def test_task_21(trajectory):
    final_answer=trajectory[-1]['content']
    answer_list=["50"]
    for ans in answer_list:
        assert ans in final_answer

def test_task_22(trajectory):
    final_answer=trajectory[-1]['content']
    answer_list=["9.6"]
    for ans in answer_list:
        assert ans in final_answer

def test_task_23(trajectory):
    final_answer=trajectory[-1]['content']
    answer_list=["47"]
    for ans in answer_list:
        assert ans in final_answer

def test_task_25(trajectory):
    final_answer=trajectory[-1]['content']
    answer_list=['Uncharted',
                'Morbius',
                'Firestarter',
                'Orphan: First Kill',
                'Nope',
                'Beast',
                'Barbarian',
                'Dog',
                'Hunt',
                'The Black Phone',
                'Scream',
                'Doctor Strange in the Multiverse of Madness',
                'Bhool Bhulaiyaa 2',
                'Men',
                'X',
                'Memory',
                'Bodies Bodies Bodies',
                'The Invitation',
                'Easter Sunday']
    flag=False
    for ans in answer_list:
        if ans in final_answer:
            flag=True
        
    assert flag

def test_task_27(trajectory):
    final_answer=trajectory[-1]['content']
    answer_list=["ABC","NBC"]
    flag=False
    for ans in answer_list:
        if ans in final_answer:
            flag=True
    assert flag

def test_task_28(trajectory):
    final_answer=trajectory[-1]['content']
    answer_list=["2017"]
    for ans in answer_list:
        assert ans in final_answer

def test_task_29(trajectory):
    final_answer=trajectory[-1]['content']
    answer_list=["XL"]
    for ans in answer_list:
        assert ans in final_answer


def test_task_30(trajectory):
    final_answer=trajectory[-1]['content']
    answer_list=["323","237"]
    flag=False
    for ans in answer_list:
        if ans in final_answer:
            flag=True
    assert flag

def test_task_31(trajectory):
    ref_path="./gpt4_output/smoker_charges_relationship.png"
    ans_path="./output/31.png"
    assert are_images_similar(ref_path,ans_path)

def test_task_32(trajectory):
    final_answer=trajectory[-1]['content']
    answer_list=["53"]
    flag=False
    for ans in answer_list:
        if ans in final_answer:
            flag=True
    assert flag

def test_task_33(trajectory):
    final_answer=trajectory[-1]['content']
    assert ("0.54" in final_answer or '0.53' in final_answer)

def test_task_34(trajectory):
    final_answer=trajectory[-1]['content']
    assert "Ellis Ave & 60th St" in final_answer 

def test_task_35(trajectory):
    final_answer=trajectory[-1]['content']
    #print(final_answer)
    assert ("United States" in final_answer or "美国" in final_answer)

def test_task_36(trajectory):
    final_answer=trajectory[-1]['content']
    #print(final_answer)
    assert "Music" in final_answer

def test_task_37(trajectory):
    final_answer=trajectory[-1]['content']
    assert ("持有" in final_answer or "出售" in final_answer or "hold" in final_answer or "sell" in final_answer)


def test_task_38(trajectory):
    df=pd.read_csv('./output/38.csv')
    null_value = df.isnull().sum().sum()
    assert null_value==0

def test_task_39(trajectory):
    final_answer=trajectory[-1]['content']
    ans="Male"
    assert (ans in final_answer or 'male' in final_answer)

def test_task_40(trajectory):
    model_path = "./output/40.pkl"
    
    # Check if the file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"The file {model_path} does not exist.")
    
    # Load and validate the .pkl file
    def load_and_validate_pkl(file_path):
        try:
            with open(file_path, 'rb') as file:
                data = pickle.load(file)
                #print("File loaded successfully. Data content:")
                print(data)
                return True
        except Exception as e:
            #print(f"Failed to load the file: {e}")
            return False
    
    # Validate the .pkl file
    is_valid = load_and_validate_pkl(model_path)
    
    # Assert that the file is valid
    assert is_valid

def test_task_41(trajectory):
    model_path = "./output/41.pkl"
    
    # Check if the file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"The file {model_path} does not exist.")
    
    # Load and validate the .pkl file
    def load_and_validate_pkl(file_path):
        try:
            with open(file_path, 'rb') as file:
                data = pickle.load(file)
                #print("File loaded successfully. Data content:")
                #print(data)
                return True
        except Exception as e:
            #print(f"Failed to load the file: {e}")
            return False
    
    # Validate the .pkl file
    is_valid = load_and_validate_pkl(model_path)
    
    # Assert that the file is valid
    assert is_valid

def test_task_42(trajectory):
    ans="./output/42.png"
    ref="./gpt4_output/clusters_scatter.png"
    assert are_images_similar(ans,ref)

def test_task_43(trajectory):
    ans="./output/43.png"
    ref="./gpt4_output/elbow_method_plot.png"
    print("WARNING BAD CASE FOR GPT-4 NEED MANUALLY FIX",ref)
    assert os.path.exists(ans)

def test_task_44(trajectory):
    ans="./output/44.png"
    ref="./gpt4_output/stock_price_trend.png"
    assert are_images_similar(ans,ref)

def test_task_45(trajectory):
    ans="./output/45.png"
    ref="./gpt4_output/monthly_ride_counts.png"
    assert are_images_similar(ans,ref)

def test_task_46(trajectory):
    
    ans="./output/46.png"
    ref="./gpt4_output/monthly_ride_counts.png"
    #print("WARNING BAD CASE FOR GPT-4 NEED MANUALLY FIX",46)
    
    assert os.path.exists(ans)

def test_task_47(trajectory):
    model_path = "./output/47.pkl"
    
    # Check if the file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"The file {model_path} does not exist.")
    
    # Load and validate the .pkl file
    def load_and_validate_pkl(file_path):
        try:
            with open(file_path, 'rb') as file:
                data = pickle.load(file)
                #print("File loaded successfully. Data content:")
                #print(data)
                return True
        except Exception as e:
            #print(f"Failed to load the file: {e}")
            return False
    
    # Validate the .pkl file
    is_valid = load_and_validate_pkl(model_path)
    
    # Assert that the file is valid
    assert is_valid

def test_task_48(trajectory):
    model_path = "./output/48.pkl"
    
    # Check if the file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"The file {model_path} does not exist.")
    
    # Load and validate the .pkl file
    def load_and_validate_pkl(file_path):
        try:
            with open(file_path, 'rb') as file:
                data = pickle.load(file)
                #print("File loaded successfully. Data content:")
                #print(data)
                return True
        except Exception as e:
            #print(f"Failed to load the file: {e}")
            return False
    
    # Validate the .pkl file
    is_valid = load_and_validate_pkl(model_path)
    
    # Assert that the file is valid
    assert is_valid

def test_task_49(trajectory):
    model_path = "./output/49.pkl"
    
    # Check if the file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"The file {model_path} does not exist.")
    
    # Load and validate the .pkl file
    def load_and_validate_pkl(file_path):
        try:
            with open(file_path, 'rb') as file:
                data = pickle.load(file)
                #print("File loaded successfully. Data content:")
                #print(data)
                return True
        except Exception as e:
            #print(f"Failed to load the file: {e}")
            return False
    
    # Validate the .pkl file
    is_valid = load_and_validate_pkl(model_path)
    
    # Assert that the file is valid
    assert is_valid

def test_task_50(trajectory):
    model_path = "./output/50.pkl"
    
    # Check if the file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"The file {model_path} does not exist.")
    
    # Load and validate the .pkl file
    def load_and_validate_pkl(file_path):
        try:
            with open(file_path, 'rb') as file:
                data = pickle.load(file)
                #print("File loaded successfully. Data content:")
                #print(data)
                return True
        except Exception as e:
            #print(f"Failed to load the file: {e}")
            return False
    
    # Validate the .pkl file
    is_valid = load_and_validate_pkl(model_path)
    
    # Assert that the file is valid
    assert is_valid

def test_task_51(trajectory):
    model_path = "./output/51.pkl"
    
    # Check if the file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"The file {model_path} does not exist.")
    
    # Load and validate the .pkl file
    def load_and_validate_pkl(file_path):
        try:
            with open(file_path, 'rb') as file:
                data = pickle.load(file)
                #print("File loaded successfully. Data content:")
                #print(data)
                return True
        except Exception as e:
            #print(f"Failed to load the file: {e}")
            return False
    
    # Validate the .pkl file
    is_valid = load_and_validate_pkl(model_path)
    
    # Assert that the file is valid
    assert is_valid

def test_task_52(trajectory):
    ans = "./output/52_neg.png"
    ans_1 = "./output/52_pos.png"
    print("WARNING 52 only verify the exist of the images")
    # Assert that both image files exist
    assert os.path.exists(ans), f"File {ans} does not exist."
    assert os.path.exists(ans_1), f"File {ans_1} does not exist."

def test_task_53(trajectory):
    final_answer=trajectory[-1]['content']
    #print(final_answer)
    assert "重庆啤酒" in final_answer

def test_task_54(trajectory):
    final_answer=trajectory[-1]['content']
    #print(final_answer)
    assert "safety" in final_answer
    assert "injection" in final_answer

def test_task_55(trajectory):
    final_answer=trajectory[-1]['content']
    #print(final_answer)
    assert ("科幻" in final_answer or "悬疑" in final_answer)


def test_task_56(trajectory):
    final_answer=trajectory[-1]['content']
    #print(final_answer)
    assert ("positive" in final_answer or "negative" in final_answer)

def test_task_57(trajectory):
    ans="./output/57.png"
    print("WARNING 57 only verify the exist of the images")
    assert os.path.exists(ans), f"File {ans} does not exist."

def test_task_58(trajectory):
    ans="./output/58.png"
    print("WARNING 58 only verify the exist of the images")
    assert os.path.exists(ans), f"File {ans} does not exist."

def test_task_59(trajectory):
    ans="./output/59.png"
    print("WARNING 59 only verify the exist of the images")
    assert os.path.exists(ans), f"File {ans} does not exist."

def test_task_60(trajectory):
    ans="./output/60.png"
    ref="./gpt4_output/china_tea_export_line_chart.png"
    #print("WARNING 60 only verify the exist of the images")
    assert are_images_similar(ans,ref)

def test_task_61(trajectory):
    ans="./output/61.png"
    ref="./gpt4_output/australian_gold_medals_over_time.png"
    #print("WARNING 60 only verify the exist of the images")
    assert are_images_similar(ans,ref)

def test_task_62(trajectory):
    ans="./output/62.png"
    ref="./gpt4_output/australian_gold_medals_over_time.png"
    print("WARNING 62 Has NO Reference!")
    assert are_images_similar(ans,ref)

def test_task_63(trajectory):
    ans="./output/63.png"
    ref="./gpt4_output/sales_by_product.png"
    #print("WARNING 60 only verify the exist of the images")
    assert are_images_similar(ans,ref)

def test_task_64(trajectory):
    ans="./output/64.png"
    ref="./gpt4_output/youtube_category_popularity.png"
    assert os.path.exists(ans)
    #print("WARNING 60 only verify the exist of the images")
    #assert are_images_similar(ans,ref,0) 

def test_task_65(trajectory):
    ans="./output/65.png"
    ref="./gpt4_output/employee_education_distribution.png"
    assert are_images_similar(ans,ref) 


def test_task_66(trajectory):
    ans="./output/66.png"
    ref="./gpt4_output/meals_distribution_pie_chart.png"
    assert are_images_similar(ans,ref) 

def test_task_67(trajectory):
    ans="./output/67.png"
    ref="./gpt4_output/X_vs_Y_scatter_plot.png"
    assert are_images_similar(ans,ref) 

def test_task_68(trajectory):
    ans="./output/67.png"
    ref="./gpt4_output/X_vs_Y_scatter_plot.png"
    assert are_images_similar(ans,ref) 

def test_task_69(trajectory):
    ans="./output/69.png"
    assert os.path.exists(ans)

def test_task_70(trajectory):
    ans="./output/70.png"
    assert os.path.exists(ans)

def test_task_71(trajectory):
    ans="./output/71.png"
    assert os.path.exists(ans)

def test_task_72(trajectory):
    ans="./output/72.png"
    assert os.path.exists(ans)

def test_task_73(trajectory):
    ans="./output/73.png"
    assert os.path.exists(ans)

def test_task_74(trajectory):
    ans="./output/74.png"
    assert os.path.exists(ans)

def test_task_75(trajectory):
    ans="./output/75.docx"
    assert os.path.exists(ans)

def test_task_76(trajectory):
    final_answer=trajectory[-1]['content']
    #print(final_answer)
    assert "WizardMath" in final_answer

def test_task_77(trajectory):
    final_answer=trajectory[-1]['content']
    #print(final_answer)
    assert "如懿" in final_answer

def test_task_78(trajectory):
    image_path="./output/78.png"
    # 检查文件是否存在
    #print("Check",os.path.exists(image_path))
    assert os.path.exists(image_path)
    with Image.open(image_path) as img:
        #print("In")
        width, height = img.size
        #print("AAA",width, height)
        assert width==224
        assert height==224

def test_task_79(trajectory):
    image_path="./output/79.png"
    # 检查文件是否存在
    #print("Check",os.path.exists(image_path))
    assert os.path.exists(image_path)
    with Image.open(image_path) as img:
        #print("In")
        width, height = img.size
        #print("AAA",width, height)
        assert width==1000
        assert height==500
        
def test_task_80(trajectory):
    print("[ERROR]This test has error!!!!!!")
    image_path="./output/80.png"
    ref_path="./data/80.jpeg"
    assert os.path.exists(image_path)
    image = Image.open(image_path)
    ref_image = Image.open(ref_path)
    rotated_image = image.rotate(270, expand=True)
    assert are_two_images_same(rotated_image,ref_image)

def test_task_81(trajectory):
    #print("[ERROR]This test has error!!!!!!")
    image_path="./output/81.png"
    ref_path="./data/81.jpeg"
    assert os.path.exists(image_path)
    image = Image.open(image_path)
    ref_image = Image.open(ref_path)
    rotated_image = image.rotate(180, expand=True)
    assert are_two_images_same(rotated_image,ref_image)

def test_task_82(trajectory):
    #print("[ERROR]This test has error!!!!!!")
    image_path="./output/81.png"
    ref_path="./data/81.jpeg"
    assert os.path.exists(image_path)
    image = Image.open(image_path)
    ref_image = Image.open(ref_path)
    rotated_image = image.rotate(180, expand=True)
    assert are_two_images_same(rotated_image,ref_image)

def test_task_83(trajectory):
    image_paths = ["./output/83_1.png", "./output/83_2.png", "./output/83_3.png", "./output/83_4.png"]
    ref_path = "./data/83.jpeg"
    
    # 打开参考图片
    ref_image = Image.open(ref_path)
    
    # 打开并拼接四张图片
    images = [Image.open(path) for path in image_paths]
    widths, heights = zip(*(img.size for img in images))
    
    total_width = sum(widths)
    max_height = max(heights)
    
    # 创建一个新的空白图像用于拼接
    new_image = Image.new('RGB', (total_width, max_height))
    
    # 将四张图片拼接到新图像上
    x_offset = 0
    for img in images:
        new_image.paste(img, (x_offset, 0))
        x_offset += img.width
    
    # 比较拼接后的图像与参考图像的尺寸比例
    assert is_proportionally_similar(new_image, ref_image), "The concatenated image is not proportionally similar to the reference image."

def test_task_83(trajectory):
    image_paths = ["./output/83_1.png", "./output/83_2.png", "./output/83_3.png", "./output/83_4.png"]
    ref_path = "./data/83.jpeg"
    
    # 打开参考图片
    ref_image = Image.open(ref_path)
    
    # 打开并拼接四张图片
    images = [Image.open(path) for path in image_paths]
    widths, heights = zip(*(img.size for img in images))
    
    total_width = sum(widths)
    max_height = max(heights)
    
    # 创建一个新的空白图像用于拼接
    new_image = Image.new('RGB', (total_width, max_height))
    
    # 将四张图片拼接到新图像上
    x_offset = 0
    for img in images:
        new_image.paste(img, (x_offset, 0))
        x_offset += img.width
    
    # 比较拼接后的图像与参考图像的尺寸比例
    assert is_proportionally_similar(new_image, ref_image), "The concatenated image is not proportionally similar to the reference image."

def test_task_84(trajectory):
    image_path ="./output/84.png"
    ref_path = "./data/84.jpeg"
    assert os.path.exists(image_path)
    with Image.open(image_path) as img:
        #print("In")
        width, height = img.size
        #print("AAA",width, height)
        assert width==height
        
    
    
def test_task_85(trajectory):
    image_path ="./output/85.png"
    ref_path = "./data/85.jpeg"
    assert os.path.exists(image_path)
    with Image.open(image_path) as img:
        #print("In")
        width, height = img.size
        #print("AAA",width, height)
        assert width==300
        assert height==300
        
  
def test_task_86(trajectory):
    image_path = "./output/86.png"
    ref_path = "./data/86.jpeg"
    
    # 打开目标图像和参考图像
    img1 = Image.open(image_path)
    img2 = Image.open(ref_path)
    
    # 将目标图像左右翻转
    img1_flipped = img1.transpose(Image.FLIP_LEFT_RIGHT)
    
    # 比较翻转后的图像与参考图像是否足够相似
    assert are_two_images_same(img1_flipped, img2), "The flipped image is not similar enough to the reference image."


def test_task_87(trajectory):
    # Same to 86
    image_path = "./output/87.png"
    ref_path = "./data/87.jpeg"
    
    # 打开目标图像和参考图像
    img1 = Image.open(image_path)
    img2 = Image.open(ref_path)
    
    # 将目标图像左右翻转
    img1_flipped = img1.transpose(Image.FLIP_LEFT_RIGHT)
    
    # 比较翻转后的图像与参考图像是否足够相似
    assert are_two_images_same(img1_flipped, img2), "The flipped image is not similar enough to the reference image."





def test_task_88(trajectory):
    image_path = "./output/88.png"
    ref_path = "./data/88.jpeg"
    
    # 打开目标图像
    image = Image.open(image_path)
    
    # 将图像转换为灰度图
    gray_image = image.convert('L')
    
    # 将灰度图转换为numpy数组
    gray_array = np.array(gray_image)
    
    # 定义黑色像素的阈值（例如，灰度值小于等于50的像素被认为是黑色）
    black_threshold = 50
    
    # 计算黑色像素的数量
    black_pixels = np.sum(gray_array <= black_threshold)
    
    # 计算总像素数量
    total_pixels = gray_array.size
    
    # 计算黑色像素比例
    black_ratio = black_pixels / total_pixels
    
    # 检查图像中黑色像素的比例是否超过30%
    assert black_ratio > 0.25, "The black pixel percentage does not exceed 30%."

def test_task_89(trajectory):
    image_path = "./output/89.png"
    ref_path = "./data/89.jpeg"
    
    # 打开目标图像
    image = Image.open(image_path)
    
    # 将图像转换为灰度图
    gray_image = image.convert('L')
    
    # 将灰度图转换为numpy数组
    gray_array = np.array(gray_image)
    
    # 定义黑色像素的阈值（例如，灰度值小于等于50的像素被认为是黑色）
    black_threshold = 50
    
    # 计算黑色像素的数量
    black_pixels = np.sum(gray_array <= black_threshold)
    
    # 计算总像素数量
    total_pixels = gray_array.size
    
    # 计算黑色像素比例
    black_ratio = black_pixels / total_pixels
    print(black_ratio)
    # 检查图像中黑色像素的比例是否超过30%
    assert black_ratio > 0.3, "The black pixel percentage does not exceed 30%."

def test_task_90(trajectory):
    image_path = "./output/90.png"
    ref_path = "./data/90.jpeg"
    
    assert os.path.exists(image_path)

def test_task_91(trajectory):
    image_path = "./output/91.png"
    ref_path = "./data/91.jpeg"
    assert os.path.exists(image_path)

def test_task_92(trajectory):
    image_path = "./output/92.png"
    ref_path = "./data/92.jpeg"
    
    # 打开目标图像和参考图像
    image = Image.open(image_path)
    ref_image = Image.open(ref_path)
    
    # 将图像转换为灰度图
    gray_image = image.convert('L')
    gray_ref_image = ref_image.convert('L')
    
    # 将灰度图转换为numpy数组
    gray_array = np.array(gray_image)
    gray_ref_array = np.array(gray_ref_image)
    
    # 计算每个图像的平均亮度
    avg_brightness_image = np.mean(gray_array)
    avg_brightness_ref_image = np.mean(gray_ref_array)
    
    assert avg_brightness_image < avg_brightness_ref_image, "The brightness of the image is not lower than the reference image."

def test_task_93(trajectory):
    image_path = "./output/93.png"
    ref_path = "./data/93.jpeg"
    # 打开目标图像和参考图像
    image = Image.open(image_path)
    ref_image = Image.open(ref_path)
    
    # 将图像转换为灰度图
    gray_image = image.convert('L')
    gray_ref_image = ref_image.convert('L')
    
    # 将灰度图转换为numpy数组
    gray_array = np.array(gray_image)
    gray_ref_array = np.array(gray_ref_image)
    
    # 计算每个图像的平均亮度
    avg_brightness_image = np.mean(gray_array)
    avg_brightness_ref_image = np.mean(gray_ref_array)
    
    assert avg_brightness_image > avg_brightness_ref_image, "The brightness of the image is not lower than the reference image."

    
def test_task_94(trajectory):
    image_path = "./output/94.png"
    ref_path = "./data/94.jpeg"
    
    # 打开目标图像和参考图像
    image = Image.open(image_path)
    ref_image = Image.open(ref_path)
    
    # 将图像转换为灰度图
    gray_image = image.convert('L')
    gray_ref_image = ref_image.convert('L')
    
    # 将灰度图转换为numpy数组
    gray_array = np.array(gray_image)
    gray_ref_array = np.array(gray_ref_image)
    
    # 计算每个图像的对比度（标准差）
    contrast_image = np.std(gray_array)
    contrast_ref_image = np.std(gray_ref_array)
    
    # 检查目标图像的对比度是否低于参考图像的对比度
    assert contrast_image < contrast_ref_image, "The contrast of the image is not lower than the reference image."

def test_task_95(trajectory):
    image_path = "./output/95.png"
    ref_path = "./data/95.jpeg"
    
    # 打开目标图像和参考图像
    image = Image.open(image_path)
    ref_image = Image.open(ref_path)
    
    # 将图像转换为灰度图
    gray_image = image.convert('L')
    gray_ref_image = ref_image.convert('L')
    
    # 将灰度图转换为numpy数组
    gray_array = np.array(gray_image)
    gray_ref_array = np.array(gray_ref_image)
    
    # 计算每个图像的对比度（标准差）
    contrast_image = np.std(gray_array)
    contrast_ref_image = np.std(gray_ref_array)
    
   
    assert contrast_image > contrast_ref_image, "The contrast of the image is not lower than the reference image."

def test_task_96(trajectory):
    image_path = "./output/96.png"
    ref_path = "./data/96.jpeg"
    
    # 打开目标图像和参考图像
    image = Image.open(image_path)
    ref_image = Image.open(ref_path)
    
    # 将图像转换为HSV颜色空间
    hsv_image = image.convert('HSV')
    hsv_ref_image = ref_image.convert('HSV')
    
    # 将HSV图像转换为numpy数组
    hsv_array = np.array(hsv_image)
    hsv_ref_array = np.array(hsv_ref_image)
    
    # 计算每个图像的平均饱和度（S通道的平均值）
    avg_saturation_image = np.mean(hsv_array[:, :, 1])
    avg_saturation_ref_image = np.mean(hsv_ref_array[:, :, 1])
    
    # 检查目标图像的饱和度是否低于参考图像的饱和度
    assert avg_saturation_image < avg_saturation_ref_image, "The saturation of the image is not lower than the reference image."

def test_task_97(trajectory):
    image_path = "./output/97.png"
    ref_path = "./data/97.jpeg"
    
    # 打开目标图像和参考图像
    image = Image.open(image_path)
    ref_image = Image.open(ref_path)
    
    # 将图像转换为HSV颜色空间
    hsv_image = image.convert('HSV')
    hsv_ref_image = ref_image.convert('HSV')
    
    # 将HSV图像转换为numpy数组
    hsv_array = np.array(hsv_image)
    hsv_ref_array = np.array(hsv_ref_image)
    
    # 计算每个图像的平均饱和度（S通道的平均值）
    avg_saturation_image = np.mean(hsv_array[:, :, 1])
    avg_saturation_ref_image = np.mean(hsv_ref_array[:, :, 1])
    
    # 检查目标图像的饱和度是否低于参考图像的饱和度
    assert avg_saturation_image > avg_saturation_ref_image, "The saturation of the image is not lower than the reference image."

def test_task_98(trajectory):
    image_path = "./output/98.png"
    ref_path = "./data/98.jpeg"
    
    # 计算目标图像和参考图像的清晰度
    sharpness_image = calculate_sharpness(image_path)
    sharpness_ref_image = calculate_sharpness(ref_path)
    
    # 检查目标图像的清晰度是否低于参考图像的清晰度
    assert sharpness_image < sharpness_ref_image, "The sharpness of the image is not lower than the reference image."

def test_task_99(trajectory):
    image_path = "./output/99.png"
    ref_path = "./data/99.jpeg"
    
    # 计算目标图像和参考图像的清晰度
    sharpness_image = calculate_sharpness(image_path)
    sharpness_ref_image = calculate_sharpness(ref_path)
    
    # 检查目标图像的清晰度是否低于参考图像的清晰度
    assert sharpness_image < sharpness_ref_image, "The sharpness of the image is not lower than the reference image."

def is_grayscale(image_path):
    """
    检查图像是否是灰度图。
    """
    image = Image.open(image_path)
    return image.mode == 'L'

def test_task_100(trajectory):
    image_path = "./output/100.png"
    ref_path = "./data/100.jpeg"
    
    # 检查目标图像是否是灰度图
    is_image_grayscale = is_grayscale(image_path)
    
    # 断言目标图像是灰度图
    assert is_image_grayscale, "The image is not a grayscale image."


def test_task_101(trajectory):
    image_path = "./output/101.png"
    ref_path = "./data/101.jpeg"
    
    # 打开目标图像
    image = Image.open(image_path)
    
    # 将图像转换为灰度图
    gray_image = image.convert('L')
    
    # 将灰度图转换为numpy数组
    gray_array = np.array(gray_image)
    
    # 定义黑色像素的阈值（例如，灰度值小于等于50的像素被认为是黑色）
    black_threshold = 50
    
    # 计算黑色像素的数量
    black_pixels = np.sum(gray_array <= black_threshold)
    
    # 计算总像素数量
    total_pixels = gray_array.size
    
    # 计算黑色像素比例
    black_ratio = black_pixels / total_pixels
    print(black_ratio)
    # 检查图像中黑色像素的比例是否超过30%
    assert black_ratio > 0.5, "The black pixel percentage does not exceed 50%."

def test_task_102(trajectory):
    image_path = "./output/102.png"
    ref_path = "./data/102.jpeg"
    
    # 打开目标图像
    image = Image.open(image_path)
    
    # 将图像转换为灰度图
    gray_image = image.convert('L')
    
    # 将灰度图转换为numpy数组
    gray_array = np.array(gray_image)
    
    # 定义黑色像素的阈值（例如，灰度值小于等于50的像素被认为是黑色）
    black_threshold = 50
    
    # 计算黑色像素的数量
    black_pixels = np.sum(gray_array <= black_threshold)
    
    # 计算总像素数量
    total_pixels = gray_array.size
    
    # 计算黑色像素比例
    black_ratio = black_pixels / total_pixels
    print(black_ratio)
    # 检查图像中黑色像素的比例是否超过30%
    assert black_ratio > 0.5, "The black pixel percentage does not exceed 50%."


def test_task_103(trajectory):
    image_path = "./output/103.png"
    assert os.path.exists(image_path)

def test_task_105(trajectory):
    image_path = "./output/105.png"
    assert os.path.exists(image_path)

def test_task_107(trajectory):
    image_path = "./output/107.png"
    
    assert os.path.exists(image_path)

def test_task_109(trajectory):
    image_path = "./output/109.png"
    
    assert os.path.exists(image_path)

def test_task_110(trajectory):
    image_path = "./output/110.png"
    
    assert os.path.exists(image_path)

def test_task_111(trajectory):
    image_path = "./output/111.jpeg"
    
    assert os.path.exists(image_path)

def test_task_112(trajectory):
    image_path = "./output/112.pdf"
    
    assert os.path.exists(image_path)

def test_task_113(trajectory):
    image_path = "./output/113.mp4"
    
    assert os.path.exists(image_path)

def test_task_114(trajectory):
    image_path = "./output/114.mp4"
    
    assert os.path.exists(image_path)

def test_task_115(trajectory):
    image_path = "./output/115.png"
    
    assert os.path.exists(image_path)

def test_task_116(trajectory):
    image_path = "./output/116.png"
    
    assert os.path.exists(image_path)

def test_task_117(trajectory):
    image_path = "./output/117.png"
    assert os.path.exists(image_path)
    
    
def test_task_118(trajectory):
    image_path = "./output/118.png"
    assert os.path.exists(image_path)
    
def test_task_119(trajectory):
    image_path = "./output/119.png"
    assert os.path.exists(image_path)
    
def test_task_120(trajectory):
    image_path = "./output/120.png"
    assert os.path.exists(image_path)

def test_task_121(trajectory):
    image_path = "./output/121.png"
    assert os.path.exists(image_path)

def test_task_122(trajectory):
    image_path = "./output/122.png"
    assert os.path.exists(image_path)

def test_task_123(trajectory):
    image_path = "./output/123.png"
    assert os.path.exists(image_path)

def test_task_124(trajectory):
    image_path = "./output/124.png"
    assert os.path.exists(image_path)

def test_task_126(trajectory):
    image_path = "./output/126.png"
    assert os.path.exists(image_path)

def test_task_128(trajectory):
    image_path = "./output/128.xlsx"
    assert os.path.exists(image_path)

def test_task_129(trajectory):
    image_path = "./output/129.csv"
    assert os.path.exists(image_path)

def test_task_130(trajectory):
    final_answer=trajectory[-1]['content']
    assert ('llama' in final_answer or 'Llama' in final_answer)

def test_task_131(trajectory):
    final_answer=trajectory[-1]['content']
    assert ('新希望' in final_answer or "猪周期" in final_answer or "饲料" in final_answer or 'pig' in final_answer or 'New Hope' in final_answer or 'new hope' in final_answer)


def test_task_132(trajectory):
    final_answer=trajectory[-1]['content']
    assert '%' in final_answer

def test_task_133(trajectory):
    final_answer=trajectory[-1]['content']
    assert '%' in final_answer

def test_task_134(trajectory):
    final_answer=trajectory[-1]['content']
    ans="10715086071862673209484250490600018105614048117055336074437503883703510511249361224931983788156958581275946729175531468251871452856923140435984577574698574803934567774824230985421074605062371141877954182153046474983581941267398767559165543946077062914571196477686542167660429831652624386837205668069376"
    assert ans in final_answer

def test_task_135(trajectory):
    final_answer=trajectory[-1]['content']
    assert '9.78' in final_answer

def test_task_136(trajectory):
    final_answer=trajectory[-1]['content']
    assert ('2.5' in final_answer or '5/2' in final_answer)

def test_task_137(trajectory):
    final_answer=trajectory[-1]['content']
    assert '8.1' in final_answer

def test_task_138(trajectory):
    final_answer=trajectory[-1]['content']
    assert ('no' in final_answer or 'not' in final_answer) 

def test_task_139(trajectory):
    final_answer=trajectory[-1]['content']
    assert 'x' in final_answer

def test_task_140(trajectory):
    output_folder = "./output/140"
    
    # 检查目标文件夹中是否存在 HTML 文件
    assert os.path.exists(output_folder)
def test_task_141(trajectory):
    output_folder = "./output/141"
    
    # 检查目标文件夹中是否存在 HTML 文件
    html_files_exist = any(file.endswith('.html') for file in os.listdir(output_folder))
    assert html_files_exist

def test_task_142(trajectory):
    output_folder = "./output/142"
    
    # 检查目标文件夹中是否存在 HTML 文件
    html_files_exist = any(file.endswith('.html') for file in os.listdir(output_folder))
    assert html_files_exist

def test_task_143(trajectory):
    output_folder = "./output/143"
    
    # 检查目标文件夹中是否存在 HTML 文件
    html_files_exist = any(file.endswith('.html') for file in os.listdir(output_folder))
    assert html_files_exist


def test_task_144(trajectory):
    image_path = "./output/144.wav"
    assert os.path.exists(image_path)

def test_task_145(trajectory):
    image_path = "./output/145.png"
    assert os.path.exists(image_path)

import wave
import numpy as np

def read_wave_file(file_path):
    with wave.open(file_path, 'rb') as wf:
        # 获取音频文件的参数
        n_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        frame_rate = wf.getframerate()
        n_frames = wf.getnframes()

        # 读取音频数据
        audio_data = wf.readframes(n_frames)

        # 将音频数据转换为 numpy 数组
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        audio_array = audio_array / (2**(8*sample_width-1))  # 归一化到 -1 到 1 之间

        return audio_array, frame_rate

def calculate_dbfs(audio_array):
    # 计算音频信号的均方根（RMS）值
    rms = np.sqrt(np.mean(audio_array**2))
    # 将 RMS 转换为分贝（dBFS）
    dbfs = 20 * np.log10(rms)
    return dbfs

def test_task_146(trajectory):
    audio_path = "./output/146.wav"
    ref_path = "./data/Ghostrifter Official - Serenity.wav"
    
    # 读取音频文件
    audio_array, _ = read_wave_file(audio_path)
    ref_audio_array, _ = read_wave_file(ref_path)
    
    # 计算音频的分贝（dBFS）
    audio_dbfs = calculate_dbfs(audio_array)
    ref_audio_dbfs = calculate_dbfs(ref_audio_array)
    
    # 比较音量
    assert ref_audio_dbfs < audio_dbfs

def test_task_147(trajectory):
    audio_path = "./output/147.mp3"
    ref_path = "./data/Ghostrifter Official - Serenity.mp3"
    
    assert os.path.exists(audio_path)
    

from mutagen.mp3 import MP3
import numpy as np
import struct

def read_mp3_file(file_path):
    audio = MP3(file_path)
    audio_data = audio.tags.get('TXXX:replaygain_track_gain')
    if audio_data:
        gain = float(audio_data.text[0].split()[0])
    else:
        gain = 0
    return gain

def test_task_149(trajectory):
    audio_path = "./output/149.mp3"
    ref_path = "./data/Ghostrifter Official - Serenity.mp3"
    
    audio_gain = read_mp3_file(audio_path)
    ref_audio_gain = read_mp3_file(ref_path)
    
    assert ref_audio_gain > audio_gain
from mutagen.mp3 import MP3

def get_mp3_duration(file_path):
    audio = MP3(file_path)
    return audio.info.length * 1000  # 持续时间以毫秒为单位

def test_task_150(trajectory):
    audio_path = "./output/150.mp3"
    ref_path = "./data/Ghostrifter Official - Serenity.mp3"
    
    audio_duration = get_mp3_duration(audio_path)
    ref_audio_duration = get_mp3_duration(ref_path)
    
    assert audio_duration < ref_audio_duration
   

def test_task_151(trajectory):
    assert os.path.exists("./output/151/")

def test_task_152(trajectory):
    assert os.path.exists("./output/152.mp3")
