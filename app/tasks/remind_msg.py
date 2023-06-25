import time
from app.common import Common
from app.models.stock_messages_model import StockMessageModel

logger = Common.get_app_logger('msg_sender')


def remind_msg():
    db_session = Common.get_global_db_session()
    msgs = StockMessageModel.get_unreminded_msg(db_session, 5)
    logger.info(f'获取到{len(msgs)}条未提醒消息')
    for msg in msgs:
        db_session.query(StockMessageModel).filter_by(id=msg.id).update(
            {'remind_status': 2})
        db_session.commit()

        deny_li = ["暂无", "未涉及", "目前无", "不涉及", "但暂未", "但无", "没有涉及", "未与", '尚未', '暂未',
                   '目前没有'
                   '不直接'
                   ]
        if any(i in msg.attached_content for i in deny_li):
            logger.info(f"不发送消息:{msg.id},内容为否定回复,内容为:{msg.attached_content},否定词为:{deny_li}")
            db_session.query(StockMessageModel).filter_by(id=msg.id).update(
                {'remind_status': 3})
            db_session.commit()
            continue

        try:
            msg_content = f"【关键词:{msg.key_word}】【{msg.company}】【{msg.trade}】【代码{msg.stock_code}】" \
                          f"\n提问:{msg.main_content}" \
                          f"\n回答:{msg.attached_content}-信息来源:互动易"
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

        time.sleep(5)


if __name__ == '__main__':
    remind_msg()
