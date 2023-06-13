from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DepartmentsModel(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='部门ID，自增主键')
    name = Column(String(255), nullable=False,default='', comment='部门名称')
    dept_id = Column(Integer, nullable=False,default=0, comment='部门编号')
    org_dept_owner = Column(String(255), nullable=False,default='', comment='部门负责人')
    parent_id = Column(Integer, nullable=False,default=0, comment='父部门ID')
    created_at = Column(DateTime, comment='创建时间')
    updated_at = Column(DateTime,comment='更新时间')
    is_deleted = Column(Integer, nullable=False, default=0,comment='是否删除，0-未删除，1-已删除')

    # 创建表的SQL语句
    create_table_sql = """
    drop table if exists departments;
    CREATE TABLE departments (
        `id` INT PRIMARY KEY AUTO_INCREMENT,
        `name` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '部门名称',
        `dept_id` INT NOT NULL DEFAULT 0 COMMENT '部门编号',
        `parent_id` INT NOT NULL DEFAULT 0 COMMENT '父部门ID',
        `org_dept_owner` VARCHAR(255) NOT NULL  DEFAULT '' COMMENT '部门负责人',
        `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '是否删除，0-未删除，1-已删除'
    );
    """

    @classmethod
    def update_or_insert(cls, db_session, data_dict):
        # 尝试根据哈希键值找到该事件
        department = db_session.query(cls).filter_by(dept_id=data_dict['dept_id']).first()
        if department:
            # 如果已存在，则更新相关字段
            for key, value in data_dict.items():
                setattr(department, key, value)
        else:
            # 如果不存在该，则创建一个新的
            event = cls(**data_dict)
            db_session.add(event)
        db_session.commit()
        return department

    @classmethod
    def get_departments(cls, db_session):
        # 从数据库中获取所有的部门is_deleted=0
        departments = db_session.query(cls).filter_by(is_deleted=0).all()
        return departments
