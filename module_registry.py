"""
Module Registry for OIC system.
Handles registration, discovery, and metadata management of autonomous modules.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum

from firebase_setup import FirebaseManager


logger = logging.getLogger(__name__)


class ModuleStatus(Enum):
    """Status of a module in the ecosystem."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    ERROR = "error"


class ModuleType(Enum):
    """Types of modules in the ecosystem."""
    DATA_PROCESSOR = "data_processor"
    ML_MODEL = "ml_model"
    API_GATEWAY = "api_gateway"
    STORAGE = "storage"
    ANALYTICS = "analytics"
    ORCHESTRATOR = "orchestrator"
    CUSTOM = "custom"


@dataclass
class ModuleCapability:
    """Represents a capability that a module provides."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore storage."""
        return asdict(self)


@dataclass
class ModuleInterface:
    """Defines how a module can be interacted with."""
    protocol: str  # e.g., "http", "grpc", "websocket"
    endpoint: str
    authentication_required: bool = False
    rate_limit: Optional[int] = None
    timeout_seconds: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore storage."""
        return asdict(self)


@dataclass
class ModuleMetadata:
    """Comprehensive metadata for an OIC module."""
    module_id: str
    name: str
    version: str
    module_type: ModuleType
    status: ModuleStatus = ModuleStatus.ACTIVE
    
    # Core attributes
    capabilities: List[ModuleCapability] = field(default_factory=list)
    interfaces: List[ModuleInterface] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # IDs of dependent modules
    tags: Set[str] = field(default_factory=set)
    
    # Performance metrics
    latency_ms: Optional[float] = None
    success_rate: Optional[float] = None
    throughput: Optional[float] = None
    
    # Discovery metadata
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    health_check_endpoint: Optional[str] = None
    
    # Resource requirements
    memory_mb: Optional[int] = None
    cpu_cores