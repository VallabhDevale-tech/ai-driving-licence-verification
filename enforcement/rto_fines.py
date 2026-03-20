RTO_FINES = {

    # -------------------------------------------------
    # 1. DRIVING WITHOUT VALID DRIVING LICENCE
    # -------------------------------------------------
    1: {
        "offence": "Driving without Valid Driving Licence",
        "valid_for": ["LICENCE", "COMBINED"],
        "sub_offences": {
            1: {
                "title": "Driving without Driving Licence",
                "fine": 5000,
                "section": "MV Act 2019 - Section 3",
                "severity": "High"
            },
            2: {
                "title": "Driving with an expired licence",
                "fine": 5000,
                "section": "MV Act 2019 - Section 3",
                "severity": "High"
            },
            3: {
                "title": "Driving without Registration Certificate (RC)",
                "fine": 5000,
                "section": "MV Act 2019 - Section 39",
                "severity": "High"
            },
            4: {
                "title": "Driving an unregistered vehicle",
                "fine": 5000,
                "section": "MV Act 2019 - Section 39",
                "severity": "High"
            },
            5: {
                "title": "Using fake licence / fake RC",
                "fine": 10000,
                "section": "MV Act 2019 - Section 192",
                "severity": "Critical"
            },
            6: {
                "title": "Allowing unauthorized person to drive",
                "fine": 5000,
                "section": "MV Act 2019 - Section 180",
                "severity": "High"
            }
        }
    },

    # -------------------------------------------------
    # 2. NO HIGH SECURITY REGISTRATION PLATE (HSRP)
    # -------------------------------------------------
    2: {
        "offence": "No High Security Registration Plate (HSRP)",
        "valid_for": ["HSRP", "COMBINED"],
        "sub_offences": {
            1: {
                "title": "HSRP not installed",
                "fine": 5000,
                "section": "MV Act 2019 - Section 39",
                "severity": "Medium"
            },
            2: {
                "title": "Damaged or tampered HSRP",
                "fine": 5000,
                "section": "MV Act 2019 - Section 39",
                "severity": "Medium"
            },
            3: {
                "title": "HSRP number mismatch",
                "fine": 5000,
                "section": "MV Act 2019 - Section 39",
                "severity": "High"
            }
        }
    },

    # -------------------------------------------------
    # 3. DRIVING WITHOUT VALID INSURANCE
    # -------------------------------------------------
    3: {
        "offence": "Driving without Valid Insurance",
        "valid_for": ["HSRP", "COMBINED"],
        "sub_offences": {
            1: {
                "title": "Insurance not available",
                "fine": 2000,
                "section": "MV Act 2019 - Section 146",
                "severity": "Medium"
            },
            2: {
                "title": "Insurance expired",
                "fine": 2000,
                "section": "MV Act 2019 - Section 146",
                "severity": "Medium"
            },
            3: {
                "title": "Fake or invalid insurance document",
                "fine": 4000,
                "section": "MV Act 2019 - Section 146",
                "severity": "High"
            }
        }
    },

    # -------------------------------------------------
    # 4. SUSPECTED DRUNK DRIVING
    # -------------------------------------------------
    4: {
        "offence": "Suspected Drunk Driving",
        "valid_for": ["LICENCE", "HSRP", "COMBINED"],
        "sub_offences": {
            1: {
                "title": "Alcohol detected above permissible limit",
                "fine": 10000,
                "section": "MV Act 2019 - Section 185",
                "severity": "Critical"
            },
            2: {
                "title": "Refusal to undergo breath analyzer test",
                "fine": 10000,
                "section": "MV Act 2019 - Section 185",
                "severity": "Critical"
            },
            3: {
                "title": "Repeat offence  drunk driving",
                "fine": 15000,
                "section": "MV Act 2019 - Section 185",
                "severity": "Critical"
            }
        }
    },

    # -------------------------------------------------
    # 5. NO VIOLATION
    # -------------------------------------------------
    5: {
        "offence": "No Violation",
        "valid_for": ["LICENCE", "HSRP", "COMBINED"],
        "sub_offences": {
            1: {
                "title": "All documents valid",
                "fine": 0,
                "section": "-",
                "severity": "None"
            }
        }
    }
}