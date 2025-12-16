def format_phone(phone):
    phone = phone.strip()

    if phone.startswith("07") or phone.startswith("01"):
        return "+254" + phone[1:]

    return phone
