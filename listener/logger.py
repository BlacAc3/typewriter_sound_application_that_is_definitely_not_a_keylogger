import logging

def get_logger(name, log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(message)s'
    )
    return logging.getLogger(name)
