class MatchTypeValidator:
    """Validates game match type identifiers.
    
    This class maintains a list of valid match types and provides
    validation functionality.
    """
    
    def validate(self, match_type: str) -> bool:
        """Validates if the given match type is supported.
        
        Args:
            match_type: The match type identifier to validate.
            
        Returns:
            bool: True if the match type is valid, False otherwise.
        """
        valid_match_types = ["gameType5", "gameType10", "club_private"]
        return match_type in valid_match_types 