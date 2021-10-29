
class saveToExcel:
    def __init__(self, excelSavePath, excel, title):
        self.excelSavePath = excelSavePath          # excel的保存路径
        self.excel = excel                       # openpyxl.Workbook()的实例话
        self.sheet = self.excel.create_sheet(title=title)   # 创建工作区
        self.Sheet_line = 1         # 表格的行

    # def CreatExcel(self):


    def SaveSpider(self, spiderName, key_links=[], subdomains=[]):

        def SaveKeyLinks():
            cprint("*"*20+"存储spider关键词数据"+"*"*20, color="green")

        def SaveSubdomains():
            cprint("*"*20+"存储spider子域名数据"+"*"*20, color="green")