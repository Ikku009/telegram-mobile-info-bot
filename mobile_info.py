 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/mobile_info.py b/mobile_info.py
index d4cf7ad774b396c54308ab94096806c372ebc9f1..5a70bf76e983f9cc4983823f34312824ae0875d0 100644
--- a/mobile_info.py
+++ b/mobile_info.py
@@ -1,116 +1,144 @@
 """
 Mobile Phone Information Retrieval Module
 Uses phonenumbers library to extract phone information
 """
 
 import phonenumbers
 from phonenumbers import geocoder, carrier
 import logging
 
 logger = logging.getLogger(__name__)
 
 
+def normalize_indian_number(phone_number: str) -> str:
+    """
+    Normalize common Indian local formats to E.164 style.
+
+    Examples:
+    - 9876543210 -> +919876543210
+    - 09876543210 -> +919876543210
+    - 919876543210 -> +919876543210
+    """
+    cleaned = phone_number.strip().replace(" ", "").replace("-", "")
+
+    if cleaned.startswith("+"):
+        return cleaned
+
+    if cleaned.startswith("0") and len(cleaned) == 11:
+        cleaned = cleaned[1:]
+
+    if len(cleaned) == 10 and cleaned.isdigit():
+        return f"+91{cleaned}"
+
+    if len(cleaned) == 12 and cleaned.startswith("91") and cleaned.isdigit():
+        return f"+{cleaned}"
+
+    return cleaned
+
+
 def get_phone_info(phone_number: str) -> dict:
     """
     Extract detailed information from a phone number
     
     Args:
         phone_number (str): Phone number in any format
         
     Returns:
         dict: Phone information or error message
     """
     try:
+        normalized_number = normalize_indian_number(phone_number)
+
         # Parse the phone number
-        # Try to parse with default region as US
-        parsed = phonenumbers.parse(phone_number, "US")
+        # Use India as default region for local Indian number formats
+        parsed = phonenumbers.parse(normalized_number, "IN")
         
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
-            'error': 'Invalid phone number format. Please use international format (e.g., +1234567890)',
+            'error': 'Invalid phone number format. Try Indian formats like 9876543210, 09123456789, or +919876543210.',
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
-        phonenumbers.NumberType.FIXED_LINE: '📞 Fixed Line',
-        phonenumbers.NumberType.MOBILE: '📱 Mobile',
-        phonenumbers.NumberType.FIXED_LINE_OR_MOBILE: '📞/📱 Fixed Line or Mobile',
-        phonenumbers.NumberType.TOLL_FREE: '🆓 Toll Free',
-        phonenumbers.NumberType.PREMIUM_RATE: '💰 Premium Rate',
-        phonenumbers.NumberType.SHARED_COST: '💸 Shared Cost',
-        phonenumbers.NumberType.VOIP: '🎤 VoIP',
-        phonenumbers.NumberType.PERSONAL_NUMBER: '👤 Personal',
-        phonenumbers.NumberType.PAGER: '📟 Pager',
-        phonenumbers.NumberType.UAN: '🔊 UAN',
-        phonenumbers.NumberType.VOICEMAIL: '🎙️ Voicemail',
-        phonenumbers.NumberType.UNKNOWN: '❓ Unknown'
+        phonenumbers.PhoneNumberType.FIXED_LINE: '📞 Fixed Line',
+        phonenumbers.PhoneNumberType.MOBILE: '📱 Mobile',
+        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: '📞/📱 Fixed Line or Mobile',
+        phonenumbers.PhoneNumberType.TOLL_FREE: '🆓 Toll Free',
+        phonenumbers.PhoneNumberType.PREMIUM_RATE: '💰 Premium Rate',
+        phonenumbers.PhoneNumberType.SHARED_COST: '💸 Shared Cost',
+        phonenumbers.PhoneNumberType.VOIP: '🎤 VoIP',
+        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: '👤 Personal',
+        phonenumbers.PhoneNumberType.PAGER: '📟 Pager',
+        phonenumbers.PhoneNumberType.UAN: '🔊 UAN',
+        phonenumbers.PhoneNumberType.VOICEMAIL: '🎙️ Voicemail',
+        phonenumbers.PhoneNumberType.UNKNOWN: '❓ Unknown'
     }
     
     return type_map.get(number_type, '❓ Unknown')
 
EOF
)
