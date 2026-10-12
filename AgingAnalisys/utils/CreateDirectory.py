import logging
import os
from pathlib import Path


class CreateDirectory:
    def __init__(self, images_folder='imagens_plottadas', 
        logs_folder='logs_monitoramento', logs_erro='logs_erros'
    ):
        if not Path(images_folder).exists():
            Path(images_folder).mkdir()
            logging.log(msg='Diretório 1 criado com sucesso.', level=3)
        else:
            logging.log(msg='verificação de diretorio 1 feita', level=3)
            
        if not Path(logs_folder).exists():
            Path(logs_folder).mkdir()
            logging.log(msg='Diretório 2 criado com sucesso.', level=3)
            
        else:
            logging.log(msg='verificação de diretorio 2 feita\n', level=3)
            
        if not Path(logs_erro).exists():
            Path(logs_erro).mkdir()
            logging.log(msg='Diretório 3 criado com sucesso.', level=3)
            
        else:
            logging.log(msg='verificação de diretorio 3 feita\n', level=3)


    def encontrarPastaLogs(self, diretorioBase='', padrao=''):
        for root, dirs, files in os.walk(diretorioBase):
            for dir_name in dirs:
                if padrao in dir_name:
                    return os.path.join(root, dir_name)
        return None
    
    
    def encontrarArquivoLogs(self, diretorioBase='', padrao=''):
        for root, _, files in os.walk(diretorioBase):
            for file_name in files:
                if padrao in file_name:
                    return os.path.join(root, file_name)
        return None