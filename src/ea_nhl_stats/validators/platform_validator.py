"""Platform validation for EA NHL stats."""

class PlatformValidator:
    """Validates gaming platform identifiers.
    
    This class maintains a list of valid gaming platforms and provides
    validation functionality.
    """
    
    def validate(self, platform: str) -> bool:
        """Validates if the given platform is supported.
        
        Args:
            platform: The platform identifier to validate.
            
        Returns:
            bool: True if the platform is valid, False otherwise.
        """
        valid_platforms = ["ps5", "ps4", "xbox-series-xs", "xboxone", "common-gen5"]
        return platform in valid_platforms 