import os
import subprocess
import sys
import time


def fix_wechat_version(wechat_version_fix_path):
    """
    This function is to fix the WeChat version
    :return: True if success, Flase if failed.
    """
    command = f"python {wechat_version_fix_path}"

    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')

    result = ''.join(result.communicate())
    print(result)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    arguments = sys.argv

    subprocess.Popen(f"{arguments[1]} {arguments[2]} {arguments[3]}", shell=True, encoding='utf-8')
    time.sleep(10)

    fix_wechat_version(arguments[4])
