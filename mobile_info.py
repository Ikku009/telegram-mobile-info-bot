"""
Mobile Phone Information Retrieval Module
Uses phonenumbers library to extract phone information
"""

import phonenumbers
from phonenumbers import geocoder, carrier
import logging

logger = logging.getLogger(__name__)


def get_phone_info(phone_number: str) -> dict:
    """
    Extract detailed information from a phone number
    
    Args:
        phone_number (str): Phone number in any format
        
    Returns:
        dict: Phone information or error message
    """
    try:
        # Parse the phone number
        # Try to parse with default region as US
        parsed = phonenumbers.parse(phone_number, "US")
        
        # Validate the number
        is_valid = phonenumbers.is_valid_number(parsed)
        
        if not is_valid:
            return {
                'success': False,
                'error': 'Invalid phone number format',
                'valid': False
            }
        
        # Get country information
        country_code = parsed.country_code
        national_number = parsed.national_number
        
        # Format the number
        formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        
        # Get country name
        country = geocoder.country_name_for_number(parsed, "en")
        
        # Get region/state
        region = geocoder.description_for_number(parsed, "en")
        if not region:
            region = "Unknown"
        
        # Get carrier name
        carrier_name = carrier.name_for_number(parsed, "en")
        if not carrier_name:
            carrier_name = "Unknown"
        
        # Get number type
        number_type = get_number_type(parsed)
        
        return {
            'success': True,
            'formatted': formatted,
            'country': country,
            'region': region,
            'carrier': carrier_name,
            'type': number_type,
            'valid': is_valid,
            'country_code': country_code,
            'national_number': national_number
        }
        
    except phonenumbers.NumberParseException as e:
        logger.warning(f"Failed to parse phone number: {e}")
        return {
            'success': False,
            'error': 'Invalid phone number format. Please use international format (e.g., +1234567890)',
            'valid': False
        }
    except Exception as e:
        logger.error(f"Error retrieving phone info: {e}")
        return {
            'success': False,
            'error': f'Error: {str(e)}',
            'valid': False
        }


def get_number_type(parsed_number) -> str:
    """
    Get human-readable phone number type
    
    Args:
        parsed_number: Parsed phone number object
        
    Returns:
        str: Human-readable number type
    """
    number_type = phonenumbers.number_type(parsed_number)
    
    type_map = {
        phonenumbers.NumberType.FIXED_LINE: '📞 Fixed Line',
        phonenumbers.NumberType.MOBILE: '📱 Mobile',
        phonenumbers.NumberType.FIXED_LINE_OR_MOBILE: '📞/📱 Fixed Line or Mobile',
        phonenumbers.NumberType.TOLL_FREE: '🆓 Toll Free',
        phonenumbers.NumberType.PREMIUM_RATE: '💰 Premium Rate',
        phonenumbers.NumberType.SHARED_COST: '💸 Shared Cost',
        phonenumbers.NumberType.VOIP: '🎤 VoIP',
        phonenumbers.NumberType.PERSONAL_NUMBER: '👤 Personal',
        phonenumbers.NumberType.PAGER: '📟 Pager',
        phonenumbers.NumberType.UAN: '🔊 UAN',
        phonenumbers.NumberType.VOICEMAIL: '🎙️ Voicemail',
        phonenumbers.NumberType.UNKNOWN: '❓ Unknown'
    }
    
    return type_map.get(number_type, '❓ Unknown')
