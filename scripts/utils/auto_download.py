from ftplib import FTP
import os
def ftpconnect(host, username, password):
    ftp = FTP()
    ftp.set_debuglevel(2)
    ftp.connect(host, 21)
    ftp.login(username, password)
    return ftp

def downloadfile(ftp, remotepath, localpath):
    # 从ftp下载文件
    bufsize = 1024
    fp = open(localpath, 'wb')
    ftp.retrbinary('RETR ' + remotepath, fp.write, bufsize)
    ftp.set_debuglevel(0)
    fp.close()


def uploadfile(ftp, localpath, remotepath):
    # 从本地上传文件到ftp
    bufsize = 1024
    fp = open(localpath, 'rb')
    ftp.storbinary('STOR ' + remotepath, fp, bufsize)
    ftp.set_debuglevel(0)
    fp.close()


def get_file_list(file_path, reverse = False, end=".tcb.zip"):
    """
    :param file_path: the file path where you want to get file
    :return: list, files sorted by name
    """
    dir_list = os.listdir(file_path)
    if not dir_list:
        return
    file_list = []
    for x in dir_list:
        if x.endswith(end):
            file_list.append(x)
    else:
        # 注意，这里使用lambda表达式，将文件按照最后修改时间顺序升序排列
        # os.path.getmtime() 函数是获取文件最后修改时间
        # os.path.getctime() 函数是获取文件最后创建时间
        file_list = sorted(file_list, key=lambda x: os.path.getmtime(os.path.join(file_path, x)),reverse=reverse)
        # dir_list = sorted(dir_list, key=lambda x: int(x[:-4]))  # 按名称排序
        # print(dir_list)
        return file_list

if __name__ == '__main__':
