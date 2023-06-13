from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DingUserModel(Base):
    __tablename__ = 'ding_users'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='用户ID，自增主键')
    name = Column(String(255), nullable=False, default='', comment='用户名')
    dept_id = Column(Integer, nullable=False, comment='部门ID')
    dept_name = Column(String(255), nullable=False, comment='部门名称')
    title = Column(String(255), nullable=False, comment='职位')
    userid = Column(String(255), nullable=False, comment='用户ID')
    unionid = Column(String(255), nullable=False, comment='UnionID')
    telephone = Column(String(255), nullable=False, comment='电话号码')
    org_email = Column(String(255), nullable=False, comment='机构邮箱')
    email = Column(String(255), nullable=False, comment='邮箱')
    mobile = Column(String(255), nullable=False, comment='手机号码')
    leader = Column(Boolean, nullable=False, default=False, comment='是否领导')
    boss = Column(Boolean, nullable=False, default=False, comment='是否老板')
    is_deleted = Column(Boolean, nullable=False, default=False, comment='是否删除')
    # 创建表的SQL语句
    create_table_sql = """
    drop table if exists ding_users;
    CREATE TABLE ding_users (
        `id` INT PRIMARY KEY AUTO_INCREMENT,
        `name` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '用户名',
        `dept_id` INT NOT NULL DEFAULT 0 COMMENT '部门ID',
        `dept_name` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '部门名称',
        `title` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '职位',
        `userid` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '用户ID',
        `unionid` VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'UnionID',
        `telephone` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '电话号码',
        `org_email` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '机构邮箱',
        `email` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '邮箱',
        `mobile` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '手机号码',
        `leader` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否领导',
        `boss` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否老板',
        is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除'
    );
    """

    @classmethod
    def update_or_insert(cls, db_session, data_dict):
        # 尝试根据userid找到该用户
        user = db_session.query(cls).filter_by(userid=data_dict['userid']).first()
        if user:
            # 如果已存在，则更新相关字段
            for key, value in data_dict.items():
                setattr(user, key, value)
        else:
            # 如果不存在，则创建一个新的
            user = cls(**data_dict)
            db_session.add(user)
        db_session.commit()
        return user

    @classmethod
    def get_department_users(cls, db_session):
        # 从数据库中获取所有的部门用户
        users = db_session.query(cls).all()
        return users

    @classmethod
    def get_unionid_by_userid(cls, db_session, userid):
        # 根据userid获取unionid
        user = db_session.query(cls).filter_by(userid=userid).first()
        if user:
            return user.unionid
        else:
            return None

    @classmethod
    def get_userid_by_unionid(cls, db_session, unionid):
        # 根据unionid获取userid
        user = db_session.query(cls).filter_by(unionid=unionid).first()
        if user:
            return user.userid
        else:
            return None

    @classmethod
    def get_unionid_by_name(cls, db_session, name):
        # 根据user_name获取unionid
        user = db_session.query(cls).filter_by(name=name).first()
        if user:
            return user.unionid
        else:
            return None

    @classmethod
    def get_user_by_unionid(cls, db_session, unionid):
        # 根据unionid获取用户
        user = db_session.query(cls).filter_by(unionid=unionid).first()
        if user:
            return user
        else:
            return None
