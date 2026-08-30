import re


def normalize_kenyan_phone(phone):
    """
    Normalize a Kenyan phone number to:
    2547XXXXXXXX or 2541XXXXXXXX
    """

    if not phone:
        return None

    phone = str(phone).strip()

    # Remove spaces, hyphens and brackets
    phone = re.sub(
        r"[\s\-()]",
        "",
        phone,
    )

    # 0712345678 -> 254712345678
    if re.fullmatch(
        r"0[17]\d{8}",
        phone,
    ):
        return "254" + phone[1:]

    # +254712345678 -> 254712345678
    if re.fullmatch(
        r"\+254[17]\d{8}",
        phone,
    ):
        return phone[1:]

    # 254712345678
    if re.fullmatch(
        r"254[17]\d{8}",
        phone,
    ):
        return phone

    return None