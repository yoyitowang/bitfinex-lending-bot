# Data Models for Bitfinex Lending Automation System

## Domain Models

### Core Entities

#### LendingOffer (借貸報價)
```python
@dataclass(frozen=True)
class LendingOffer:
    """借貸報價實體"""
    id: Optional[str] = None
    user_id: str = ""
    symbol: str = ""  # fUSD, fBTC, etc.
    amount: Decimal = Decimal('0')
    rate: Decimal = Decimal('0')  # Daily rate
    period: int = 2  # Days
    status: str = "pending"  # pending, active, completed, cancelled
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        """業務規則驗證"""
        return (
            self.amount >= Decimal('150') and  # Bitfinex minimum
            self.rate > Decimal('0') and
            self.period in [2, 7, 14, 30, 60, 90, 120, 180, 365] and
            self.symbol.startswith('f') and
            len(self.symbol) > 1
        )

    def daily_earnings(self) -> Decimal:
        """計算日收益"""
        return self.amount * self.rate

    def annual_earnings(self) -> Decimal:
        """計算年收益"""
        return self.daily_earnings() * Decimal('365')
```

#### Portfolio (投資組合)
```python
@dataclass
class Portfolio:
    """投資組合實體"""
    user_id: str
    total_lent: Decimal = Decimal('0')
    total_earned: Decimal = Decimal('0')
    active_positions: List[LendingOffer] = field(default_factory=list)
    completed_positions: List[LendingOffer] = field(default_factory=list)

    def add_position(self, offer: LendingOffer) -> None:
        """添加新頭寸"""
        if offer.status == "active":
            self.active_positions.append(offer)
            self.total_lent += offer.amount
        elif offer.status == "completed":
            self.completed_positions.append(offer)

    def calculate_daily_income(self) -> Decimal:
        """計算當前日收益"""
        return sum(pos.daily_earnings() for pos in self.active_positions)

    def calculate_total_return(self) -> Decimal:
        """計算總回報率"""
        if self.total_lent == 0:
            return Decimal('0')
        return (self.total_earned / self.total_lent) * Decimal('100')
```

#### MarketData (市場數據)
```python
@dataclass(frozen=True)
class MarketData:
    """市場數據實體"""
    symbol: str
    timestamp: datetime
    best_bid_rate: Decimal = Decimal('0')
    best_bid_amount: Decimal = Decimal('0')
    best_bid_period: int = 2
    best_ask_rate: Decimal = Decimal('0')
    best_ask_amount: Decimal = Decimal('0')
    best_ask_period: int = 2
    daily_change: Decimal = Decimal('0')
    last_price: Decimal = Decimal('0')
    volume_24h: Decimal = Decimal('0')

    def bid_annual_rate(self) -> Decimal:
        """買方年化利率"""
        return self.best_bid_rate * Decimal('365')

    def ask_annual_rate(self) -> Decimal:
        """賣方年化利率"""
        return self.best_ask_rate * Decimal('365')

    def spread_percentage(self) -> Decimal:
        """買賣價差百分比"""
        if self.best_ask_rate == 0:
            return Decimal('0')
        return ((self.best_ask_rate - self.best_bid_rate) / self.best_ask_rate) * Decimal('100')
```

## Value Objects

#### Money (金錢)
```python
@dataclass(frozen=True)
class Money:
    """金錢值物件"""
    amount: Decimal
    currency: str

    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Currency mismatch: {self.currency} vs {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: Union[int, float, Decimal]) -> 'Money':
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def to_string(self) -> str:
        return f"{self.amount:,.2f} {self.currency}"
```

#### Percentage (百分比)
```python
@dataclass(frozen=True)
class Percentage:
    """百分比值物件"""
    value: Decimal  # 0.05 = 5%

    def to_decimal(self) -> Decimal:
        """轉換為小數"""
        return self.value

    def to_percentage_string(self) -> str:
        """轉換為百分比字符串"""
        return f"{self.value * 100:.2f}%"

    def apply_to(self, amount: Decimal) -> Decimal:
        """應用到金額"""
        return amount * self.value
```

#### TimePeriod (時間週期)
```python
@dataclass(frozen=True)
class TimePeriod:
    """時間週期值物件"""
    days: int

    def to_hours(self) -> int:
        return self.days * 24

    def to_seconds(self) -> int:
        return self.days * 24 * 60 * 60

    def __str__(self) -> str:
        if self.days < 30:
            return f"{self.days}d"
        elif self.days < 365:
            months = self.days // 30
            return f"{months}mo"
        else:
            years = self.days // 365
            return f"{years}y"
```

## API Data Transfer Objects

### Request DTOs

#### SubmitLendingOfferRequest
```python
@dataclass
class SubmitLendingOfferRequest:
    """提交借貸報價請求"""
    symbol: str
    amount: Decimal
    rate: Decimal
    period: int

    def __post_init__(self):
        """驗證初始化"""
        if not self.symbol.startswith('f'):
            raise ValueError("Symbol must start with 'f'")
        if self.amount < Decimal('150'):
            raise ValueError("Amount must be at least 150")
        if self.rate <= 0:
            raise ValueError("Rate must be positive")
```

#### PortfolioQueryRequest
```python
@dataclass
class PortfolioQueryRequest:
    """投資組合查詢請求"""
    user_id: str
    include_completed: bool = False
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
```

### Response DTOs

#### LendingOfferResponse
```python
@dataclass
class LendingOfferResponse:
    """借貸報價響應"""
    offer_id: str
    status: str
    symbol: str
    amount: Decimal
    rate: Decimal
    period: int
    created_at: datetime
    estimated_daily_earnings: Decimal
    estimated_annual_earnings: Decimal

    @classmethod
    def from_entity(cls, offer: LendingOffer) -> 'LendingOfferResponse':
        """從實體創建響應"""
        return cls(
            offer_id=offer.id or "",
            status=offer.status,
            symbol=offer.symbol,
            amount=offer.amount,
            rate=offer.rate,
            period=offer.period,
            created_at=offer.created_at,
            estimated_daily_earnings=offer.daily_earnings(),
            estimated_annual_earnings=offer.annual_earnings()
        )
```

#### PortfolioResponse
```python
@dataclass
class PortfolioResponse:
    """投資組合響應"""
    user_id: str
    summary: Dict[str, Any]
    active_positions: List[LendingOfferResponse]
    completed_positions: List[LendingOfferResponse]
    performance_metrics: Dict[str, Any]

    @classmethod
    def from_portfolio(cls, portfolio: Portfolio) -> 'PortfolioResponse':
        """從投資組合實體創建響應"""
        return cls(
            user_id=portfolio.user_id,
            summary={
                "total_lent": str(portfolio.total_lent),
                "total_earned": str(portfolio.total_earned),
                "active_positions_count": len(portfolio.active_positions),
                "completed_positions_count": len(portfolio.completed_positions),
                "current_daily_income": str(portfolio.calculate_daily_income()),
                "total_return_percentage": str(portfolio.calculate_total_return())
            },
            active_positions=[
                LendingOfferResponse.from_entity(pos)
                for pos in portfolio.active_positions
            ],
            completed_positions=[
                LendingOfferResponse.from_entity(pos)
                for pos in portfolio.completed_positions
            ],
            performance_metrics={
                "total_return_rate": str(portfolio.calculate_total_return()),
                "daily_income": str(portfolio.calculate_daily_income()),
                "active_amount": str(sum(pos.amount for pos in portfolio.active_positions))
            }
        )
```

## Database Models

### SQLAlchemy Models (for PostgreSQL)

#### User Model
```python
class User(Base):
    """用戶數據庫模型"""
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lending_offers = relationship("LendingOffer", back_populates="user")
    portfolios = relationship("Portfolio", back_populates="user")
```

#### LendingOffer Model
```python
class LendingOfferModel(Base):
    """借貸報價數據庫模型"""
    __tablename__ = "lending_offers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False)
    amount = Column(DECIMAL(precision=20, scale=8), nullable=False)
    rate = Column(DECIMAL(precision=10, scale=8), nullable=False)
    period = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="lending_offers")

    def to_entity(self) -> LendingOffer:
        """轉換為領域實體"""
        return LendingOffer(
            id=self.id,
            user_id=self.user_id,
            symbol=self.symbol,
            amount=Decimal(str(self.amount)),
            rate=Decimal(str(self.rate)),
            period=self.period,
            status=self.status,
            created_at=self.created_at,
            executed_at=self.executed_at,
            completed_at=self.completed_at
        )
```

## Cache Models (Redis)

### Market Data Cache Structure
```
market:{symbol} → {
  "best_bid_rate": "0.00015",
  "best_bid_amount": "10000.00",
  "best_ask_rate": "0.00016",
  "timestamp": "2024-01-01T12:00:00Z",
  "ttl": 300
}
```

### User Session Cache Structure
```
session:{user_id} → {
  "user_id": "user123",
  "last_activity": "2024-01-01T12:00:00Z",
  "preferences": {"theme": "dark", "currency": "USD"}
}
```

## Validation Rules

### Business Rules
1. **Minimum Order Amount**: All lending offers must be ≥ 150 units
2. **Valid Symbols**: Only f-prefixed symbols (fUSD, fBTC, fETH, etc.)
3. **Valid Periods**: Only predefined periods (2, 7, 14, 30, 60, 90, 120, 180, 365 days)
4. **Rate Bounds**: Rates must be > 0 and reasonable for market conditions
5. **Balance Checks**: Orders cannot exceed available wallet balance

### Data Integrity Rules
1. **Referential Integrity**: All foreign keys must reference valid entities
2. **Temporal Consistency**: executed_at < completed_at where applicable
3. **Amount Precision**: All monetary values stored with appropriate precision
4. **Status Transitions**: Valid state transitions only (pending → active → completed/cancelled)

## Migration Strategy

### From Current File-based to Database
1. **Schema Creation**: Create initial PostgreSQL schema
2. **Data Migration**: Import existing configuration and historical data
3. **Dual Write**: Write to both old and new systems during transition
4. **Feature Flags**: Gradually enable database features
5. **Cleanup**: Remove file-based storage after successful migration

### Performance Considerations
1. **Indexing Strategy**: Proper indexes on frequently queried columns
2. **Partitioning**: Time-based partitioning for historical data
3. **Connection Pooling**: Efficient database connection management
4. **Caching Strategy**: Multi-level caching to reduce database load

This data model provides a solid foundation for the Clean Architecture implementation, ensuring type safety, business rule enforcement, and scalable data access patterns.