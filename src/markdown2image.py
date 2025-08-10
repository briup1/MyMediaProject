import requests
from bs4 import BeautifulSoup

# 示例Markdown内容
markdown_content = """
# Hello World
This is a **Markdown** example.
- Item 1
- Item 2
"""

# 目标URL（假设是提交表单的URL）
submit_url = "https://www.strerr.com/cn/markdown2jpg.html"

# 模拟表单提交的参数
data = {
    "markdown": markdown_content,  # Markdown内容
    # 其他可能需要的参数（根据实际页面分析）
}

# 发送POST请求
response = requests.post(submit_url, data=data)

# 检查响应
if response.status_code == 200:
    # 如果成功，解析返回的HTML页面
    soup = BeautifulSoup(response.text, "html.parser")

    # 假设图片URL在某个特定的标签中（需要根据实际页面结构调整）
    img_tag = soup.find("img", {"class": "result-image"})
    if img_tag:
        img_url = img_tag.get("src")
        print(f"图片URL: {img_url}")

        # 下载图片
        img_response = requests.get(img_url)
        if img_response.status_code == 200:
            with open("output.jpg", "wb") as f:
                f.write(img_response.content)
            print("图片已保存为 output.jpg")
        else:
            print("无法下载图片")
    else:
        print("未找到图片URL")
else:
    print(f"请求失败，状态码: {response.status_code}")