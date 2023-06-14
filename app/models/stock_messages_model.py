from sqlalchemy import Column, Integer, String, Boolean, DateTime,Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class StockMessageModel(Base):
    __tablename__ = 'stock_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    unkey = Column(String(64), nullable=False, comment='去重值')
    content_type = Column(Integer, nullable=False, default=0, comment='内容类型')
    trade = Column(String(64), nullable=False, default='', comment='交易类型')
    main_content = Column(Text, nullable=True, default='', comment='主要内容')
    attached_content = Column(String(255), nullable=False, default='', comment='附加内容')
    stock_code = Column(String(10), nullable=False, default='', comment='股票代码')
    sec_id = Column(String(20), nullable=False, default='', comment='证券 ID')
    company = Column(String(64), nullable=False, default='', comment='公司简称')
    board_type = Column(String(64), nullable=False, default='', comment='板块类型')
    key_word = Column(String(64), nullable=False, default='', comment='关键字')
    update_date = Column(DateTime, comment='更新时间')
    pub_date = Column(DateTime, comment='发布时间')
    remind_status = Column(Boolean, nullable=False, default=False, comment='提醒状态1已提醒0未提醒')

    def __repr__(self):
        return f"<StockMessageModel(id={self.id}, main_content='{self.main_content}', stock_code='{self.stock_code}')>"

    @classmethod
    def update_or_insert(cls, db_session, data_dict):
        item = db_session.query(cls).filter_by(unkey=data_dict['unkey']).first()
        if item:
            # 如果已存在，则更新相关字段
            for key, value in data_dict.items():
                setattr(item, key, value)
        else:
            # 如果不存在，则创建一个新的
            item = cls(**data_dict)
            db_session.add(item)
        db_session.commit()
        return item
