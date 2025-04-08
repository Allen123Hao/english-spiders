import argparse
import os
import sys
import logging

try:
    from .importer import CambridgeDictImporter
    print("使用相对路径包")
except ImportError:
    # 当作为脚本直接运行时，添加父目录到 Python 路径
    print("使用绝对路径包")
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(parent_dir)
    from dict_data_importer.data_importer.importer import CambridgeDictImporter

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cambridge_dict_import.log')
    ]
)

logger = logging.getLogger(__name__)

def run_import(input_path: str, dict_uuid: str):
    if not dict_uuid:
        raise ValueError("必须提供词典UUID")

    if not input_path:
        raise ValueError("必须提供输入路径")
    
    # 将输入路径转换为绝对路径
    input_path = os.path.abspath(input_path)
    
    if not os.path.exists(input_path):
        logger.error(f"错误: 路径 '{input_path}' 不存在")
        return

    importer = CambridgeDictImporter(dict_uuid=dict_uuid)
    
    if os.path.isfile(input_path):
        logger.info(f"开始导入文件: {input_path}")
        importer.import_file(input_path)
        logger.info(f"完成导入文件: {input_path}")
    elif os.path.isdir(input_path):
        logger.info(f"开始导入目录: {input_path}")
        importer.import_directory(input_path)
        logger.info(f"完成导入目录: {input_path}")
    else:
        logger.error(f"错误: '{input_path}' 既不是文件也不是目录")


def main():
    parser = argparse.ArgumentParser(
        description='导入剑桥词典数据到数据库')
    
    # 没有 -- 前缀的参数是位置参数（positional argument），必须按顺序提供
    parser.add_argument(
        'input_path',
        help='JSON文件或目录的路径（必需）'
    )

    # 有 -- 前缀的参数是可选参数（optional argument），可以按顺序提供，也可以通过 --key=value 的形式提供
    parser.add_argument(
        '--dict-uuid',
        required=True,
        help='指定词典的UUID（必需）'
    )
    
    try:
        args = parser.parse_args()
        run_import(args.input_path, args.dict_uuid)
    except Exception as e:
        parser.error(str(e))


if __name__ == '__main__':
    # 如果有命令行参数，使用命令行模式
    if len(sys.argv) > 1:
        main()
    # 否则使用直接设置的路径（用于调试）
    else:
        input_path = "../../cambridge_dict/cambridge_dict/spiders/output/stats.json"  # 在这里修改你要导入的路径
        debug_dict_uuid = "74647342-8698-4cac-a666-70b3e601f1fa"  # 在这里设置调试用的词典UUID
        logger.info(f"调试模式：使用路径 '{input_path}' 和词典UUID '{debug_dict_uuid}'")
        run_import(input_path, debug_dict_uuid) 