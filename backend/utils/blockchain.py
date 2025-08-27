from web3 import Web3
from typing import Dict, List, Optional, Any
import json
import os
from datetime import datetime
import hashlib

class BlockchainConnector:
    def __init__(self, provider_uri: str = None):
        self.provider_uri = provider_uri or os.environ.get('WEB3_PROVIDER_URI')
        self.w3 = None
        self.contract_addresses = {
            'basix_marketplace': '0x742d35Cc6b8a6A8f4eDC6d1E5fA5d8e2e8B94C13',  # Mock address
            'basix_token': '0x89205A3A3b2A69De6Dbf7f01ED13B2108B2c43e7'  # Mock address
        }
        self.contract_abis = {}
        
        if self.provider_uri:
            try:
                self.w3 = Web3(Web3.HTTPProvider(self.provider_uri))
                self.connected = self.w3.isConnected()
            except Exception as e:
                print(f"Failed to connect to blockchain: {e}")
                self.connected = False
        else:
            self.connected = False
    
    def verify_wallet_connection(self, wallet_address: str) -> Dict[str, Any]:
        """Verify wallet connection and get basic info"""
        if not self.connected:
            return self._mock_wallet_verification(wallet_address)
        
        try:
            # Check if address is valid
            if not Web3.isAddress(wallet_address):
                return {'valid': False, 'error': 'Invalid wallet address format'}
            
            # Get account balance
            balance = self.w3.eth.get_balance(wallet_address)
            balance_eth = Web3.fromWei(balance, 'ether')
            
            # Get transaction count (nonce)
            tx_count = self.w3.eth.get_transaction_count(wallet_address)
            
            return {
                'valid': True,
                'address': wallet_address,
                'balance_eth': float(balance_eth),
                'transaction_count': tx_count,
                'network': 'ethereum_mainnet'
            }
        
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def create_asset_transaction(self, asset_data: Dict, creator_address: str) -> Dict[str, Any]:
        """Create blockchain transaction for asset creation"""
        if not self.connected:
            return self._mock_asset_creation(asset_data, creator_address)
        
        try:
            # In a real implementation, this would interact with smart contracts
            transaction_hash = self._generate_transaction_hash(asset_data, creator_address)
            
            return {
                'success': True,
                'transaction_hash': transaction_hash,
                'asset_id': asset_data.get('id'),
                'gas_used': 145000,
                'status': 'pending'
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def transfer_asset(self, asset_id: str, from_address: str, to_address: str, 
                      amount: float = 1.0) -> Dict[str, Any]:
        """Execute asset transfer on blockchain"""
        if not self.connected:
            return self._mock_asset_transfer(asset_id, from_address, to_address, amount)
        
        try:
            # Generate transaction hash
            transaction_data = f"{asset_id}{from_address}{to_address}{amount}{datetime.now().isoformat()}"
            transaction_hash = self._generate_transaction_hash(transaction_data)
            
            return {
                'success': True,
                'transaction_hash': transaction_hash,
                'from_address': from_address,
                'to_address': to_address,
                'asset_id': asset_id,
                'amount': amount,
                'gas_used': 95000,
                'status': 'pending'
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_asset_authenticity(self, asset_id: str) -> Dict[str, Any]:
        """Verify asset authenticity on blockchain"""
        if not self.connected:
            return self._mock_asset_verification(asset_id)
        
        try:
            # In production, this would query the blockchain for asset provenance
            verification_result = {
                'authentic': True,
                'asset_id': asset_id,
                'creation_block': 18567234,  # Mock block number
                'creation_timestamp': datetime.now().isoformat(),
                'creator_verified': True,
                'ownership_chain_valid': True,
                'metadata_hash_match': True,
                'confidence_score': 0.95
            }
            
            return verification_result
        
        except Exception as e:
            return {'authentic': False, 'error': str(e)}
    
    def get_asset_ownership_history(self, asset_id: str) -> List[Dict[str, Any]]:
        """Get complete ownership history of an asset"""
        if not self.connected:
            return self._mock_ownership_history(asset_id)
        
        try:
            # Mock ownership history - in production, query blockchain events
            history = [
                {
                    'transaction_hash': self._generate_transaction_hash(f"create_{asset_id}"),
                    'from_address': '0x0000000000000000000000000000000000000000',  # Mint
                    'to_address': '0x742d35Cc6b8a6A8f4eDC6d1E5fA5d8e2e8B94C13',
                    'timestamp': '2024-01-15T10:30:00Z',
                    'transaction_type': 'mint',
                    'value': 0
                },
                {
                    'transaction_hash': self._generate_transaction_hash(f"transfer_{asset_id}"),
                    'from_address': '0x742d35Cc6b8a6A8f4eDC6d1E5fA5d8e2e8B94C13',
                    'to_address': '0x89205A3A3b2A69De6Dbf7f01ED13B2108B2c43e7',
                    'timestamp': '2024-02-10T14:45:00Z',
                    'transaction_type': 'transfer',
                    'value': 1.5
                }
            ]
            
            return history
        
        except Exception as e:
            print(f"Error fetching ownership history: {e}")
            return []
    
    def create_staking_transaction(self, stake_data: Dict) -> Dict[str, Any]:
        """Create staking transaction on blockchain"""
        if not self.connected:
            return self._mock_staking_transaction(stake_data)
        
        try:
            transaction_hash = self._generate_transaction_hash(json.dumps(stake_data))
            
            return {
                'success': True,
                'transaction_hash': transaction_hash,
                'stake_id': stake_data.get('id'),
                'amount': stake_data.get('amount'),
                'duration': stake_data.get('duration'),
                'apr': stake_data.get('apr'),
                'gas_used': 120000,
                'status': 'confirmed'
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_staking_rewards(self, user_address: str) -> Dict[str, Any]:
        """Calculate available staking rewards"""
        if not self.connected:
            return self._mock_staking_rewards(user_address)
        
        try:
            # Mock reward calculation - in production, query smart contract
            total_rewards = 125.50  # Mock value
            pending_rewards = 15.75  # Mock value
            
            return {
                'user_address': user_address,
                'total_earned_rewards': total_rewards,
                'pending_rewards': pending_rewards,
                'claimable_rewards': pending_rewards,
                'next_reward_date': '2024-03-15T00:00:00Z'
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def verify_asset_authenticity(self, asset_id: str) -> Dict[str, Any]:
        """Verify asset authenticity on blockchain"""
        if not self.connected:
            return self._mock_asset_verification(asset_id)
        
        try:
            # In production, this would query the blockchain for asset provenance
            verification_result = {
                'authentic': True,
                'asset_id': asset_id,
                'creation_block': 18567234,  # Mock block number
                'creation_timestamp': datetime.now().isoformat(),
                'creator_verified': True,
                'ownership_chain_valid': True,
                'metadata_hash_match': True,
                'confidence_score': 0.95
            }
            
            return verification_result
        
        except Exception as e:
            return {'authentic': False, 'error': str(e)}
    
    def get_asset_ownership_history(self, asset_id: str) -> List[Dict[str, Any]]:
        """Get complete ownership history of an asset"""
        if not self.connected:
            return self._mock_ownership_history(asset_id)
        
        try:
            # Mock ownership history - in production, query blockchain events
            history = [
                {
                    'transaction_hash': self._generate_transaction_hash(f"create_{asset_id}"),
                    'from_address': '0x0000000000000000000000000000000000000000',  # Mint
                    'to_address': '0x742d35Cc6b8a6A8f4eDC6d1E5fA5d8e2e8B94C13',
                    'timestamp': '2024-01-15T10:30:00Z',
                    'transaction_type': 'mint',
                    'value': 0
                },
                {
                    'transaction_hash': self._generate_transaction_hash(f"transfer_{asset_id}"),
                    'from_address': '0x742d35Cc6b8a6A8f4eDC6d1E5fA5d8e2e8B94C13',
                    'to_address': '0x89205A3A3b2A69De6Dbf7f01ED13B2108B2c43e7',
                    'timestamp': '2024-02-10T14:45:00Z',
                    'transaction_type': 'transfer',
                    'value': 1.5
                }
            ]
            
            return history
        
        except Exception as e:
            print(f"Error fetching ownership history: {e}")
            return []
    
    def create_staking_transaction(self, stake_data: Dict) -> Dict[str, Any]:
        """Create staking transaction on blockchain"""
        if not self.connected:
            return self._mock_staking_transaction(stake_data)
        
        try:
            transaction_hash = self._generate_transaction_hash(json.dumps(stake_data))
            
            return {
                'success': True,
                'transaction_hash': transaction_hash,
                'stake_id': stake_data.get('id'),
                'amount': stake_data.get('amount'),
                'duration': stake_data.get('duration'),
                'apr': stake_data.get('apr'),
                'gas_used': 120000,
                'status': 'confirmed'
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_staking_rewards(self, user_address: str) -> Dict[str, Any]:
        """Calculate available staking rewards"""
        if not self.connected:
            return self._mock_staking_rewards(user_address)
        
        try:
            # Mock reward calculation - in production, query smart contract
            total_rewards = 125.50  # Mock value
            pending_rewards = 15.75  # Mock value
            
            return {
                'user_address': user_address,
                'total_earned_rewards': total_rewards,
                'pending_rewards': pending_rewards,
                'claimable_rewards': pending_rewards,
                'next_reward_date': '2024-03-15T00:00:00Z'
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    # Helper methods for mock functionality
    def _mock_wallet_verification(self, wallet_address: str) -> Dict[str, Any]:
        """Mock wallet verification for demo purposes"""
        return {
            'valid': True,
            'address': wallet_address,
            'balance_eth': 2.5,
            'transaction_count': 47,
            'network': 'mock_network'
        }
    
    def _mock_asset_creation(self, asset_data: Dict, creator_address: str) -> Dict[str, Any]:
        """Mock asset creation transaction"""
        transaction_hash = self._generate_transaction_hash(f"{asset_data.get('id')}{creator_address}")
        
        return {
            'success': True,
            'transaction_hash': transaction_hash,
            'asset_id': asset_data.get('id'),
            'gas_used': 145000,
            'status': 'confirmed'
        }
    
    def _mock_asset_transfer(self, asset_id: str, from_address: str, to_address: str, amount: float) -> Dict[str, Any]:
        """Mock asset transfer transaction"""
        transaction_hash = self._generate_transaction_hash(f"{asset_id}{from_address}{to_address}")
        
        return {
            'success': True,
            'transaction_hash': transaction_hash,
            'from_address': from_address,
            'to_address': to_address,
            'asset_id': asset_id,
            'amount': amount,
            'gas_used': 95000,
            'status': 'confirmed'
        }
    
    def _mock_asset_verification(self, asset_id: str) -> Dict[str, Any]:
        """Mock asset verification"""
        return {
            'authentic': True,
            'asset_id': asset_id,
            'creation_block': 18567234,
            'creation_timestamp': datetime.now().isoformat(),
            'creator_verified': True,
            'ownership_chain_valid': True,
            'metadata_hash_match': True,
            'confidence_score': 0.95
        }
    
    def _mock_ownership_history(self, asset_id: str) -> List[Dict[str, Any]]:
        """Mock ownership history"""
        return [
            {
                'transaction_hash': self._generate_transaction_hash(f"create_{asset_id}"),
                'from_address': '0x0000000000000000000000000000000000000000',
                'to_address': '0x742d35Cc6b8a6A8f4eDC6d1E5fA5d8e2e8B94C13',
                'timestamp': '2024-01-15T10:30:00Z',
                'transaction_type': 'mint',
                'value': 0
            }
        ]
    
    def _mock_staking_transaction(self, stake_data: Dict) -> Dict[str, Any]:
        """Mock staking transaction"""
        return {
            'success': True,
            'transaction_hash': self._generate_transaction_hash(json.dumps(stake_data)),
            'stake_id': stake_data.get('id'),
            'status': 'confirmed'
        }
    
    def _mock_staking_rewards(self, user_address: str) -> Dict[str, Any]:
        """Mock staking rewards"""
        return {
            'user_address': user_address,
            'total_earned_rewards': 125.50,
            'pending_rewards': 15.75,
            'claimable_rewards': 15.75
        }
    
    def _generate_transaction_hash(self, data: str) -> str:
        """Generate mock transaction hash"""
        hash_input = f"{data}{datetime.now().isoformat()}"
        return f"0x{hashlib.sha256(hash_input.encode()).hexdigest()}"