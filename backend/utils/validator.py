"""
BASIX IP-Marketplace: Advanced Validation System
Senior-level validation and verification for marketplace operations
"""

import re
import json
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
from web3 import Web3
import ipaddress

class ValidationError(Exception):
    """Custom validation error with detailed context"""
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(self.message)

class AssetValidator:
    """Comprehensive asset validation system"""
    
    def __init__(self):
        self.valid_asset_types = ['NFT', 'Phygital', 'Digital', 'RealWorldAsset']
        self.valid_regions = ['Mumbai', 'Delhi', 'Bangalore', 'Global', 'International']
        self.valid_utility_features = [
            'streaming_rights', 'revenue_share', 'exclusive_access', 
            'commercial_license', 'platform_access', 'ai_credits',
            'rental_income', 'virtual_tours', 'metaverse_presence',
            'usage_rights', 'tracking_data', 'maintenance_records'
        ]
    
    def validate_asset_creation(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complete asset creation data"""
        errors = []
        
        # Required fields validation
        required_fields = ['name', 'asset_type', 'price', 'creators']
        for field in required_fields:
            if field not in asset_data or not asset_data[field]:
                errors.append(ValidationError(f"Missing required field: {field}", field))
        
        if errors:
            raise ValidationError(f"Asset validation failed: {len(errors)} errors", code="VALIDATION_FAILED")
        
        # Validate individual components
        self._validate_asset_name(asset_data.get('name', ''))
        self._validate_asset_type(asset_data.get('asset_type', ''))
        self._validate_price(asset_data.get('price', 0))
        self._validate_creators(asset_data.get('creators', {}))
        self._validate_metadata(asset_data.get('metadata', {}))
        self._validate_utility_features(asset_data.get('utility_features', []))
        
        return {'valid': True, 'asset_data': asset_data}
    
    def _validate_asset_name(self, name: str) -> None:
        """Validate asset name"""
        if not name or not isinstance(name, str):
            raise ValidationError("Asset name is required and must be a string", "name")
        
        if len(name.strip()) < 3:
            raise ValidationError("Asset name must be at least 3 characters long", "name")
        
        if len(name) > 200:
            raise ValidationError("Asset name cannot exceed 200 characters", "name")
        
        # Check for invalid characters
        if re.search(r'[<>:"/\\|?*]', name):
            raise ValidationError("Asset name contains invalid characters", "name")
    
    def _validate_asset_type(self, asset_type: str) -> None:
        """Validate asset type"""
        if asset_type not in self.valid_asset_types:
            raise ValidationError(
                f"Invalid asset type. Must be one of: {', '.join(self.valid_asset_types)}", 
                "asset_type"
            )
    
    def _validate_price(self, price: Union[float, Decimal, str]) -> None:
        """Validate asset price"""
        try:
            price_decimal = Decimal(str(price))
            if price_decimal <= 0:
                raise ValidationError("Price must be greater than 0", "price")
            
            if price_decimal > Decimal('1000000'):  # 1M limit
                raise ValidationError("Price cannot exceed 1,000,000", "price")
                
        except (ValueError, TypeError):
            raise ValidationError("Invalid price format", "price")
    
    def _validate_creators(self, creators: Dict[str, float]) -> None:
        """Validate creator ownership structure"""
        if not creators:
            raise ValidationError("At least one creator must be specified", "creators")
        
        total_percentage = 0
        for creator_id, percentage in creators.items():
            if not isinstance(percentage, (int, float)) or percentage <= 0:
                raise ValidationError(f"Invalid percentage for creator {creator_id}", "creators")
            total_percentage += percentage
        
        if abs(total_percentage - 100.0) > 0.01:  # Allow small floating point errors
            raise ValidationError("Creator percentages must sum to 100%", "creators")
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> None:
        """Validate asset metadata"""
        if not isinstance(metadata, dict):
            raise ValidationError("Metadata must be a dictionary", "metadata")
        
        # Check metadata size limit (1MB)
        metadata_size = len(json.dumps(metadata))
        if metadata_size > 1024 * 1024:
            raise ValidationError("Metadata size exceeds 1MB limit", "metadata")
    
    def _validate_utility_features(self, features: List[str]) -> None:
        """Validate utility features"""
        if not isinstance(features, list):
            raise ValidationError("Utility features must be a list", "utility_features")
        
        for feature in features:
            if feature not in self.valid_utility_features:
                raise ValidationError(f"Invalid utility feature: {feature}", "utility_features")

class CreatorValidator:
    """Creator profile validation system"""
    
    def __init__(self):
        self.valid_regions = ['Mumbai', 'Delhi', 'Bangalore', 'Global', 'International']
        self.valid_skills = [
            'AI_Art', 'Digital_Design', 'Music_Production', 'Photography', 
            'Video_Editing', 'AI_Platform', 'Development', 'Blockchain',
            'Smart_Contracts', 'UI_UX', '3D_Modeling', 'Animation'
        ]
    
    def validate_creator_registration(self, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate creator registration data"""
        errors = []
        
        # Required fields
        required_fields = ['name', 'wallet_address', 'email']
        for field in required_fields:
            if field not in creator_data or not creator_data[field]:
                errors.append(ValidationError(f"Missing required field: {field}", field))
        
        if errors:
            raise ValidationError(f"Creator validation failed: {len(errors)} errors", code="VALIDATION_FAILED")
        
        # Validate individual components
        self._validate_creator_name(creator_data.get('name', ''))
        self._validate_wallet_address(creator_data.get('wallet_address', ''))
        self._validate_email(creator_data.get('email', ''))
        self._validate_region(creator_data.get('region', 'Global'))
        self._validate_skills(creator_data.get('skills', []))
        
        return {'valid': True, 'creator_data': creator_data}
    
    def _validate_creator_name(self, name: str) -> None:
        """Validate creator name"""
        if not name or not isinstance(name, str):
            raise ValidationError("Creator name is required and must be a string", "name")
        
        if len(name.strip()) < 2:
            raise ValidationError("Creator name must be at least 2 characters long", "name")
        
        if len(name) > 100:
            raise ValidationError("Creator name cannot exceed 100 characters", "name")
    
    def _validate_wallet_address(self, address: str) -> None:
        """Validate Ethereum wallet address"""
        if not address or not isinstance(address, str):
            raise ValidationError("Wallet address is required", "wallet_address")
        
        if not Web3.isAddress(address):
            raise ValidationError("Invalid Ethereum wallet address format", "wallet_address")
    
    def _validate_email(self, email: str) -> None:
        """Validate email address"""
        if not email or not isinstance(email, str):
            raise ValidationError("Email is required", "email")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format", "email")
    
    def _validate_region(self, region: str) -> None:
        """Validate creator region"""
        if region not in self.valid_regions:
            raise ValidationError(
                f"Invalid region. Must be one of: {', '.join(self.valid_regions)}", 
                "region"
            )
    
    def _validate_skills(self, skills: List[str]) -> None:
        """Validate creator skills"""
        if not isinstance(skills, list):
            raise ValidationError("Skills must be a list", "skills")
        
        for skill in skills:
            if skill not in self.valid_skills:
                raise ValidationError(f"Invalid skill: {skill}", "skills")

class TransactionValidator:
    """Transaction validation system"""
    
    def __init__(self):
        self.min_transaction_amount = Decimal('0.001')
        self.max_transaction_amount = Decimal('1000000')
    
    def validate_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate transaction data"""
        errors = []
        
        # Required fields
        required_fields = ['from_address', 'to_address', 'amount', 'transaction_type']
        for field in required_fields:
            if field not in transaction_data:
                errors.append(ValidationError(f"Missing required field: {field}", field))
        
        if errors:
            raise ValidationError(f"Transaction validation failed: {len(errors)} errors", code="VALIDATION_FAILED")
        
        # Validate individual components
        self._validate_addresses(transaction_data.get('from_address'), transaction_data.get('to_address'))
        self._validate_amount(transaction_data.get('amount', 0))
        self._validate_transaction_type(transaction_data.get('transaction_type', ''))
        
        return {'valid': True, 'transaction_data': transaction_data}
    
    def _validate_addresses(self, from_address: str, to_address: str) -> None:
        """Validate transaction addresses"""
        if not Web3.isAddress(from_address):
            raise ValidationError("Invalid from address", "from_address")
        
        if not Web3.isAddress(to_address):
            raise ValidationError("Invalid to address", "to_address")
        
        if from_address == to_address:
            raise ValidationError("From and to addresses cannot be the same", "addresses")
    
    def _validate_amount(self, amount: Union[float, Decimal, str]) -> None:
        """Validate transaction amount"""
        try:
            amount_decimal = Decimal(str(amount))
            if amount_decimal < self.min_transaction_amount:
                raise ValidationError(f"Amount must be at least {self.min_transaction_amount}", "amount")
            
            if amount_decimal > self.max_transaction_amount:
                raise ValidationError(f"Amount cannot exceed {self.max_transaction_amount}", "amount")
                
        except (ValueError, TypeError):
            raise ValidationError("Invalid amount format", "amount")
    
    def _validate_transaction_type(self, tx_type: str) -> None:
        """Validate transaction type"""
        valid_types = ['purchase', 'transfer', 'stake', 'unstake', 'royalty_payment']
        if tx_type not in valid_types:
            raise ValidationError(f"Invalid transaction type. Must be one of: {', '.join(valid_types)}", "transaction_type")

class OwnershipValidator:
    """Ownership transfer validation system"""
    
    def validate_ownership_transfer(self, transfer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ownership transfer request"""
        errors = []
        
        # Required fields
        required_fields = ['asset_id', 'from_creator', 'to_creator', 'percentage']
        for field in required_fields:
            if field not in transfer_data:
                errors.append(ValidationError(f"Missing required field: {field}", field))
        
        if errors:
            raise ValidationError(f"Ownership transfer validation failed: {len(errors)} errors", code="VALIDATION_FAILED")
        
        # Validate percentage
        percentage = transfer_data.get('percentage', 0)
        if not isinstance(percentage, (int, float)) or percentage <= 0 or percentage > 100:
            raise ValidationError("Percentage must be between 0 and 100", "percentage")
        
        return {'valid': True, 'transfer_data': transfer_data}

class StakingValidator:
    """Staking validation system"""
    
    def __init__(self):
        self.valid_durations = [30, 90, 365]  # days
        self.min_stake_amount = Decimal('0.1')
        self.max_stake_amount = Decimal('100000')
    
    def validate_staking_request(self, staking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate staking request"""
        errors = []
        
        # Required fields
        required_fields = ['asset_id', 'amount', 'duration']
        for field in required_fields:
            if field not in staking_data:
                errors.append(ValidationError(f"Missing required field: {field}", field))
        
        if errors:
            raise ValidationError(f"Staking validation failed: {len(errors)} errors", code="VALIDATION_FAILED")
        
        # Validate amount
        amount = staking_data.get('amount', 0)
        try:
            amount_decimal = Decimal(str(amount))
            if amount_decimal < self.min_stake_amount:
                raise ValidationError(f"Stake amount must be at least {self.min_stake_amount}", "amount")
            
            if amount_decimal > self.max_stake_amount:
                raise ValidationError(f"Stake amount cannot exceed {self.max_stake_amount}", "amount")
                
        except (ValueError, TypeError):
            raise ValidationError("Invalid stake amount format", "amount")
        
        # Validate duration
        duration = staking_data.get('duration', 0)
        if duration not in self.valid_durations:
            raise ValidationError(f"Duration must be one of: {', '.join(map(str, self.valid_durations))}", "duration")
        
        return {'valid': True, 'staking_data': staking_data}

# Global validator instances
asset_validator = AssetValidator()
creator_validator = CreatorValidator()
transaction_validator = TransactionValidator()
ownership_validator = OwnershipValidator()
staking_validator = StakingValidator()

def validate_json_schema(schema_class):
    """Decorator for JSON schema validation"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            try:
                # This would integrate with marshmallow schemas
                return f(*args, **kwargs)
            except ValidationError as e:
                return {'error': e.message, 'field': e.field, 'code': e.code}, 400
        return wrapper
    return decorator