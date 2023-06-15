import time
from app.common import Common
from app.models.stock_messages_model import StockMessageModel

logger = Common.get_app_logger('msg_sender')
db_session = Common.get_global_db_session()
msgs = StockMessageModel.get_unreminded_msg(db_session, 10)
logger.info(f'获取到{len(msgs)}条未提醒消息')
for msg in msgs:
    db_session.query(StockMessageModel).filter_by(id=msg.id).update(
        {'remind_status': 2})
    db_session.commit()
    try:
        msg_content = f"【{msg.key_word}】【{msg.company}】【{msg.trade}】【代码{msg.stock_code}】" \
                      f"\n提问:{msg.main_content}" \
                      f"\n回答:{msg.attached_content}"
        time.sleep(5)
        r = Common.send_ding_msg(msg_content)
        if r:
            logger.info(f"发送成功:{msg.id}")
            db_session.query(StockMessageModel).filter_by(id=msg.id).update(
                {'remind_status': 1})
            db_session.commit()
        else:
            logger.error(f"发送消息失败:{msg.id}")

    except (Exception,) as e:
        logger.error(f"msg:{msg}")
        logger.exception(e)
        continue

    time.sleep(3)
