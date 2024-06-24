import os
import inspect


def mkdir(relative_path: str):
    """
    以调用者文件所在的目录为根目录，创建relative_path的文件夹
    例如：relative_path='Data/sub_Data1'，调用者文件的路径为'D:/python/caller.py'，且D:/python目录下没有其余文件夹，则该函数会创建D:/python/Data文件夹以及D:/python/Data/sub_Data1文件夹
    """
    # 获取调用栈
    frame = inspect.currentframe()
    caller_frame = frame.f_back

    # 获取调用者的文件路径
    caller_file = caller_frame.f_globals['__file__']

    # 获取调用者文件所在的目录
    caller_dir = os.path.dirname(os.path.abspath(caller_file))

    directory = os.path.join(caller_dir, relative_path)

    # 检测目录是否存在
    if not os.path.exists(directory):
        # 如果目录不存在，则创建目录
        os.makedirs(directory)
        print(f"Directory '{directory}' created.")
    else:
        print(f"Directory '{directory}' already exists.")