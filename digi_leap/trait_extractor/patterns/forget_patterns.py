"""Remove entities when they meet these criteria."""
# Forget traits were supposed to be parts of a larger trait
FORGET = """
    us_county us_state us_state_or_county
    time_units month
""".split()
