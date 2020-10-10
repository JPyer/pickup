import logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s %(filename)s [line:%(lineno)d]] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='device.log',
                    filemode='w')
sg_logger = logging.getLogger(__name__)
