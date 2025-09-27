import logging
from email_validator import validate_email, EmailNotValidError

logger = logging.getLogger(__name__)

def is_valid_email(email:str) -> bool:
    try:
        validate_email(email)
        return True
    except EmailNotValidError as e:
        logger.warning(f"Invalid email'{email}':{str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error validating email '{email}:{str(e)}'")
        return False