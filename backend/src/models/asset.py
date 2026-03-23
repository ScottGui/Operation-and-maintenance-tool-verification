"""
资产台账模型 (CMDB)
定义系统资产的基本信息和管理
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from backend.src.database import Base


class AssetType(str, enum.Enum):
    """
    资产类型枚举
    """
    SERVER = "server"              # 服务器
    DATABASE = "database"          # 数据库
    MIDDLEWARE = "middleware"      # 中间件
    NETWORK = "network"            # 网络设备
    STORAGE = "storage"            # 存储设备
    SECURITY = "security"          # 安全设备
    SOFTWARE = "software"          # 软件
    OTHER = "other"                # 其他


class AssetStatus(str, enum.Enum):
    """
    资产状态枚举
    """
    IN_USE = "in_use"              # 在用
    IDLE = "idle"                  # 闲置
    MAINTENANCE = "maintenance"    # 维护中
    RETIRED = "retired"            # 已下线
    RESERVED = "reserved"          # 预留


class Asset(Base):
    """
    资产台账表
    存储所有IT资产的信息
    """
    __tablename__ = "asset"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="资产ID")
    
    # 资产编号（系统自动生成，如：AST-202403230001）
    asset_no = Column(String(50), unique=True, nullable=False, index=True, comment="资产编号")
    
    # 基本信息
    name = Column(String(100), nullable=False, comment="资产名称")
    asset_type = Column(String(50), nullable=False, comment="资产类型")
    status = Column(String(20), default=AssetStatus.IN_USE.value, comment="资产状态")
    
    # 厂商信息
    vendor = Column(String(100), nullable=True, comment="厂商")
    model = Column(String(100), nullable=True, comment="型号")
    serial_number = Column(String(100), nullable=True, comment="序列号")
    
    # 配置信息（JSON格式存储）
    configuration = Column(Text, nullable=True, comment="配置信息（JSON）")
    
    # 位置信息
    location = Column(String(200), nullable=True, comment="存放位置")
    
    # 关联信息
    service_id = Column(Integer, ForeignKey("service.id"), nullable=True, comment="所属服务ID")
    service = relationship("Service", back_populates="assets")
    
    # 负责人
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=True, comment="负责人ID")
    owner = relationship("User", foreign_keys=[owner_id])
    
    # 购买信息
    purchase_date = Column(DateTime, nullable=True, comment="购买日期")
    warranty_expire_date = Column(DateTime, nullable=True, comment="保修到期日")
    purchase_price = Column(Numeric(15, 2), nullable=True, comment="购买价格")
    
    # IP地址（服务器/网络设备）
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    
    # 备注
    remark = Column(Text, nullable=True, comment="备注")
    
    # 软删除
    is_deleted = Column(Boolean, default=False, comment="是否删除")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(Integer, ForeignKey("user.id"), nullable=True, comment="创建人ID")
    updated_by = Column(Integer, ForeignKey("user.id"), nullable=True, comment="更新人ID")
    
    def __repr__(self):
        return f"<Asset(id={self.id}, asset_no={self.asset_no}, name={self.name})>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "asset_no": self.asset_no,
            "name": self.name,
            "asset_type": self.asset_type,
            "status": self.status,
            "vendor": self.vendor,
            "model": self.model,
            "serial_number": self.serial_number,
            "configuration": self.configuration,
            "location": self.location,
            "service_id": self.service_id,
            "owner_id": self.owner_id,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "warranty_expire_date": self.warranty_expire_date.isoformat() if self.warranty_expire_date else None,
            "purchase_price": float(self.purchase_price) if self.purchase_price else None,
            "ip_address": self.ip_address,
            "remark": self.remark,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def get_asset_type_display(self):
        """获取资产类型显示名称"""
        type_map = {
            AssetType.SERVER.value: "服务器",
            AssetType.DATABASE.value: "数据库",
            AssetType.MIDDLEWARE.value: "中间件",
            AssetType.NETWORK.value: "网络设备",
            AssetType.STORAGE.value: "存储设备",
            AssetType.SECURITY.value: "安全设备",
            AssetType.SOFTWARE.value: "软件",
            AssetType.OTHER.value: "其他",
        }
        return type_map.get(self.asset_type, self.asset_type)
    
    def get_status_display(self):
        """获取状态显示名称"""
        status_map = {
            AssetStatus.IN_USE.value: "在用",
            AssetStatus.IDLE.value: "闲置",
            AssetStatus.MAINTENANCE.value: "维护中",
            AssetStatus.RETIRED.value: "已下线",
            AssetStatus.RESERVED.value: "预留",
        }
        return status_map.get(self.status, self.status)
