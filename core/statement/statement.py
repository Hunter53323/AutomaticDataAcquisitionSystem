import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.colors import Color
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
import matplotlib.pyplot as plt
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer
import mysql.connector
from io import BytesIO
from reportlab.platypus import Image
from reportlab.platypus import PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, landscape
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, PageTemplate, Frame
from reportlab.lib.units import inch

try:
    pdfmetrics.registerFont(TTFont("SimHei", "SimHei.ttf"))
except IOError:
    print("字体 'SimHei' 无法加载，请确保字体文件存在。")


# 定义公司名称
COMPANY_NAME = "Haier"


# 连接数据库
def connect_database():
    db_config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "liuqi"),
        "password": os.getenv("DB_PASSWORD", "liuqi9713"),
        "database": os.getenv("DB_NAME", "world"),
    }
    try:
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            print("Successfully connected to the database.")
            # 创建游标对象
            cursor = connection.cursor()

            # 执行SQL查询
            query = "SELECT * FROM 风机数据;"  # 替换为你的表名
            cursor.execute(query)

            # 获取所有查询结果
            records = cursor.fetchall()

            # 打印结果
            for row in records:
                print(row)
            return connection
    except mysql.connector.Error as e:
        print("Error connecting to MySQL Platform:", e)
        sys.exit(0)


# 从数据库获取数据
def fetch_data(connection: mysql.connector.MySQLConnection, parameters):
    try:
        cursor = connection.cursor()
        # 动态构建查询的列名部分，这里我们查询所有列，然后只返回参数指定的列
        columns = ", ".join(parameters)

        # 构建完整的SQL查询语句
        sql = f"SELECT {columns} FROM '风机数据' "

        cursor.execute(sql)
        # 获取查询结果
        result = cursor.fetchall()

        # 从结果中提取指定参数的数据
        extracted_data = [dict(zip(columns.split(", "), row)) for row in result]

        return extracted_data
    except mysql.connector.Error as e:
        print("Error fetching data from MySQL Platform:", e)
        return None


def table_pdf(data):
    # 提取键名作为列名
    headers = [key for key in data[0].keys()]

    # 创建表格数据和样式
    table_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), Color(163 / 255, 190 / 255, 219 / 255)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), "SimHei"),
            ("FONTSIZE", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )

    # 初始化表格列表
    tables = []
    table_data = [headers]
    max_rows_per_page = 15  # 每页最多15条数据

    # 填充表格数据，如果超过15条则创建新的表格
    for row in data:
        table_row = [row[key] for key in headers]
        table_data.append(table_row)
        if len(table_data) - 1 == max_rows_per_page:
            tables.append((table_data, table_style))
            table_data = [headers]  # 重置表格数据，保留表头

    # 添加最后一页的数据（如果有的话）
    if len(table_data) > 1:
        tables.append((table_data, table_style))

    return [(table_data, table_style) for table_data, table_style in tables]


# 定义函数来绘制折线图并将其保存为图片
def draw_line_chart(parameters, data):
    fig, ax = plt.subplots()

    # 设置横坐标（实验次数）
    x_data = [i + 1 for i, row in enumerate(data)]

    # 设置纵坐标（参数值）
    y_data = [row[parameters] if row[parameters] is not None else -1 for row in data]

    # 绘制折线图
    ax.plot(x_data, y_data, label=parameters)
    # 遍历每个点，如果值是-1，则标记一个红色的×
    for i, y in enumerate(y_data):
        if y == -1:
            ax.plot(x_data[i], y_data[i], "x", color="red")
    # ax.set_title(f'{parameters} Trend')
    ax.set_xlabel("实验次数")
    ax.set_ylabel(parameters)
    ax.legend()

    # 保存图表为图片
    buf = BytesIO()
    # 设置中文字体
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 用于正常显示中文字体
    plt.rcParams["axes.unicode_minus"] = False  # 用来正常显示负号
    plt.savefig(buf, format="png", dpi=600, bbox_inches="tight")
    buf.seek(0)

    # 将图片添加到 PDF 中
    img = Image(BytesIO(buf.read()), width=400, height=300)
    return img


# PDF合并文件
def merge_pdfs(paths, output):
    pdf_writer = PdfWriter()

    for path in paths:
        pdf_reader = PdfReader(path)
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

    with open(output, "wb") as out:
        pdf_writer.write(out)

    # 删除原始 PDF 文件
    for path in paths:
        os.remove(path)


def generate_pdf(parameters: list[str], experimenter: str, data: dict[str, any], search_data: dict[str, any], direction_vertical=False):
    """
    :param parameters: 要绘图的参数列表
    :param experimenter: 实验员姓名
    :param data: 所有数据
    :param search_data: 从数据库中获取的数据
    :param direction_vertical: 是否纵向排布
    """
    doc = SimpleDocTemplate("report.pdf", pagesize=letter)

    # 首页内容样式
    first_page_style = ParagraphStyle("FirstPage", fontName="SimHei", fontSize=14, alignment=TA_CENTER, fontWeight="bold")

    title_style = ParagraphStyle("Title", fontName="SimHei", fontSize=36, alignment=TA_CENTER, spaceBefore=10, spaceAfter=18, fontWeight="bold")

    # 创建一个Frame专门用于放置图片，位于页面的左上角
    logo_frame = Frame(
        doc.leftMargin,
        doc.height - doc.topMargin - inch * 2,  # 位于顶部，图片高度为2英寸
        inch * 2,  # 假设图片宽度为2英寸
        inch * 2,  # 假设图片高度为2英寸
        id="logo_frame",
    )

    # 创建一个首页的Frame，位于页面顶部，宽度为页面宽度，高度自定义
    frame1 = Frame(doc.leftMargin, doc.height - doc.bottomMargin - inch * 7, doc.width, inch * 7.5, id="first_page_frame")

    # 定义首页模板
    first_page_template = PageTemplate(
        id="FirstPage",
        frames=[logo_frame, frame1],  # 注意frames列表的顺序
    )

    # 将首页模板添加到文档模板中
    doc.addPageTemplates([first_page_template])

    # 首页内容
    story = [
        Paragraph("电机测试报告", title_style),
        Spacer(1, 200),
        Paragraph(f"公司名称: {COMPANY_NAME}", first_page_style),
        Spacer(1, 12),
        Paragraph(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", first_page_style),
        Spacer(1, 12),
        Paragraph(f"实验员: {experimenter}", first_page_style),
        Spacer(1, 12),
        PageBreak(),
    ]

    # 添加图片到story中，确保它位于logo_frame中
    # TODO: 修改图片路径
    logo_path = "./logo.png"  # 替换为您的图片路径
    logo = Image(logo_path, width=inch * 2, height=inch * 2)  # 设置图片宽高
    story.insert(0, logo)  # 将图片插入到故事列表的开始位置

    if not direction_vertical:
        # 横板PDF

        # 构建首页的PDF
        doc.build(story)

        # 第二页和第三页需要横向排布，创建一个新的PDF文档
        landscape_doc = SimpleDocTemplate("report_landscape.pdf", pagesize=landscape(letter))
        landscape_story = []

        # 第二页展示所有数据，分页处理
        tables = table_pdf(data)
        for table_data, table_style in tables:
            table = Table(table_data)
            table.setStyle(table_style)
            landscape_story.append(table)
            landscape_story.append(PageBreak())

        # 构建第二页和第三页的PDF
        landscape_doc.build(landscape_story)

        # 第四页需要纵向排布，创建另一个新的PDF文档
        portrait_doc = SimpleDocTemplate("report_portrait.pdf", pagesize=letter)
        portrait_story = []

        # 第四页对选择的参数依次开始画图
        for param in parameters:
            chart = draw_line_chart(param, data)
            portrait_story.append(chart)
            portrait_story.append(Spacer(1, 12))  # 添加一些间距

        # 构建第四页的PDF
        portrait_doc.build(portrait_story)

        paths_to_merge = ["report.pdf", "report_landscape.pdf", "report_portrait.pdf"]
        output_file = "merged_report.pdf"
        merge_pdfs(paths_to_merge, output_file)
        # TODO:pdf导出的路径自定义

        # 最后，将三个PDF合并为一个PDF（这一步需要额外的处理）
        print("PDF reports with tables and charts generated successfully.")
    else:
        # 添加一个页面分隔符以开始第2页
        story.append(PageBreak())

        # 第二页展示所有数据，分页处理
        tables = table_pdf(data)
        for table_data, table_style in tables:
            table = Table(table_data)
            table.setStyle(table_style)
            story.append(table)
            story.append(PageBreak())

        # 第四页对选择的参数依次开始画图
        for param in parameters:
            chart = draw_line_chart(param, data)
            story.append(chart)
            story.append(Spacer(1, 12))  # 添加一些间距

        # 构建并保存文档
        doc.build(story)
        print("PDF report with table generated successfully.")


def main():
    experimenter = "Yuxiang Liu"
    motor_name = "示例风机1"
    motor_model = "型号X"
    parameters = ["转速", "功率", "速度环补偿系数", "观测器补偿系数"]
    data = [
        {
            "ID": 1,
            "风机名称": "示例风机1",
            "风机型号": "型号X",
            "转速": 1200,
            "速度环补偿系数": 2.0,
            "电流环带宽": 300.0,
            "观测器补偿系数": 1.6,
            "负载量": 900,
            "功率": 3.0,
            "时间戳": datetime(2024, 7, 13, 10, 1, 23),
        },
        {
            "ID": 2,
            "风机名称": "示例风机1",
            "风机型号": "型号X",
            "转速": 1200,
            "速度环补偿系数": 2.0,
            "电流环带宽": 300.0,
            "观测器补偿系数": 1.2,
            "负载量": 900,
            "功率": 3.0,
            "时间戳": datetime(2024, 7, 13, 10, 1, 25),
        },
        {
            "ID": 3,
            "风机名称": "示例风机1",
            "风机型号": "型号X",
            "转速": 1200,
            "速度环补偿系数": 2.0,
            "电流环带宽": 300.0,
            "观测器补偿系数": 1.2,
            "负载量": 900,
            "功率": 3.0,
            "时间戳": datetime(2024, 7, 13, 10, 1, 27),
        },
        {
            "ID": 4,
            "风机名称": "示例风机2",
            "风机型号": "型号X",
            "转速": 1000,
            "速度环补偿系数": 3.0,
            "电流环带宽": 400.0,
            "观测器补偿系数": 1.5,
            "负载量": 800,
            "功率": 2.0,
            "时间戳": datetime(2024, 7, 13, 10, 1, 51),
        },
        {
            "ID": 5,
            "风机名称": "示例风机2",
            "风机型号": "型号B",
            "转速": 1000,
            "速度环补偿系数": 3.0,
            "电流环带宽": 400.0,
            "观测器补偿系数": 1.5,
            "负载量": 800,
            "功率": 2.0,
            "时间戳": datetime(2024, 7, 13, 10, 1, 53),
        },
        {
            "ID": 6,
            "风机名称": "示例风机2",
            "风机型号": "型号B",
            "转速": 1000,
            "速度环补偿系数": 3.0,
            "电流环带宽": 400.0,
            "观测器补偿系数": 1.5,
            "负载量": 800,
            "功率": 2.0,
            "时间戳": datetime(2024, 7, 13, 10, 1, 55),
        },
        {
            "ID": 7,
            "风机名称": "风机示例3",
            "风机型号": "-1",
            "转速": None,
            "速度环补偿系数": None,
            "电流环带宽": None,
            "观测器补偿系数": None,
            "负载量": None,
            "功率": None,
            "时间戳": datetime(2024, 7, 13, 10, 17, 31),
        },
        {
            "ID": 8,
            "风机名称": "示例风机1",
            "风机型号": "型号A",
            "转速": 1200,
            "速度环补偿系数": 2.0,
            "电流环带宽": 300.0,
            "观测器补偿系数": 1.2,
            "负载量": 900,
            "功率": 3.0,
            "时间戳": datetime(2024, 7, 14, 8, 56, 23),
        },
        {
            "ID": 9,
            "风机名称": "示例风机1",
            "风机型号": "型号X",
            "转速": 1200,
            "速度环补偿系数": 2.0,
            "电流环带宽": 300.0,
            "观测器补偿系数": 1.6,
            "负载量": 900,
            "功率": 3.0,
            "时间戳": datetime(2024, 7, 13, 10, 1, 23),
        },
        {
            "ID": 10,
            "风机名称": "示例风机1",
            "风机型号": "型号X",
            "转速": 1200,
            "速度环补偿系数": 2.0,
            "电流环带宽": 300.0,
            "观测器补偿系数": 1.2,
            "负载量": 900,
            "功率": 3.0,
            "时间戳": datetime(2024, 7, 13, 10, 1, 25),
        },
        {
            "ID": 11,
            "风机名称": "示例风机1",
            "风机型号": "型号X",
            "转速": 1200,
            "速度环补偿系数": 2.0,
            "电流环带宽": 300.0,
            "观测器补偿系数": 1.2,
            "负载量": 900,
            "功率": 3.0,
            "时间戳": datetime(2024, 7, 13, 10, 1, 27),
        },
        {
            "ID": 12,
            "风机名称": "示例风机2",
            "风机型号": "型号X",
            "转速": 1000,
            "速度环补偿系数": 3.0,
            "电流环带宽": 400.0,
            "观测器补偿系数": 1.5,
            "负载量": 800,
            "功率": 2.0,
            "时间戳": datetime(2024, 7, 13, 10, 1, 51),
        },
        {
            "ID": 13,
            "风机名称": "示例风机2",
            "风机型号": "型号B",
            "转速": 1000,
            "速度环补偿系数": 3.0,
            "电流环带宽": 400.0,
            "观测器补偿系数": 1.5,
            "负载量": 800,
            "功率": 2.0,
            "时间戳": datetime(2024, 7, 13, 10, 1, 53),
        },
        {
            "ID": 14,
            "风机名称": "示例风机2",
            "风机型号": "型号B",
            "转速": 1000,
            "速度环补偿系数": 3.0,
            "电流环带宽": 400.0,
            "观测器补偿系数": 1.5,
            "负载量": 800,
            "功率": 2.0,
            "时间戳": datetime(2024, 7, 13, 10, 1, 55),
        },
        {
            "ID": 15,
            "风机名称": "风机示例3",
            "风机型号": "-1",
            "转速": None,
            "速度环补偿系数": None,
            "电流环带宽": None,
            "观测器补偿系数": None,
            "负载量": None,
            "功率": None,
            "时间戳": datetime(2024, 7, 13, 10, 17, 31),
        },
        {
            "ID": 16,
            "风机名称": "示例风机1",
            "风机型号": "型号A",
            "转速": 1200,
            "速度环补偿系数": 2.0,
            "电流环带宽": 300.0,
            "观测器补偿系数": 1.2,
            "负载量": 900,
            "功率": 3.0,
            "时间戳": datetime(2024, 7, 14, 8, 56, 23),
        },
        {
            "ID": 17,
            "风机名称": "示例风机1",
            "风机型号": "型号A",
            "转速": 1200,
            "速度环补偿系数": 2.0,
            "电流环带宽": 300.0,
            "观测器补偿系数": 1.2,
            "负载量": 900,
            "功率": 3.0,
            "时间戳": datetime(2024, 7, 14, 8, 56, 23),
        },
        {
            "ID": 18,
            "风机名称": "示例风机2",
            "风机型号": "型号B",
            "转速": 1000,
            "速度环补偿系数": 3.0,
            "电流环带宽": 400.0,
            "观测器补偿系数": 1.5,
            "负载量": 800,
            "功率": 2.0,
            "时间戳": datetime(2024, 7, 13, 10, 1, 55),
        },
        {
            "ID": 19,
            "风机名称": "风机示例3",
            "风机型号": "-1",
            "转速": None,
            "速度环补偿系数": None,
            "电流环带宽": None,
            "观测器补偿系数": None,
            "负载量": None,
            "功率": None,
            "时间戳": datetime(2024, 7, 13, 10, 17, 31),
        },
        {
            "ID": 20,
            "风机名称": "示例风机1",
            "风机型号": "型号A",
            "转速": 1200,
            "速度环补偿系数": 2.0,
            "电流环带宽": 300.0,
            "观测器补偿系数": 1.2,
            "负载量": 900,
            "功率": 3.0,
            "时间戳": datetime(2024, 7, 14, 8, 56, 23),
        },
    ]

    # 连接数据库
    connection = connect_database()

    # 确保至少输入了一个列名
    if not parameters:
        print("At least one column name is required.")
        return

    # 获取数据
    search_data = fetch_data(connection, parameters)
    if search_data is None:
        print("No data found or error occurred.")
        return

    # 生成PDF报告
    generate_pdf(parameters, experimenter, data, search_data)

    print("Report generated successfully.")


# 输入的自定义信息是一个字典，根据从字典中解析出来的数值罗列到pdf里面
# 根据输入的路径进行导出
# 报表里面可以没有图

if __name__ == "__main__":
    main()
